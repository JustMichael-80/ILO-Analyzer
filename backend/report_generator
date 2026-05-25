"""
ChronoDyne Systems // ILO Analyzer v4.2
Report Generator

Assembles a full diagnostic report from a completed PPSVerdict and passes it
to Gemini for investigative pattern analysis with confidence-rated hypotheses.

Two-stage design:
  Stage 1: Deterministic report assembly — structured markdown from physics block,
           source matrix, and verdict. No LLM involvement. Ground truth only.

  Stage 2: Gemini Analyst Pass — the compiled report is passed to a separate
           Gemini instance acting as an investigative analyst, not a verdict
           synthesizer. Different prompt, higher temperature, output includes:
             - Narrative summary for non-technical readers
             - Pattern hypotheses rated by statistical confidence
             - Most likely campaign type classification
             - Suggested investigative next steps
             - Red flags and anomalous observations
             - Recommended follow-up claims to test

The physics block constrains the hallucination space. Gemini reasons over
verified measurements, not raw search results.
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional

from google import genai
from google.genai import types


# ── Analyst prompt ────────────────────────────────────────────────────────────

ANALYST_PROMPT = """You are a senior intelligence analyst and disinformation researcher reviewing a completed ILO Analyzer diagnostic report.

The physics block below contains verified, deterministically computed measurements. Do not recompute or contradict them. Reason over them as an analyst would reason over forensic evidence.

Your output must be a JSON object with these exact fields:

{
  "executive_summary": "2-3 sentence plain-language summary for a non-technical reader",
  "campaign_type": "most likely campaign classification (e.g. State-Sponsored IO, Domestic Astroturfing, Organic Conspiracy, Suppressed Legitimate Event, Ambiguous)",
  "campaign_confidence": 0.0-1.0,
  "pattern_hypotheses": [
    {
      "hypothesis": "specific testable claim about what is happening",
      "confidence": 0.0-1.0,
      "supporting_evidence": "which physics metrics support this",
      "contradicting_evidence": "what would need to be true to rule this out"
    }
  ],
  "actor_profile": "description of likely actor type based on signature (state, domestic political, commercial, organic community)",
  "red_flags": ["list of specific anomalous observations from the physics block"],
  "investigative_next_steps": ["prioritized list of follow-up actions an analyst should take"],
  "follow_up_claims": ["2-3 related claims worth running through the analyzer to test campaign scope"],
  "confidence_ceiling": "what evidence would be needed to increase confidence beyond current level",
  "analyst_notes": "any additional observations, caveats, or context an experienced analyst would flag"
}

