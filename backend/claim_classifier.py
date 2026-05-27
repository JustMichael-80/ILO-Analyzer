"""
ChronoDyne Systems // ILO Analyzer v4.5
Claim Classifier — Cultural Persistence Baseline Adjuster

Classifies the target claim into one of 12 topic classes and returns
a cultural persistence multiplier κ(C) that corrects τ_predicted(S)
for substrate heterogeneity.

Theoretical grounding:
  STOC derives τ_predicted(S) from citation graph Shannon entropy alone.
  It has no prior on the type of information ecosystem the claim inhabits.
  A conspiracy theory with dedicated subcultural infrastructure (books,
  podcasts, forums, researchers) will naturally sustain higher τ_observed
  than a breaking news story of equal complexity — not because of artificial
  maintenance, but because the substrate class has a longer natural half-life.

  The corrected persistence ratio is:

    Π_adjusted = τ_observed / (τ_predicted(S) · κ(C))

  Where κ(C) is the cultural persistence multiplier for claim class C.
  κ > 1 means the natural lifespan for this class is longer than base STOC
  predicts. κ = 1.0 means no adjustment. κ < 1 means shorter than base.

  The raw Π is always preserved and reported. The adjusted Π is a separate
  interpretive layer, transparently labeled. The P4 Gate receives both.

Claim classes:
  1  — Breaking News              κ: 0.3–0.5
  2  — Political Scandal          κ: 0.8–1.2
  3  — Suppressed Tech/Energy     κ: 4.0–8.0
  4  — Government Cover-Up        κ: 3.0–6.0
  5  — UFO/Non-Human Intelligence κ: 4.0–7.0
  6  — Assassination/Death        κ: 3.0–5.0
  7  — Pop Culture/Celebrity      κ: 2.0–4.0
  8  — Health/Medical Conspiracy  κ: 2.5–5.0
  9  — Financial/Economic         κ: 1.5–3.0
  10 — Academic/Technical Fringe  κ: 5.0–12.0
  11 — State IO (Suspected)       κ: 1.0 (no adjustment — Π speaks)
  12 — Organic Mundane News       κ: 0.3–0.8

Memetic trait detection:
  The classifier also scores the claim on six memetic fitness traits
  that predict organic long-term persistence independent of coordination:
    - suppressed_genius    (lone inventor vs. establishment narrative)
    - anti_authority       (appeals to distrust of institutions)
    - partial_docs         (real but miscontextualized documents exist)
    - mystery_core         (unanswerable central question)
    - martyr_element       (persecution of the truth-teller)
    - cyclical_trigger     (tied to recurring external events)

  High memetic fitness + high Π = organic fringe persistence.
  High memetic fitness + high Π + anomalous Γ = ILO using fringe as cover.
  This is the most dangerous and previously undetectable pattern.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Optional

from google import genai
from google.genai import types


# ── Claim class definitions ───────────────────────────────────────────────────

CLAIM_CLASSES = {
    1:  {"label": "Breaking News",              "kappa_mid": 0.40,  "kappa_range": (0.30, 0.50)},
    2:  {"label": "Political Scandal",          "kappa_mid": 1.00,  "kappa_range": (0.80, 1.20)},
    3:  {"label": "Suppressed Tech/Energy",     "kappa_mid": 6.00,  "kappa_range": (4.00, 8.00)},
    4:  {"label": "Government Cover-Up",        "kappa_mid": 4.50,  "kappa_range": (3.00, 6.00)},
    5:  {"label": "UFO/Non-Human Intelligence", "kappa_mid": 5.50,  "kappa_range": (4.00, 7.00)},
    6:  {"label": "Assassination/Death",        "kappa_mid": 4.00,  "kappa_range": (3.00, 5.00)},
    7:  {"label": "Pop Culture/Celebrity",      "kappa_mid": 3.00,  "kappa_range": (2.00, 4.00)},
    8:  {"label": "Health/Medical Conspiracy",  "kappa_mid": 3.75,  "kappa_range": (2.50, 5.00)},
    9:  {"label": "Financial/Economic",         "kappa_mid": 2.25,  "kappa_range": (1.50, 3.00)},
    10: {"label": "Academic/Technical Fringe",  "kappa_mid": 8.50,  "kappa_range": (5.00, 12.00)},
    11: {"label": "State IO (Suspected)",       "kappa_mid": 1.00,  "kappa_range": (1.00, 1.00)},
    12: {"label": "Organic Mundane News",       "kappa_mid": 0.55,  "kappa_range": (0.30, 0.80)},
}

# Evergreen reference narratives — used to anchor classification
EVERGREEN_ARCHETYPES = [
    "Roswell UFO crash (1947)",
    "Philadelphia Experiment",
    "HAARP weather control",
    "Tesla free energy suppression",
    "JFK assassination (lone gunman vs. conspiracy)",
    "Moon landing hoax",
    "Flat Earth",
    "Ancient aliens / Nazca lines",
    "Chemtrails / geoengineering",
    "Nikola Tesla vs. Edison establishment suppression",
    "MKUltra mind control programs",
    "Area 51 / reverse-engineered alien tech",
    "Mandela Effect",
    "Paul McCartney death hoax",
    "Bigfoot / Sasquatch",
    "Loch Ness Monster",
]


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class ClaimClassification:
    claim:                str
    claim_class_id:       int
    claim_class_label:    str
    kappa:                float          # Cultural persistence multiplier
    kappa_range:          tuple          # (min, max) for the class
    classifier_confidence: float         # 0.0–1.0
    memetic_traits:       dict           # Six trait scores 0.0–1.0
    memetic_fitness:      float          # Aggregate 0.0–1.0
    evergreen_archetype:  Optional[str]  # Closest reference narrative
    cyclical_signals:     list[str]      # Detected injection window correlations
    pi_interpretation_note: str          # Plain-language note for P4 Gate
    raw_response:         dict = field(default_factory=dict)


# ── Classifier system prompt ──────────────────────────────────────────────────

CLASSIFIER_SYSTEM_PROMPT = """You are the Claim Classifier module of the ChronoDyne ILO Analyzer.

