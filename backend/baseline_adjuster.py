"""
ChronoDyne Systems // ILO Analyzer v4.5
Baseline Adjuster

Thin glue layer that applies:
  1. κ(C) cultural persistence correction from claim_classifier.py
  2. Multi-substrate consensus λ from physical_baselines.py

to a completed PiResult, returning an AdjustedDiagnostics object that
the engine injects into the P4 Gate context alongside the raw physics.

Design principle:
  The raw Π, Γ, S, E values are NEVER modified. AdjustedDiagnostics is
  an additive interpretive layer. The P4 Gate receives both the raw
  physics block (ground truth) and the adjusted block (interpreted),
  clearly labeled. The LLM synthesizes both — it does not recompute either.

  This preserves the core architectural guarantee: physics is computed
  deterministically, LLM synthesizes only.
"""

from dataclasses import dataclass, field
from typing import Optional

from claim_classifier import ClaimClassification, compute_adjusted_pi
from physical_baselines import compute_consensus_baseline, compute_deviation_consensus


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class AdjustedDiagnostics:
    """
    The complete adjusted diagnostic block for P4 Gate injection.

    Raw values from PiResult are preserved unchanged.
    All adjustments are additive and transparently labeled.
    """

    # Raw physics (unchanged)
    pi_raw:                   float
    tau_observed_days:        float
    tau_predicted_days:       float

    # κ adjustment
    kappa:                    float
    tau_predicted_adj:        float        # τ_predicted × κ
    pi_adjusted:              float        # τ_observed / τ_predicted_adj
    organic_persistence:      bool         # True if Π_adj in [0.70, 1.40]
    adjustment_note:          str

    # Claim classification
    claim_class_id:           int
    claim_class_label:        str
    classifier_confidence:    float
    memetic_fitness:          float
    memetic_traits:           dict
    evergreen_archetype:      Optional[str]
    cyclical_signals:         list
    pi_interpretation_note:   str

    # Multi-substrate baseline
    lambda_consensus:         float
    consensus_quality:        str          # "high" | "medium" | "low"
    saddle_consensus:         dict         # Full deviation result vs consensus
    substrates:               dict         # Per-substrate breakdown

    # Verdict guidance for P4 Gate
    adjusted_verdict_weight:  str          # Plain-language guidance
    ilo_survives_correction:  bool         # True if Π_adj still anomalous after κ


# ── Main entry point ──────────────────────────────────────────────────────────

def compute_adjusted_diagnostics(
    pi_result,
    classification: ClaimClassification,
    lambda_observed: Optional[float] = None,
) -> AdjustedDiagnostics:
    """
    Apply κ correction and consensus baseline to a completed PiResult.

    Args:
      pi_result:        PiResult from compute_pi()
      classification:   ClaimClassification from classify_claim()
      lambda_observed:  λ from CDX snapshot curve (pi_result.saddle_point
                        contains this; passed explicitly for clarity)

    Returns AdjustedDiagnostics ready for P4 Gate injection.
    """

    # ── Apply κ correction ────────────────────────────────────────────────────
    adjusted = compute_adjusted_pi(
        pi_raw=pi_result.pi,
        tau_predicted=pi_result.tau_predicted_days,
        classification=classification,
    )

    # ── Compute consensus baseline deviation ──────────────────────────────────
    # Extract lambda_observed from saddle_point if not passed explicitly
    if lambda_observed is None:
        sp = pi_result.saddle_point
        if isinstance(sp, dict):
            lambda_observed = sp.get("lambda_observed")
        else:
            lambda_observed = getattr(sp, "lambda_observed", None)

    consensus = compute_consensus_baseline()
    saddle_consensus = compute_deviation_consensus(lambda_observed)

    # ── Determine whether ILO signal survives κ correction ───────────────────
    pi_adj = adjusted["pi_adjusted"]
    organic_low  = 0.70
    organic_high = 1.40
    ilo_survives = pi_adj > organic_high * 1.5   # Significantly above organic even after correction

    # ── Generate P4 Gate verdict guidance ────────────────────────────────────
    verdict_weight = _verdict_guidance(
        pi_raw=pi_result.pi,
        pi_adj=pi_adj,
        kappa=classification.kappa,
        claim_class=classification.claim_class_label,
        memetic_fitness=classification.memetic_fitness,
        ilo_survives=ilo_survives,
        organic_persistence=adjusted["organic_persistence"],
        classifier_confidence=classification.classifier_confidence,
        cyclical_signals=classification.cyclical_signals,
        consensus_quality=consensus["consensus_quality"],
    )

    return AdjustedDiagnostics(
        # Raw physics
        pi_raw=pi_result.pi,
        tau_observed_days=pi_result.tau_observed_days,
        tau_predicted_days=pi_result.tau_predicted_days,

        # κ adjustment
        kappa=adjusted["kappa"],
        tau_predicted_adj=adjusted["tau_predicted_adj"],
        pi_adjusted=pi_adj,
        organic_persistence=adjusted["organic_persistence"],
        adjustment_note=adjusted["adjustment_note"],

        # Claim classification
        claim_class_id=classification.claim_class_id,
        claim_class_label=classification.claim_class_label,
        classifier_confidence=classification.classifier_confidence,
        memetic_fitness=classification.memetic_fitness,
        memetic_traits=classification.memetic_traits,
        evergreen_archetype=classification.evergreen_archetype,
        cyclical_signals=classification.cyclical_signals,
        pi_interpretation_note=classification.pi_interpretation_note,

        # Multi-substrate baseline
        lambda_consensus=consensus["lambda_consensus"],
        consensus_quality=consensus["consensus_quality"],
        saddle_consensus=saddle_consensus,
        substrates=consensus["substrates"],

        # Verdict guidance
        adjusted_verdict_weight=verdict_weight,
        ilo_survives_correction=ilo_survives,
    )


