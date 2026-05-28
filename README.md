# ChronoDyne Systems, Inc. // ILO Analyzer v4.5

An automated, cloud-isolated information triage engine built to identify and map **Information Laundering Operations (ILOs)** — coordinated campaigns to manufacture, amplify, or suppress narratives. This architecture bypasses surface-level text classification by measuring the **thermodynamic footprint of data propagation** directly — computing whether a narrative is persisting naturally or being artificially sustained against entropic decay, across both temporal and geographic dimensions simultaneously.

---

## Theoretical Framework: The Principle of Persistent Structurization (PPS)

Standard fact-checking utilities fail because they treat disinformation as a static content problem. The ILO Analyzer treats information as an open, non-equilibrium thermodynamic system governed by the Constructal Law (Bejan, 2011).

When a real-world event occurs, the resulting information naturally optimizes its access paths over time, maintaining structural integrity across varying geographical and institutional nodes. Conversely, an engineered campaign exhibits a distinct artificial signature: a rapid injection of organized configuration that fails to structurally adapt, or a narrative held artificially above its natural decay threshold by coordinated propagation.

### Primary Metric: Persistence Ratio (Π)

**Π = τ_observed / τ_predicted(S)**

Where τ_predicted(S) is derived from the Scale-Timescale Optimization Corollary (STOC):

**τ*(S) ~ S^α · E^(-β)**

- **S** = Shannon entropy of the citation graph edge weight distribution
- **E** = System complexity (trust-weighted node count)
- **α = 1.2** (superlinear scaling exponent; α > 1 per STOC)
- **β = 0.5** (energy flux exponent)

Π ≈ 1.0 indicates organic natural persistence. Π >> 1.0 indicates artificial maintenance. Π << 1.0 indicates ILO Fade — engineered collapse faster than natural decay predicts.

### Cultural Persistence Correction: κ(C)

v4.5 introduces the **cultural persistence multiplier κ(C)**, which corrects τ_predicted for substrate heterogeneity:

**Π_adjusted = τ_observed / (τ_predicted(S) · κ(C))**

Evergreen conspiracy narratives, academic fringe communities, and pop culture myths have naturally longer information half-lives than breaking news — not because of artificial maintenance, but because dedicated subcultural infrastructure (books, podcasts, forums, researchers) organically sustains them. κ(C) corrects for this prior so the system distinguishes:

- **Organic evergreen persistence** — Π_adj ≈ 1.0 even when raw Π is very high
- **Engineered maintenance surviving correction** — Π_adj >> 1.0 even after κ applied
- **State IO using fringe as cover** — the most dangerous pattern: Γ anomalous + Π_adj > 2.0 + near-zero Class A despite decades of claimed research

| Claim Class | κ range | Example |
|-------------|---------|---------|
| Breaking News | 0.3–0.5 | Plane crash |
| Political Scandal | 0.8–1.2 | Watergate |
| Suppressed Tech/Energy | 4.0–8.0 | TT Brown, free energy |
| Government Cover-Up | 3.0–6.0 | Black projects, state secrets |
| UFO/Non-Human Intelligence | 4.0–7.0 | UAPs, alien contact |
| Assassination/Death | 3.0–5.0 | Celebrity death conspiracies |
| Pop Culture/Celebrity | 2.0–4.0 | Mandela Effect |
| Health/Medical Conspiracy | 2.5–5.0 | Vaccine claims |
| Financial/Economic | 1.5–3.0 | Market manipulation |
| Academic/Technical Fringe | 5.0–12.0 | Alternative physics |
| State IO (Suspected) | 1.0 | No adjustment — Π speaks |
| Organic Mundane News | 0.3–0.8 | Standard journalism |

### Second Metric: Geographic Entropy (Γ)

**Γ = H_geographic / H_expected(t)**

Where H_expected(t) models organic geographic diffusion:

**H_expected(t) = H_max · (1 - e^(-t / τ_diffusion))**

- **H_geographic** = Shannon entropy of source geographic scope distribution
- **H_expected(t)** = expected entropy for a naturally diffusing story at time t
- **τ_diffusion = 14 days** (characteristic local→international timescale)

Γ ≈ 1.0 indicates organic diffusion. Γ >> 1.0 indicates coordinated geographic injection — narrative appearing simultaneously at global scope with no local precursor. Γ << 1.0 indicates suppression — narrative geographically contained below natural diffusion prediction.

### The Π/Γ Diagnostic Coordinate Space

