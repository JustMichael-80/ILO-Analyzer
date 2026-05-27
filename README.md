# ChronoDyne Systems, Inc. // ILO Analyzer v4.3

An automated, cloud-isolated information triage engine built to identify and map Engineered Information Laundering Operations (ILOs). This architecture bypasses surface-level text classification by measuring the **thermodynamic footprint of data propagation** directly — computing whether a narrative is persisting naturally or being artificially sustained against entropic decay, across both temporal and geographic dimensions simultaneously.

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

### Second Metric: Geographic Entropy (Γ)

**Γ = H_geographic / H_expected(t)**

Where H_expected(t) models organic geographic diffusion:

**H_expected(t) = H_max · (1 - e^(-t / τ_diffusion))**

- **H_geographic** = Shannon entropy of source geographic scope distribution
- **H_expected(t)** = expected entropy for a naturally diffusing story at time t
- **τ_diffusion = 14 days** (characteristic local→international timescale)

Γ ≈ 1.0 indicates organic diffusion. Γ >> 1.0 indicates coordinated geographic injection — narrative appearing simultaneously at global scope with no local precursor. Γ << 1.0 indicates suppression — narrative geographically contained below natural diffusion prediction.

### The Π/Γ Diagnostic Coordinate Space

Π and Γ are orthogonal measurements — temporal persistence anomaly and spatial diffusion anomaly — derived independently from the same theoretical framework. Together they define a two-dimensional diagnostic space:

| | Γ high | Γ low |
|---|---|---|
| **Π high** | **Quadrant I — Confirmed ILO** (injected AND maintained) | **Quadrant II — Astroturfed Local** (manufactured, geographically contained) |
| **Π low** | **Quadrant III — Viral Suppression** (spreading fast, dying artificially) | **Quadrant IV — Suppressed Real Event** (neither persisting nor diffusing) |

Center (both near 1.0) = Organic.

This is not a heuristic. Both metrics are derived from PPS and STOC as published in the formal framework below.

---

## Architecture: What Actually Runs

### Source Classification (Class A/B/C/D)

Every source URL returned by the search cascade is classified against a 60+ domain bias table with trust weights derived from:

- **AllSides**, **Ad Fontes Media**, and **Media Bias/Fact Check** triangulated lean scores
- Political capture penalty (applied when |lean| > 0.6 AND reliability < 0.5)
- Hard lean penalty (applied when |lean| > 0.8 regardless of reliability)
- Cross-rater volatility decay (applied when σ_political > 0.3)
- **Geographic scope and country tags** (feeds Γ calculation)

| Class | Type | Trust Weight | Contribution |
|-------|------|-------------|--------------|
| A | Primary sources (academic, gov, court records) | ~0.85–1.00 | Positive |
| B | Credentialed intermediaries (wire services, established news) | ~0.45–0.65 | Positive |
| C | Volatile/captured outlets, low-reliability aggregators | ~0.00–0.25 | Reduced |
| D | Propagation nodes (social media, forums) | ~0.01–0.08 | **Inverted — presence raises suspicion** |

Class D nodes (Facebook, Reddit, Twitter/X, TikTok, 4chan, etc.) do not contribute credibility — their presence in a narrative's citation graph is treated as an ILO distribution signature. Class D nodes are excluded from geographic entropy calculation.

### Saddle-Point Tracker: NOAA Weather Baseline

The saddle-point tracker compares the observed narrative decay constant λ_observed against λ_weather — derived from open-meteo atmospheric forecast accuracy degradation over a 7-day forecast window.

Weather systems are open non-equilibrium thermodynamic systems — the original domain of Constructal Law. Using atmospheric decay as the natural persistence reference is not decorative: it calibrates the PPS reference curve against the physical system that motivated the theory.

**Δ = |λ_observed - λ_weather| / λ_weather**

- Δ < 0.30: **Organic** — natural decay within atmospheric tolerance
- Δ > 0.30, λ_obs > λ_weather: **ILO Fade** — collapsing faster than nature predicts
- Δ > 0.30, λ_obs < λ_weather: **Artificial Maintenance** — being held above natural decay threshold

### CDX Temporal Measurement

Source URLs are queried against the Wayback Machine CDX API to extract τ_observed — the actual time delta between first and last confirmed archival citation, measured in days. CDX calls run in parallel with an 8-second hard timeout, degrading gracefully on slow responses. Results are cached for 7 days.

