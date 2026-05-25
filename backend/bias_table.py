"""
ChronoDyne Systems // ILO Analyzer v4
Source Classification & Bias Lookup

Node Classes:
  A — Primary Sources       (highest T, direct evidential weight)
  B — Credentialed Media    (medium T, bias-adjusted)
  C — Volatile/Captured     (low T, watch-listed)
  D — Propagation Nodes     (inverted contribution — presence raises suspicion)

Geographic Scope:
  local        — city/regional outlet (e.g. local TV, city newspaper)
  national     — country-wide outlet
  international — multi-country / global reach
  global       — wire services, international bodies

Geo fields feed the Geographic Entropy (Γ) calculator.
"""

from dataclasses import dataclass, field
from typing import Optional
import math

# ── Node classification ───────────────────────────────────────────────────────

NODE_CLASS_A = "A"
NODE_CLASS_B = "B"
NODE_CLASS_C = "C"
NODE_CLASS_D = "D"

BASE_TRUST = {
    NODE_CLASS_A: 1.00,
    NODE_CLASS_B: 0.65,
    NODE_CLASS_C: 0.25,
    NODE_CLASS_D: 0.05,
}

CAPTURE_PENALTY   = 0.40
VOLATILITY_DECAY  = 0.20
HARD_LEAN_PENALTY = 0.25

GEO_SCOPES = ("local", "national", "international", "global", "unknown")


# ── Source record ─────────────────────────────────────────────────────────────

@dataclass
class SourceRecord:
    domain:      str
    node_class:  str
    lean:        float
    reliability: float
    sigma:       float
    notes:       str   = ""
    impact:      float = 1.0
    geo_scope:   str   = "unknown"   # local | national | international | global | unknown
    country:     str   = "unknown"   # ISO 3166-1 alpha-2 or 'intl'


@dataclass
class TrustScore:
    domain:      str
    node_class:  str
    base:        float
    adjusted:    float
    captured:    bool
    volatile:    bool
    inverted:    bool
    geo_scope:   str  = "unknown"
    country:     str  = "unknown"
    notes:       str  = ""


# ── Lookup table ──────────────────────────────────────────────────────────────

