import { useState, useRef, useEffect } from "react";

const API_BASE = "https://ilo-analyzer.onrender.com";

const PHASES = [
  { label: "Phase 1 // Primary source ingestion", max: 3 },
  { label: "Phase 2 // Local journalism scan", max: 3 },
  { label: "Phase 3 // Deep archive cascade", max: 5 },
  { label: "Phase 4 // Debunking cross-reference", max: 3 },
  { label: "Phase 5 // Institutional corroboration", max: 3 },
];

const CLASS_COLORS = {
  A: { text: "text-emerald-400", bg: "bg-emerald-950/40", border: "border-emerald-500/30", label: "PRIMARY" },
  B: { text: "text-sky-400",     bg: "bg-sky-950/40",     border: "border-sky-500/30",     label: "CREDENTIALED" },
  C: { text: "text-amber-400",   bg: "bg-amber-950/40",   border: "border-amber-500/30",   label: "VOLATILE" },
  D: { text: "text-rose-500",    bg: "bg-rose-950/40",    border: "border-rose-500/30",    label: "PROPAGATION ⚠" },
};

const VERDICT_STYLE = (verdict = "") => {
  const v = verdict.toLowerCase();
  if (v.includes("clean"))       return { border: "border-emerald-500/40", bg: "bg-emerald-950/20", text: "text-emerald-400", glow: "#34d39966" };
  if (v.includes("suppression")) return { border: "border-amber-500/40",   bg: "bg-amber-950/20",   text: "text-amber-400",   glow: "#fbbf2466" };
  if (v.includes("anomalous"))   return { border: "border-cyan-500/40",    bg: "bg-cyan-950/20",    text: "text-cyan-400",    glow: "#22d3ee66" };
  if (v.includes("insufficient"))return { border: "border-slate-600/40",   bg: "bg-slate-900/20",   text: "text-slate-400",   glow: "#94a3b866" };
  return                                 { border: "border-rose-500/40",    bg: "bg-rose-950/20",    text: "text-rose-400",    glow: "#f43f5e66" };
};

const WILDNESS_COLOR = (tier) => ({
  1: "text-emerald-400", 2: "text-sky-400", 3: "text-yellow-400",
  4: "text-orange-400",  5: "text-rose-400", 6: "text-purple-400",
}[tier] || "text-teal-400");

const SADDLE_STYLE = (classification) => ({
  organic:    { text: "text-emerald-400", label: "ORGANIC DECAY" },
  ilo_fade:   { text: "text-rose-400",    label: "ILO FADE ⚠" },
  maintained: { text: "text-amber-400",   label: "ARTIFICIAL MAINTENANCE ⚠" },
  no_data:    { text: "text-slate-500",   label: "NO DATA" },
}[classification] || { text: "text-slate-500", label: "UNKNOWN" });

function PiGauge({ pi }) {
  const clamped = Math.min(Math.max(pi, 0), 3);
  // Organic zone: 0.70–1.40
  const color =
    pi >= 0.70 && pi <= 1.40 ? "#34d399" :
    pi < 0.35                 ? "#f43f5e" :
    pi > 2.50                 ? "#fbbf24" :
    pi < 0.70                 ? "#fb923c" : "#22d3ee";

  const pct = Math.min((clamped / 3) * 100, 100);

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-end">
        <span className="text-[10px] uppercase tracking-widest text-slate-500">
          Persistence Ratio Π = τ<sub>obs</sub> / τ<sub>pred</sub>(S)
        </span>
        <span className="font-black text-xl tabular-nums" style={{ color }}>
          {pi.toFixed(4)}
        </span>
      </div>
      <div className="relative h-2 bg-slate-800 rounded overflow-hidden">
        {/* Organic zone marker */}
        <div className="absolute h-full bg-emerald-900/40 rounded"
             style={{ left: `${(0.70/3)*100}%`, width: `${((1.40-0.70)/3)*100}%` }} />
        {/* Π bar */}
        <div className="absolute h-full rounded transition-all duration-700"
             style={{ width: `${pct}%`, background: color, boxShadow: `0 0 10px ${color}88` }} />
      </div>
      <div className="flex justify-between text-[9px] text-slate-700 uppercase tracking-wider">
        <span>ILO Fade</span>
        <span className="text-emerald-800">Organic Zone</span>
        <span>Maintained</span>
      </div>
    </div>
  );
}

