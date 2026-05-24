# ChronoDyne Systems, Inc. // ILO Analyzer v4

An automated, cloud-isolated information triage engine built to identify and map Engineered Information Laundering Operations (ILOs). This architecture bypasses surface-level text classification by measuring the **thermodynamic footprint of data propagation** directly — computing whether a narrative is persisting naturally or being artificially sustained against entropic decay.

---

## Theoretical Framework: The Principle of Persistent Structurization (PPS)

Standard fact-checking utilities fail because they treat disinformation as a static content problem. The ILO Analyzer treats information as an open, non-equilibrium thermodynamic system governed by the Constructal Law (Bejan, 2011).

When a real-world event occurs, the resulting information naturally optimizes its access paths over time, maintaining structural integrity across varying geographical and institutional nodes. Conversely, an engineered campaign exhibits a distinct artificial signature: a rapid injection of organized configuration that fails to structurally adapt, or a narrative held artificially above its natural decay threshold by coordinated propagation.

The Persistence Ratio Π is the primary diagnostic instrument:

**Π = τ_observed / τ_predicted(S)**

Where τ_predicted(S) is derived from the Scale-Timescale Optimization Corollary (STOC):

**τ*(S) ~ S^α · E^(-β)**

- **S** = Shannon entropy of the citation graph edge weight distribution
- **E** = System complexity (trust-weighted node count)
- **α = 1.2** (superlinear scaling exponent; α > 1 per STOC)
- **β = 0.5** (energy flux exponent)

Π ≈ 1.0 indicates organic natural persistence. Π >> 1.0 indicates artificial maintenance. Π << 1.0 indicates ILO Fade — engineered collapse faster than natural decay predicts.

This is not a heuristic. The formula is derived from PPS and STOC as published in the formal framework below.

---

## Architecture: What Actually Runs

### Source Classification (Class A/B/C/D)

Every source URL returned by the search cascade is classified against a 60+ domain bias table with trust weights derived from:

- **AllSides**, **Ad Fontes Media**, and **Media Bias/Fact Check** triangulated lean scores
- Political capture penalty (applied when |lean| > 0.6 AND reliability < 0.5)
- Hard lean penalty (applied when |lean| > 0.8 regardless of reliability)
- Cross-rater volatility decay (applied when σ_political > 0.3)

| Class | Type | Trust Weight | Contribution |
|-------|------|-------------|--------------|
| A | Primary sources (academic, gov, court records) | ~0.85–1.00 | Positive |
| B | Credentialed intermediaries (wire services, established news) | ~0.45–0.65 | Positive |
| C | Volatile/captured outlets, low-reliability aggregators | ~0.00–0.25 | Reduced |
| D | Propagation nodes (social media, forums) | ~0.01–0.08 | **Inverted — presence raises suspicion** |

Class D nodes (Facebook, Reddit, Twitter/X, TikTok, 4chan, etc.) do not contribute credibility — their presence in a narrative's citation graph is treated as an ILO distribution signature.

### Saddle-Point Tracker: NOAA Weather Baseline

The saddle-point tracker compares the observed narrative decay constant λ_observed against λ_weather — derived from open-meteo atmospheric forecast accuracy degradation over a 7-day forecast window.

Weather systems are open non-equilibrium thermodynamic systems — the original domain of Constructal Law. Using atmospheric decay as the natural persistence reference is not decorative: it calibrates the PPS reference curve against the physical system that motivated the theory.

**Δ = |λ_observed - λ_weather| / λ_weather**

- Δ < 0.30: **Organic** — natural decay within atmospheric tolerance
- Δ > 0.30, λ_obs > λ_weather: **ILO Fade** — collapsing faster than nature predicts
- Δ > 0.30, λ_obs < λ_weather: **Artificial Maintenance** — being held above natural decay threshold

### CDX Temporal Measurement

Source URLs are queried against the Wayback Machine CDX API to extract τ_observed — the actual time delta between first and last confirmed archival citation, measured in days. This converts Π from a theoretical construct into a measured physical quantity. CDX results are cached for 7 days to minimize redundant API calls.

### Five-Phase Search Cascade

1. Primary source ingestion
2. Local journalism scan
3. Deep archive cascade (advanced depth)
4. Debunking cross-reference
5. Institutional corroboration