BIAS_TABLE: dict[str, SourceRecord] = {

    # ── CLASS A: Primary Sources ──────────────────────────────────────────────
    "arxiv.org":          SourceRecord("arxiv.org",          NODE_CLASS_A, 0.0,  0.95, 0.05, "Open preprint",                    geo_scope="global",        country="intl"),
    "pubmed.ncbi":        SourceRecord("pubmed.ncbi",         NODE_CLASS_A, 0.0,  0.98, 0.02, "NIH indexed",                      geo_scope="global",        country="US"),
    "sciencedirect.com":  SourceRecord("sciencedirect.com",   NODE_CLASS_A, 0.0,  0.97, 0.02,                                     geo_scope="global",        country="intl"),
    "nature.com":         SourceRecord("nature.com",          NODE_CLASS_A, 0.0,  0.97, 0.03,                                     geo_scope="global",        country="GB"),
    "science.org":        SourceRecord("science.org",         NODE_CLASS_A, 0.0,  0.97, 0.03,                                     geo_scope="global",        country="US"),
    "ieee.org":           SourceRecord("ieee.org",            NODE_CLASS_A, 0.0,  0.96, 0.02,                                     geo_scope="global",        country="US"),
    "jstor.org":          SourceRecord("jstor.org",           NODE_CLASS_A, 0.0,  0.95, 0.03,                                     geo_scope="global",        country="US"),
    "semanticscholar":    SourceRecord("semanticscholar",      NODE_CLASS_A, 0.0,  0.93, 0.04,                                     geo_scope="global",        country="US"),
    "openalex.org":       SourceRecord("openalex.org",        NODE_CLASS_A, 0.0,  0.95, 0.02,                                     geo_scope="global",        country="intl"),
    "scholar.google":     SourceRecord("scholar.google",      NODE_CLASS_A, 0.0,  0.90, 0.05, "Index only",                       geo_scope="global",        country="US"),
    "ssrn.com":           SourceRecord("ssrn.com",            NODE_CLASS_A, 0.0,  0.88, 0.06, "Preprint — unreviewed",            geo_scope="global",        country="US"),
    "figshare.com":       SourceRecord("figshare.com",        NODE_CLASS_A, 0.0,  0.85, 0.06, "Repository",                       geo_scope="global",        country="intl"),

    # Government & institutional
    ".gov":               SourceRecord(".gov",                NODE_CLASS_A, 0.0,  0.88, 0.08, "US gov TLD",                       geo_scope="national",      country="US"),
    ".mil":               SourceRecord(".mil",                NODE_CLASS_A, 0.0,  0.85, 0.08, "US military",                      geo_scope="national",      country="US"),
    ".edu":               SourceRecord(".edu",                NODE_CLASS_A, 0.0,  0.87, 0.07, "Academic TLD",                     geo_scope="national",      country="US"),
    "sec.gov":            SourceRecord("sec.gov",             NODE_CLASS_A, 0.0,  0.95, 0.02, "Regulatory filings",               geo_scope="national",      country="US"),
    "courtlistener.com":  SourceRecord("courtlistener.com",   NODE_CLASS_A, 0.0,  0.95, 0.02, "Court records",                    geo_scope="national",      country="US"),
    "pacer.gov":          SourceRecord("pacer.gov",           NODE_CLASS_A, 0.0,  0.97, 0.01, "Federal court",                    geo_scope="national",      country="US"),
    "congress.gov":       SourceRecord("congress.gov",        NODE_CLASS_A, 0.0,  0.95, 0.02,                                     geo_scope="national",      country="US"),
    "noaa.gov":           SourceRecord("noaa.gov",            NODE_CLASS_A, 0.0,  0.97, 0.01, "Weather baseline source",          geo_scope="national",      country="US"),
    "nasa.gov":           SourceRecord("nasa.gov",            NODE_CLASS_A, 0.0,  0.96, 0.02,                                     geo_scope="national",      country="US"),
    "who.int":            SourceRecord("who.int",             NODE_CLASS_A, 0.0,  0.88, 0.08, "International body",               geo_scope="global",        country="intl"),
    "un.org":             SourceRecord("un.org",              NODE_CLASS_A, 0.0,  0.82, 0.12, "Political exposure",               geo_scope="global",        country="intl"),

    # ── CLASS B: Credentialed Intermediaries ──────────────────────────────────
    # Wire services
    "reuters.com":        SourceRecord("reuters.com",         NODE_CLASS_B,  0.05, 0.90, 0.08,                                    geo_scope="global",        country="intl"),
    "apnews.com":         SourceRecord("apnews.com",          NODE_CLASS_B,  0.05, 0.91, 0.07,                                    geo_scope="global",        country="US"),
    "afp.com":            SourceRecord("afp.com",             NODE_CLASS_B,  0.05, 0.89, 0.08,                                    geo_scope="global",        country="FR"),

    # Center / center-adjacent
    "bbc.com":            SourceRecord("bbc.com",             NODE_CLASS_B, -0.10, 0.85, 0.12,                                    geo_scope="international", country="GB"),
    "bbc.co.uk":          SourceRecord("bbc.co.uk",           NODE_CLASS_B, -0.10, 0.85, 0.12,                                    geo_scope="international", country="GB"),
    "pbs.org":            SourceRecord("pbs.org",             NODE_CLASS_B, -0.15, 0.84, 0.10,                                    geo_scope="national",      country="US"),
    "npr.org":            SourceRecord("npr.org",             NODE_CLASS_B, -0.20, 0.82, 0.14,                                    geo_scope="national",      country="US"),
    "thehill.com":        SourceRecord("thehill.com",         NODE_CLASS_B,  0.00, 0.78, 0.18,                                    geo_scope="national",      country="US"),
    "bloomberg.com":      SourceRecord("bloomberg.com",       NODE_CLASS_B,  0.05, 0.86, 0.10,                                    geo_scope="international", country="US"),
    "wsj.com":            SourceRecord("wsj.com",             NODE_CLASS_B,  0.20, 0.85, 0.12,                                    geo_scope="international", country="US"),
    "economist.com":      SourceRecord("economist.com",       NODE_CLASS_B,  0.10, 0.88, 0.09,                                    geo_scope="international", country="GB"),
    "ft.com":             SourceRecord("ft.com",              NODE_CLASS_B,  0.10, 0.87, 0.09,                                    geo_scope="international", country="GB"),

    # Center-left
    "nytimes.com":        SourceRecord("nytimes.com",         NODE_CLASS_B, -0.30, 0.80, 0.18,                                    geo_scope="international", country="US"),
    "washingtonpost.com": SourceRecord("washingtonpost.com",  NODE_CLASS_B, -0.35, 0.78, 0.20,                                    geo_scope="national",      country="US"),
    "theguardian.com":    SourceRecord("theguardian.com",     NODE_CLASS_B, -0.35, 0.78, 0.18,                                    geo_scope="international", country="GB"),
    "politico.com":       SourceRecord("politico.com",        NODE_CLASS_B, -0.15, 0.80, 0.16,                                    geo_scope="national",      country="US"),
    "theatlantic.com":    SourceRecord("theatlantic.com",     NODE_CLASS_B, -0.30, 0.78, 0.16,                                    geo_scope="national",      country="US"),

    # Center-right
    "nypost.com":         SourceRecord("nypost.com",          NODE_CLASS_B,  0.40, 0.65, 0.25, "Approaching C threshold",         geo_scope="national",      country="US"),
    "reason.com":         SourceRecord("reason.com",          NODE_CLASS_B,  0.30, 0.75, 0.15, "Libertarian",                     geo_scope="national",      country="US"),
    "nationalreview.com": SourceRecord("nationalreview.com",  NODE_CLASS_B,  0.45, 0.70, 0.18, "Approaching C threshold",         geo_scope="national",      country="US"),

    # Think tanks
    "brookings.edu":      SourceRecord("brookings.edu",       NODE_CLASS_B, -0.20, 0.80, 0.15, "Center-left think tank",          geo_scope="national",      country="US"),
    "heritage.org":       SourceRecord("heritage.org",        NODE_CLASS_B,  0.55, 0.62, 0.22, "Right think tank",                geo_scope="national",      country="US"),
    "cato.org":           SourceRecord("cato.org",            NODE_CLASS_B,  0.35, 0.72, 0.18, "Libertarian think tank",          geo_scope="national",      country="US"),
    "aei.org":            SourceRecord("aei.org",             NODE_CLASS_B,  0.50, 0.68, 0.20, "Right think tank",                geo_scope="national",      country="US"),
    "cfr.org":            SourceRecord("cfr.org",             NODE_CLASS_B, -0.10, 0.80, 0.14, "Foreign policy establishment",    geo_scope="international", country="US"),

    # ── CLASS C: Volatile / Captured Outlets ──────────────────────────────────
    "foxnews.com":        SourceRecord("foxnews.com",         NODE_CLASS_C,  0.65, 0.50, 0.28, "High lean",                       geo_scope="national",      country="US"),
    "msnbc.com":          SourceRecord("msnbc.com",           NODE_CLASS_C, -0.65, 0.50, 0.28, "High lean",                       geo_scope="national",      country="US"),
    "cnn.com":            SourceRecord("cnn.com",             NODE_CLASS_C, -0.45, 0.60, 0.25, "Lean + volatile",                 geo_scope="international", country="US"),
    "huffpost.com":       SourceRecord("huffpost.com",        NODE_CLASS_C, -0.60, 0.52, 0.28,                                    geo_scope="national",      country="US"),
    "breitbart.com":      SourceRecord("breitbart.com",       NODE_CLASS_C,  0.85, 0.25, 0.35, "Hard capture",                    geo_scope="national",      country="US"),
    "dailykos.com":       SourceRecord("dailykos.com",        NODE_CLASS_C, -0.80, 0.28, 0.32, "Hard capture",                    geo_scope="national",      country="US"),
    "thefederalist.com":  SourceRecord("thefederalist.com",   NODE_CLASS_C,  0.75, 0.38, 0.30,                                    geo_scope="national",      country="US"),
    "salon.com":          SourceRecord("salon.com",           NODE_CLASS_C, -0.65, 0.45, 0.28,                                    geo_scope="national",      country="US"),
    "dailywire.com":      SourceRecord("dailywire.com",       NODE_CLASS_C,  0.80, 0.35, 0.32,                                    geo_scope="national",      country="US"),
    "mediamatters.org":   SourceRecord("mediamatters.org",    NODE_CLASS_C, -0.85, 0.30, 0.35, "Advocacy — not journalism",       geo_scope="national",      country="US"),
    "newsmax.com":        SourceRecord("newsmax.com",         NODE_CLASS_C,  0.80, 0.30, 0.35,                                    geo_scope="national",      country="US"),
    "oann.com":           SourceRecord("oann.com",            NODE_CLASS_C,  0.90, 0.20, 0.40, "Extreme capture",                 geo_scope="national",      country="US"),
    "snopes.com":         SourceRecord("snopes.com",          NODE_CLASS_C, -0.20, 0.45, 0.30, "Volunteer editorial",             geo_scope="national",      country="US"),
    "factcheck.org":      SourceRecord("factcheck.org",       NODE_CLASS_C, -0.15, 0.58, 0.22, "Institutional lean",              geo_scope="national",      country="US"),
    "politifact.com":     SourceRecord("politifact.com",      NODE_CLASS_C, -0.20, 0.55, 0.25, "Selection bias",                  geo_scope="national",      country="US"),
    "wikipedia.org":      SourceRecord("wikipedia.org",       NODE_CLASS_C,  0.0,  0.30, 0.40, "Open editing — pointer only",     geo_scope="global",        country="intl"),

    # ── CLASS D: Propagation Nodes ────────────────────────────────────────────
    "facebook.com":       SourceRecord("facebook.com",        NODE_CLASS_D,  0.0,  0.05, 0.50, "Documented ILO vector",           geo_scope="global",        country="US"),
    "twitter.com":        SourceRecord("twitter.com",         NODE_CLASS_D,  0.0,  0.05, 0.50, "Bot amplification",               geo_scope="global",        country="US"),
    "x.com":              SourceRecord("x.com",               NODE_CLASS_D,  0.0,  0.05, 0.50, "Same as twitter.com",             geo_scope="global",        country="US"),
    "tiktok.com":         SourceRecord("tiktok.com",          NODE_CLASS_D,  0.0,  0.04, 0.55, "Algorithmic + state-adjacent",    geo_scope="global",        country="CN"),
    "reddit.com":         SourceRecord("reddit.com",          NODE_CLASS_D,  0.0,  0.08, 0.48, "Brigading documented",            geo_scope="global",        country="US"),
    "instagram.com":      SourceRecord("instagram.com",       NODE_CLASS_D,  0.0,  0.05, 0.50,                                    geo_scope="global",        country="US"),
    "youtube.com":        SourceRecord("youtube.com",         NODE_CLASS_D,  0.0,  0.08, 0.45, "Watch-time decoupled from truth", geo_scope="global",        country="US"),
    "substack.com":       SourceRecord("substack.com",        NODE_CLASS_D,  0.0,  0.15, 0.40, "Unvetted",                        geo_scope="global",        country="US"),
    "medium.com":         SourceRecord("medium.com",          NODE_CLASS_D,  0.0,  0.12, 0.42, "Unvetted",                        geo_scope="global",        country="US"),
    "telegram.org":       SourceRecord("telegram.org",        NODE_CLASS_D,  0.0,  0.03, 0.60, "Encrypted propagation",           geo_scope="global",        country="intl"),
    "4chan.org":          SourceRecord("4chan.org",            NODE_CLASS_D,  0.0,  0.01, 0.70, "Coordinated campaign origination",geo_scope="global",        country="US"),
    "8kun.top":           SourceRecord("8kun.top",            NODE_CLASS_D,  0.0,  0.01, 0.75, "Extremist propagation",           geo_scope="global",        country="US"),
    "gab.com":            SourceRecord("gab.com",             NODE_CLASS_D,  0.0,  0.02, 0.70,                                    geo_scope="global",        country="US"),
    "truthsocial.com":    SourceRecord("truthsocial.com",     NODE_CLASS_D,  0.0,  0.03, 0.65,                                    geo_scope="national",      country="US"),
}


