"""
ChronoDyne Systems // ILO Analyzer v4
Persistence Ratio (Π) Calculator

Implements Π = τ_observed / τ_predicted(S) derived from the
Scale-Timescale Optimization Corollary (STOC).

From the FIIH (Stewart, 2026):
  τ*(S) = argmin_τ [ σ(T,τ) / Φ(T,τ) ]
  τ*(S) ~ S^α · E^(-β)

  where:
    S = Shannon entropy of citation graph edge weight distribution
    E = system complexity proxy (total weighted node count)
    α = 1.2  (conservative empirical estimate; α > 1 per STOC)
    β = 0.5  (initial estimate; awaits full benchmark derivation)

  Π = τ_observed / τ_predicted(S)
    → Π ≈ 1.0  : persistent, naturally structured information
    → Π >> 1.0 : slower than predicted (bot-maintained, artificial)
    → Π << 1.0 : faster than predicted (ILO Fade, engineered collapse)

Citation graph construction:
  - Nodes = source URLs from search cascade
  - Edge weights = trust-adjusted credibility scores (from bias_table)
  - Class D nodes contribute negative signal (inverted weight)
  - S computed from normalized edge weight distribution
"""

import math
from typing import Optional
from dataclasses import dataclass, field

from bias_table import classify_domain, NODE_CLASS_D, NODE_CLASS_A
from cdx import fetch_snapshot_history, compute_snapshot_decay_lambda
from weather_baseline import compute_deviation

# ── STOC constants ────────────────────────────────────────────────────────────
ALPHA = 1.2    # Superlinear scaling exponent (α > 1 per STOC; conservative estimate)
BETA  = 0.5    # Energy flux exponent (awaits full benchmark derivation)
TAU_SCALE = 30.0  # Normalization: τ*(S=1.0, E=1.0) = 30 days (calibration anchor)

# ── Π interpretation thresholds ───────────────────────────────────────────────
PI_ORGANIC_LOW  = 0.70
PI_ORGANIC_HIGH = 1.40
PI_FADE_THRESH  = 0.35   # Below this → strong ILO Fade signal
PI_MAINTAIN_THRESH = 2.5 # Above this → strong artificial maintenance signal


@dataclass
class CitationNode:
    url:          str
    node_class:   str
    trust:        float
    inverted:     bool
    tau_days:     Optional[float]       # From CDX
    lambda_obs:   Optional[float]       # Decay constant from snapshot curve
    snapshot_count: int = 0


@dataclass
class PiResult:
    pi:                   float
    tau_observed_days:    float
    tau_predicted_days:   float
    S:                    float         # Shannon entropy of citation graph
    E:                    float         # System complexity (weighted node count)
    node_count:           int
    class_a_count:        int
    class_d_count:        int
    inverted_signal:      float         # Sum of inverted (Class D) weights — ILO amplifier flag
    saddle_point:         dict          # Weather baseline deviation analysis
    pi_interpretation:    str
    node_details:         list[dict] = field(default_factory=list)


def _shannon_entropy(weights: list[float]) -> float:
    """
    Shannon entropy of a probability distribution derived from weights.
    H = -∑ p_i · log(p_i)
    """
    total = sum(weights)
    if total <= 0:
        return 0.0
    probs = [w / total for w in weights if w > 0]
    return -sum(p * math.log(p) for p in probs if p > 0)


def _tau_predicted(S: float, E: float) -> float:
    """
    STOC-derived predicted reorganization timescale (days).
    τ*(S) ~ S^α · E^(-β) · TAU_SCALE

    S and E are normalized to [0, ∞). TAU_SCALE anchors the units.
    """
    s_safe = max(S, 0.01)   # Avoid log(0)
    e_safe = max(E, 0.01)
    return TAU_SCALE * (s_safe ** ALPHA) * (e_safe ** (-BETA))


def _interpret_pi(pi: float, inverted_signal: float, saddle: dict) -> str:
    """Human-readable Π interpretation for P4 Gate context."""
    if PI_ORGANIC_LOW <= pi <= PI_ORGANIC_HIGH:
        base = "Organic persistence — Π within natural range"
    elif pi < PI_FADE_THRESH:
        base = "Strong ILO Fade signal — τ_observed far below prediction"
    elif pi < PI_ORGANIC_LOW:
        base = "Mild decay anomaly — faster than predicted natural persistence"
    elif pi > PI_MAINTAIN_THRESH:
        base = "Artificial maintenance signal — τ_observed far exceeds prediction"
    else:
        base = "Mild persistence anomaly — slower than predicted natural decay"

    if inverted_signal > 2.0:
        base += f" | High Class D amplification ({inverted_signal:.2f}) — ILO distribution signature"

    saddle_class = saddle.get("classification", "no_data")
    if saddle_class == "ilo_fade":
        base += f" | Saddle-point: ILO Fade confirmed (Δ={saddle.get('delta', '?')})"
    elif saddle_class == "maintained":
        base += f" | Saddle-point: artificial maintenance (Δ={saddle.get('delta', '?')})"

    return base