function PhysicsPanel({ diag }) {
  if (!diag) return null;
  const { pi_final, tau_observed_days, tau_predicted_days, S, E,
          node_count, class_a_count, class_d_count, inverted_signal,
          pi_interpretation, saddle_point } = diag;
  const saddle = SADDLE_STYLE(saddle_point?.classification);

  return (
    <div className="border border-slate-700/50 rounded bg-slate-950 p-4 space-y-4">
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        <div className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
        <span className="text-[10px] uppercase tracking-widest text-teal-400 font-bold">
          Physics Diagnostic Block
        </span>
        <span className="text-[9px] text-slate-600 ml-auto">STOC · PPS · NOAA Baseline</span>
      </div>

      <PiGauge pi={pi_final} />

      <p className="text-[10px] text-slate-400 leading-relaxed border-l-2 border-teal-500/30 pl-3">
        {pi_interpretation}
      </p>

      <div className="grid grid-cols-2 gap-2 text-[10px]">
        {[
          ["τ observed",    `${tau_observed_days}d`],
          ["τ predicted",   `${tau_predicted_days}d`],
          ["S (entropy)",   S.toFixed(4)],
          ["E (complexity)",E.toFixed(4)],
          ["Nodes",         node_count],
          ["Class A",       class_a_count],
          ["Class D",       class_d_count],
          ["Inv. signal",   inverted_signal.toFixed(4)],
        ].map(([label, val]) => (
          <div key={label} className="flex justify-between bg-slate-900 rounded px-2 py-1.5">
            <span className="text-slate-600 uppercase tracking-wider">{label}</span>
            <span className="text-slate-300 font-bold tabular-nums">{val}</span>
          </div>
        ))}
      </div>

      {saddle_point && (
        <div className="border border-slate-800 rounded p-3 space-y-1">
          <div className="flex justify-between items-center">
            <span className="text-[9px] uppercase tracking-widest text-slate-600">
              Saddle-Point // NOAA Weather Baseline
            </span>
            <span className={`text-[10px] font-bold ${saddle.text}`}>{saddle.label}</span>
          </div>
          {saddle_point.delta !== null && saddle_point.delta !== undefined && (
            <div className="flex gap-4 text-[9px] text-slate-600">
              <span>λ<sub>obs</sub> = {saddle_point.lambda_observed?.toFixed(4) ?? "—"}</span>
              <span>λ<sub>wx</sub> = {saddle_point.lambda_weather?.toFixed(4)}</span>
              <span>Δ = {saddle_point.delta?.toFixed(4)}</span>
              <span className="ml-auto text-slate-700">{saddle_point.baseline_source}</span>
            </div>
          )}
        </div>
      )}

      {inverted_signal > 2.0 && (
        <div className="border border-rose-500/30 bg-rose-950/10 rounded px-3 py-2">
          <span className="text-[10px] text-rose-400 font-bold">
            ⚠ High Class D amplification — ILO distribution signature detected
          </span>
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value, detail, accent = "text-teal-400" }) {
  return (
    <div className="bg-slate-950 p-3 rounded border border-slate-800/60 space-y-1">
      <span className="block text-[10px] uppercase tracking-widest text-slate-500">{label}</span>
      <span className={`text-sm font-bold ${accent}`}>{value}</span>
      {detail && (
        <p className="text-xs text-slate-400 leading-relaxed pt-1 border-t border-slate-900 mt-1">
          {detail}
        </p>
      )}
    </div>
  );
}

export default function ILOAnalyzerConsole() {
  const [claim, setClaim]           = useState("");
  const [loading, setLoading]       = useState(false);
  const [phaseIndex, setPhaseIndex] = useState(0);
  const [runningPi, setRunningPi]   = useState(null);
  const [verdict, setVerdict]       = useState(null);
  const [error, setError]           = useState(null);
  const [tab, setTab]               = useState("verdict"); // verdict | physics
  const phaseTimer                  = useRef(null);

  const simulatePhases = () => {
    let idx = 0;
    setPhaseIndex(0);
    setRunningPi(null);
    phaseTimer.current = setInterval(() => {
      idx++;
      if (idx < PHASES.length) {
        setPhaseIndex(idx);
        setRunningPi(parseFloat((Math.random() * 0.4 + 0.05).toFixed(3)));
      } else {
        clearInterval(phaseTimer.current);
      }
    }, 2000);
  };

  const executeAnalysis = async () => {
    if (!claim.trim() || loading) return;
    setLoading(true);
    setError(null);
    setVerdict(null);
    setTab("verdict");
    simulatePhases();

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ claim, fetch_cdx: true }),
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data = await res.json();
      clearInterval(phaseTimer.current);
      setRunningPi(data.pi_diagnostics?.pi_final ?? null);
      setVerdict(data);
    } catch (err) {
      clearInterval(phaseTimer.current);
      setError(`Pipeline collapsed: ${err.message}`);
    } finally {
      setLoading(false);
      setPhaseIndex(0);
    }
  };

  const vs = VERDICT_STYLE(verdict?.verdict || "");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-mono p-4 md:p-6 selection:bg-teal-500 selection:text-slate-950">

      {/* Header */}
      <header className="border-b border-slate-800 pb-4 mb-6">
        <div className="flex justify-between items-start flex-wrap gap-3">
          <div>
            <h1 className="text-lg md:text-xl font-bold tracking-wider text-teal-400">
              CHRONODYNE SYSTEMS // ILO ANALYZER
            </h1>
            <p className="text-[11px] text-slate-500 mt-1">
              Sieve Module v4.0.0 · PPS · STOC · NOAA Weather Baseline · Wayback CDX
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] px-2.5 py-1 rounded border border-teal-500/30 bg-teal-950/20 text-teal-400 tracking-wider">
              P4 GATE ACTIVE
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left: Input + cascade log */}
        <section className="lg:col-span-1 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded p-5 shadow-xl">
            <h2 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-4">
              Ingestion Interface
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-[10px] text-slate-500 uppercase tracking-wider mb-2">
                  Target Flux String
                </label>
                <textarea
                  value={claim}
                  onChange={(e) => setClaim(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && e.metaKey) executeAnalysis(); }}
                  placeholder="Enter unverified narrative..."
                  className="w-full h-32 bg-slate-950 border border-slate-800 rounded p-3 text-sm text-slate-200 focus:outline-none focus:border-teal-500/60 transition-colors resize-none placeholder-slate-700"
                  disabled={loading}
                />
              </div>
              <button
                onClick={executeAnalysis}
                disabled={loading || !claim.trim()}
                className="w-full bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-bold py-2.5 px-4 rounded text-[11px] uppercase tracking-widest transition-colors cursor-pointer"
              >
                {loading ? "Cascading..." : "Execute Triage Sieve"}
              </button>
              <p className="text-[9px] text-slate-700 text-right">⌘+Enter to execute</p>
            </div>
          </div>

          {/* Cascade log */}
          {loading && (
            <div className="bg-slate-900/50 border border-teal-500/20 rounded p-4 space-y-3">
              <div className="text-teal-400 font-bold uppercase tracking-widest text-[10px] flex items-center gap-2">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
                Live Cascade
              </div>
              <div className="space-y-2">
                {PHASES.map((p, i) => (
                  <div key={i} className={`flex items-start gap-2 text-[10px] transition-colors ${i <= phaseIndex ? "text-slate-300" : "text-slate-700"}`}>
                    <span className={`mt-0.5 w-1 h-1 rounded-full flex-shrink-0 ${i < phaseIndex ? "bg-teal-500" : i === phaseIndex ? "bg-teal-400 animate-pulse" : "bg-slate-700"}`} />
                    {p.label}
                  </div>
                ))}
              </div>
              {runningPi !== null && (
                <div className="border-t border-slate-800 pt-3">
                  <div className="flex justify-between text-[9px] text-slate-600 mb-1">
                    <span>Running Π estimate</span>
                    <span className="text-teal-500">{runningPi.toFixed(3)}</span>
                  </div>
                  <div className="h-1 bg-slate-800 rounded overflow-hidden">
                    <div className="h-full bg-teal-500/60 rounded animate-pulse"
                         style={{ width: `${Math.min(runningPi * 33, 100)}%` }} />
                  </div>
                </div>
              )}
              <p className="text-[9px] text-slate-700 mt-2">
                CDX queries in progress — τ_observed being measured...
              </p>
            </div>
          )}

          {error && (
            <div className="bg-red-950/20 border border-red-500/30 rounded p-4 text-[11px] text-red-400">
              <span className="font-bold">[-] PIPELINE COLLAPSE</span>
              <p className="mt-1 text-red-500/70">{error}</p>
            </div>
          )}
        </section>

        {/* Right: Results */}
        <section className="lg:col-span-2">
          {verdict ? (
            <div className="space-y-4">

              {/* Verdict header */}
              <div className={`border ${vs.border} ${vs.bg} p-5 rounded flex items-center justify-between gap-4 flex-wrap`}
                   style={{ boxShadow: `0 0 24px ${vs.glow}` }}>
                <div>
                  <span className={`text-[10px] uppercase font-bold tracking-widest opacity-60 ${vs.text}`}>
                    Diagnostic Decision
                  </span>
                  <h3 className={`text-xl font-black uppercase tracking-tight mt-0.5 ${vs.text}`}>
                    {verdict.verdict}
                  </h3>
                  <p className="text-xs text-slate-400 mt-2 max-w-md leading-relaxed">
                    {verdict.verdict_summary}
                  </p>
                </div>
                <div className="text-right flex-shrink-0">
                  <span className={`text-[10px] uppercase font-bold tracking-widest opacity-60 ${vs.text}`}>
                    ILO Probability
                  </span>
                  <p className={`text-4xl font-black mt-0.5 ${vs.text}`}>
                    {verdict.ilo_probability}
                    <span className="text-lg opacity-50">%</span>
                  </p>
                </div>
              </div>

              {/* WTF factor */}
              {verdict.wtf_factor && !verdict.wtf_factor.toLowerCase().includes("no significant") && (
                <div className="bg-slate-900/50 border border-rose-500/20 border-l-2 border-l-rose-500 rounded p-4">
                  <span className="block text-[10px] uppercase tracking-widest text-rose-500 mb-1.5">
                    ⚡ Core Anomaly
                  </span>
                  <p className="text-xs text-slate-300 leading-relaxed">{verdict.wtf_factor}</p>
                </div>
              )}

              {/* Tab switcher */}
              <div className="flex border-b border-slate-800">
                {["verdict", "physics"].map((t) => (
                  <button
                    key={t}
                    onClick={() => setTab(t)}
                    className={`px-4 py-2 text-[10px] uppercase tracking-widest transition-colors cursor-pointer ${
                      tab === t
                        ? "text-teal-400 border-b-2 border-teal-400 -mb-px"
                        : "text-slate-600 hover:text-slate-400"
                    }`}
                  >
                    {t === "verdict" ? "Verdict Matrix" : "Physics Diagnostics"}
                  </button>
                ))}
              </div>

              {/* Verdict tab */}
              {tab === "verdict" && (
                <div className="space-y-4">
                  <div className="bg-slate-900 border border-slate-800 rounded p-5 space-y-4">
                    <div className="px-1">
                      <PiGauge pi={verdict.pi_diagnostics?.pi_final ?? 0} />
                    </div>
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest border-b border-slate-800 pb-2">
                      System Parameter Assessment
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <MetricCard
                        label="Wildness Profile"
                        value={`Tier ${verdict.wildness_tier} // ${verdict.wildness_label}`}
                        detail={verdict.wildness_justification}
                        accent={WILDNESS_COLOR(verdict.wildness_tier)}
                      />
                      <MetricCard
                        label="Thermodynamic Trend"
                        value={verdict.pps_assessment}
                        detail={verdict.pps_justification}
                      />
                      <MetricCard
                        label="Signal Pattern"
                        value={verdict.signal_pattern}
                        detail={verdict.signal_justification}
                        accent="text-slate-200"
                      />
                      <MetricCard
                        label="Local Credibility"
                        value={verdict.local_credibility}
                        detail={verdict.local_credibility_justification}
                        accent={verdict.local_credibility?.toLowerCase().includes("met") &&
                                !verdict.local_credibility?.toLowerCase().includes("not")
                                  ? "text-emerald-400" : "text-rose-400"}
                      />
                      <MetricCard
                        label="Admissibility Bound"
                        value={verdict.admissibility_bound}
                        detail={verdict.admissibility_justification}
                      />
                      <MetricCard
                        label="Vanish Pattern"
                        value={verdict.vanish_pattern}
                        detail={verdict.vanish_justification}
                        accent="text-slate-300"
                      />
                    </div>

                    {/* Source matrix */}
                    {verdict.source_analysis && (
                      <div className="border-t border-slate-800 pt-4 space-y-3">
                        <h5 className="text-[10px] uppercase tracking-widest text-slate-500">Source Matrix</h5>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[10px]">
                          {[
                            ["Diversity",      verdict.source_analysis.source_diversity],
                            ["Trajectory",     verdict.source_analysis.coverage_trajectory],
                            ["Earliest",       verdict.source_analysis.earliest_source_found],
                            ["Grassroots",     verdict.source_analysis.grassroots_signals],
                          ].map(([label, val]) => (
                            <div key={label}>
                              <span className="block text-slate-600 uppercase mb-1">{label}</span>
                              <span className="text-slate-300 font-bold">{val}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Confirmation path */}
                    {verdict.what_would_confirm && (
                      <div className="border-t border-slate-800 pt-4">
                        <span className="block text-[10px] uppercase tracking-widest text-slate-600 mb-2">
                          What Would Confirm
                        </span>
                        <p className="text-xs text-slate-400 leading-relaxed">{verdict.what_would_confirm}</p>
                      </div>
                    )}
                  </div>

                  {/* Anomalous patterns */}
                  {verdict.anomalous_patterns?.length > 0 && (
                    <div className="bg-slate-900/50 border border-amber-500/20 rounded p-4">
                      <span className="block text-[10px] uppercase tracking-widest text-amber-500 mb-2">
                        Anomalous Patterns
                      </span>
                      <ul className="space-y-1">
                        {verdict.anomalous_patterns.map((p, i) => (
                          <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                            <span className="text-amber-600 mt-0.5">›</span>{p}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Physics tab */}
              {tab === "physics" && (
                <PhysicsPanel diag={verdict.pi_diagnostics} />
              )}
            </div>

          ) : (
            <div className="h-full min-h-64 flex flex-col items-center justify-center border border-dashed border-slate-800 rounded p-12 text-center text-slate-600">
              <div className="w-8 h-8 mb-4 opacity-30 border border-slate-600 rounded flex items-center justify-center">
                <div className="w-2 h-2 bg-teal-500 rounded-full animate-pulse" />
              </div>
              <p className="text-[11px] uppercase tracking-widest">Awaiting Stream Ingestion Target</p>
              <p className="text-[10px] max-w-xs mt-2 opacity-50 leading-relaxed">
                Submit a narrative segment to initialize the cascade. CDX temporal measurement active.
              </p>
            </div>
          )}
        </section>
      </main>

      <footer className="max-w-6xl mx-auto mt-8 pt-4 border-t border-slate-900 flex justify-between items-center flex-wrap gap-2">
        <span className="text-[9px] text-slate-700 uppercase tracking-widest">
          ChronoDyne Systems · PPS · STOC · Π = τ_obs / τ_pred(S)
        </span>
        <span className="text-[9px] text-slate-700 uppercase tracking-widest">
          CDX · NOAA Baseline · P4 Gate · v4.0.0
        </span>
      </footer>
    </div>
  );
}
