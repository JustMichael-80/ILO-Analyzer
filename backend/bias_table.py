"""
ChronoDyne Systems // ILO Analyzer v4
Source Classification & Bias Lookup

Node Classes:
  A — Primary Sources       (highest T, direct evidential weight)
  B — Credentialed Media    (medium T, bias-adjusted)
  C — Volatile/Captured     (low T, watch-listed)
  D — Propagation Nodes     (inverted contribution — presence raises suspicion)

Bias scores sourced from:
  - AllSides Media Bias Ratings (published, crowd+editorial)
  - Ad Fontes Media Bias Chart (reliability + bias axes)
  - Media Bias/Fact Check (factual reporting score separate from lean)

Lean scale:  -1.0 (hard left) → 0.0 (center) → +1.0 (hard right)
Reliability:  0.0 (unreliable) → 1.0 (maximally reliable)

Political capture penalty applies when:
  |lean| > 0.6 AND reliability < 0.5  →  T decays by capture_penalty factor
  |lean| > 0.8                         →  additional hard penalty regardless of reliability

Volatility penalty applies when σ_political (variance across raters) > 0.3
"""

from dataclasses import dataclass, field
from typing import Optional
import math

# ── Node classification ───────────────────────────────────────────────────────

NODE_CLASS_A = "A"   # Primary sources
NODE_CLASS_B = "B"   # Credentialed intermediaries
NODE_CLASS_C = "C"   # Volatile / captured
NODE_CLASS_D = "D"   # Propagation nodes (inverted)

# Base trust weights by class
BASE_TRUST = {
    NODE_CLASS_A: 1.00,
    NODE_CLASS_B: 0.65,
    NODE_CLASS_C: 0.25,
    NODE_CLASS_D: 0.05,   # Near-zero positive; inversion handled separately
}

CAPTURE_PENALTY  = 0.40   # Multiplier applied on political capture detection
VOLATILITY_DECAY = 0.20   # Subtracted from trust when σ_political > 0.3
HARD_LEAN_PENALTY = 0.25  # Additional multiplier when |lean| > 0.8


# ── Source record ─────────────────────────────────────────────────────────────

@dataclass
class SourceRecord:
    domain:      str
    node_class:  str
    lean:        float        # -1.0 → +1.0
    reliability: float        # 0.0  → 1.0
    sigma:       float        # Cross-rater variance (0.0 = unanimous, 1.0 = maximal disagreement)
    notes:       str = ""
    impact:      float = 1.0  # Journal/outlet impact multiplier (OpenAlex/Scimago for Class A)


@dataclass
class TrustScore:
    domain:      str
    node_class:  str
    base:        float
    adjusted:    float
    captured:    bool
    volatile:    bool
    inverted:    bool         # True for Class D — high reach = suspicion signal
    notes:       str = ""


# ── Lookup table ──────────────────────────────────────────────────────────────
# Format: domain_fragment → SourceRecord
# Domain fragments are matched as substrings of the lowercased URL.