### Five-Phase Search Cascade

1. Primary source ingestion
2. Local journalism scan
3. Deep archive cascade (advanced depth)
4. Debunking cross-reference
5. Institutional corroboration

### P4 Gate (Gemini Verdict Synthesis)

The full physics block — Π, Γ, quadrant, τ_observed, τ_predicted, S, E, node classification, saddle-point deviation, geographic scope distribution — is computed deterministically and injected into the P4 Gate as ground truth. Gemini synthesizes a structured verdict from the physics block and qualitative source content. The LLM does not compute Π or Γ and cannot override either.

### Analyst Report (Gemini Analyst Pass)

A second, separate Gemini pass at higher temperature reasons over the compiled physics report as an investigative analyst — generating pattern hypotheses with confidence scores, actor profiling, red flags, investigative next steps, and follow-up claims to test. The physics block constrains the hallucination space; the analyst reasons over verified measurements, not raw search results. Output is a downloadable markdown intelligence document.

### MCP Interface (AI Agent Integration)

An MCP server exposes the analyzer as a native tool for any MCP-compatible AI agent. Dual-mode:
- **Hosted mode** — routes to the live API, zero setup required
- **Local mode** — runs the engine with the user's own API keys, claims never leave their machine

---

## Empirical Demonstration

Three live tests conducted May 24–25, 2026:

| Claim | Π | Γ | Quadrant | ILO % |
|-------|---|---|----------|-------|
| JFK/Israeli Intelligence/Dimona | 41.91 | — | I — Confirmed ILO | 95% |
| Podesta is Chester Bennington's father | 0.0 | 5.0 | III — Viral Suppression | 95% |
| GPT-4.0 is AGI | 25.10 | 0.46 | II — Astroturfed Local | 85% |

Three different claims. Three different quadrants. Three different actor signatures. All from physics.

**First test detail — JFK/Dimona claim:**

| Metric | Value |
|--------|-------|
| Π (Persistence Ratio) | **41.9065** |
| τ_observed | 613.93 days |
| τ_predicted(S) | 14.65 days |
| λ_observed | 0.0001 /day |
| λ_weather (NOAA) | 0.1200 /day |
| Saddle-point Δ | 0.9993 |
| Saddle classification | **Artificial Maintenance** |
| Class A nodes | 2 |
| Class D nodes | 4 |
| Verdict | **Confirmed ILO Pattern** |
| ILO Probability | 95% |

The narrative has persisted 42× longer than STOC predicts. The observed decay constant deviates from the NOAA atmospheric baseline by Δ = 0.9993 — indicating active artificial maintenance above the natural decay threshold.

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
| Discussions | https://github.com/JustMichael-80/ILO-Analyzer/discussions |

**Request schema:**
```json
{
  "claim": "narrative string to analyze",
  "fetch_cdx": true
}
```

Setting `fetch_cdx: false` skips Wayback Machine temporal measurement for faster results (Π will reflect citation graph structure only, without τ_observed; Γ still computes from source scope distribution).

**Note on API keys:** The hosted endpoint runs on free tier infrastructure with shared keys. For full speed, privacy, and no rate limits, run locally with your own Gemini and Tavily keys — both have generous free tiers. See setup instructions in the MCP section of the docs.

---

## Roadmap

The following modules are in active development. Each extends the existing architecture without replacing it — the analyst report is the delivery surface for all downstream additions.

**v4.3 — ILO Signature Library**
Cosine similarity matching against a reference library of known ILO campaign vectors — Russian IRA, Spamouflage, domestic astroturfing archetypes, and others sourced from Twitter/Meta/Stanford Internet Observatory public datasets. Output: "most similar known campaign" with confidence score, added as a report section.

**v4.4 — Geolocation Map**
World map visualization of source node geographic distribution, color-coded by Class A/B/C/D, with edge weight rendering. Makes Γ tangible for non-technical audiences and visually surfaces coordinated injection patterns. Toggle overlay for known state-actor geographic footprints.

**v4.5 — State-Actor Correlation**
Similarity scoring against known state-linked IO geographic and behavioral fingerprints. When a narrative's country distribution and Π/Γ signature matches a known actor's historical campaigns, flag it with confidence rating. Legal review before public release.

