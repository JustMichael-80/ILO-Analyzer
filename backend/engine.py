"""
ChronoDyne Systems // ILO Analyzer v4
Engine — FastAPI backend with physics-grounded Π and Γ metrics.

Architecture:
  1. Tavily 5-phase search cascade with Class A/B/C/D source filtering
  2. CDX-backed τ_observed measurement per source URL (parallel, timeout-safe)
  3. STOC-derived τ_predicted(S) from citation graph Shannon entropy → Π
  4. Geographic Entropy Γ from source scope distribution → spatial diffusion signal
  5. Π/Γ quadrant assignment — two-dimensional ILO diagnostic space
  6. Weather baseline saddle-point tracker (NOAA/open-meteo λ reference)
  7. Gemini P4 Gate verdict synthesis (GeminiVerdict schema — no dict fields)
  8. Authoritative physics injection post-synthesis

Version: 4.4.0
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import json
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
from gamma_calculator import compute_gamma, assign_quadrant, GammaResult
from report_generator import generate_report
from claim_classifier import classify_claim, ClaimClassification
from baseline_adjuster import compute_adjusted_diagnostics, adjusted_diagnostics_to_dict
from physical_baselines import compute_deviation_consensus
from signature_library import match_against_library, LibraryResult


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
    version="4.4.0",
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
    claim:     str  = Field(...,  description="The unverified target flux string to analyze")
    fetch_cdx: bool = Field(True, description="Enable Wayback Machine τ_observed measurement")


class SourceMatrix(BaseModel):
    earliest_source_found:  str
    source_diversity:       str
    institutional_sources:  List[str]
    grassroots_signals:     str
    coverage_trajectory:    str


class SaddlePoint(BaseModel):
    classification:  str
    delta:           Optional[float]
    lambda_weather:  float
    lambda_observed: Optional[float]
    baseline_source: str


class PiDiagnostics(BaseModel):
    pi_final:           float
    tau_observed_days:  float
    tau_predicted_days: float
    S:                  float
    E:                  float
    node_count:         int
    class_a_count:      int
    class_d_count:      int
    inverted_signal:    float
    pi_interpretation:  str
    saddle_point:       SaddlePoint


class GammaDiagnostics(BaseModel):
    gamma:                float
    h_geographic:         float
    h_expected:           float
    scope_distribution:   dict
    country_distribution: dict
    max_scope_rank:       int
    diffusion_velocity:   str
    quadrant:             str
    gamma_interpretation: str


# Slim schema for Gemini — excludes dict fields (additionalProperties not supported
# in Gemini Developer API mode). Physics diagnostics injected authoritatively post-synthesis.
class GeminiVerdict(BaseModel):
    wildness_tier:                   int
    wildness_label:                  str
    wildness_justification:          str
    signal_pattern:                  str
    signal_justification:            str
    pps_assessment:                  str
    pps_justification:               str
    local_credibility:               str
    local_credibility_justification: str
    admissibility_bound:             str
    admissibility_justification:     str
    vanish_pattern:                  str
    vanish_justification:            str
    suppression_signals:             List[str]
    anomalous_patterns:              List[str]
    source_analysis:                 SourceMatrix
    ilo_probability:                 float
    verdict:                         str
    verdict_summary:                 str
    what_would_confirm:              str
    wtf_factor:                      str


# Full response model — GeminiVerdict fields + authoritative physics blocks
class PPSVerdict(BaseModel):
    wildness_tier:                   int
    wildness_label:                  str
    wildness_justification:          str
    signal_pattern:                  str
    signal_justification:            str
    pps_assessment:                  str
    pps_justification:               str
    local_credibility:               str
    local_credibility_justification: str
    admissibility_bound:             str
    admissibility_justification:     str
    vanish_pattern:                  str
    vanish_justification:            str
    suppression_signals:             List[str]
    anomalous_patterns:              List[str]
    source_analysis:                 SourceMatrix
    ilo_probability:                 float
    verdict:                         str
    verdict_summary:                 str
    what_would_confirm:              str
    wtf_factor:                      str
    pi_diagnostics:                  PiDiagnostics
    gamma_diagnostics:               GammaDiagnostics
    signature_result:                Optional[dict] = None
    source_nodes:                    Optional[List[dict]] = None
    adjusted_diagnostics:            Optional[dict] = None


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the P4 Gate processing module of the ILO Analyzer, powered by the
Principle of Persistent Structurization (PPS) — ChronoDyne Systems.

You receive:
  1. The claim under analysis
  2. A compressed source matrix from a 5-phase Tavily search cascade
  3. A fully computed physics diagnostic block including:
     - Π (Persistence Ratio) = τ_observed / τ_predicted(S) derived from STOC
     - Γ (Geographic Entropy Ratio) = H_geographic / H_expected(t)
     - Π/Γ Quadrant — two-dimensional ILO diagnostic space
     - S (Shannon entropy of citation graph edge weight distribution)
     - E (system complexity — weighted node count)
     - Class A/B/C/D source breakdown
     - Inverted signal mass (Class D amplification — ILO indicator)
     - Saddle-point classification vs NOAA weather baseline
     - Geographic scope and country distribution

Your role is VERDICT SYNTHESIS only. Do not recompute Π or Γ. Accept the physics block as
ground truth and synthesize it with the qualitative source content to produce a structured verdict.

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
Π rules:
- Π < 0.35:       weight toward ILO Fade / Confirmed ILO Pattern
- Π 0.70-1.40:    weight toward Clean Signal / True Signal
- Π > 2.50:       weight toward artificial maintenance / bot-sustained narrative

Γ rules:
- Γ > 1.40:       geographic injection signal
- Γ 0.70-1.40:    organic geographic diffusion
- Γ < 0.70:       suppression signal
- diffusion_velocity = fast_injection:   corroborates coordinated ILO
- diffusion_velocity = slow_suppression: corroborates suppression verdict

Quadrant rules:
- Quadrant I (Π high, Γ high):  Confirmed ILO
- Quadrant II (Π high, Γ low):  Astroturfed local
- Quadrant III (Π low, Γ high): Viral suppression
- Quadrant IV (Π low, Γ low):   Suppressed real event

Other rules:
- saddle = ilo_fade:     corroborates ILO verdict
- saddle = maintained:   corroborates artificial maintenance
- inverted_signal > 2.0: flag Class D amplification as anomalous pattern
- class_a_count = 0:     local_credibility -> 'Threshold Not Met'
- class_d_count > class_a_count + class_b_count: strong ILO distribution signature

κ correction rules:
- pi_adjusted is Π corrected for cultural substrate class — use this as primary signal
- If ilo_survives_correction = True: artificial maintenance survives κ — strong ILO weight
- If ilo_survives_correction = False and pi_raw high: organic cultural persistence — reduce ILO weight
- claim_class informs wildness_tier: 'Suppressed Tech/Energy' → Tier 3-4 baseline
- memetic_fitness > 0.6 with organic Π_adj → corroborate 'Organic Conspiracy' signal_pattern
- evergreen_archetype present → note in verdict_summary as historical context
- adjusted_verdict_weight contains full interpretive guidance — incorporate into pps_justification
- lambda_consensus is multi-substrate physical reference — more reliable than single weather baseline

SUPPRESSION LOGIC: Π very low + no debunking trail = weight toward 'Possible Suppression'.

Do NOT invent custom taxonomy labels. Do NOT include conversational markup.
Output ONLY the JSON verdict object."""