BIAS_TABLE: dict[str, SourceRecord] = {

    # ── CLASS A: Primary Sources ──────────────────────────────────────────────
    # Academic & scientific infrastructure
    "arxiv.org":          SourceRecord("arxiv.org",          NODE_CLASS_A, 0.0,  0.95, 0.05, "Open preprint — weight by citation count"),
    "pubmed.ncbi":        SourceRecord("pubmed.ncbi",         NODE_CLASS_A, 0.0,  0.98, 0.02, "NIH indexed"),
    "sciencedirect.com":  SourceRecord("sciencedirect.com",   NODE_CLASS_A, 0.0,  0.97, 0.02),
    "nature.com":         SourceRecord("nature.com",          NODE_CLASS_A, 0.0,  0.97, 0.03),
    "science.org":        SourceRecord("science.org",         NODE_CLASS_A, 0.0,  0.97, 0.03),
    "ieee.org":           SourceRecord("ieee.org",            NODE_CLASS_A, 0.0,  0.96, 0.02),
    "jstor.org":          SourceRecord("jstor.org",           NODE_CLASS_A, 0.0,  0.95, 0.03),
    "semanticscholar":    SourceRecord("semanticscholar",      NODE_CLASS_A, 0.0,  0.93, 0.04),
    "openalex.org":       SourceRecord("openalex.org",        NODE_CLASS_A, 0.0,  0.95, 0.02),
    "scholar.google":     SourceRecord("scholar.google",      NODE_CLASS_A, 0.0,  0.90, 0.05, "Index only — follow to primary"),
    "ssrn.com":           SourceRecord("ssrn.com",            NODE_CLASS_A, 0.0,  0.88, 0.06, "Preprint — unreviewed"),
    "figshare.com":       SourceRecord("figshare.com",        NODE_CLASS_A, 0.0,  0.85, 0.06, "Repository — weight by citation"),

    # Government & institutional primary
    ".gov":               SourceRecord(".gov",                NODE_CLASS_A, 0.0,  0.88, 0.08, "TLD — apply agency-specific scrutiny"),
    ".mil":               SourceRecord(".mil",                NODE_CLASS_A, 0.0,  0.85, 0.08, "Military — official but narrow scope"),
    ".edu":               SourceRecord(".edu",                NODE_CLASS_A, 0.0,  0.87, 0.07, "Academic TLD"),
    "sec.gov":            SourceRecord("sec.gov",             NODE_CLASS_A, 0.0,  0.95, 0.02, "Regulatory filings — primary documents"),
    "courtlistener.com":  SourceRecord("courtlistener.com",   NODE_CLASS_A, 0.0,  0.95, 0.02, "Court records"),
    "pacer.gov":          SourceRecord("pacer.gov",           NODE_CLASS_A, 0.0,  0.97, 0.01, "Federal court — primary"),
    "congress.gov":       SourceRecord("congress.gov",        NODE_CLASS_A, 0.0,  0.95, 0.02),
    "noaa.gov":           SourceRecord("noaa.gov",            NODE_CLASS_A, 0.0,  0.97, 0.01, "Weather baseline source"),
    "nasa.gov":           SourceRecord("nasa.gov",            NODE_CLASS_A, 0.0,  0.96, 0.02),
    "who.int":            SourceRecord("who.int",             NODE_CLASS_A, 0.0,  0.88, 0.08, "International body — political exposure"),
    "un.org":             SourceRecord("un.org",              NODE_CLASS_A, 0.0,  0.82, 0.12, "Political exposure — apply scrutiny"),

    # ── CLASS B: Credentialed Intermediaries ──────────────────────────────────
    # Wire services (lowest bias, highest reliability in class)
    "reuters.com":        SourceRecord("reuters.com",         NODE_CLASS_B,  0.05, 0.90, 0.08),
    "apnews.com":         SourceRecord("apnews.com",          NODE_CLASS_B,  0.05, 0.91, 0.07),
    "afp.com":            SourceRecord("afp.com",             NODE_CLASS_B,  0.05, 0.89, 0.08),

    # Center / center-adjacent
    "bbc.com":            SourceRecord("bbc.com",             NODE_CLASS_B, -0.10, 0.85, 0.12),
    "bbc.co.uk":          SourceRecord("bbc.co.uk",           NODE_CLASS_B, -0.10, 0.85, 0.12),
    "pbs.org":            SourceRecord("pbs.org",             NODE_CLASS_B, -0.15, 0.84, 0.10),
    "npr.org":            SourceRecord("npr.org",             NODE_CLASS_B, -0.20, 0.82, 0.14),
    "thehill.com":        SourceRecord("thehill.com",         NODE_CLASS_B,  0.00, 0.78, 0.18),
    "bloomberg.com":      SourceRecord("bloomberg.com",       NODE_CLASS_B,  0.05, 0.86, 0.10),
    "wsj.com":            SourceRecord("wsj.com",             NODE_CLASS_B,  0.20, 0.85, 0.12),
    "economist.com":      SourceRecord("economist.com",       NODE_CLASS_B,  0.10, 0.88, 0.09),
    "ft.com":             SourceRecord("ft.com",              NODE_CLASS_B,  0.10, 0.87, 0.09),

    # Center-left
    "nytimes.com":        SourceRecord("nytimes.com",         NODE_CLASS_B, -0.30, 0.80, 0.18),
    "washingtonpost.com": SourceRecord("washingtonpost.com",  NODE_CLASS_B, -0.35, 0.78, 0.20),
    "theguardian.com":    SourceRecord("theguardian.com",     NODE_CLASS_B, -0.35, 0.78, 0.18),
    "politico.com":       SourceRecord("politico.com",        NODE_CLASS_B, -0.15, 0.80, 0.16),
    "theatlantic.com":    SourceRecord("theatlantic.com",     NODE_CLASS_B, -0.30, 0.78, 0.16),

    # Center-right
    "nypost.com":         SourceRecord("nypost.com",          NODE_CLASS_B,  0.40, 0.65, 0.25, "Approaching C threshold"),
    "reason.com":         SourceRecord("reason.com",          NODE_CLASS_B,  0.30, 0.75, 0.15, "Libertarian — consistent lean"),
    "nationalreview.com": SourceRecord("nationalreview.com",  NODE_CLASS_B,  0.45, 0.70, 0.18, "Approaching C threshold"),

    # Think tanks (capture-flagged)
    "brookings.edu":      SourceRecord("brookings.edu",       NODE_CLASS_B, -0.20, 0.80, 0.15, "Center-left think tank"),
    "heritage.org":       SourceRecord("heritage.org",        NODE_CLASS_B,  0.55, 0.62, 0.22, "Right think tank — near C"),
    "cato.org":           SourceRecord("cato.org",            NODE_CLASS_B,  0.35, 0.72, 0.18, "Libertarian think tank"),
    "aei.org":            SourceRecord("aei.org",             NODE_CLASS_B,  0.50, 0.68, 0.20, "Right think tank"),
    "cfr.org":            SourceRecord("cfr.org",             NODE_CLASS_B, -0.10, 0.80, 0.14, "Foreign policy establishment"),

    # ── CLASS C: Volatile / Captured Outlets ──────────────────────────────────
    "foxnews.com":        SourceRecord("foxnews.com",         NODE_CLASS_C,  0.65, 0.50, 0.28, "High lean, reliability declining"),
    "msnbc.com":          SourceRecord("msnbc.com",           NODE_CLASS_C, -0.65, 0.50, 0.28, "High lean, reliability declining"),
    "cnn.com":            SourceRecord("cnn.com",             NODE_CLASS_C, -0.45, 0.60, 0.25, "Lean + volatile editorial"),
    "huffpost.com":       SourceRecord("huffpost.com",        NODE_CLASS_C, -0.60, 0.52, 0.28),
    "breitbart.com":      SourceRecord("breitbart.com",       NODE_CLASS_C,  0.85, 0.25, 0.35, "Hard capture — near D"),
    "dailykos.com":       SourceRecord("dailykos.com",        NODE_CLASS_C, -0.80, 0.28, 0.32, "Hard capture — near D"),
    "thefederalist.com":  SourceRecord("thefederalist.com",   NODE_CLASS_C,  0.75, 0.38, 0.30),
    "salon.com":          SourceRecord("salon.com",           NODE_CLASS_C, -0.65, 0.45, 0.28),
    "dailywire.com":      SourceRecord("dailywire.com",       NODE_CLASS_C,  0.80, 0.35, 0.32),
    "mediamatters.org":   SourceRecord("mediamatters.org",    NODE_CLASS_C, -0.85, 0.30, 0.35, "Advocacy — not journalism"),
    "newsmax.com":        SourceRecord("newsmax.com",         NODE_CLASS_C,  0.80, 0.30, 0.35),
    "oann.com":           SourceRecord("oann.com",            NODE_CLASS_C,  0.90, 0.20, 0.40, "Extreme capture"),

    # Low-reliability aggregators
    "snopes.com":         SourceRecord("snopes.com",          NODE_CLASS_C, -0.20, 0.45, 0.30, "Volunteer editorial, documented bias cases — pointer only"),
    "factcheck.org":      SourceRecord("factcheck.org",       NODE_CLASS_C, -0.15, 0.58, 0.22, "Generally reliable but institutional lean"),
    "politifact.com":     SourceRecord("politifact.com",      NODE_CLASS_C, -0.20, 0.55, 0.25, "Documented selection bias in claim choice"),

    # Human-corruption-vulnerable reference
    "wikipedia.org":      SourceRecord("wikipedia.org",       NODE_CLASS_C,  0.0,  0.30, 0.40, "Open editing — circular citation risk. Pointer only, never terminal"),

    # ── CLASS D: Propagation Nodes (inverted contribution) ────────────────────
    # Presence in citation graph = ILO signal, not credibility
    "facebook.com":       SourceRecord("facebook.com",        NODE_CLASS_D,  0.0,  0.05, 0.50, "Algorithmic amplification — documented ILO vector"),
    "twitter.com":        SourceRecord("twitter.com",         NODE_CLASS_D,  0.0,  0.05, 0.50, "Bot amplification infrastructure"),
    "x.com":              SourceRecord("x.com",               NODE_CLASS_D,  0.0,  0.05, 0.50, "Same as twitter.com post-rebrand"),
    "tiktok.com":         SourceRecord("tiktok.com",          NODE_CLASS_D,  0.0,  0.04, 0.55, "Algorithmic + state-adjacent"),
    "reddit.com":         SourceRecord("reddit.com",          NODE_CLASS_D,  0.0,  0.08, 0.48, "Upvote mechanics trivially gameable — brigading documented"),
    "instagram.com":      SourceRecord("instagram.com",       NODE_CLASS_D,  0.0,  0.05, 0.50),
    "youtube.com":        SourceRecord("youtube.com",         NODE_CLASS_D,  0.0,  0.08, 0.45, "Watch-time optimization decoupled from accuracy"),
    "substack.com":       SourceRecord("substack.com",        NODE_CLASS_D,  0.0,  0.15, 0.40, "Unvetted — treat as social unless author is Class A/B credentialed"),
    "medium.com":         SourceRecord("medium.com",          NODE_CLASS_D,  0.0,  0.12, 0.42, "Unvetted — same as Substack"),
    "telegram.org":       SourceRecord("telegram.org",        NODE_CLASS_D,  0.0,  0.03, 0.60, "Encrypted propagation — high ILO vector"),
    "4chan.org":          SourceRecord("4chan.org",            NODE_CLASS_D,  0.0,  0.01, 0.70, "Origination node for coordinated campaigns"),
    "8kun.top":           SourceRecord("8kun.top",            NODE_CLASS_D,  0.0,  0.01, 0.75, "Extremist propagation node"),
    "gab.com":            SourceRecord("gab.com",             NODE_CLASS_D,  0.0,  0.02, 0.70),
    "truthsocial.com":    SourceRecord("truthsocial.com",     NODE_CLASS_D,  0.0,  0.03, 0.65),
}


