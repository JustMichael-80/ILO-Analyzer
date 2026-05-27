"""
ChronoDyne Systems // ILO Analyzer v4.5
ILO Signature Library

Cosine similarity matching of incoming Π/Γ physics vectors against a library
of known ILO campaign signatures derived from validated benchmark runs.

Architecture:
  - Each signature is a normalized physics vector in 8-dimensional space:
    [π, γ, S, E, inverted_signal, class_d_ratio, class_a_ratio, saddle_encoded]
  - Cosine similarity measures directional alignment in campaign-space
  - Threshold-gated match reporting avoids false positives on noisy queries
  - Signatures are versioned and traceable to benchmark claim IDs

v4.5 additions:
  SYN-008 through SYN-012 address the organic cultural persistence problem.
  Evergreen conspiracy narratives produce high raw Π via subcultural
  infrastructure — not coordinated artificial maintenance. These signatures
  define the conspiracy-aware space and enable the κ-corrected Π_adj to
  distinguish organic fringe communities from engineered operations.

  The most critical new signature is SYN-010 (Astroturfed via Conspiracy
  Fringe) — a state actor deliberately using existing conspiracy communities
  as a laundering vector. Previously undetectable without κ correction.

Physics vector dimensions:
  dim 0  π              — Persistence Ratio (core temporal anomaly, RAW)
  dim 1  γ              — Geographic Entropy Ratio (spatial diffusion anomaly)
  dim 2  S              — Shannon entropy of citation graph (source diversity)
  dim 3  E              — System complexity / trust-weighted node count
  dim 4  inverted_signal — Raw Class D (propagation node) mass
  dim 5  class_d_ratio  — Class D nodes / total nodes
  dim 6  class_a_ratio  — Class A nodes / total nodes (primary source presence)
  dim 7  saddle_encoded — Saddle-point classification as float:
                            organic=0.0, no_data=0.5, ilo_fade=0.8, maintained=1.0

Note on raw Π in vectors:
  Signature vectors use RAW Π (before κ correction). The matching system
  compares raw physics vectors — κ adjustment is applied at interpretation
  stage by baseline_adjuster.py. This preserves the ability to match
  against known campaign fingerprints regardless of classification.

Cosine similarity interpretation:
  sim ≥ 0.97  — Strong match (same campaign family, high confidence)
  sim 0.90-0.97 — Probable match (similar structural signature)
  sim 0.80-0.90 — Partial match (shared campaign mechanics, different deployment)
  sim < 0.80  — No match (structurally distinct)

Validated benchmark claims used to derive signatures are identified by their
benchmark_id, which maps to the 30-claim validation dataset (in development).

Reference: PPS/STOC paper DOI: https://doi.org/10.6084/m9.figshare.32307087
"""

import math
from dataclasses import dataclass, field
from typing import Optional


# ── Vector dimension indices ───────────────────────────────────────────────────

DIM_PI             = 0
DIM_GAMMA          = 1
DIM_S              = 2
DIM_E              = 3
DIM_INVERTED       = 4
DIM_CLASS_D_RATIO  = 5
DIM_CLASS_A_RATIO  = 6
DIM_SADDLE         = 7

VECTOR_DIM = 8

SADDLE_ENCODING = {
    "organic":    0.0,
    "no_data":    0.5,
    "ilo_fade":   0.8,
    "maintained": 1.0,
}

# ── Match thresholds ───────────────────────────────────────────────────────────

THRESHOLD_STRONG   = 0.97
THRESHOLD_PROBABLE = 0.90
THRESHOLD_PARTIAL  = 0.80


# ── Signature record ───────────────────────────────────────────────────────────