# ── Search cascade ────────────────────────────────────────────────────────────

SEARCH_PHASES = [
    {"query_suffix": "primary source reports",                                                    "depth": "basic",    "max": 3},
    {"query_suffix": "local news reports journalism",                                              "depth": "basic",    "max": 3},
    {"query_suffix": "local archives timeline historical",                                         "depth": "advanced", "max": 5},
    {"query_suffix": "debunked verified factual truth",                                            "depth": "basic",    "max": 3},
    {"query_suffix": "study research institutional corroboration",                                 "depth": "basic",    "max": 3},
    {"query_suffix": "declassified FOIA government document official archive record",              "depth": "advanced", "max": 4},
]


def _filter_results(results: list) -> list:
    seen: set[str] = set()
    clean = []
    for item in results:
        url = item.get("url", "").lower().strip()
        if not url or url in seen:
            continue
        seen.add(url)
        record, trust = classify_domain(url)
        item["node_class"]  = record.node_class
        item["trust_score"] = trust.adjusted
        item["inverted"]    = trust.inverted
        item["captured"]    = trust.captured
        item["geo_scope"]   = record.geo_scope
        item["country"]     = record.country
        clean.append(item)
    return clean


def _compress(results: list) -> list:
    return [
        {
            "url":       r.get("url", ""),
            "class":     r.get("node_class", "?"),
            "trust":     round(r.get("trust_score", 0.0), 3),
            "inverted":  r.get("inverted", False),
            "geo_scope": r.get("geo_scope", "unknown"),
            "country":   r.get("country", "unknown"),
            "snippet":   r.get("content", "")[:300],
        }
        for r in results
    ]