Be specific. Cite actual metric values. Do not use generic language.
Output ONLY the JSON object. No preamble, no markdown fences."""


# ── Report assembly ───────────────────────────────────────────────────────────

def assemble_report(claim: str, verdict: dict) -> dict:
    """
    Assemble a structured report dict from a PPSVerdict.
    Pure deterministic assembly — no LLM involved at this stage.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    pi_diag    = verdict.get("pi_diagnostics", {})
    gamma_diag = verdict.get("gamma_diagnostics", {})
    saddle     = pi_diag.get("saddle_point", {})
    source     = verdict.get("source_analysis", {})

    return {
        "meta": {
            "claim":         claim,
            "generated_at":  now,
            "engine_version": "4.2.0",
            "framework":     "ChronoDyne Systems // PPS · STOC · Π · Γ",
        },
        "verdict": {
            "classification":    verdict.get("verdict", ""),
            "ilo_probability":   verdict.get("ilo_probability", 0),
            "wildness_tier":     verdict.get("wildness_tier", 0),
            "wildness_label":    verdict.get("wildness_label", ""),
            "signal_pattern":    verdict.get("signal_pattern", ""),
            "pps_assessment":    verdict.get("pps_assessment", ""),
            "admissibility":     verdict.get("admissibility_bound", ""),
            "vanish_pattern":    verdict.get("vanish_pattern", ""),
            "verdict_summary":   verdict.get("verdict_summary", ""),
            "wtf_factor":        verdict.get("wtf_factor", ""),
            "what_would_confirm":verdict.get("what_would_confirm", ""),
        },
        "pi_metrics": {
            "pi":                pi_diag.get("pi_final", 0),
            "tau_observed_days": pi_diag.get("tau_observed_days", 0),
            "tau_predicted_days":pi_diag.get("tau_predicted_days", 0),
            "S":                 pi_diag.get("S", 0),
            "E":                 pi_diag.get("E", 0),
            "interpretation":    pi_diag.get("pi_interpretation", ""),
            "saddle": {
                "classification":  saddle.get("classification", "no_data"),
                "delta":           saddle.get("delta"),
                "lambda_observed": saddle.get("lambda_observed"),
                "lambda_weather":  saddle.get("lambda_weather", 0.12),
                "baseline_source": saddle.get("baseline_source", "noaa_fallback"),
            },
        },
        "gamma_metrics": {
            "gamma":              gamma_diag.get("gamma", 0),
            "h_geographic":       gamma_diag.get("h_geographic", 0),
            "h_expected":         gamma_diag.get("h_expected", 0),
            "diffusion_velocity": gamma_diag.get("diffusion_velocity", ""),
            "quadrant":           gamma_diag.get("quadrant", ""),
            "scope_distribution": gamma_diag.get("scope_distribution", {}),
            "country_distribution": gamma_diag.get("country_distribution", {}),
            "interpretation":     gamma_diag.get("gamma_interpretation", ""),
        },
        "source_profile": {
            "node_count":         pi_diag.get("node_count", 0),
            "class_a_count":      pi_diag.get("class_a_count", 0),
            "class_d_count":      pi_diag.get("class_d_count", 0),
            "inverted_signal":    pi_diag.get("inverted_signal", 0),
            "source_diversity":   source.get("source_diversity", ""),
            "coverage_trajectory":source.get("coverage_trajectory", ""),
            "earliest_signal":    source.get("earliest_source_found", ""),
            "grassroots":         source.get("grassroots_signals", ""),
            "institutional":      source.get("institutional_sources", []),
        },
        "anomalous_patterns":  verdict.get("anomalous_patterns", []),
        "suppression_signals": verdict.get("suppression_signals", []),
    }