@dataclass
class ILOSignature:
    """
    A normalized physics vector for a known ILO campaign type.

    benchmark_id:    Maps to the 30-claim validation dataset entry.
                     Format: "BM-{n:03d}" for validated claims, "SYN-{n:03d}" for
                     synthetically derived archetypes.
    campaign_type:   Human-readable campaign classification.
    quadrant:        Π/Γ quadrant — confirms the physics space location.
    vector:          Raw (unnormalized) 8-dimensional physics vector.
    description:     What this campaign pattern looks like operationally.
    notes:           Caveats, derivation notes, confidence flags.
    """
    benchmark_id:  str
    campaign_type: str
    quadrant:      str
    vector:        list[float]   # length VECTOR_DIM, raw (normalized at query time)
    description:   str
    notes:         str = ""


@dataclass
class SignatureMatch:
    """Result of a single signature comparison."""
    benchmark_id:    str
    campaign_type:   str
    quadrant:        str
    similarity:      float
    match_tier:      str        # "strong" | "probable" | "partial" | "none"
    description:     str
    notes:           str


@dataclass
class LibraryResult:
    """Full library scan result."""
    query_vector:         list[float]
    matches:              list[SignatureMatch]
    best_match:           Optional[SignatureMatch]
    best_similarity:      float
    campaign_family:      str          # Dominant campaign type across top matches
    library_interpretation: str


# ── Signature library ──────────────────────────────────────────────────────────
# Vectors are raw — normalized at query time. Ordering matches DIM_* constants.
# Format: [π, γ, S, E, inverted_signal, class_d_ratio, class_a_ratio, saddle]
#
# Validated entries (BM-*) are derived from confirmed benchmark runs.
# Synthetic archetypes (SYN-*) are theoretically derived from PPS/STOC first
# principles and await empirical validation from the benchmark suite.