def execute_search_cascade(claim: str, tavily: TavilyClient) -> list:
    cache_key = f"cascade:{claim.strip().lower()[:200]}"
    cached = cache.get("tavily", cache_key)
    if cached is not None:
        return cached

    accumulated: list = []
    seen_urls:   set  = set()

    for idx, phase in enumerate(SEARCH_PHASES, 1):
        query     = f'"{claim}" {phase["query_suffix"]}'
        depth     = phase["depth"]
        max_r     = phase["max"]

        try:
            res        = tavily.search(query=query, max_results=max_r,
                                       include_answer=False, search_depth=depth)
            phase_data = res.get("results", [])
        except Exception:
            phase_data = []

        filtered = _filter_results(phase_data)
        for item in filtered:
            url = item.get("url", "").lower().strip()
            if url not in seen_urls:
                seen_urls.add(url)
                accumulated.append(item)

        if idx == 1 and not accumulated:
            break
        if idx == 3:
            class_d_count = sum(1 for r in accumulated if r.get("inverted"))
            if class_d_count == len(accumulated) and len(accumulated) > 0:
                break

    cache.set("tavily", cache_key, accumulated)
    return accumulated


def _build_source_matrix_context(results: list) -> dict:
    institutional = [
        r["url"] for r in results
        if r.get("node_class") in (NODE_CLASS_A, NODE_CLASS_B) and not r.get("inverted")
    ]
    class_d_urls = [r["url"] for r in results if r.get("inverted")]
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
        raise HTTPException(status_code=500,
                            detail="Environment configuration missing required credentials.")

    try:
        tavily = TavilyClient(api_key=tavily_key)
        ai     = genai.Client(api_key=gemini_key)

        # ── Step 1: Search cascade ────────────────────────────────────────────
        results = execute_search_cascade(request.claim, tavily)

        # ── Step 1.5: Claim classification + κ baseline ───────────────────────
        loop = asyncio.get_event_loop()
        classification: ClaimClassification = await loop.run_in_executor(
            None,
            lambda: classify_claim(request.claim, gemini_key)
        )
        print(f"[ClaimClassifier] Class: {classification.claim_class_label} "
              f"κ={classification.kappa} confidence={classification.classifier_confidence:.0%}")

        # ── Step 2: Π computation (CDX parallel, timeout-safe) ────────────────
        pi_result: PiResult = await loop.run_in_executor(
            None,
            lambda: compute_pi(results, fetch_cdx=request.fetch_cdx)
        )

        # ── Step 3: Γ computation ─────────────────────────────────────────────
        gamma_result: GammaResult = compute_gamma(
            results,
            tau_observed_days=pi_result.tau_observed_days
        )
        quadrant = assign_quadrant(pi_result.pi, gamma_result.gamma)
        gamma_result.quadrant = quadrant

        # ── Step 3.5: Adjusted diagnostics (κ + consensus baseline) ──────────
        adj_diagnostics = compute_adjusted_diagnostics(
            pi_result=pi_result,
            classification=classification,
        )
        print(f"[BaselineAdjuster] Π_raw={pi_result.pi:.4f} "
              f"Π_adj={adj_diagnostics.pi_adjusted:.4f} "
              f"κ={adj_diagnostics.kappa:.2f} "
              f"λ_consensus={adj_diagnostics.lambda_consensus:.6f} "
              f"({adj_diagnostics.consensus_quality})")

        # ── Step 4: Signature library scan ───────────────────────────────────────
        library_result = match_against_library(pi_result, gamma_result)

        # ── Step 5: Build P4 Gate context ─────────────────────────────────────
        compressed = _compress(results)
        source_ctx = _build_source_matrix_context(results)

        physics_block = {
            "pi":                pi_result.pi,
            "tau_observed_days": pi_result.tau_observed_days,
            "tau_predicted_days":pi_result.tau_predicted_days,
            "S":                 pi_result.S,
            "E":                 pi_result.E,
            "node_count":        pi_result.node_count,
            "class_a_count":     pi_result.class_a_count,
            "class_d_count":     pi_result.class_d_count,
            "inverted_signal":   pi_result.inverted_signal,
            "pi_interpretation": pi_result.pi_interpretation,
            "saddle_point":      pi_result.saddle_point,
            "gamma":             gamma_result.gamma,
            "h_geographic":      gamma_result.h_geographic,
            "h_expected":        gamma_result.h_expected,
            "scope_distribution":gamma_result.scope_distribution,
            "country_distribution":gamma_result.country_distribution,
            "diffusion_velocity":gamma_result.diffusion_velocity,
            "quadrant":          quadrant,
            "gamma_interpretation":gamma_result.gamma_interpretation,
            "pi_adjusted":          adj_diagnostics.pi_adjusted,
            "kappa":                adj_diagnostics.kappa,
            "claim_class":          adj_diagnostics.claim_class_label,
            "memetic_fitness":      adj_diagnostics.memetic_fitness,
            "evergreen_archetype":  adj_diagnostics.evergreen_archetype,
            "ilo_survives_correction": adj_diagnostics.ilo_survives_correction,
            "adjusted_verdict_weight": adj_diagnostics.adjusted_verdict_weight,
            "lambda_consensus":     adj_diagnostics.lambda_consensus,
            "consensus_quality":    adj_diagnostics.consensus_quality,
        }

        user_prompt = f"""Claim under analysis: "{request.claim}"

=== PHYSICS DIAGNOSTIC BLOCK (ground truth — do not recompute) ===
{json.dumps(physics_block, indent=2)}

=== SOURCE CONTEXT ===
{json.dumps(source_ctx, indent=2)}

=== COMPRESSED SOURCE MATRIX ===
{json.dumps(compressed, indent=2)}

Synthesize the above into a structured verdict. Populate all schema fields.
Do not include conversational markup or preamble."""

        # ── Step 5: P4 Gate — Gemini verdict synthesis ────────────────────────
        # GeminiVerdict excludes dict fields (additionalProperties unsupported
        # in Gemini Developer API mode). Physics blocks injected post-synthesis.
        response = ai.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.05,
                response_mime_type="application/json",
                response_schema=GeminiVerdict,
            ),
        )

        raw = json.loads(response.text)

        # ── Step 6: Inject authoritative physics blocks ───────────────────────
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

        gamma_diagnostics = GammaDiagnostics(
            gamma=gamma_result.gamma,
            h_geographic=gamma_result.h_geographic,
            h_expected=gamma_result.h_expected,
            scope_distribution=gamma_result.scope_distribution,
            country_distribution=gamma_result.country_distribution,
            max_scope_rank=gamma_result.max_scope_rank,
            diffusion_velocity=gamma_result.diffusion_velocity,
            quadrant=quadrant,
            gamma_interpretation=gamma_result.gamma_interpretation,
        )

        raw["pi_diagnostics"]    = pi_diagnostics.model_dump()
        raw["gamma_diagnostics"] = gamma_diagnostics.model_dump()
        raw["signature_result"]  = {                                    # ← insert here
            "best_similarity":        library_result.best_similarity,
            "campaign_family":        library_result.campaign_family,
            "library_interpretation": library_result.library_interpretation,
            "matches": [
                {
                    "benchmark_id":  m.benchmark_id,
                    "campaign_type": m.campaign_type,
                    "quadrant":      m.quadrant,
                    "similarity":    m.similarity,
                    "match_tier":    m.match_tier,
                    "description":   m.description,
                }
                for m in library_result.matches
            ],
            "best_match": {
                "benchmark_id":  library_result.best_match.benchmark_id,
                "campaign_type": library_result.best_match.campaign_type,
                "quadrant":      library_result.best_match.quadrant,
                "similarity":    library_result.best_match.similarity,
                "match_tier":    library_result.best_match.match_tier,
                "description":   library_result.best_match.description,
            } if library_result.best_match else None,
        }
        raw["source_nodes"]      = pi_result.node_details
        raw["adjusted_diagnostics"] = adjusted_diagnostics_to_dict(adj_diagnostics)
        return PPSVerdict(**raw)

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"P4 Gate returned malformed JSON: {str(e)}")
    except Exception as e:
        import traceback
        print(f"[ChronoDyne ERROR] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Pipeline collapsed: {str(e)}")