| | Γ high | Γ low |
|---|---|---|
| **Π high** | **Quadrant I — Confirmed ILO** | **Quadrant II — Astroturfed Local** |
| **Π low** | **Quadrant III — Viral Suppression** | **Quadrant IV — Suppressed Real Event** |

Center (both near 1.0) = Organic.

Both metrics are derived from PPS and STOC as published in the formal framework below.

---

## Architecture: What Actually Runs

### Six-Phase Search Cascade

1. Primary source ingestion
2. Local journalism scan
3. Deep archive cascade (advanced depth)
4. Debunking cross-reference
5. Institutional corroboration
6. **Declassified document archaeology** — FOIA archives, National Archives, DTIC, FBI Vault, CIA CREST reading room, DOE/OSTI

Phase 6 is what separates this tool from every other disinformation detector. A narrative with a real government paper trail is diagnostically different from one with zero primary source archaeology — and the system now goes looking for that evidence deliberately.

### Source Classification (Class A/B/C/D)

Every source URL is classified against an 80+ domain bias table:

| Class | Type | Trust Weight | Contribution |
|-------|------|-------------|--------------|
| A | Primary sources (academic, gov, court, FOIA archives) | ~0.85–1.00 | Positive |
| B | Credentialed intermediaries (wire services, established news) | ~0.45–0.65 | Positive |
| C | Volatile/captured outlets | ~0.00–0.25 | Reduced |
| D | Propagation nodes (social media, forums) | ~0.01–0.08 | **Inverted — raises suspicion** |

New Class A entries include: `archives.gov`, `vault.fbi.gov`, `dtic.mil`, `cia.gov` (CREST), `osti.gov`, `gao.gov`, `govinfo.gov`, `history.state.gov`, `nationalarchives.gov.uk`, and others.

### Multi-Substrate Physical Baseline (v4.5)

The saddle-point tracker now computes a **consensus decay constant λ_consensus** from six independent physical substrates — processes with zero correlation to human information systems:

| Substrate | Source | Why it matters |
|-----------|--------|----------------|
| Atmospheric forecast decay | NOAA/open-meteo | Original PPS theoretical grounding |
| Geomagnetic Kp index | NOAA SWPC | 70-year daily record, independent of civilization |
| Solar F10.7 flux | NOAA SWPC | 75-year record, solar activity proxy |
| Lunar phase cycle | Deterministic ephemeris | Exact to milliseconds, zero measurement error |
| Seismic noise floor | USGS FDSN | Earth's background hum |
| Quasar flux variability | 3C 273 literature (τ=12d) | Accretion disk physics — as substrate-independent as it gets |

**λ_consensus = Σ(w_i · λ_i) / Σ(w_i)**

The multi-substrate reference cannot be gamed, faked, or correlated with any information operation. This is the foundation of the v5.x cross-substrate Λ index.

### Claim Classifier (v4.5)

A dedicated Gemini call classifies the claim before physics computation:

- **Claim class** (one of 12) → κ multiplier
- **Memetic trait scores** — suppressed_genius, anti_authority, partial_docs, mystery_core, martyr_element, cyclical_trigger
- **Memetic fitness** — aggregate 0.0–1.0; high fitness + organic Π_adj = genuine community persistence
- **Evergreen archetype** — closest reference narrative (Roswell, Philadelphia Experiment, etc.)
- **Cyclical signals** — detected injection window correlations (congressional hearings, election cycles, anniversaries)

### ILO Signature Library (v4.5 — 12 signatures)

Cosine similarity matching against known campaign vectors in 8-dimensional physics space:
`[Π, Γ, S, E, inverted_signal, class_d_ratio, class_a_ratio, saddle_encoded]`

| ID | Type | Quadrant |
|----|------|---------|
| BM-001 | State-Sponsored Historical Revisionism | I — Confirmed ILO |
| BM-002 | Domestic Astroturfing | II — Astroturfed Local |
| BM-003 | Coordinated Suppression | III — Viral Suppression |
| SYN-001 | Organic True Signal | Organic |
| SYN-002 | Fast Injection Campaign | I — Confirmed ILO |
| SYN-003 | Suppressed Real Event | IV — Suppressed Real Event |
| SYN-004 | Organic Conspiracy | Organic |
| SYN-005 | Narrative Spent | Organic |
| SYN-006 | Commercial Clickbait | III — Viral Suppression |
| SYN-007 | State Media Narrative | I — Confirmed ILO |
| SYN-008 | **Organic Evergreen Conspiracy** | II (raw) → Organic (adj) |
| SYN-009 | **Cyclically Stirred Narrative** | II — Periodic re-injection |
| SYN-010 | **Astroturfed via Conspiracy Fringe** | I — Most dangerous pattern |
| SYN-011 | **Academic/Technical Fringe** | Organic |
| SYN-012 | **Pop Culture Myth** | Organic |