SIGNATURE_LIBRARY: list[ILOSignature] = [

    # ── Validated: Confirmed ILO (Quadrant I — Π high, Γ high) ───────────────

    ILOSignature(
        benchmark_id="BM-001",
        campaign_type="State-Sponsored Historical Revisionism",
        quadrant="I — Confirmed ILO",
        vector=[41.91, 2.10, 1.82, 3.20, 4.10, 0.48, 0.05, 0.8],
        description=(
            "Long-duration artificial maintenance of a historical claim. Π far exceeds "
            "organic range — the narrative is actively bot-sustained long past its natural "
            "decay. Simultaneous multi-geographic injection (Γ > 2.0) with near-zero Class A "
            "sourcing. ILO Fade saddle confirms engineered persistence."
        ),
        notes="Derived from JFK/Dimona benchmark run. Π=41.91 is anchoring calibration point.",
    ),

    ILOSignature(
        benchmark_id="BM-002",
        campaign_type="Domestic Astroturfing — Manufactured Local Consensus",
        quadrant="II — Astroturfed Local",
        vector=[25.10, 0.46, 0.95, 1.40, 2.20, 0.38, 0.08, 0.8],
        description=(
            "High artificial maintenance (Π >> 1) but geographically contained (Γ < 0.7). "
            "Story is kept alive by coordinated accounts but never broke out of domestic "
            "distribution — signature of a domestic political operation without international "
            "amplification infrastructure."
        ),
        notes="Derived from GPT-4.0 is AGI benchmark run. Π=25.10, Γ=0.46.",
    ),

    # ── Validated: Viral Suppression (Quadrant III — Π low, Γ high) ──────────

    ILOSignature(
        benchmark_id="BM-003",
        campaign_type="Coordinated Suppression of Legitimate Event",
        quadrant="III — Viral Suppression",
        vector=[0.0, 5.0, 1.45, 0.80, 1.50, 0.35, 0.10, 0.5],
        description=(
            "Story spread rapidly across geographic scopes (Γ = 5.0) but τ_observed "
            "collapses to zero — the narrative was killed before it could accumulate "
            "temporal structure. High Class D presence suggests algorithmic suppression "
            "or coordinated deplatforming. No CDX trail."
        ),
        notes="Derived from Podesta/Bennington benchmark run. Π=0.0, Γ=5.0.",
    ),

    # ── Synthetic Archetypes ──────────────────────────────────────────────────
    # Theoretically derived from PPS/STOC. Awaiting empirical benchmark validation.

    ILOSignature(
        benchmark_id="SYN-001",
        campaign_type="Organic True Signal",
        quadrant="Organic",
        vector=[1.0, 1.0, 1.60, 4.50, 0.20, 0.08, 0.35, 0.0],
        description=(
            "Π and Γ both within organic range. High Class A presence, low Class D. "
            "Saddle classification: organic. S and E values consistent with natural "
            "multi-source citation graph formation. This is what a real story looks like."
        ),
        notes="Synthetic archetype — no benchmark validation yet.",
    ),

    ILOSignature(
        benchmark_id="SYN-002",
        campaign_type="Fast Injection Campaign — Simultaneous Global Deployment",
        quadrant="I — Confirmed ILO",
        vector=[3.50, 2.80, 0.85, 0.90, 3.80, 0.55, 0.02, 0.8],
        description=(
            "Moderate Π with very high Γ — story appeared simultaneously across global "
            "scope with no local precursor. Fast injection velocity. Almost no Class A "
            "sources; high Class D mass. Consistent with a coordinated narrative seeded "
            "across multiple platforms simultaneously."
        ),
        notes="Synthetic archetype. Fast_injection velocity is the primary diagnostic signal.",
    ),

    ILOSignature(
        benchmark_id="SYN-003",
        campaign_type="Suppressed Real Event — No Amplification",
        quadrant="IV — Suppressed Real Event",
        vector=[0.25, 0.30, 0.70, 0.60, 0.40, 0.12, 0.28, 0.5],
        description=(
            "Both Π and Γ below organic floor. Story has Class A sourcing (real event) "
            "but failed to diffuse nationally or maintain temporal structure. Neither "
            "artificially maintained nor organically spreading. May indicate institutional "
            "suppression or story that failed to find distribution."
        ),
        notes="Synthetic archetype. Class A presence is key differentiator from Quadrant III.",
    ),

    ILOSignature(
        benchmark_id="SYN-004",
        campaign_type="Organic Conspiracy — Natural Spread, No Coordination",
        quadrant="Organic",
        vector=[1.15, 1.20, 1.80, 2.10, 0.60, 0.15, 0.10, 0.0],
        description=(
            "Π and Γ in organic range but Class A count low and Class D elevated. "
            "Story persists and diffuses naturally but lacks institutional sourcing. "
            "Pattern is consistent with an organic conspiracy theory — no coordination "
            "signal, but also no credentialed corroboration. Wildness tier 3-4 expected."
        ),
        notes="Synthetic archetype. Distinguishable from ILO by organic Π/Γ values.",
    ),

    ILOSignature(
        benchmark_id="SYN-005",
        campaign_type="Narrative Spent — Former ILO Now Decaying",
        quadrant="Organic",
        vector=[0.65, 0.85, 1.20, 1.80, 0.90, 0.20, 0.15, 0.0],
        description=(
            "Π slightly below organic floor — story once maintained artificially is "
            "now decaying at near-natural rate. Class D residue present but declining. "
            "Saddle: organic (maintenance infrastructure dismantled). Pattern consistent "
            "with a former ILO campaign that has been abandoned."
        ),
        notes="Synthetic archetype. Temporal trajectory matters — static snapshot may miss.",
    ),

    ILOSignature(
        benchmark_id="SYN-006",
        campaign_type="Commercial Clickbait — High Velocity, No Persistence",
        quadrant="III — Viral Suppression",
        vector=[0.15, 1.80, 0.95, 2.20, 1.20, 0.28, 0.05, 0.5],
        description=(
            "Low Π with moderately high Γ. Story spread rapidly but lacks persistence "
            "structure — consistent with viral commercial content that burns fast and "
            "leaves no CDX trail. High domain count but low trust weights; no Class A. "
            "Not a suppression event — organic decay after rapid spread."
        ),
        notes=(
            "Synthetic archetype. Distinguishable from genuine suppression by "
            "absence of Class A sourcing and no debunking trail."
        ),
    ),

    ILOSignature(
        benchmark_id="SYN-007",
        campaign_type="State Media Narrative — Sustained International Coverage",
        quadrant="I — Confirmed ILO",
        vector=[8.50, 1.80, 1.35, 2.60, 2.80, 0.40, 0.06, 1.0],
        description=(
            "High Π with elevated Γ — narrative artificially maintained at international "
            "scope. Saddle: maintained (bot infrastructure active). Class B sources "
            "present but captured (lean > 0.6); near-zero Class A. Pattern consistent "
            "with state media operation sustaining a narrative past its organic lifetime."
        ),
        notes="Synthetic archetype. Maintained saddle + international scope is key signal.",
    ),

    # ── v4.5 additions: Conspiracy-aware signatures ───────────────────────────
    # These five signatures address the organic cultural persistence problem:
    # evergreen conspiracy narratives produce high raw Π via subcultural
    # infrastructure, not coordinated artificial maintenance. The κ-adjusted
    # Π_adj is the operative signal for these classes — raw Π alone is
    # insufficient and will over-flag genuine organic fringe communities.
    #
    # Key differentiator across all five:
    #   Organic evergreen:            Π_adj ≈ 1.0,  Class D moderate, Class A present
    #   Cyclically stirred:           Π_adj spikes periodically, Class D surges during windows
    #   Astroturfed via fringe cover: Π_adj > 2.0, Γ anomalous, Class A laundered through B
    #
    # Vector format: [π, γ, S, E, inverted_signal, class_d_ratio, class_a_ratio, saddle]
    # Note: π values here are RAW Π before κ correction. The matching system
    # compares raw vectors — κ adjustment is applied at interpretation stage.

    ILOSignature(
        benchmark_id="SYN-008",
        campaign_type="Organic Evergreen Conspiracy — Subcultural Persistence",
        quadrant="II — Astroturfed Local",
        vector=[85.0, 0.65, 1.45, 2.80, 1.20, 0.22, 0.18, 0.8],
        description=(
            "Very high raw Π with geographic containment (Γ < 0.70) — superficially "
            "resembles Quadrant II astroturfing but is driven by organic subcultural "
            "infrastructure: books, podcasts, dedicated researchers, and community forums. "
            "Class A sourcing present (real historical documents exist and are cited). "
            "Class D moderate but not dominant. Saddle: maintained appearance is artifact "
            "of community curation, not bot infrastructure. κ correction resolves: "
            "Π_adj ≈ 1.0 for Suppressed Tech/Energy class (κ ≈ 6.0). "
            "Key differentiator from engineered ILO: Class A ≥ Class D, Γ organic, "
            "no fast-injection velocity, no geographic anomaly."
        ),
        notes=(
            "Synthetic archetype. TT Brown / Philadelphia Experiment cluster. "
            "Raw Π alone will over-flag this — always apply κ correction before verdict. "
            "Π_adj is the operative signal. Awaiting empirical benchmark validation."
        ),
    ),

    ILOSignature(
        benchmark_id="SYN-009",
        campaign_type="Cyclically Stirred Narrative — Periodic Re-injection",
        quadrant="II — Astroturfed Local",
        vector=[45.0, 0.72, 1.30, 2.20, 2.40, 0.35, 0.12, 0.8],
        description=(
            "High raw Π with near-organic Γ. CDX snapshot curve shows periodic spikes "
            "correlated with external events (election cycles, congressional hearings, "
            "budget fights, anniversaries). Class D elevated during injection windows, "
            "decays between them. Distinct from pure organic evergreen: the periodic "
            "amplification is coordinated even if the underlying narrative is organic. "
            "Cyclical signals in claim text (e.g. 'congressional hearing', 'whistleblower', "
            "'declassified') are a strong positive indicator. "
            "Treatment: flag cyclical maintenance rather than sustained artificial maintenance. "
            "Distraction score should be computed against known political calendars."
        ),
        notes=(
            "Synthetic archetype. UAP hearing cycles, election-timed conspiracy surges. "
            "Awaiting empirical benchmark validation with CDX timestamp periodicity data. "
            "Cyclical detection in pi_calculator.py (v4.5) will improve this signature."
        ),
    ),

    ILOSignature(
        benchmark_id="SYN-010",
        campaign_type="Astroturfed via Conspiracy Fringe — ILO Using Organic Cover",
        quadrant="I — Confirmed ILO",
        vector=[120.0, 1.55, 1.20, 2.40, 3.60, 0.48, 0.04, 1.0],
        description=(
            "The most dangerous and previously undetectable pattern. Superficially "
            "resembles organic evergreen conspiracy (high raw Π, moderate Class D), "
            "but three signals distinguish it: (1) Γ > 1.40 — geographic injection "
            "anomaly inconsistent with organic subcultural persistence which is "
            "geographically contained; (2) Class A near-zero despite decades of "
            "claimed research — organic fringe communities generate real primary "
            "source archaeology over time; (3) Π_adj > 2.0 even after κ correction "
            "for the conspiracy substrate class. A state actor or coordinated campaign "
            "has deliberately seeded content into existing conspiracy communities to "
            "exploit their organic persistence infrastructure as a laundering vector. "
            "The fringe community provides plausible deniability and organic-looking "
            "Class D amplification while the actual maintenance is artificial."
        ),
        notes=(
            "Synthetic archetype. Critical signature — highest priority for human review. "
            "Distinguishing feature vs SYN-008: Γ > 1.40 and Π_adj > 2.0 after κ. "
            "Awaiting empirical benchmark validation. Legal review required before "
            "attributing to specific actors."
        ),
    ),

    ILOSignature(
        benchmark_id="SYN-011",
        campaign_type="Academic/Technical Fringe — Long Natural Half-Life",
        quadrant="Organic",
        vector=[200.0, 0.80, 1.65, 3.20, 0.40, 0.08, 0.42, 0.5],
        description=(
            "Extremely high raw Π with organic Γ and very high Class A ratio. "
            "Story has deep citation structure in academic and technical literature. "
            "Raw Π appears catastrophically anomalous but κ correction for "
            "Academic/Technical Fringe class (κ ≈ 8.5) resolves to Π_adj ≈ 1.0. "
            "This is what legitimate fringe science looks like: real papers, real "
            "researchers, real institutional sourcing, organic geographic diffusion. "
            "No artificial maintenance — the academic citation network itself "
            "provides the persistence infrastructure. "
            "Distinguishable from ILO by: Class A dominant, Class D minimal, "
            "Γ organic, saddle showing organic decay (not maintained)."
        ),
        notes=(
            "Synthetic archetype. Electrogravitics, cold fusion, alternative cosmology. "
            "High Class A is the key signal — legitimate academic fringe generates "
            "real primary source trails. Awaiting empirical benchmark validation."
        ),
    ),

    ILOSignature(
        benchmark_id="SYN-012",
        campaign_type="Pop Culture Myth — Memetically Fit, No Coordination",
        quadrant="Organic",
        vector=[18.0, 1.10, 1.75, 3.40, 0.80, 0.16, 0.08, 0.0],
        description=(
            "Moderate-high raw Π with organic Γ and organic saddle. High source "
            "diversity and system complexity — the narrative is widely discussed "
            "across many independent domains. Class D present but not dominant. "
            "No Class A (no institutional sourcing — it's a myth, not a documented "
            "event). κ correction for Pop Culture/Celebrity class (κ ≈ 3.0) "
            "resolves raw Π to Π_adj ≈ 1.0. Saddle: organic decay — the narrative "
            "is fading naturally from its peak even if absolute persistence is high. "
            "Mandela Effect, celebrity death hoaxes, and internet urban legends "
            "cluster here. No coordination signal — pure memetic fitness drives "
            "the persistence. High engagement on Class D nodes is expected and "
            "not anomalous for this class."
        ),
        notes=(
            "Synthetic archetype. Mandela Effect, Paul McCartney death hoax, "
            "Avril Lavigne replacement theory cluster. "
            "Key differentiator: organic saddle + organic Γ + zero Class A. "
            "Awaiting empirical benchmark validation."
        ),
    ),
]