@app.get("/health")
async def health_check():
    return {
        "status":    "online",
        "framework": "ChronoDyne P4 Gate",
        "version":   "4.4.0",
        "cache":     cache.stats(),
    }


@app.post("/cache/purge")
async def purge_cache():
    purged = cache.purge_expired()
    return {"purged_entries": purged, "stats": cache.stats()}

# ── Report endpoint ───────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    claim:     str  = Field(...,  description="The claim to analyze and report on")
    fetch_cdx: bool = Field(True, description="Enable Wayback Machine τ_observed measurement")


class ReportResponse(BaseModel):
    claim:    str
    report:   dict
    analyst:  dict
    markdown: str


@app.post("/report", response_model=ReportResponse)
async def generate_full_report(request: ReportRequest):
    """
    Full analysis + investigative report with Gemini analyst pass.
    Runs the complete /analyze pipeline then generates a structured
    markdown report with pattern hypotheses and investigative guidance.
    """

    gemini_key = os.environ.get("GEMINI_API_KEY")
    tavily_key = os.environ.get("TAVILY_API_KEY")

    if not gemini_key or not tavily_key:
        raise HTTPException(status_code=500,
                            detail="Environment configuration missing required credentials.")

    try:
        # Run full analysis pipeline
        analysis_request = AnalysisRequest(claim=request.claim, fetch_cdx=request.fetch_cdx)
        verdict = await execute_triage_sieve(analysis_request)
        verdict_dict = verdict.model_dump()

        # Generate report with Gemini analyst pass
        result = await generate_report(request.claim, verdict_dict, gemini_key)

        return ReportResponse(
            claim=request.claim,
            report=result["report"],
            analyst=result["analyst"],
            markdown=result["markdown"],
        )

    except Exception as e:
        import traceback
        print(f"[ChronoDyne REPORT ERROR] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