Your task: classify a claim into exactly one of 12 topic classes and return a structured
JSON object. This classification is used to compute κ(C), the cultural persistence
multiplier that corrects the STOC-derived τ_predicted(S) for substrate heterogeneity.

CLAIM CLASSES:
1  — Breaking News              (κ mid: 0.40)  Recent events, fast decay expected
2  — Political Scandal          (κ mid: 1.00)  Standard political news cycle
3  — Suppressed Tech/Energy     (κ mid: 6.00)  Free energy, anti-gravity, suppressed inventors
4  — Government Cover-Up        (κ mid: 4.50)  Black projects, hidden programs, state secrets
5  — UFO/Non-Human Intelligence (κ mid: 5.50)  UAPs, alien contact, non-human tech
6  — Assassination/Death        (κ mid: 4.00)  Celebrity death conspiracies, political assassinations
7  — Pop Culture/Celebrity      (κ mid: 3.00)  Urban legends, celebrity myths, internet hoaxes
8  — Health/Medical Conspiracy  (κ mid: 3.75)  Vaccine claims, pharma suppression, cures
9  — Financial/Economic         (κ mid: 2.25)  Market manipulation, banking conspiracies
10 — Academic/Technical Fringe  (κ mid: 8.50)  Fringe physics, alternative science, pseudoscience
11 — State IO (Suspected)       (κ mid: 1.00)  Appears coordinated, no organic community signal
12 — Organic Mundane News       (κ mid: 0.55)  Standard journalism, no conspiracy framing

MEMETIC TRAIT SCORING (0.0–1.0 each):
- suppressed_genius:   Lone inventor or researcher vs. corrupt establishment narrative
- anti_authority:      Appeals to distrust of governments, corporations, or institutions
- partial_docs:        Real documents exist but are miscontextualized or incomplete
- mystery_core:        Central question that cannot be definitively answered
- martyr_element:      Truth-teller was persecuted, silenced, or died suspiciously
- cyclical_trigger:    Claim resurfaces predictably around elections, hearings, or anniversaries

CYCLICAL SIGNAL DETECTION:
Look for language suggesting the claim is tied to recurring external events:
- Congressional hearings or budget cycles
- Election seasons
- Anniversaries of original events
- Major news distractions
- Whistleblower disclosure windows