# ── Vector operations ──────────────────────────────────────────────────────────

def _normalize(v: list[float]) -> list[float]:
    """L2 normalize a vector. Returns zero vector if magnitude is zero."""
    mag = math.sqrt(sum(x * x for x in v))
    if mag < 1e-12:
        return [0.0] * len(v)
    return [x / mag for x in v]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Cosine similarity between two pre-normalized vectors.
    Returns value in [-1.0, 1.0].
    """
    if len(a) != len(b):
        raise ValueError(f"Vector dimension mismatch: {len(a)} vs {len(b)}")
    return sum(x * y for x, y in zip(a, b))


def _match_tier(sim: float) -> str:
    if sim >= THRESHOLD_STRONG:   return "strong"
    if sim >= THRESHOLD_PROBABLE: return "probable"
    if sim >= THRESHOLD_PARTIAL:  return "partial"
    return "none"


# ── Query vector construction ──────────────────────────────────────────────────

def build_query_vector(
    pi:             float,
    gamma:          float,
    S:              float,
    E:              float,
    inverted_signal: float,
    node_count:     int,
    class_d_count:  int,
    class_a_count:  int,
    saddle_classification: str,
) -> list[float]:
    """
    Construct the 8-dimensional physics vector from a PiResult + GammaResult.

    All derived ratios are computed here. Raw counts are not used directly —
    ratios are needed for cross-query comparability at different cascade sizes.
    """
    class_d_ratio = class_d_count / max(node_count, 1)
    class_a_ratio = class_a_count / max(node_count, 1)
    saddle_enc    = SADDLE_ENCODING.get(saddle_classification, 0.5)

    return [
        float(pi),
        float(gamma),
        float(S),
        float(E),
        float(inverted_signal),
        class_d_ratio,
        class_a_ratio,
        saddle_enc,
    ]


# ── Library scan ───────────────────────────────────────────────────────────────

def scan_library(
    query_vector: list[float],
    top_k: int = 3,
    min_tier: str = "partial",
) -> LibraryResult:
    """
    Scan all signatures and return the top-k matches above min_tier threshold.

    Args:
      query_vector: Raw 8-dimensional physics vector from build_query_vector().
      top_k:        Maximum matches to return.
      min_tier:     Minimum match tier to include ("strong" | "probable" | "partial").

    Returns LibraryResult with ranked matches and campaign family assessment.
    """
    min_sim = {
        "strong":   THRESHOLD_STRONG,
        "probable": THRESHOLD_PROBABLE,
        "partial":  THRESHOLD_PARTIAL,
        "none":     0.0,
    }.get(min_tier, THRESHOLD_PARTIAL)

    q_norm = _normalize(query_vector)

    matches: list[SignatureMatch] = []
    for sig in SIGNATURE_LIBRARY:
        s_norm = _normalize(sig.vector)
        sim    = _cosine_similarity(q_norm, s_norm)
        tier   = _match_tier(sim)

        if sim >= min_sim:
            matches.append(SignatureMatch(
                benchmark_id=sig.benchmark_id,
                campaign_type=sig.campaign_type,
                quadrant=sig.quadrant,
                similarity=round(sim, 6),
                match_tier=tier,
                description=sig.description,
                notes=sig.notes,
            ))

    matches.sort(key=lambda m: m.similarity, reverse=True)
    matches = matches[:top_k]

    best       = matches[0] if matches else None
    best_sim   = best.similarity if best else 0.0

    # Campaign family: majority vote across top matches
    if matches:
        type_counts: dict[str, int] = {}
        for m in matches:
            type_counts[m.campaign_type] = type_counts.get(m.campaign_type, 0) + 1
        campaign_family = max(type_counts, key=type_counts.get)
    else:
        campaign_family = "No match found"

    interpretation = _interpret_library_result(best, best_sim, campaign_family)

    return LibraryResult(
        query_vector=query_vector,
        matches=matches,
        best_match=best,
        best_similarity=best_sim,
        campaign_family=campaign_family,
        library_interpretation=interpretation,
    )


def _interpret_library_result(
    best: Optional[SignatureMatch],
    sim: float,
    campaign_family: str,
) -> str:
    """Human-readable library scan interpretation for P4 Gate context."""
    if best is None or sim < THRESHOLD_PARTIAL:
        return (
            "No signature match above threshold. Physics vector is structurally "
            "distinct from all known campaign archetypes — this is either a novel "
            "campaign pattern or an organic signal."
        )

    tier_desc = {
        "strong":   f"Strong match (cosine similarity {sim:.4f})",
        "probable": f"Probable match (cosine similarity {sim:.4f})",
        "partial":  f"Partial match (cosine similarity {sim:.4f})",
    }[best.match_tier]

    return (
        f"{tier_desc} with '{best.campaign_type}' [{best.benchmark_id}]. "
        f"Quadrant alignment: {best.quadrant}. "
        f"{best.description}"
    )


# ── Integration entry point ────────────────────────────────────────────────────

def match_against_library(
    pi_result,
    gamma_result,
    top_k: int = 3,
    min_tier: str = "partial",
) -> LibraryResult:
    """
    Convenience wrapper: build vector from PiResult + GammaResult and scan.

    Intended for direct integration into engine.py after Step 3 (Γ computation):

        from signature_library import match_against_library
        library_result = match_against_library(pi_result, gamma_result)

    Args:
      pi_result:    PiResult from compute_pi()
      gamma_result: GammaResult from compute_gamma()
      top_k:        Top matches to return.
      min_tier:     Minimum tier threshold.

    Returns LibraryResult.
    """
    saddle_class = (
        pi_result.saddle_point.get("classification", "no_data")
        if isinstance(pi_result.saddle_point, dict)
        else getattr(pi_result.saddle_point, "classification", "no_data")
    )

    query_vector = build_query_vector(
        pi=pi_result.pi,
        gamma=gamma_result.gamma,
        S=pi_result.S,
        E=pi_result.E,
        inverted_signal=pi_result.inverted_signal,
        node_count=pi_result.node_count,
        class_d_count=pi_result.class_d_count,
        class_a_count=pi_result.class_a_count,
        saddle_classification=saddle_class,
    )

    return scan_library(query_vector, top_k=top_k, min_tier=min_tier)


# ── Library management utilities ───────────────────────────────────────────────

def add_signature(sig: ILOSignature) -> None:
    """
    Add a new signature to the runtime library.
    Does not persist to disk — for persistence, serialize SIGNATURE_LIBRARY to JSON.

    Validates:
      - benchmark_id is unique
      - vector has correct dimension
    """
    if len(sig.vector) != VECTOR_DIM:
        raise ValueError(
            f"Vector must have {VECTOR_DIM} dimensions, got {len(sig.vector)}"
        )
    existing_ids = {s.benchmark_id for s in SIGNATURE_LIBRARY}
    if sig.benchmark_id in existing_ids:
        raise ValueError(
            f"Signature with benchmark_id '{sig.benchmark_id}' already exists"
        )
    SIGNATURE_LIBRARY.append(sig)


def list_signatures() -> list[dict]:
    """Return a summary list of all registered signatures."""
    return [
        {
            "benchmark_id":  s.benchmark_id,
            "campaign_type": s.campaign_type,
            "quadrant":      s.quadrant,
            "notes":         s.notes,
        }
        for s in SIGNATURE_LIBRARY
    ]


def serialize_library() -> list[dict]:
    """Serialize full library to JSON-compatible list for persistence."""
    return [
        {
            "benchmark_id":  s.benchmark_id,
            "campaign_type": s.campaign_type,
            "quadrant":      s.quadrant,
            "vector":        s.vector,
            "description":   s.description,
            "notes":         s.notes,
        }
        for s in SIGNATURE_LIBRARY
    ]
