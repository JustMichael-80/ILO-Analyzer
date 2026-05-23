import os
import json
import math
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
from google.genai import types
from tavily import TavilyClient

app = FastAPI(
    title="ChronoDyne Systems // ILO Analyzer Engine",
    description="Thermodynamic information triage via the Principle of Persistent Structurization",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your Vercel URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# CREDIBILITY SIEVE CONFIGURATION
# =====================================================================

DOMAIN_BLACKLIST = [
    "reddit.com/r/factorio", "reddit.com/r/gaming", "steamcommunity.com",
    "gamefaqs", "fandom.com", "twitch.tv", "youtube.com/watch?v=",
    "discord.gg", "resetera", "neogaf", "kotaku", "polygon"
]

DOMAIN_WHITELIST = [
    "reuters.com", "apnews.com", "bloomberg.com", "nytimes.com",
    "wsj.com", "politico.com", "bbc.com", "ieee.org", "sciencedirect.com",
    "gov", "edu", "mil", "epri.com", "pnnl.gov", "sandia.gov"
]

# =====================================================================
# SCHEMAS
# =====================================================================

class AnalysisRequest(BaseModel):
    claim: str = Field(..., description="The unverified target flux string to analyze")

class SourceMatrix(BaseModel):
    earliest_source_found: str
    source_diversity: str
    institutional_sources: List[str]
    grassroots_signals: str
    coverage_trajectory: str

class PPSVerdict(BaseModel):
    wildness_tier: int
    wildness_label: str
    wildness_justification: str
    signal_pattern: str
    signal_justification: str
    pps_assessment: str
    pps_justification: str
    local_credibility: str
    local_credibility_justification: str
    admissibility_bound: str
    admissibility_justification: str
    vanish_pattern: str
    vanish_justification: str
    suppression_signals: List[str]
    anomalous_patterns: List[str]
    source_analysis: SourceMatrix
    ilo_probability: float
    verdict: str
    verdict_summary: str
    what_would_confirm: str
    wtf_factor: str
    pi_final: float = Field(..., description="Final computed Persistence Ratio from structural accumulation metric")

# =====================================================================
# SYSTEM PROMPT
# =====================================================================

SYSTEM_PROMPT = """You are the P4 Gate processing module of the Information Laundering Operation (ILO) Analyzer, powered by the Principle of Persistent Structurization (PPS).

Analyze the submitted claim and return a structured verdict using the compiled search matrix provided.

TAXONOMY INTEGRITY PROTOCOL — use ONLY these exact values:
- wildness_label: 'Mundane' | 'Murky' | 'Mysterious' | 'Manufactured' | 'Manic' | 'Mythological'
- signal_pattern: 'True Signal' | 'ILO Laundered' | 'Narrative Spent' | 'Suppressed Real Event' | 'Anomalous Pattern' | 'Insufficient Data'
- pps_assessment: 'Structurizing' | 'Entropifying' | 'Hard Cutoff Detected' | 'Unknown'
- local_credibility: 'Threshold Met' | 'Threshold Not Met' | 'Unknown'
- admissibility_bound: 'Within Bound' | 'Bound Violated' | 'Approaching Limit'
- vanish_pattern: 'Natural Taper' | 'ILO Fade' | 'Hard Cutoff' | 'Still Active' | 'Unknown'
- source_diversity: 'High' | 'Medium' | 'Low' | 'Anomalously Uniform'
- coverage_trajectory: 'Expanding' | 'Contracting' | 'Stable' | 'Hard Cutoff' | 'Never Consolidated'
- verdict: 'Clean Signal' | 'Likely ILO' | 'Probable ILO' | 'Confirmed ILO Pattern' | 'Possible Suppression' | 'Anomalous - Investigate Further' | 'Insufficient Data'

SUPPRESSION LOGIC: If the computed Persistence Ratio (Π) is very low with no debunking trail present, weight your verdict toward 'Possible Suppression' or 'Suppressed Real Event' unless the search data explicitly contradicts this.

If structural markers are missing, drop to 'Insufficient Data' or 'Murky'. Do NOT invent custom taxonomy labels."""

# =====================================================================
# CREDIBILITY FILTER + DEDUPLICATION + Π CALCULATION
# (Ported directly from Colab PPSEngine)
# =====================================================================

def filter_and_score(results: list) -> list:
    """Applies domain blacklist pruning and credibility weight scoring."""
    clean = []
    seen_urls = set()
    for item in results:
        url = item.get("url", "").lower().strip()
        if url in seen_urls:
            continue
        seen_urls.add(url)
        if any(b in url for b in DOMAIN_BLACKLIST):
            continue
        score = 1.0
        if any(w in url for w in DOMAIN_WHITELIST):
            score += 1.5
        item["credibility_score"] = score
        clean.append(item)
    return clean


def calculate_pi(results: list) -> float:
    """
    Computes the Persistence Ratio (Π) — the core PPS thermodynamic metric.
    Incorporates named entity whitelist multiplier and logarithmic domain diversity bonus.
    """
    if not results:
        return 0.0

    named_sources = 0.0
    unverified_claims = 0.0
    weighted_total = 0.0

    for item in results:
        text = (item.get("content", "") + " " + item.get("title", "")).lower()
        url = item.get("url", "").lower()
        weight = item.get("credibility_score", 1.0)

        is_whitelisted = any(w in url for w in DOMAIN_WHITELIST)
        has_attribution = any(m in text for m in ["said", "reported by", "according to", "confirmed by"])

        # Named entity whitelist multiplier
        if is_whitelisted and has_attribution:
            weight *= 1.25

        weighted_total += weight

        if has_attribution:
            named_sources += weight
        if any(m in text for m in ["alleged", "unconfirmed", "anonymous", "rumor", "speculation"]):
            unverified_claims += weight

    structural_weight = named_sources / weighted_total if weighted_total > 0 else 0.0
    entropy_weight = unverified_claims / weighted_total if weighted_total > 0 else 0.0
    base_ratio = structural_weight / (1.0 + entropy_weight)

    try:
        unique_domains = len(set(
            r.get("url", "").split("/")[2]
            for r in results
            if "://" in r.get("url", "")
        ))
    except Exception:
        unique_domains = 1

    diversity_bonus = math.log1p(unique_domains) / 10.0
    return min(max(base_ratio + diversity_bonus, 0.0), 1.0)


def compress_matrix(results: list) -> list:
    """Trims each result to URL + credibility score + 300-char snippet for token efficiency."""
    return [
        {
            "url": r.get("url", ""),
            "score": r.get("credibility_score", 1.0),
            "snippet": r.get("content", "")[:300]
        }
        for r in results
    ]


def execute_search_cascade(claim: str, tavily: TavilyClient) -> tuple[list, float, bool, str]:
    """
    Runs the 5-phase sequential search cascade with graduated suppression detection.
    Returns: (compressed_payload, pi_final, is_suppressed, suppression_confidence)
    """
    phases = [
        {"query": f'"{claim}" primary source reports',              "depth": "basic",    "max": 3},
        {"query": f'{claim} local news reports journalism',          "depth": "basic",    "max": 3},
        {"query": f'{claim} local archives timeline historical',     "depth": "advanced", "max": 5},
        {"query": f'{claim} debunked verified factual truth',        "depth": "basic",    "max": 3},
        {"query": f'{claim} study research institutional corroboration', "depth": "basic", "max": 3},
    ]

    accumulated = []
    possible_suppression = False
    suppression_confidence = "None"
    cache = {}

    for idx, phase in enumerate(phases, 1):
        query, depth, max_r = phase["query"], phase["depth"], phase["max"]
        cache_key = f"{query}_{depth}_{max_r}"

        if cache_key in cache:
            phase_data = cache[cache_key]
        else:
            try:
                res = tavily.search(
                    query=query,
                    max_results=max_r,
                    include_answer=False,
                    search_depth=depth
                )
                phase_data = res.get("results", [])
                cache[cache_key] = phase_data
            except Exception:
                phase_data = []

        filtered = filter_and_score(phase_data)
        accumulated.extend(filtered)

        # Deduplicate for checkpoint Π calculation
        seen = set()
        checkpoint = []
        for r in accumulated:
            url = r.get("url", "").lower().strip()
            if url not in seen:
                seen.add(url)
                checkpoint.append(r)

        pi = calculate_pi(checkpoint)

        # Phase 1: absolute zero exit
        if idx == 1 and len(filtered) == 0:
            break

        # Phase 2: graduated suppression detection
        if idx == 2:
            if pi < 0.05:
                possible_suppression = True
                suppression_confidence = "High"
            elif pi < 0.12:
                possible_suppression = True
                suppression_confidence = "Medium"

        # Phase 3: early exit if cleanly entropifying with no suppression flag
        if idx == 3 and pi < 0.15 and not possible_suppression:
            break

    # Final deduplication
    seen = set()
    validated = []
    for r in accumulated:
        url = r.get("url", "").lower().strip()
        if url not in seen:
            seen.add(url)
            validated.append(r)

    pi_final = calculate_pi(validated)
    compressed = compress_matrix(validated)
    return compressed, pi_final, possible_suppression, suppression_confidence


# =====================================================================
# API ENDPOINT
# =====================================================================

@app.post("/analyze", response_model=PPSVerdict)
async def execute_triage_sieve(request: AnalysisRequest):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    tavily_key = os.environ.get("TAVILY_API_KEY")

    if not gemini_key or not tavily_key:
        raise HTTPException(
            status_code=500,
            detail="Environment configuration missing required credentials."
        )

    try:
        tavily = TavilyClient(api_key=tavily_key)
        ai = genai.Client(api_key=gemini_key)

        # Step 1: Execute search cascade with credibility filtering and Π calculation
        compressed_payload, pi_final, is_suppressed, suppression_confidence = execute_search_cascade(
            request.claim, tavily
        )

        # Step 2: Build user prompt with computed metrics
        user_prompt = f"""Analyze this narrative target: "{request.claim}"

Compressed and Scored Validation Data Matrix:
{json.dumps(compressed_payload, indent=2)}

Calculated Structural Accumulation Metrics:
- Final Persistence Ratio (Π): {pi_final:.4f}
- Physical Suppression Adaptive Branch Engaged: {is_suppressed}
- Suppression Confidence Metric: {suppression_confidence}

Output the final verdict strictly populating all schema parameters. Do not include conversational markup."""

        # Step 3: Fire to Gemini P4 Gate with schema enforcement
        response = ai.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.05,
                response_mime_type="application/json",
                response_schema=PPSVerdict,
            ),
        )

        # Step 4: Parse, inject computed Π, return validated object
        result = json.loads(response.text)
        result["pi_final"] = round(pi_final, 4)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline collapsed: {str(e)}")


@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "framework": "ChronoDyne P4 Gate",
        "version": "2.1.0"
    }