EVERGREEN ARCHETYPES:
If the claim closely resembles a known long-running narrative, identify the closest match.
Examples: Roswell, Philadelphia Experiment, HAARP, Tesla suppression, JFK, Moon landing hoax,
Flat Earth, Ancient aliens, Chemtrails, MKUltra, Area 51, Mandela Effect.

OUTPUT FORMAT — return ONLY this JSON object, no preamble, no markdown:
{
  "claim_class_id": <int 1-12>,
  "claim_class_label": <string>,
  "kappa": <float — your best estimate within the class range>,
  "classifier_confidence": <float 0.0-1.0>,
  "memetic_traits": {
    "suppressed_genius": <float 0.0-1.0>,
    "anti_authority": <float 0.0-1.0>,
    "partial_docs": <float 0.0-1.0>,
    "mystery_core": <float 0.0-1.0>,
    "martyr_element": <float 0.0-1.0>,
    "cyclical_trigger": <float 0.0-1.0>
  },
  "memetic_fitness": <float 0.0-1.0, aggregate of traits>,
  "evergreen_archetype": <string or null>,
  "cyclical_signals": [<list of specific signals detected, empty if none>],
  "pi_interpretation_note": <string — one sentence explaining what high Π means for THIS claim class>
}"""


# ── Classifier ────────────────────────────────────────────────────────────────

def classify_claim(claim: str, gemini_key: Optional[str] = None) -> ClaimClassification:
    """
    Classify a claim and return cultural persistence multiplier κ(C).

    Args:
      claim:      The unverified target flux string.
      gemini_key: Gemini API key. Falls back to GEMINI_API_KEY env var.

    Returns ClaimClassification with all fields populated.
    On API failure, returns a safe default (class 12, κ=1.0, no adjustment).
    """
    key = gemini_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return _default_classification(claim, reason="No Gemini API key available")

    try:
        ai = genai.Client(api_key=key)
        response = ai.models.generate_content(
            model="gemini-2.5-flash",
            contents=f'Classify this claim:\n\n"{claim}"',
            config=types.GenerateContentConfig(
                system_instruction=CLASSIFIER_SYSTEM_PROMPT,
                temperature=0.05,
                response_mime_type="application/json",
            ),
        )

        raw = json.loads(response.text)
        return _parse_response(claim, raw)

    except json.JSONDecodeError as e:
        return _default_classification(claim, reason=f"Malformed JSON from classifier: {e}")
    except Exception as e:
        return _default_classification(claim, reason=f"Classifier API error: {e}")


def _parse_response(claim: str, raw: dict) -> ClaimClassification:
    """Parse and validate the Gemini classifier response."""
    class_id = int(raw.get("claim_class_id", 12))
    if class_id not in CLAIM_CLASSES:
        class_id = 12

    class_def   = CLAIM_CLASSES[class_id]
    kappa_raw   = float(raw.get("kappa", class_def["kappa_mid"]))
    kappa_min, kappa_max = class_def["kappa_range"]
    kappa       = max(kappa_min, min(kappa_max, kappa_raw))

    traits_raw  = raw.get("memetic_traits", {})
    traits = {
        "suppressed_genius": float(traits_raw.get("suppressed_genius", 0.0)),
        "anti_authority":    float(traits_raw.get("anti_authority",    0.0)),
        "partial_docs":      float(traits_raw.get("partial_docs",      0.0)),
        "mystery_core":      float(traits_raw.get("mystery_core",      0.0)),
        "martyr_element":    float(traits_raw.get("martyr_element",    0.0)),
        "cyclical_trigger":  float(traits_raw.get("cyclical_trigger",  0.0)),
    }
    for k in traits:
        traits[k] = max(0.0, min(1.0, traits[k]))

    memetic_fitness = round(sum(traits.values()) / len(traits), 4)

    return ClaimClassification(
        claim=claim,
        claim_class_id=class_id,
        claim_class_label=raw.get("claim_class_label", class_def["label"]),
        kappa=round(kappa, 4),
        kappa_range=class_def["kappa_range"],
        classifier_confidence=max(0.0, min(1.0, float(raw.get("classifier_confidence", 0.5)))),
        memetic_traits=traits,
        memetic_fitness=memetic_fitness,
        evergreen_archetype=raw.get("evergreen_archetype"),
        cyclical_signals=raw.get("cyclical_signals", []),
        pi_interpretation_note=raw.get("pi_interpretation_note", ""),
        raw_response=raw,
    )


def _default_classification(claim: str, reason: str = "") -> ClaimClassification:
    """
    Safe fallback when classifier is unavailable.
    Returns class 12 (Organic Mundane) with κ=1.0 — no adjustment applied.
    The pipeline continues normally; classification is logged as unavailable.
    """
    print(f"[ClaimClassifier] Fallback classification. Reason: {reason}")
    return ClaimClassification(
        claim=claim,
        claim_class_id=12,
        claim_class_label="Organic Mundane News",
        kappa=1.0,
        kappa_range=(1.0, 1.0),
        classifier_confidence=0.0,
        memetic_traits={k: 0.0 for k in [
            "suppressed_genius", "anti_authority", "partial_docs",
            "mystery_core", "martyr_element", "cyclical_trigger"
        ]},
        memetic_fitness=0.0,
        evergreen_archetype=None,
        cyclical_signals=[],
        pi_interpretation_note="Classification unavailable — no κ adjustment applied.",
        raw_response={"error": reason},
    )


# ── Adjusted Π computation ────────────────────────────────────────────────────

def compute_adjusted_pi(pi_raw: float, tau_predicted: float, classification: ClaimClassification) -> dict:
    """
    Compute the κ-adjusted Persistence Ratio.

    Π_adjusted = τ_observed / (τ_predicted(S) · κ(C))

    A Π_adjusted near 1.0 means the story is persisting at the natural rate
    for its substrate class — even if the raw Π is very high.

    Returns a dict with:
      pi_adjusted:        float — the corrected Π
      pi_raw:             float — the original STOC-derived Π
      kappa:              float — the multiplier applied
      tau_predicted_adj:  float — κ-corrected τ_predicted
      adjustment_note:    str   — plain-language explanation
      organic_persistence: bool — True if Π_adjusted is within organic range
    """
    kappa = classification.kappa
    tau_predicted_adj = round(tau_predicted * kappa, 2)

    if tau_predicted_adj > 0:
        pi_adjusted = round(pi_raw * tau_predicted / tau_predicted_adj, 4)
    else:
        pi_adjusted = pi_raw

    organic_low  = 0.70
    organic_high = 1.40
    organic_persistence = organic_low <= pi_adjusted <= organic_high

    if classification.classifier_confidence == 0.0:
        note = "No κ adjustment — classifier unavailable."
    elif kappa == 1.0:
        note = (
            f"No κ adjustment for class '{classification.claim_class_label}' — "
            f"raw Π is the operative signal."
        )
    elif organic_persistence and pi_raw > organic_high:
        note = (
            f"Raw Π = {pi_raw:.2f} appears anomalous but adjusts to "
            f"Π_adj = {pi_adjusted:.4f} after κ = {kappa:.2f} correction for "
            f"'{classification.claim_class_label}' substrate. "
            f"This is consistent with organic cultural persistence — not engineered maintenance. "
            f"Confidence: {classification.classifier_confidence:.0%}."
        )
    elif not organic_persistence and pi_raw > organic_high:
        note = (
            f"Raw Π = {pi_raw:.2f} adjusts to Π_adj = {pi_adjusted:.4f} after "
            f"κ = {kappa:.2f} correction for '{classification.claim_class_label}' substrate. "
            f"Even accounting for organic cultural persistence, this narrative is "
            f"persisting {pi_adjusted:.1f}x longer than the adjusted natural lifespan. "
            f"Artificial maintenance signal survives κ correction. "
            f"Confidence: {classification.classifier_confidence:.0%}."
        )
    else:
        note = (
            f"κ = {kappa:.2f} correction applied for '{classification.claim_class_label}'. "
            f"Π_adj = {pi_adjusted:.4f}."
        )

    return {
        "pi_adjusted":       pi_adjusted,
        "pi_raw":            pi_raw,
        "kappa":             kappa,
        "tau_predicted_adj": tau_predicted_adj,
        "adjustment_note":   note,
        "organic_persistence": organic_persistence,
        "claim_class":       classification.claim_class_label,
        "memetic_fitness":   classification.memetic_fitness,
        "evergreen_archetype": classification.evergreen_archetype,
    }
