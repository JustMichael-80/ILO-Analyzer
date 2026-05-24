"""
ChronoDyne Systems // ILO Analyzer v4
Engine — FastAPI backend with physics-grounded Persistence Ratio.

Architecture:
  1. Tavily 5-phase search cascade with Class A/B/C/D source filtering
  2. CDX-backed τ_observed measurement per source URL
  3. STOC-derived τ_predicted(S) from citation graph Shannon entropy
  4. Weather baseline saddle-point tracker (NOAA/open-meteo λ reference)
  5. Gemini P4 Gate verdict with full diagnostic context injection

Version: 4.0.0
"""

import os
sys.path.insert(0, os.path.dirname(__file__))
import json
import time
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from google import genai
from google.genai import types
from tavily import TavilyClient

import cache
from bias_table import classify_domain, NODE_CLASS_D, NODE_CLASS_A, NODE_CLASS_B
from pi_calculator import compute_pi, PiResult


# ── Startup ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    cache.initialize_db()
    purged = cache.purge_expired()
    print(f"[ChronoDyne] Cache initialized. Purged {purged} expired entries.")
    yield


app = FastAPI(
    title="ChronoDyne Systems // ILO Analyzer Engine",
    description="Thermodynamic information triage via the Principle of Persistent Structurization",
    version="4.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    claim: str = Field(..., description="The unverified target flux string to analyze")
    fetch_cdx: bool = Field(True, description="Enable Wayback Machine τ_observed measurement")


class SourceMatrix(BaseModel):
    earliest_source_found:  str
    source_diversity:       str
    institutional_sources:  List[str]
    grassroots_signals:     str
    coverage_trajectory:    str


class SaddlePoint(BaseModel):
    classification:   str    # organic | ilo_fade | maintained | no_data
    delta:            Optional[float]
    lambda_weather:   float
    lambda_observed:  Optional[float]
    baseline_source:  str


class PiDiagnostics(BaseModel):
    pi_final:            float
    tau_observed_days:   float
    tau_predicted_days:  float
    S:                   float
    E:                   float
    node_count:          int
    class_a_count:       int
    class_d_count:       int
    inverted_signal:     float
    pi_interpretation:   str
    saddle_point:        SaddlePoint


class PPSVerdict(BaseModel):
    # Taxonomy fields (P4 Gate enforced)
    wildness_tier:              int
    wildness_label:             str
    wildness_justification:     str
    signal_pattern:             str
    signal_justification:       str
    pps_assessment:             str
    pps_justification:          str
    local_credibility:          str
    local_credibility_justification: str
    admissibility_bound:        str
    admissibility_justification: str
    vanish_pattern:             str
    vanish_justification:       str
    suppression_signals:        List[str]
    anomalous_patterns:         List[str]
    source_analysis:            SourceMatrix
    ilo_probability:            float
    verdict:                    str
    verdict_summary:            str
    what_would_confirm:         str
    wtf_factor:                 str

    # Physics diagnostics (computed, not LLM-generated)
    pi_diagnostics:             PiDiagnostics


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the P4 Gate processing module of the ILO Analyzer, powered by the
Principle of Persistent Structurization (PPS) — ChronoDyne Systems.

You receive:
  1. The claim under analysis
  2. A compressed source matrix from a 5-phase Tavily search cascade
  3. A fully computed physics diagnostic block including:
     - Π (Persistence Ratio) = τ_observed / τ_predicted(S) derived from STOC
     - S (Shannon entropy of citation graph edge weight distribution)
     - E (system complexity — weighted node count)
     - Class A/B/C/D source breakdown
     - Inverted signal mass (Class D amplification — ILO indicator)
     - Saddle-point classification vs NOAA weather baseline (organic | ilo_fade | maintained | no_data)

Your role is VERDICT SYNTHESIS only. Do not recompute Π. Accept the physics block as ground truth
and synthesize it with the qualitative source content to produce a structured verdict.

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

PHYSICS INTEGRATION RULES:
- Π < 0.35:  weight toward ILO Fade / Confirmed ILO Pattern
- Π 0.70–1.40: weight toward Clean Signal / True Signal
- Π > 2.50:  weight toward artificial maintenance / bot-sustained narrative
- saddle = ilo_fade: corroborates ILO verdict
- saddle = maintained: corroborates artificial maintenance
- inverted_signal > 2.0: flag Class D amplification as anomalous pattern
- class_a_count = 0: local_credibility → 'Threshold Not Met'
- class_d_count > class_a_count + class_b_count: strong ILO distribution signature

SUPPRESSION LOGIC: Π very low + no debunking trail = weight toward 'Possible Suppression'.

Do NOT invent custom taxonomy labels. Do NOT include conversational markup.
Output ONLY the JSON verdict object."""


# ── Search cascade ────────────────────────────────────────────────────────────

SEARCH_PHASES = [
    {"query_suffix": "primary source reports",                "depth": "basic",    "max": 3},
    {"query_suffix": "local news reports journalism",          "depth": "basic",    "max": 3},
    {"query_suffix": "local archives timeline historical",     "depth": "advanced", "max": 5},
    {"query_suffix": "debunked verified factual truth",        "depth": "basic",    "max": 3},
    {"query_suffix": "study research institutional corroboration", "depth": "basic","max": 3},
]


def _filter_results(results: list) -> list:
    """
    Deduplicate and apply bias-table classification to raw Tavily results.
    Attaches node_class and trust_score to each result for downstream use.
    """
    seen: set[str] = set()
    clean = []
    for item in results:
        url = item.get("url", "").lower().strip()
        if not url or url in seen:
            continue
        seen.add(url)

        record, trust = classify_domain(url)
        item["node_class"]   = record.node_class
        item["trust_score"]  = trust.adjusted
        item["inverted"]     = trust.inverted
        item["captured"]     = trust.captured
        clean.append(item)

    return clean


def _compress(results: list) -> list:
    """Token-efficient payload for P4 Gate prompt."""
    return [
        {
            "url":        r.get("url", ""),
            "class":      r.get("node_class", "?"),
            "trust":      round(r.get("trust_score", 0.0), 3),
            "inverted":   r.get("inverted", False),
            "snippet":    r.get("content", "")[:300],
        }
        for r in results
    ]


def execute_search_cascade(claim: str, tavily: TavilyClient) -> list:
    """
    5-phase Tavily search cascade with bias-table filtering.
    Returns deduplicated, classified result list.
    """
    accumulated: list = []
    seen_urls:   set  = set()
    cache_store: dict = {}

    for idx, phase in enumerate(SEARCH_PHASES, 1):
        query     = f'"{claim}" {phase["query_suffix"]}'
        depth     = phase["depth"]
        max_r     = phase["max"]
        cache_key = f"tavily:{query}:{depth}:{max_r}"

        if cache_key in cache_store:
            phase_data = cache_store[cache_key]
        else:
            try:
                res        = tavily.search(query=query, max_results=max_r,
                                           include_answer=False, search_depth=depth)
                phase_data = res.get("results", [])
                cache_store[cache_key] = phase_data
            except Exception:
                phase_data = []

        filtered = _filter_results(phase_data)

        for item in filtered:
            url = item.get("url", "").lower().strip()
            if url not in seen_urls:
                seen_urls.add(url)
                accumulated.append(item)

        # Early exit: Phase 1 total miss
        if idx == 1 and not accumulated:
            break

        # Early exit: Phase 3 — all Class C/D, no suppression indicators
        if idx == 3:
            class_d_count = sum(1 for r in accumulated if r.get("inverted"))
            if class_d_count == len(accumulated) and len(accumulated) > 0:
                break

    return accumulated


# ── Source matrix builder (for P4 Gate context) ───────────────────────────────

def _build_source_matrix_context(results: list) -> dict:
    """Qualitative source summary for P4 Gate prompt context."""
    institutional = [
        r["url"] for r in results
        if r.get("node_class") in (NODE_CLASS_A, NODE_CLASS_B) and not r.get("inverted")
    ]
    class_d_urls = [r["url"] for r in results if r.get("inverted")]

    # Diversity: unique domains
    domains = set()
    for r in results:
        url = r.get("url", "")
        if "://" in url:
            domains.add(url.split("/")[2])

    if len(domains) >= 5:
        diversity = "High"
    elif len(domains) >= 3:
        diversity = "Medium"
    elif len(domains) >= 1:
        diversity = "Low"
    else:
        diversity = "Anomalously Uniform"

    # Anomalously uniform override: if all results from same 1-2 domains
    if len(domains) <= 2 and len(results) >= 4:
        diversity = "Anomalously Uniform"

    return {
        "institutional_count":  len(institutional),
        "class_d_count":        len(class_d_urls),
        "domain_count":         len(domains),
        "diversity_label":      diversity,
        "institutional_sample": institutional[:5],
        "class_d_sample":       class_d_urls[:3],
    }


# ── API endpoints ─────────────────────────────────────────────────────────────

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
        ai     = genai.Client(api_key=gemini_key)

        # ── Step 1: Search cascade ────────────────────────────────────────────
        results = execute_search_cascade(request.claim, tavily)

        # ── Step 2: Physics Π computation ─────────────────────────────────────
        # CDX calls are I/O bound — run in thread pool to avoid blocking
        loop     = asyncio.get_event_loop()
        pi_result: PiResult = await loop.run_in_executor(
            None,
            lambda: compute_pi(results, fetch_cdx=request.fetch_cdx)
        )

        # ── Step 3: Build context for P4 Gate ────────────────────────────────
        compressed   = _compress(results)
        source_ctx   = _build_source_matrix_context(results)

        pi_block = {
            "pi":                 pi_result.pi,
            "tau_observed_days":  pi_result.tau_observed_days,
            "tau_predicted_days": pi_result.tau_predicted_days,
            "S":                  pi_result.S,
            "E":                  pi_result.E,
            "node_count":         pi_result.node_count,
            "class_a_count":      pi_result.class_a_count,
            "class_d_count":      pi_result.class_d_count,
            "inverted_signal":    pi_result.inverted_signal,
            "pi_interpretation":  pi_result.pi_interpretation,
            "saddle_point":       pi_result.saddle_point,
        }

        user_prompt = f"""Claim under analysis: "{request.claim}"

=== PHYSICS DIAGNOSTIC BLOCK (ground truth — do not recompute) ===
{json.dumps(pi_block, indent=2)}

=== SOURCE CONTEXT ===
{json.dumps(source_ctx, indent=2)}

=== COMPRESSED SOURCE MATRIX ===
{json.dumps(compressed, indent=2)}

Synthesize the above into a structured verdict. Populate all schema fields.
Do not include conversational markup or preamble."""

        # ── Step 4: P4 Gate — Gemini verdict synthesis ────────────────────────
        response = ai.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.05,
                response_mime_type="application/json",
            ),
        )

        raw = json.loads(response.text)

        # ── Step 5: Inject computed physics block (authoritative) ─────────────
        saddle = pi_result.saddle_point
        pi_diagnostics = PiDiagnostics(
            pi_final=pi_result.pi,
            tau_observed_days=pi_result.tau_observed_days,
            tau_predicted_days=pi_result.tau_predicted_days,
            S=pi_result.S,
            E=pi_result.E,
            node_count=pi_result.node_count,
            class_a_count=pi_result.class_a_count,
            class_d_count=pi_result.class_d_count,
            inverted_signal=pi_result.inverted_signal,
            pi_interpretation=pi_result.pi_interpretation,
            saddle_point=SaddlePoint(
                classification=saddle.get("classification", "no_data"),
                delta=saddle.get("delta"),
                lambda_weather=saddle.get("lambda_weather", 0.12),
                lambda_observed=saddle.get("lambda_observed"),
                baseline_source=saddle.get("baseline_source", "noaa_fallback"),
            ),
        )

        # Merge: LLM verdict + authoritative physics
        raw["pi_diagnostics"] = pi_diagnostics.model_dump()
        return PPSVerdict(**raw)

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"P4 Gate returned malformed JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline collapsed: {str(e)}")


@app.get("/health")
async def health_check():
    stats = cache.stats()
    return {
        "status":    "online",
        "framework": "ChronoDyne P4 Gate",
        "version":   "4.0.0",
        "cache":     stats,
    }


@app.post("/cache/purge")
async def purge_cache():
    """Manual cache purge endpoint — admin use."""
    purged = cache.purge_expired()
    return {"purged_entries": purged, "stats": cache.stats()}