def compute_pi(search_results: list[dict], fetch_cdx: bool = True) -> PiResult:
    """
    Build the citation graph and compute Π.

    Args:
      search_results: Raw results from Tavily cascade (list of dicts with 'url', 'content', etc.)
      fetch_cdx:      Whether to query Wayback Machine for τ_observed data.
                      Set False for testing or when CDX is unavailable.

    Returns PiResult with full diagnostic breakdown.
    """
    nodes: list[CitationNode] = []
    seen_urls: set[str] = set()

    for result in search_results:
        url = result.get("url", "").lower().strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        record, trust_score = classify_domain(url)

        # CDX lookup for τ_observed
        tau_days    = None
        lambda_obs  = None
        snap_count  = 0

        if fetch_cdx:
            cdx_data = fetch_snapshot_history(url)
            if cdx_data:
                tau_days   = cdx_data.get("tau_observed_days")
                snap_count = cdx_data.get("snapshot_count", 0)
                curve      = cdx_data.get("frequency_curve", [])
                lambda_obs = compute_snapshot_decay_lambda(curve)

        nodes.append(CitationNode(
            url=url,
            node_class=record.node_class,
            trust=trust_score.adjusted,
            inverted=trust_score.inverted,
            tau_days=tau_days,
            lambda_obs=lambda_obs,
            snapshot_count=snap_count,
        ))

    if not nodes:
        # No data — return zero Π
        return PiResult(
            pi=0.0,
            tau_observed_days=0.0,
            tau_predicted_days=1.0,
            S=0.0,
            E=0.0,
            node_count=0,
            class_a_count=0,
            class_d_count=0,
            inverted_signal=0.0,
            saddle_point={"classification": "no_data"},
            pi_interpretation="Insufficient data — no valid source nodes",
        )

    # ── Build citation graph metrics ──────────────────────────────────────────

    forward_nodes  = [n for n in nodes if not n.inverted]
    inverted_nodes = [n for n in nodes if n.inverted]

    # Trust weights for non-inverted nodes
    forward_weights = [n.trust for n in forward_nodes]
    inverted_signal = sum(n.trust for n in inverted_nodes)  # Raw inverted mass

    # Shannon entropy S of the forward edge weight distribution
    S = _shannon_entropy(forward_weights) if forward_weights else 0.0

    # System complexity E = total weighted node count (forward only)
    E = sum(forward_weights)

    # τ_observed: weighted median of CDX tau_days across forward nodes
    # Prefer nodes with actual CDX data; fall back to 0 for nodes without
    tau_values = [n.tau_days for n in forward_nodes if n.tau_days is not None]
    if tau_values:
        tau_observed = sum(tau_values) / len(tau_values)   # Weighted mean
    else:
        tau_observed = 0.0

    # τ_predicted from STOC
    tau_predicted = _tau_predicted(S, E)

    # Π
    if tau_predicted > 0:
        pi = tau_observed / tau_predicted
    else:
        pi = 0.0

    pi = round(pi, 4)

    # ── Saddle-point analysis via weather baseline ────────────────────────────
    # Use the lambda from the source with the most snapshots (richest curve)
    best_node = max(
        (n for n in forward_nodes if n.lambda_obs is not None),
        key=lambda n: n.snapshot_count,
        default=None
    )
    lambda_observed = best_node.lambda_obs if best_node else None
    saddle = compute_deviation(lambda_observed)

    # ── Counts for P4 Gate context ────────────────────────────────────────────
    class_a_count = sum(1 for n in nodes if n.node_class == NODE_CLASS_A)
    class_d_count = len(inverted_nodes)

    interpretation = _interpret_pi(pi, inverted_signal, saddle)

    node_details = [
        {
            "url":          n.url,
            "class":        n.node_class,
            "trust":        round(n.trust, 4),
            "inverted":     n.inverted,
            "tau_days":     n.tau_days,
            "lambda_obs":   round(n.lambda_obs, 6) if n.lambda_obs else None,
            "snapshots":    n.snapshot_count,
        }
        for n in nodes
    ]

    return PiResult(
        pi=pi,
        tau_observed_days=round(tau_observed, 2),
        tau_predicted_days=round(tau_predicted, 2),
        S=round(S, 4),
        E=round(E, 4),
        node_count=len(nodes),
        class_a_count=class_a_count,
        class_d_count=class_d_count,
        inverted_signal=round(inverted_signal, 4),
        saddle_point=saddle,
        pi_interpretation=interpretation,
        node_details=node_details,
    )