SYN-010 is the most significant addition: a state actor deliberately using existing conspiracy communities as a laundering vector. Previously undetectable without κ correction.

### GEOINT Globe (v4.4)

Three.js globe visualization of source node geographic distribution:
- Auto-rotating dark sphere with latitude/longitude grid and Earth texture
- Color-coded pins by class (A=green, B=blue, C=yellow, D=red)
- Pin size scaled by trust score
- Red arc lines connecting Class D propagation nodes
- Mouse wheel zoom, drag to rotate, click pin to inspect full node details
- Sticky sidebar on xl screens; collapsible panel on mobile

### P4 Gate (Gemini Verdict Synthesis)

The full physics block — raw Π, Π_adjusted, κ, Γ, quadrant, τ_observed, τ_predicted, S, E, node classification, saddle-point deviation, λ_consensus, claim class, memetic fitness, evergreen archetype, ilo_survives_correction, adjusted_verdict_weight — is computed deterministically and injected as ground truth. Gemini synthesizes only. The LLM does not compute Π or Γ and cannot override either.

### Analyst Report

A second Gemini pass at higher temperature reasons over the compiled physics report as an investigative analyst — generating pattern hypotheses with confidence scores, actor profiling, red flags, investigative next steps, and follow-up claims. Downloadable as markdown.

---

## Empirical Results

| Claim | Π_raw | Π_adj | κ | Γ | Quadrant | Verdict |
|-------|-------|-------|---|---|----------|---------|
| JFK/Dimona | 41.91 | — | — | — | I — Confirmed ILO | 95% |
| Podesta/Bennington | 0.0 | — | — | 5.0 | III — Viral Suppression | 95% |
| GPT-4.0 is AGI | 25.10 | — | — | 0.46 | II — Astroturfed Local | 85% |
| TT Brown USAF suppression | 118–289 | ~19–48 | 6.0 | 0.66–0.68 | II — Astroturfed Local | 85–90% |

The TT Brown result demonstrates κ correction in practice: raw Π = 118–289 appears catastrophically anomalous. After κ = 6.0 correction for "Suppressed Tech/Energy" substrate, Π_adj = 19–48 — still 19–48× the adjusted natural lifespan. Artificial maintenance survives κ correction. The system correctly identifies engineered persistence even within a genuinely active fringe community.

---

## 6M Wildness Scale

| Tier | Label | Physics Signature |
|------|-------|------------------|
| 1 | Mundane | Π ≈ 1.0, Γ ≈ 1.0, Class A/B dominated |
| 2 | Murky | Π slightly elevated, mixed sourcing |
| 3 | Mysterious | Π deviation emerging, Class C present |
| 4 | Manufactured | Π significantly deviated, Class D amplification, Γ anomaly |
| 5 | Manic | Π extreme, saddle-point triggered, Γ injection signal |
| 6 | Mythological | No traceable Class A/B sourcing, pure propagation signal, Quadrant I |

---

## Live Deployment

| Endpoint | URL |
|----------|-----|
| Frontend | https://ilo-analyzer.vercel.app |
| API Base | https://ilo-analyzer.onrender.com |
| API Docs | https://ilo-analyzer.onrender.com/docs |
| Source | https://github.com/JustMichael-80/ILO-Analyzer |
| X / Twitter | https://x.com/ChronoDyneSys |
| LinkedIn | https://www.linkedin.com/company/chronodyne-systems-inc/ |

**Request schema:**
```json
{
  "claim": "narrative string to analyze",
  "fetch_cdx": true
}
```

---

## Repository Structure

