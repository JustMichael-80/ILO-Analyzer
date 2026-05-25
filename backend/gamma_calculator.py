"""
ChronoDyne Systems // ILO Analyzer v4
Geographic Entropy (Γ) Calculator

Second independent PPS metric alongside Π.

Theory:
  Organic information propagation follows Constructal Law — it originates at
  local nodes and diffuses outward along natural access paths, like a river
  system branching from tributaries. Coordinated campaigns violate this by
  injecting simultaneously across geographically dispersed nodes.

  Γ = H_geographic / H_expected(t)

  Where:
    H_geographic = Shannon entropy of source geographic scope distribution
    H_expected(t) = expected geographic entropy at time t for a naturally
                    diffusing story of comparable complexity

  Γ ≈ 1.0  →  organic diffusion pattern
  Γ >> 1.0 →  anomalously uniform geographic distribution = coordinated injection
  Γ << 1.0 →  anomalously local = suppression or very early stage

Diffusion velocity:
  Too fast  — story appears simultaneously at national/international level
              with no local precursor. Γ jumps to high immediately.
  Natural   — story originates local, diffuses outward over days/weeks.
  Too slow  — strong local signal, fails to diffuse nationally despite
              content that would normally propagate. Suppression signature.

This gives Γ a two-tailed detection capability:
  Γ >> 1.0  →  artificial injection (coordinated, geographically uniform)
  Γ ≈ 1.0   →  organic
  Γ << 1.0  →  suppression (geographically contained anomalously long)

Combined with Π, the two metrics define a diagnostic coordinate space:

  Quadrant I   (Π high, Γ high) →  Confirmed ILO — injected and maintained
  Quadrant II  (Π high, Γ low)  →  Astroturfed local — manufactured, contained
  Quadrant III (Π low,  Γ high) →  Viral suppression — spreading fast, dying artificially
  Quadrant IV  (Π low,  Γ low)  →  Suppressed real event — neither persisting nor diffusing
  Center       (Π ≈ 1, Γ ≈ 1)  →  Organic
"""

import math
from dataclasses import dataclass
from typing import Optional

from bias_table import classify_domain, NODE_CLASS_D

# ── Geographic scope hierarchy ────────────────────────────────────────────────
# Ordered from most local to most global.
# Used to compute diffusion velocity — how fast scope expands.

SCOPE_RANK = {
    "local":         0,
    "national":      1,
    "international": 2,
    "global":        3,
    "unknown":       1,   # Treat unknown as national for conservatism
}

# Natural diffusion timescales (days) for a story to reach each scope level
# from a local origin — calibrated from empirical journalism studies.
# A genuine local-to-national story takes ~3-7 days on average.
# Local-to-international: ~7-21 days.
# Simultaneous global appearance: strong ILO signal.
TAU_GEO = {
    "local":         0.0,
    "national":      5.0,
    "international": 14.0,
    "global":        21.0,
}

# Maximum geographic entropy (all four scope levels equally represented)
H_GEO_MAX = math.log(4)  # ≈ 1.386


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class GammaResult:
    gamma:                float         # Γ = H_geo / H_expected
    h_geographic:         float         # Observed geographic entropy
    h_expected:           float         # Expected entropy for natural diffusion
    scope_distribution:   dict          # {scope: count}
    country_distribution: dict          # {country: count}
    max_scope_rank:       int           # Highest scope level observed
    diffusion_velocity:   str           # organic | fast_injection | slow_suppression
    quadrant:             str           # Combined Π/Γ quadrant (set externally)
    gamma_interpretation: str