# ── Trust computation ─────────────────────────────────────────────────────────

def compute_trust(record: SourceRecord) -> TrustScore:
    """
    Apply capture and volatility penalties to base class trust weight.
    Class D nodes are flagged as inverted — caller handles sign flip.
    """
    base = BASE_TRUST[record.node_class] * record.reliability * record.impact
    adjusted = base
    captured = False
    volatile = False

    if record.node_class == NODE_CLASS_D:
        return TrustScore(
            domain=record.domain,
            node_class=record.node_class,
            base=base,
            adjusted=adjusted,
            captured=False,
            volatile=False,
            inverted=True,
            notes=record.notes,
        )

    # Political capture check
    if abs(record.lean) > 0.6 and record.reliability < 0.5:
        adjusted *= CAPTURE_PENALTY
        captured = True

    # Hard lean penalty (regardless of reliability)
    if abs(record.lean) > 0.8:
        adjusted *= HARD_LEAN_PENALTY
        captured = True

    # Cross-rater volatility decay
    if record.sigma > 0.3:
        adjusted = max(0.0, adjusted - VOLATILITY_DECAY)
        volatile = True

    return TrustScore(
        domain=record.domain,
        node_class=record.node_class,
        base=round(base, 4),
        adjusted=round(adjusted, 4),
        captured=captured,
        volatile=volatile,
        inverted=False,
        notes=record.notes,
    )


def classify_domain(url: str) -> tuple[SourceRecord, TrustScore]:
    """
    Match a URL against the bias table. Returns (record, trust_score).
    Falls back to a generic unknown record if no match found.
    """
    url_lower = url.lower()

    # Longest-match wins (more specific entries override TLD entries)
    best_match: Optional[str] = None
    best_len = 0
    for fragment in BIAS_TABLE:
        if fragment in url_lower and len(fragment) > best_len:
            best_match = fragment
            best_len = len(fragment)

    if best_match:
        record = BIAS_TABLE[best_match]
    else:
        # Unknown domain — treat as Class C with neutral lean, low reliability
        record = SourceRecord(
            domain=url_lower,
            node_class=NODE_CLASS_C,
            lean=0.0,
            reliability=0.35,
            sigma=0.35,
            notes="Unknown domain — no bias record available",
        )

    trust = compute_trust(record)
    return record, trust


def domain_is_inverted(url: str) -> bool:
    """Quick check: is this URL a Class D propagation node?"""
    _, trust = classify_domain(url)
    return trust.inverted