def render_markdown(report: dict, analyst: dict) -> str:
    """
    Render the full report as markdown for display and download.
    """
    meta    = report["meta"]
    verdict = report["verdict"]
    pi      = report["pi_metrics"]
    gamma   = report["gamma_metrics"]
    sources = report["source_profile"]
    saddle  = pi["saddle"]

    lines = [
        f"# ChronoDyne Systems // ILO Analyzer Report",
        f"",
        f"**Claim:** {meta['claim']}",
        f"**Generated:** {meta['generated_at']}",
        f"**Engine:** {meta['engine_version']} · {meta['framework']}",
        f"",
        f"---",
        f"",
        f"## Diagnostic Decision",
        f"",
        f"**Verdict:** {verdict['classification']}",
        f"**ILO Probability:** {verdict['ilo_probability']}%",
        f"**Wildness:** Tier {verdict['wildness_tier']} // {verdict['wildness_label']}",
        f"**Signal Pattern:** {verdict['signal_pattern']}",
        f"**Thermodynamic Trend:** {verdict['pps_assessment']}",
        f"**Vanish Pattern:** {verdict['vanish_pattern']}",
        f"",
        f"> {verdict['verdict_summary']}",
        f"",
    ]

    if verdict.get("wtf_factor") and "no significant" not in verdict["wtf_factor"].lower():
        lines += [
            f"**⚡ Core Anomaly:** {verdict['wtf_factor']}",
            f"",
        ]

    lines += [
        f"---",
        f"",
        f"## Physics Diagnostic Block",
        f"",
        f"### Persistence Ratio (Π) — Temporal Anomaly",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Π = τ_obs / τ_pred(S) | **{pi['pi']:.4f}** |",
        f"| τ_observed | {pi['tau_observed_days']} days |",
        f"| τ_predicted(S) | {pi['tau_predicted_days']} days |",
        f"| S (Shannon entropy) | {pi['S']:.4f} |",
        f"| E (system complexity) | {pi['E']:.4f} |",
        f"",
        f"**Interpretation:** {pi['interpretation']}",
        f"",
        f"**Saddle-Point // NOAA Weather Baseline**",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Classification | {saddle['classification']} |",
        f"| λ_observed | {saddle.get('lambda_observed', 'N/A')} /day |",
        f"| λ_weather | {saddle['lambda_weather']} /day |",
        f"| Δ | {saddle.get('delta', 'N/A')} |",
        f"| Baseline | {saddle['baseline_source']} |",
        f"",
        f"---",
        f"",
        f"### Geographic Entropy (Γ) — Spatial Diffusion Anomaly",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Γ = H_geo / H_exp(t) | **{gamma['gamma']:.4f}** |",
        f"| H_geographic | {gamma['h_geographic']:.4f} |",
        f"| H_expected(t) | {gamma['h_expected']:.4f} |",
        f"| Diffusion Velocity | {gamma['diffusion_velocity']} |",
        f"| Π/Γ Quadrant | **{gamma['quadrant']}** |",
        f"",
        f"**Scope Distribution:**",
    ]

    scope_dist = gamma.get("scope_distribution") or {}
    for scope, count in scope_dist.items():
        lines.append(f"- {scope}: {count}")

    country_dist = gamma.get("country_distribution") or {}
    if country_dist:
        lines += [f"", f"**Country Distribution:**"]
        for country, count in sorted(country_dist.items(), key=lambda x: -x[1]):
            lines.append(f"- {country}: {count}")

    lines += [
        f"",
        f"**Interpretation:** {gamma['interpretation']}",
        f"",
        f"---",
        f"",
        f"## Source Profile",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Nodes | {sources['node_count']} |",
        f"| Class A (Primary) | {sources['class_a_count']} |",
        f"| Class D (Propagation) | {sources['class_d_count']} |",
        f"| Inverted Signal Mass | {sources['inverted_signal']:.4f} |",
        f"| Source Diversity | {sources['source_diversity']} |",
        f"| Coverage Trajectory | {sources['coverage_trajectory']} |",
        f"| Earliest Signal | {sources['earliest_signal']} |",
        f"",
    ]

    if sources.get("institutional"):
        lines += [f"**Institutional Sources:**"]
        for src in sources["institutional"][:5]:
            lines.append(f"- {src}")
        lines.append("")

    if report.get("anomalous_patterns"):
        lines += [f"**Anomalous Patterns:**"]
        for p in report["anomalous_patterns"]:
            lines.append(f"- {p}")
        lines.append("")

    lines += [
        f"---",
        f"",
        f"## Analyst Assessment",
        f"",
        f"**Executive Summary**",
        f"",
        f"{analyst.get('executive_summary', '')}",
        f"",
        f"**Campaign Classification:** {analyst.get('campaign_type', '')} (confidence: {analyst.get('campaign_confidence', 0):.0%})",
        f"",
        f"**Actor Profile:** {analyst.get('actor_profile', '')}",
        f"",
    ]

    hypotheses = analyst.get("pattern_hypotheses") or []
    if hypotheses:
        lines += [f"### Pattern Hypotheses", f""]
        for i, h in enumerate(hypotheses, 1):
            lines += [
                f"**{i}. {h.get('hypothesis', '')}** (confidence: {h.get('confidence', 0):.0%})",
                f"",
                f"- *Supporting:* {h.get('supporting_evidence', '')}",
                f"- *Contradicting:* {h.get('contradicting_evidence', '')}",
                f"",
            ]

    red_flags = analyst.get("red_flags") or []
    if red_flags:
        lines += [f"### Red Flags", f""]
        for flag in red_flags:
            lines.append(f"- {flag}")
        lines.append("")

    next_steps = analyst.get("investigative_next_steps") or []
    if next_steps:
        lines += [f"### Investigative Next Steps", f""]
        for i, step in enumerate(next_steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    follow_up = analyst.get("follow_up_claims") or []
    if follow_up:
        lines += [f"### Follow-Up Claims to Test", f""]
        for claim in follow_up:
            lines.append(f"- {claim}")
        lines.append("")

    if analyst.get("confidence_ceiling"):
        lines += [
            f"### Confidence Ceiling",
            f"",
            f"{analyst['confidence_ceiling']}",
            f"",
        ]

    if analyst.get("analyst_notes"):
        lines += [
            f"### Analyst Notes",
            f"",
            f"{analyst['analyst_notes']}",
            f"",
        ]

    lines += [
        f"---",
        f"",
        f"**What Would Confirm:** {verdict.get('what_would_confirm', '')}",
        f"",
        f"---",
        f"",
        f"*ChronoDyne Systems · PPS · STOC · Π = τ_obs/τ_pred(S) · Γ = H_geo/H_exp(t)*",
        f"*https://doi.org/10.6084/m9.figshare.32307087*",
    ]

    return "\n".join(lines)


async def generate_report(claim: str, verdict: dict, gemini_key: str) -> dict:
    """
    Full report generation pipeline.

    Returns:
      {
        "report":    dict,      # structured report
        "analyst":   dict,      # Gemini analyst output
        "markdown":  str,       # full rendered markdown
      }
    """
    report = assemble_report(claim, verdict)

    ai = genai.Client(api_key=gemini_key)

    analyst_input = f"""ILO ANALYZER DIAGNOSTIC REPORT
================================

Claim: {claim}

PHYSICS BLOCK:
{json.dumps({
    "pi":                report["pi_metrics"]["pi"],
    "tau_observed_days": report["pi_metrics"]["tau_observed_days"],
    "tau_predicted_days":report["pi_metrics"]["tau_predicted_days"],
    "saddle":            report["pi_metrics"]["saddle"],
    "gamma":             report["gamma_metrics"]["gamma"],
    "diffusion_velocity":report["gamma_metrics"]["diffusion_velocity"],
    "quadrant":          report["gamma_metrics"]["quadrant"],
    "scope_distribution":report["gamma_metrics"]["scope_distribution"],
    "country_distribution":report["gamma_metrics"]["country_distribution"],
}, indent=2)}

VERDICT BLOCK:
{json.dumps(report["verdict"], indent=2)}

SOURCE PROFILE:
{json.dumps(report["source_profile"], indent=2)}

ANOMALOUS PATTERNS:
{json.dumps(report["anomalous_patterns"], indent=2)}
"""

    response = ai.models.generate_content(
        model="gemini-2.5-flash",
        contents=analyst_input,
        config=types.GenerateContentConfig(
            system_instruction=ANALYST_PROMPT,
            temperature=0.20,
            response_mime_type="application/json",
        ),
    )

    try:
        analyst = json.loads(response.text)
    except Exception:
        analyst = {
            "executive_summary":     "Analyst pass failed — physics block available above.",
            "campaign_type":         "Unknown",
            "campaign_confidence":   0.0,
            "pattern_hypotheses":    [],
            "actor_profile":         "Unavailable",
            "red_flags":             [],
            "investigative_next_steps": [],
            "follow_up_claims":      [],
            "confidence_ceiling":    "Unavailable",
            "analyst_notes":         "Gemini analyst pass returned malformed JSON.",
        }

    markdown = render_markdown(report, analyst)

    return {
        "report":   report,
        "analyst":  analyst,
        "markdown": markdown,
    }