# ── Verdict guidance generator ────────────────────────────────────────────────

def _verdict_guidance(
    pi_raw:               float,
    pi_adj:               float,
    kappa:                float,
    claim_class:          str,
    memetic_fitness:      float,
    ilo_survives:         bool,
    organic_persistence:  bool,
    classifier_confidence: float,
    cyclical_signals:     list,
    consensus_quality:    str,
) -> str:
    """
    Generate plain-language verdict guidance for the P4 Gate.

    This is NOT a verdict — it is interpretive guidance that the P4 Gate
    weighs alongside all other physics. The LLM makes the final synthesis.
    """

    if classifier_confidence < 0.3:
        return (
            f"Classification confidence low ({classifier_confidence:.0%}) — "
            f"κ correction unreliable. Weight raw Π = {pi_raw:.2f} as primary signal."
        )

    lines = []

    if organic_persistence and pi_raw > 1.40:
        lines.append(
            f"Raw Π = {pi_raw:.2f} NORMALIZES to Π_adj = {pi_adj:.4f} after "
            f"κ = {kappa:.2f} correction for '{claim_class}'. "
            f"This is within the organic range — consistent with natural subcultural "
            f"persistence, NOT engineered maintenance."
        )
        if memetic_fitness > 0.6:
            lines.append(
                f"High memetic fitness ({memetic_fitness:.2f}) corroborates organic persistence: "
                f"this narrative has structural traits that naturally sustain long-term community interest."
            )

    elif ilo_survives:
        lines.append(
            f"Raw Π = {pi_raw:.2f} remains anomalous at Π_adj = {pi_adj:.4f} even after "
            f"κ = {kappa:.2f} correction for '{claim_class}'. "
            f"The narrative is persisting {pi_adj:.1f}x longer than the κ-adjusted natural lifespan. "
            f"Artificial maintenance signal SURVIVES cultural persistence correction — "
            f"weight toward ILO verdict."
        )
        if memetic_fitness > 0.6:
            lines.append(
                f"High memetic fitness ({memetic_fitness:.2f}) with ILO signal surviving correction "
                f"is the signature of a state actor or coordinated campaign using existing "
                f"conspiracy fringe as a laundering vector. This is the most dangerous pattern."
            )

    else:
        lines.append(
            f"Π_adj = {pi_adj:.4f} after κ = {kappa:.2f} correction. "
            f"Mild anomaly — does not strongly support ILO or organic verdict alone."
        )

    if cyclical_signals:
        lines.append(
            f"Cyclical signals detected: {'; '.join(cyclical_signals[:3])}. "
            f"Consider 'Cyclical Maintenance' rather than sustained artificial maintenance."
        )

    if consensus_quality == "low":
        lines.append(
            f"Consensus baseline quality LOW — fewer than 2 live physical substrates. "
            f"Baseline comparison is less reliable; weight Π values with caution."
        )
    elif consensus_quality == "high":
        lines.append(
            f"Consensus baseline HIGH quality ({consensus_quality}) — "
            f"multi-substrate reference is reliable."
        )

    return " | ".join(lines)


# ── Serialization for P4 Gate injection ──────────────────────────────────────

def adjusted_diagnostics_to_dict(adj: AdjustedDiagnostics) -> dict:
    """
    Serialize AdjustedDiagnostics to a dict for P4 Gate JSON injection.
    Keeps substrate breakdown concise — lambda values only, not raw data.
    """
    substrate_summary = {
        name: {
            "lambda": round(s["lambda"], 6),
            "source": s["source"],
            "live":   s.get("live", False),
            "weight": s["weight"],
        }
        for name, s in adj.substrates.items()
    }

    return {
        # κ adjustment
        "pi_raw":               adj.pi_raw,
        "pi_adjusted":          adj.pi_adjusted,
        "kappa":                adj.kappa,
        "tau_predicted_raw":    adj.tau_predicted_days,
        "tau_predicted_adj":    adj.tau_predicted_adj,
        "organic_persistence":  adj.organic_persistence,
        "ilo_survives_correction": adj.ilo_survives_correction,
        "adjustment_note":      adj.adjustment_note,
        "adjusted_verdict_weight": adj.adjusted_verdict_weight,

        # Claim classification
        "claim_class_id":       adj.claim_class_id,
        "claim_class_label":    adj.claim_class_label,
        "classifier_confidence": adj.classifier_confidence,
        "memetic_fitness":      adj.memetic_fitness,
        "memetic_traits":       adj.memetic_traits,
        "evergreen_archetype":  adj.evergreen_archetype,
        "cyclical_signals":     adj.cyclical_signals,
        "pi_interpretation_note": adj.pi_interpretation_note,

        # Multi-substrate baseline
        "lambda_consensus":     adj.lambda_consensus,
        "consensus_quality":    adj.consensus_quality,
        "saddle_consensus":     {
            "classification":   adj.saddle_consensus.get("classification"),
            "delta":            adj.saddle_consensus.get("delta"),
            "lambda_observed":  adj.saddle_consensus.get("lambda_observed"),
            "lambda_consensus": adj.saddle_consensus.get("lambda_consensus"),
        },
        "substrate_summary":    substrate_summary,
    }
