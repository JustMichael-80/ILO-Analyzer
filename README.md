# ChronoDyne Systems, Inc. // ILO-Analyzer-v3 (WARNING - EXPERIMENTAL PROTOTYPE)

An automated, cloud-isolated information triage engine built to identify and map Engineered Information Laundering Operations (ILOs). This architecture bypasses standard surface-level text classification by looking directly at the thermodynamic footprint of data propagation.

## Theoretical Framework: The Principle of Persistent Structurization (PPS)

Standard fact-checking utilities fail because they treat disinformation as a static content problem. The ILO Analyzer treats information as an open, non-equilibrium thermodynamic system governed by the **Constructal Law**. 

When a real-world event occurs, the resulting information naturally optimizes its access paths over time, maintaining structural integrity across varying geographical and institutional nodes. Conversely, an engineered campaign exhibits a distinct, artificial signature: a rapid injection of organized configuration that fails to structurally adapt, resulting in an anomalous, localized collapse of the system's persistence ratio ($\Pi$).

### Core Diagnostics Matrix
The processing pipeline routes unverified narrative strings through a five-phase search cascade, evaluating the payload against a strict, deterministic schema:
* **The 6M Wildness Scale:** Classifies narrative velocity and intent across fixed diagnostic tiers (Mundane, Murky, Mysterious, Manufactured, Manic, Mythological).
* **Saddle-Point Tracking:** Monitors the transmission derivative to spot sudden programmatic drop-offs (*ILO Fade*) or artificial distribution uniformity across alternative nodes.

---

## 🚀 Production API & Testing

The backend engine is deployed and running live on Render. 

* **Live API Base URL:** `https://ilo-analyzer.onrender.com`
* **Interactive Testing Dashboard:** [https://ilo-analyzer.onrender.com/docs](https://ilo-analyzer.onrender.com/docs)

### How to Test via the Dashboard:
1. Navigate to the `/docs` link above to open the Swagger UI.
2. Expand the green **POST `/analyze`** endpoint panel.
3. Click **"Try it out"**.
4. Input your JSON payload structure into the request body and click **Execute**.

## ⚠️ Limitations & Current Status

**This is an experimental research prototype** — not a production-grade or authoritative fact-checking tool. It was shipped quickly to test core ideas in public and gather user feedback.

### Key Limitations

* **Heavy Reliance on External Frameworks:** The system depends entirely on Google's Gemini and Tavily for live analysis and data gathering. Outputs can inherit biases, hallucinations, rate limits, or structural inconsistencies from these upstream services. Results may vary over time as underlying models and search indices evolve.
* **Heuristic, Not Fully Physics-Based Modeling:** The **Persistence Ratio ($\Pi$)** and saddle-point tracking are practical composite scores derived from real-time search results, source diversity, and credibility weights. They are *inspired by* the Constructal Law and the **Principle of Persistent Structurization (PPS)**, but do not currently run live dynamical systems simulations or non-equilibrium thermodynamic models.
* **Early-Stage Validation:** No large-scale benchmarks have been run against known disinformation datasets, nor has it been formally compared to established OSINT tools yet. False positives and false negatives are expected, especially on edge cases, fast-moving events, or highly coordinated but organic narrative flows.
* **Search-Dependent Horizon:** Processing performance relies heavily on what is publicly indexed at the exact second of analysis. Paywalled content, hyper-recent events, or heavily suppressed information may produce an incomplete picture.
* **Adversarial Vulnerability:** Sophisticated adversarial actors could potentially craft narrative footprints designed to mimic natural structural persistence patterns. This tool should be leveraged as one signal among many, never as a standalone verdict.
* **Operational Scope:** Best suited for exploratory triage and hypothesis generation. It is not designed for legal, journalistic, or high-stakes decision-making without significant human oversight.

### Development Philosophy

The goal of ChronoDyne Systems is iterative improvement through active, real-world testing. Flow metrics like $\Pi$ and the **6M Wildness Scale** will be continuously refined based on user feedback, empirical data, and validation experiments. 

Contributions, edge-case test profiles (both successes and failures), and technical suggestions for further grounding the physical framework are highly welcome.

> 🧠 **Dive into the Physics:** See the formal [theoretical paper](https://doi.org/10.6084/m9.figshare.32307087) for the deeper mathematical and thermodynamic architecture behind PPS.

---

## Academic & Corporate Context

This architecture represents an implementation milestone for **ChronoDyne Systems, Inc.** structural modeling. 

### Citation
For the underlying mathematical models, thermodynamic derivations, and formal proofs behind the Fractal Information Iteration Hypothesis, please reference the primary repository documentation and peer-reviewed framework:

> **Stewart, M.** *The Fractal Information Iteration Hypothesis*. 
> [https://doi.org/10.6084/m9.figshare.32307087]

### Upcoming Presentations
A live demonstration of this engine's algorithmic translation of Constructal dynamics—specifically focusing on dynamic expert expansion models—will be presented at the **16th Annual Constructal Law Conference** in Paris, France.

---

## Repository Structure

```text
├── backend/
│   ├── engine.py            # P4 Gate processing module & JSON schema validation
│   └── requirements.txt     # Python dependencies (google-genai, tavily-python)
└── frontend/
    └── ilo-analyzer-v3.jsx  # React-based Tailwind utility dashboard & live trace telemetry