# ── Trust computation ─────────────────────────────────────────────────────────

def compute_trust(record: SourceRecord) -> TrustScore:
    base     = BASE_TRUST[record.node_class] * record.reliability * record.impact
    adjusted = base
    captured = False
    volatile = False

    if record.node_class == NODE_CLASS_D:
        return TrustScore(
            domain=record.domain, node_class=record.node_class,
            base=base, adjusted=adjusted,
            captured=False, volatile=False, inverted=True,
            geo_scope=record.geo_scope, country=record.country,
            notes=record.notes,
        )

    if abs(record.lean) > 0.6 and record.reliability < 0.5:
        adjusted *= CAPTURE_PENALTY
        captured = True

    if abs(record.lean) > 0.8:
        adjusted *= HARD_LEAN_PENALTY
        captured = True

    if record.sigma > 0.3:
        adjusted = max(0.0, adjusted - VOLATILITY_DECAY)
        volatile = True

    return TrustScore(
        domain=record.domain, node_class=record.node_class,
        base=round(base, 4), adjusted=round(adjusted, 4),
        captured=captured, volatile=volatile, inverted=False,
        geo_scope=record.geo_scope, country=record.country,
        notes=record.notes,
    )


def classify_domain(url: str) -> tuple[SourceRecord, TrustScore]:
    url_lower = url.lower()
    best_match: Optional[str] = None
    best_len = 0
    for fragment in BIAS_TABLE:
        if fragment in url_lower and len(fragment) > best_len:
            best_match = fragment
            best_len = len(fragment)

    if best_match:
        record = BIAS_TABLE[best_match]
    else:
        record = SourceRecord(
            domain=url_lower, node_class=NODE_CLASS_C,
            lean=0.0, reliability=0.35, sigma=0.35,
            notes="Unknown domain — no bias record available",
            geo_scope="unknown", country="unknown",
        )

    trust = compute_trust(record)
    return record, trust


def domain_is_inverted(url: str) -> bool:
    _, trust = classify_domain(url)
    return trust.inverted