**v4.6 — Multi-Timescale Tracking**
Longitudinal monitoring mode — run the analyzer repeatedly on a claim over time and track how Π and Γ evolve. Natural stories show rise → peak → logarithmic fade. Manufactured ones show plateaus, secondary injections, or artificial floors. Turns the snapshot tool into a continuous monitoring instrument.

**v4.7 — Early-Stage Detection**
Watchdog mode for emerging local claims. Monitor Π deviation before national media picks up a story. A genuine threshold cross would show predicted vs observed persistence aligning as coverage broadens organically. Flag anomalous early-stage injection before it consolidates.

**v4.8 — CLEO Integration**
Network instance support for CLEO (Constructal Law Evolutionary Optimizer) continual learning architecture. Cross-claim campaign memory, adaptive threshold calibration from empirical results, predictive routing to high-signal cascade phases. Turns per-claim detection into campaign-level pattern recognition across continuous sessions.

---

## Limitations & Scope

- **Search-dependent horizon:** Analysis reflects what is publicly indexed at the moment of query. Paywalled, suppressed, or hyper-recent content produces incomplete pictures.
- **CDX coverage:** Wayback Machine archives vary in completeness. τ_observed is a lower bound on actual narrative age.
- **α and β calibration:** STOC scaling exponents are empirically estimated (α = 1.2, β = 0.5). Full derivation from the benchmark suite is ongoing.
- **τ_diffusion calibration:** Geographic diffusion timescale set at 14 days. Empirical validation against known organic stories is the next benchmark milestone.
- **Adversarial vulnerability:** Sophisticated actors could craft narrative footprints designed to mimic natural persistence and diffusion patterns.
- **Operational scope:** Best suited for exploratory triage and hypothesis generation. Not designed for legal, journalistic, or high-stakes decisions without human oversight.

---

## Validation Benchmark

A 30-claim validation dataset is in active development:
- **15 known ILOs** — documented disinformation campaigns across multiple categories
- **15 known clean signals** — verified organic events with documented factual records

Target metrics: Π clustering near 1.0 for clean signals, Quadrant I/II placement for confirmed ILOs. Results will be used to calibrate α, β, and τ_diffusion empirically. Community contributions welcome — see Discussions.

---

## Repository Structure

```
├── backend/
│   ├── engine.py               # FastAPI P4 Gate — search cascade, verdict synthesis
│   ├── pi_calculator.py        # STOC-derived Π computation from citation graph
│   ├── gamma_calculator.py     # Geographic Entropy Γ + Π/Γ quadrant assignment
│   ├── bias_table.py           # Class A/B/C/D classification, trust weights, geo tags
│   ├── cdx.py                  # Wayback Machine CDX API — τ_observed measurement
│   ├── weather_baseline.py     # NOAA/open-meteo λ_weather reference curve
│   ├── cache.py                # SQLite TTL cache (CDX: 7d, bias: 30d, weather: 1d)
│   ├── report_generator.py     # Two-stage analyst report — deterministic + Gemini pass
│   ├── mcp_server.py           # MCP interface — hosted and local mode
│   ├── mcp_config_example.json # Claude Desktop configuration examples
│   └── requirements.txt
└── frontend/
    └── src/
        └── App.jsx             # React/Vite/Tailwind dashboard — Verdict Matrix,
                                # Physics Diagnostics, Analyst Report tabs
```

---

## Academic & Corporate Context

This architecture is an implementation milestone for ChronoDyne Systems, Inc. The Persistence Ratio Π and Geographic Entropy Γ represent the first empirical operationalization of the Principle of Persistent Structurization applied to information systems — two independently derived metrics from the same theoretical framework measuring orthogonal dimensions of the same phenomenon.

**Upcoming:** A demonstration of this engine as a first empirical probe of Constructal dynamics applied to information propagation will be presented at the **16th Annual Constructal Law Conference (CLC2026), Paris, France, October 2026.**

---

## Citation

Stewart, M. *The Principle of Persistent Structurization.* CLC2026 Extended Abstract, Figshare, 2026. https://doi.org/10.6084/m9.figshare.32307087

---

*ChronoDyne Systems, Inc. · Principle of Persistent Structurization · Π = τ_obs / τ_pred(S) · Γ = H_geo / H_exp(t)*