### P4 Gate (Gemini Verdict Synthesis)

The physics block — Π, τ_observed, τ_predicted, S, E, node classification, saddle-point deviation — is computed deterministically and injected into the P4 Gate as ground truth. Gemini synthesizes a structured verdict from the physics block and qualitative source content. The LLM does not compute Π and cannot override it.

---

## Empirical Demonstration

First live test conducted May 24, 2026:

**Claim:** *"Israeli Intelligence was behind the JFK assassination in retaliation for not approving Dimona."*

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

**Interpretation:** The narrative has persisted 42× longer than STOC predicts for a natural information structure of its complexity. The observed decay constant (λ = 0.0001/day) deviates from the NOAA atmospheric baseline (λ = 0.12/day) by Δ = 0.9993 — indicating the narrative is being actively held above its natural decay threshold. Class A sources provide historical context but do not support the assassination claim. Class D sources actively propagate it.

---

## 6M Wildness Scale

| Tier | Label | Physics Signature |
|------|-------|------------------|
| 1 | Mundane | Π ≈ 1.0, Class A/B dominated |
| 2 | Murky | Π slightly elevated, mixed sourcing |
| 3 | Mysterious | Π deviation emerging, Class C present |
| 4 | Manufactured | Π significantly deviated, Class D amplification |
| 5 | Manic | Π collapsed or extreme, saddle-point triggered |
| 6 | Mythological | No traceable Class A/B sourcing, pure propagation signal |

---

## Live Deployment

| Endpoint | URL |
|----------|-----|
| Frontend | https://ilo-analyzer.vercel.app |
| API Base | https://ilo-analyzer.onrender.com |
| API Docs | https://ilo-analyzer.onrender.com/docs |

**Request schema:**
```json
{
  "claim": "narrative string to analyze",
  "fetch_cdx": true
}
```

Setting `fetch_cdx: false` skips Wayback Machine temporal measurement for faster results (Π will reflect citation graph structure only, without τ_observed).

---

## Limitations & Scope

- **Search-dependent horizon:** Analysis reflects what is publicly indexed at the moment of query. Paywalled, suppressed, or hyper-recent content produces incomplete pictures.
- **CDX coverage:** Wayback Machine archives vary in completeness. τ_observed is a lower bound on actual narrative age.
- **α and β calibration:** STOC scaling exponents are empirically estimated (α = 1.2, β = 0.5). Full derivation from the benchmark suite is ongoing.
- **Adversarial vulnerability:** Sophisticated actors could craft narrative footprints designed to mimic natural persistence patterns.
- **Operational scope:** Best suited for exploratory triage and hypothesis generation. Not designed for legal, journalistic, or high-stakes decisions without human oversight.

---

## Repository Structure

```
├── backend/
│   ├── engine.py            # FastAPI P4 Gate — search cascade, verdict synthesis
│   ├── pi_calculator.py     # STOC-derived Π computation from citation graph
│   ├── bias_table.py        # Class A/B/C/D source classification & trust weights
│   ├── cdx.py               # Wayback Machine CDX API — τ_observed measurement
│   ├── weather_baseline.py  # NOAA/open-meteo λ_weather reference curve
│   ├── cache.py             # SQLite TTL cache (CDX: 7d, bias: 30d, weather: 1d)
│   └── requirements.txt
└── frontend/
    └── src/
        └── App.jsx          # React/Vite/Tailwind dashboard with Physics Diagnostics tab
```

---

## Academic & Corporate Context

This architecture is an implementation milestone for ChronoDyne Systems, Inc. The Persistence Ratio Π and STOC-derived τ_predicted represent the first empirical operationalization of the Principle of Persistent Structurization applied to information systems.

**Upcoming:** A demonstration of this engine as a first empirical probe of Constructal dynamics applied to information propagation will be presented at the **16th Annual Constructal Law Conference (CLC2026), Paris, France, October 2026.**

---

## Citation

Stewart, M. *The Principle of Persistent Structurization.* Figshare, 2026. https://doi.org/10.6084/m9.figshare.32307087

---

*ChronoDyne Systems, Inc. · Principle of Persistent Structurization · Π = τ_obs / τ_pred(S)*