```
├── backend/
│   ├── engine.py                  # FastAPI P4 Gate — 6-phase cascade, verdict synthesis
│   ├── pi_calculator.py           # STOC-derived Π + node_details with CDX temporal data
│   ├── gamma_calculator.py        # Geographic Entropy Γ + Π/Γ quadrant assignment
│   ├── bias_table.py              # 80+ domain Class A/B/C/D table with FOIA repositories
│   ├── cdx.py                     # Wayback Machine CDX API — τ_observed measurement
│   ├── claim_classifier.py        # Gemini claim classification + κ(C) multiplier (v4.5)
│   ├── baseline_adjuster.py       # κ correction + consensus baseline glue layer (v4.5)
│   ├── physical_baselines.py      # 6-substrate consensus λ reference stack (v4.5)
│   ├── signature_library.py       # 12-signature cosine similarity campaign matching
│   ├── weather_baseline.py        # NOAA/open-meteo λ_weather (superseded by physical_baselines)
│   ├── cache.py                   # SQLite TTL cache (CDX: 7d, bias: 30d, weather: 6h, Tavily: 1d)
│   ├── report_generator.py        # Two-stage analyst report — deterministic + Gemini pass
│   ├── mcp_server.py              # MCP interface — hosted and local mode
│   ├── mcp_config_example.json    # Claude Desktop configuration examples
│   └── requirements.txt
└── frontend/
    └── src/
        └── App.jsx                # React/Vite/Tailwind + Three.js — Summary, Physics,
                                   # Report tabs + XCOM GEOINT globe sidebar
```

---

## Limitations & Scope

- **Search-dependent horizon** — Analysis reflects what is publicly indexed at the moment of query. Paywalled or suppressed content produces incomplete pictures.
- **CDX coverage** — Wayback Machine archives vary in completeness. τ_observed is a lower bound on actual narrative age.
- **α and β calibration** — STOC scaling exponents are empirically estimated (α = 1.2, β = 0.5). Full derivation from the benchmark suite is ongoing.
- **κ calibration** — Cultural persistence multipliers are theoretically grounded but await empirical validation from the 30-claim benchmark suite.
- **Quasar baseline** — 3C 273 variability timescale is from literature consensus. Live NASA/IPAC NED API integration is planned for v5.x.
- **Adversarial vulnerability** — Sophisticated actors could craft narrative footprints designed to mimic natural persistence and diffusion patterns.
- **Operational scope** — Designed for exploratory triage and hypothesis generation. Not for legal, journalistic, or high-stakes decisions without human oversight.

---

## Roadmap

| Version | Feature |
|---------|---------|
| ✅ v4.3 | ILO Signature Library — cosine similarity campaign matching |
| ✅ v4.4 | GEOINT Globe — Three.js XCOM-aesthetic source distribution map |
| ✅ v4.5 | Cultural persistence correction (κ), multi-substrate physical baseline, claim classifier, 12-signature library |
| v4.6 | Multi-timescale longitudinal tracking — Π/Γ evolution over time |
| v4.7 | Early-stage detection / watchdog mode |
| v4.8 | CLEO network instance integration |
| v5.x | Cross-substrate Λ index — decoupling between content anomaly and physical reality |
| v6.x | Full cross-substrate stack (Π_net, Π_econ, Π_phys, Π_geo) |

---

## Validation Benchmark

A 30-claim validation dataset is in active development:
- **15 known ILOs** — documented disinformation campaigns
- **15 known clean signals** — verified organic events

Four confirmed results to date: JFK/Dimona (Q-I), Podesta/Bennington (Q-III), GPT-4.0 is AGI (Q-II), TT Brown USAF suppression (Q-II, κ-corrected).

Target: empirical calibration of α = 1.2, β = 0.5, τ_diffusion = 14d, and κ per class. Community contributions welcome — see Discussions.

---

## Academic & Corporate Context

This architecture is an implementation milestone for ChronoDyne Systems, Inc. The Persistence Ratio Π and Geographic Entropy Γ represent the first empirical operationalization of the Principle of Persistent Structurization applied to information systems.

The v4.5 multi-substrate physical baseline — calibrated against atmospheric decay, geomagnetic flux, solar activity, lunar cycles, seismic noise, and quasar variability — provides a reference that cannot be gamed, faked, or correlated with any human information process. This is the foundation of the v5.x cross-substrate Λ index and the decoupling hypothesis: manufactured events produce content-layer anomalies decoupled from physical substrate reality.

**CLC2026:** A demonstration of this engine as a first empirical probe of Constructal dynamics applied to information propagation will be presented at the **16th Annual Constructal Law Conference, Paris, France, October 2026.**

---

## Citation

Stewart, M. *The Principle of Persistent Structurization.* CLC2026 Extended Abstract, Figshare, 2026. https://doi.org/10.6084/m9.figshare.32307087

---

*ChronoDyne Systems, Inc. · [X](https://x.com/ChronoDyneSys) · [LinkedIn](https://www.linkedin.com/company/chronodyne-systems-inc/) · Π = τ_obs / τ_pred(S) · Γ = H_geo / H_exp(t) · v4.5.0*