def _shannon_entropy(counts: dict) -> float:
    """Shannon entropy of a count distribution."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counts.values() if c > 0]
    return -sum(p * math.log(p) for p in probs if p > 0)


def _expected_entropy(tau_observed_days: float) -> float:
    """
    Expected geographic entropy H_expected(t) for a naturally diffusing story.

    Models organic diffusion as progressive scope expansion:
      H(t) = H_max · (1 - e^(-t / τ_diffusion))

    Where τ_diffusion = 14 days (characteristic timescale for local→international).
    At t=0:  H = 0 (purely local)
    At t=14: H ≈ 0.63 · H_max
    At t=∞:  H → H_max
    """
    TAU_DIFFUSION = 14.0  # days — characteristic geographic diffusion timescale
    if tau_observed_days <= 0:
        return H_GEO_MAX * 0.1   # Minimum expected entropy for any indexed story
    return H_GEO_MAX * (1.0 - math.exp(-tau_observed_days / TAU_DIFFUSION))


def _classify_diffusion_velocity(
    gamma: float,
    max_scope_rank: int,
    tau_observed_days: float,
) -> str:
    """
    Classify the diffusion velocity signal.

    fast_injection:  Story appeared at high scope immediately (no local buildup)
    slow_suppression: Story has local signal but failed to diffuse outward
    organic:         Normal diffusion pattern
    """
    if gamma > 1.5 and max_scope_rank >= 3 and tau_observed_days < 7:
        return "fast_injection"
    elif gamma < 0.4 and max_scope_rank <= 1:
        return "slow_suppression"
    else:
        return "organic"


def _interpret_gamma(
    gamma: float,
    diffusion_velocity: str,
    scope_distribution: dict,
) -> str:
    """Human-readable Γ interpretation for P4 Gate context."""
    if 0.70 <= gamma <= 1.40:
        base = "Organic geographic diffusion — Γ within natural range"
    elif gamma > 2.0:
        base = "Strong coordinated injection signal — geographic entropy far exceeds natural diffusion prediction"
    elif gamma > 1.40:
        base = "Mild geographic anomaly — spreading faster or more uniformly than organic diffusion predicts"
    elif gamma < 0.25:
        base = "Strong suppression signal — narrative geographically contained far below natural diffusion prediction"
    else:
        base = "Mild geographic containment — slower diffusion than predicted"

    if diffusion_velocity == "fast_injection":
        base += " | Fast injection: high-scope sources present with insufficient local precursor"
    elif diffusion_velocity == "slow_suppression":
        base += " | Slow suppression: local signal present but national/international diffusion blocked"

    dominant = max(scope_distribution, key=scope_distribution.get) if scope_distribution else "unknown"
    base += f" | Dominant scope: {dominant}"

    return base


def assign_quadrant(pi: float, gamma: float) -> str:
    """
    Assign the Π/Γ diagnostic quadrant.

    Quadrant I   (Π high, Γ high) →  Confirmed ILO
    Quadrant II  (Π high, Γ low)  →  Astroturfed Local
    Quadrant III (Π low,  Γ high) →  Viral Suppression
    Quadrant IV  (Π low,  Γ low)  →  Suppressed Real Event
    Center                        →  Organic
    """
    pi_high  = pi    > 1.40
    pi_low   = pi    < 0.70
    gam_high = gamma > 1.40
    gam_low  = gamma < 0.70

    if pi_high  and gam_high: return "I — Confirmed ILO"
    if pi_high  and gam_low:  return "II — Astroturfed Local"
    if pi_low   and gam_high: return "III — Viral Suppression"
    if pi_low   and gam_low:  return "IV — Suppressed Real Event"
    return "Organic"


def compute_gamma(
    search_results: list[dict],
    tau_observed_days: float = 0.0,
) -> GammaResult:
    """
    Compute Geographic Entropy Γ from the search result citation graph.

    Args:
      search_results:    Raw results from Tavily cascade
      tau_observed_days: τ_observed from CDX (used to compute H_expected)
                         Pass 0.0 if CDX is disabled.

    Returns GammaResult with full diagnostic breakdown.
    """
    scope_counts:   dict[str, int] = {}
    country_counts: dict[str, int] = {}
    max_scope_rank = 0
    seen_urls: set[str] = set()

    for result in search_results:
        url = result.get("url", "").lower().strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        record, trust = classify_domain(url)

        # Class D nodes excluded from geographic analysis
        # Their geographic presence is a propagation artifact, not organic signal
        if trust.inverted:
            continue

        scope   = record.geo_scope   or "unknown"
        country = record.country     or "unknown"

        scope_counts[scope]     = scope_counts.get(scope, 0) + 1
        country_counts[country] = country_counts.get(country, 0) + 1

        rank = SCOPE_RANK.get(scope, 1)
        if rank > max_scope_rank:
            max_scope_rank = rank

    # Compute H_geographic
    h_geo = _shannon_entropy(scope_counts)

    # Compute H_expected from natural diffusion model
    h_exp = _expected_entropy(tau_observed_days)

    # Γ
    if h_exp > 0:
        gamma = h_geo / h_exp
    else:
        gamma = 1.0 if h_geo == 0 else 2.0   # No expected baseline — flag as anomalous if any signal

    gamma = round(gamma, 4)

    diffusion_velocity = _classify_diffusion_velocity(gamma, max_scope_rank, tau_observed_days)
    interpretation     = _interpret_gamma(gamma, diffusion_velocity, scope_counts)

    return GammaResult(
        gamma=gamma,
        h_geographic=round(h_geo, 4),
        h_expected=round(h_exp, 4),
        scope_distribution=scope_counts,
        country_distribution=country_counts,
        max_scope_rank=max_scope_rank,
        diffusion_velocity=diffusion_velocity,
        quadrant="",   # Populated externally after Π is known
        gamma_interpretation=interpretation,
    )
