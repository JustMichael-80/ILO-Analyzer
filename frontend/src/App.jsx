import { useState, useRef } from "react";

const API_BASE = "https://ilo-analyzer.onrender.com";

const PHASES = [
  { label: "Phase 1 // Primary source ingestion", max: 3 },
  { label: "Phase 2 // Local journalism scan", max: 3 },
  { label: "Phase 3 // Deep archive cascade", max: 5 },
  { label: "Phase 4 // Debunking cross-reference", max: 3 },
  { label: "Phase 5 // Institutional corroboration", max: 3 },
];

const VERDICT_STYLE = (verdict = "") => {
  const v = verdict.toLowerCase();
  if (v.includes("clean"))        return { border: "border-emerald-500/40", bg: "bg-emerald-950/20", text: "text-emerald-400", glow: "#34d39966" };
  if (v.includes("suppression"))  return { border: "border-amber-500/40",   bg: "bg-amber-950/20",   text: "text-amber-400",   glow: "#fbbf2466" };
  if (v.includes("anomalous"))    return { border: "border-cyan-500/40",    bg: "bg-cyan-950/20",    text: "text-cyan-400",    glow: "#22d3ee66" };
  if (v.includes("insufficient")) return { border: "border-slate-600/40",   bg: "bg-slate-900/20",   text: "text-slate-400",   glow: "#94a3b866" };
  return                                  { border: "border-rose-500/40",    bg: "bg-rose-950/20",    text: "text-rose-400",    glow: "#f43f5e66" };
};

const WILDNESS_COLOR = (tier) => ({
  1: "text-emerald-400", 2: "text-sky-400", 3: "text-yellow-400",
  4: "text-orange-400",  5: "text-rose-400", 6: "text-purple-400",
}[tier] || "text-teal-400");

const SADDLE_STYLE = (c) => ({
  organic:    { text: "text-emerald-400", label: "ORGANIC DECAY" },
  ilo_fade:   { text: "text-rose-400",    label: "ILO FADE ⚠" },
  maintained: { text: "text-amber-400",   label: "ARTIFICIAL MAINTENANCE ⚠" },
  no_data:    { text: "text-slate-500",   label: "NO DATA" },
}[c] || { text: "text-slate-500", label: "UNKNOWN" });

const VELOCITY_STYLE = (v) => ({
  organic:          { text: "text-emerald-400", label: "ORGANIC DIFFUSION" },
  fast_injection:   { text: "text-rose-400",    label: "FAST INJECTION ⚠" },
  slow_suppression: { text: "text-amber-400",   label: "SUPPRESSION SIGNAL ⚠" },
}[v] || { text: "text-slate-500", label: "UNKNOWN" });

const QUADRANT_COLOR = (q = "") => {
  if (q.includes("I —"))  return "text-rose-400";
  if (q.includes("II"))   return "text-orange-400";
  if (q.includes("III"))  return "text-amber-400";
  if (q.includes("IV"))   return "text-sky-400";
  return "text-emerald-400";
};

function PiBar({ value = 0 }) {
  const v = Number(value) || 0;
  const color =
    v >= 0.70 && v <= 1.40 ? "#34d399" :
    v < 0.35               ? "#f43f5e" :
    v > 2.50               ? "#fbbf24" :
    v < 0.70               ? "#fb923c" : "#22d3ee";
  const pct = Math.min((Math.min(v, 3) / 3) * 100, 100);
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-end">
        <span className="text-[10px] uppercase tracking-widest text-slate-500">
          Persistence Ratio Π = τobs / τpred(S)
        </span>
        <span className="font-black text-xl tabular-nums" style={{ color }}>{v.toFixed(4)}</span>
      </div>
      <div className="relative h-2 bg-slate-800 rounded overflow-hidden">
        <div className="absolute h-full bg-emerald-900/40 rounded"
             style={{ left: `${(0.70/3)*100}%`, width: `${((1.40-0.70)/3)*100}%` }} />
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

function GammaBar({ value = 0 }) {
  const v = Number(value) || 0;
  const color =
    v >= 0.70 && v <= 1.40 ? "#34d399" :
    v > 1.40               ? "#f43f5e" : "#fbbf24";
  const pct = Math.min((Math.min(v, 3) / 3) * 100, 100);
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-end">
        <span className="text-[10px] uppercase tracking-widest text-slate-500">
          Geographic Entropy Γ = Hgeo / Hexpected(t)
        </span>
        <span className="font-black text-xl tabular-nums" style={{ color }}>{v.toFixed(4)}</span>
      </div>
      <div className="relative h-2 bg-slate-800 rounded overflow-hidden">
        <div className="absolute h-full bg-emerald-900/40 rounded"
             style={{ left: `${(0.70/3)*100}%`, width: `${((1.40-0.70)/3)*100}%` }} />
        <div className="absolute h-full rounded transition-all duration-700"
             style={{ width: `${pct}%`, background: color, boxShadow: `0 0 10px ${color}88` }} />
      </div>
      <div className="flex justify-between text-[9px] text-slate-700 uppercase tracking-wider">
        <span>Suppression</span>
        <span className="text-emerald-800">Organic Zone</span>
        <span>Injection</span>
      </div>
    </div>
  );
}

function QuadrantMap({ pi = 0, gamma = 0, quadrant = "" }) {
  const piV   = Number(pi)    || 0;
  const gamV  = Number(gamma) || 0;
  const piHigh  = piV  > 1.40;
  const piLow   = piV  < 0.70;
  const gamHigh = gamV > 1.40;
  const gamLow  = gamV < 0.70;
  const isOrganic = !piHigh && !piLow && !gamHigh && !gamLow;

  const cells = [
    { label: "I — Confirmed ILO",       active: piHigh && gamHigh,  color: "#f43f5e" },
    { label: "III — Viral Suppression",  active: piLow  && gamHigh,  color: "#fbbf24" },
    { label: "II — Astroturfed Local",   active: piHigh && gamLow,   color: "#fb923c" },
    { label: "IV — Suppressed Event",    active: piLow  && gamLow,   color: "#38bdf8" },
  ];

  return (
    <div className="space-y-2">
      <span className="text-[10px] uppercase tracking-widest text-slate-500">Π/Γ Diagnostic Quadrant</span>
      <div className="grid grid-cols-2 gap-1">
        {cells.map((cell, i) => (
          <div key={i} className="rounded p-2 border text-center text-[9px] uppercase tracking-wider leading-tight transition-all"
               style={{
                 borderColor: cell.active ? cell.color : "#1e293b",
                 background:  cell.active ? `${cell.color}22` : "#0f172a",
                 color:       cell.active ? cell.color : "#475569",
                 boxShadow:   cell.active ? `0 0 12px ${cell.color}44` : "none",
               }}>
            {cell.label}
          </div>
        ))}
      </div>
      {isOrganic && (
        <div className="text-center text-[10px] text-emerald-400 font-bold tracking-widest">● ORGANIC</div>
      )}
      {quadrant && (
        <p className={`text-[10px] font-bold tracking-wider ${QUADRANT_COLOR(quadrant)}`}>{quadrant}</p>
      )}
    </div>
  );
}

function MetricCard({ label, value, detail, accent = "text-teal-400" }) {
  return (
    <div className="bg-slate-950 p-3 rounded border border-slate-800/60 space-y-1">
      <span className="block text-[10px] uppercase tracking-widest text-slate-500">{label}</span>
      <span className={`text-sm font-bold ${accent}`}>{value}</span>
      {detail && <p className="text-xs text-slate-400 leading-relaxed pt-1 border-t border-slate-900 mt-1">{detail}</p>}
    </div>
  );
}

function PhysicsPanel({ pi_diag, gamma_diag }) {
  if (!pi_diag) return (
    <div className="text-slate-600 text-[10px] text-center py-8">No physics data available.</div>
  );

  const saddle      = SADDLE_STYLE(pi_diag.saddle_point?.classification);
  const scopeDist   = (gamma_diag && gamma_diag.scope_distribution)   ? gamma_diag.scope_distribution   : {};
  const countryDist = (gamma_diag && gamma_diag.country_distribution)  ? gamma_diag.country_distribution  : {};
  const velocity    = VELOCITY_STYLE(gamma_diag?.diffusion_velocity);
  const scopeEntries   = Object.entries(scopeDist);
  const scopeRankLabel = ["local","national","international","global"][gamma_diag?.max_scope_rank ?? 1] ?? "unknown";

  return (
    <div className="space-y-4">

      {/* Π block */}
      <div className="border border-slate-700/50 rounded bg-slate-950 p-4 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
          <div className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
          <span className="text-[10px] uppercase tracking-widest text-teal-400 font-bold">
            Persistence Ratio (Π) — Temporal Anomaly
          </span>
        </div>
        <PiBar value={pi_diag.pi_final} />
        <p className="text-[10px] text-slate-400 leading-relaxed border-l-2 border-teal-500/30 pl-3">
          {pi_diag.pi_interpretation || ""}
        </p>
        <div className="grid grid-cols-2 gap-2 text-[10px]">
          {[
            ["τ observed",     `${pi_diag.tau_observed_days ?? 0}d`],
            ["τ predicted",    `${pi_diag.tau_predicted_days ?? 0}d`],
            ["S (entropy)",    (pi_diag.S ?? 0).toFixed(4)],
            ["E (complexity)", (pi_diag.E ?? 0).toFixed(4)],
            ["Nodes",          pi_diag.node_count ?? 0],
            ["Class A",        pi_diag.class_a_count ?? 0],
            ["Class D",        pi_diag.class_d_count ?? 0],
            ["Inv. signal",    (pi_diag.inverted_signal ?? 0).toFixed(4)],
          ].map(([label, val]) => (
            <div key={label} className="flex justify-between bg-slate-900 rounded px-2 py-1.5">
              <span className="text-slate-600 uppercase tracking-wider">{label}</span>
              <span className="text-slate-300 font-bold tabular-nums">{val}</span>
            </div>
          ))}
        </div>
        {pi_diag.saddle_point && (
          <div className="border border-slate-800 rounded p-3 space-y-1">
            <div className="flex justify-between items-center">
              <span className="text-[9px] uppercase tracking-widest text-slate-600">Saddle-Point // NOAA Weather Baseline</span>
              <span className={`text-[10px] font-bold ${saddle.text}`}>{saddle.label}</span>
            </div>
            {pi_diag.saddle_point.delta != null && (
              <div className="flex gap-4 text-[9px] text-slate-600">
                <span>λobs = {(pi_diag.saddle_point.lambda_observed ?? 0).toFixed(4)}</span>
                <span>λwx = {(pi_diag.saddle_point.lambda_weather ?? 0).toFixed(4)}</span>
                <span>Δ = {(pi_diag.saddle_point.delta ?? 0).toFixed(4)}</span>
                <span className="ml-auto text-slate-700">{pi_diag.saddle_point.baseline_source ?? ""}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Γ block */}
      {gamma_diag && (
        <div className="border border-slate-700/50 rounded bg-slate-950 p-4 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <div className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" />
            <span className="text-[10px] uppercase tracking-widest text-purple-400 font-bold">
              Geographic Entropy (Γ) — Spatial Diffusion Anomaly
            </span>
          </div>
          <GammaBar value={gamma_diag.gamma} />
          <p className="text-[10px] text-slate-400 leading-relaxed border-l-2 border-purple-500/30 pl-3">
            {gamma_diag.gamma_interpretation || ""}
          </p>
          <div className="grid grid-cols-2 gap-2 text-[10px]">
            {[
              ["H geographic", (gamma_diag.h_geographic ?? 0).toFixed(4)],
              ["H expected",   (gamma_diag.h_expected   ?? 0).toFixed(4)],
              ["Max scope",    scopeRankLabel],
            ].map(([label, val]) => (
              <div key={label} className="flex justify-between bg-slate-900 rounded px-2 py-1.5">
                <span className="text-slate-600 uppercase tracking-wider">{label}</span>
                <span className="text-slate-300 font-bold tabular-nums">{val}</span>
              </div>
            ))}
            <div className="flex justify-between bg-slate-900 rounded px-2 py-1.5">
              <span className="text-slate-600 uppercase tracking-wider">Velocity</span>
              <span className={`font-bold text-[10px] ${velocity.text}`}>{velocity.label}</span>
            </div>
          </div>

          {scopeEntries.length > 0 && (
            <div className="border border-slate-800 rounded p-3 space-y-2">
              <span className="text-[9px] uppercase tracking-widest text-slate-600">Scope Distribution</span>
              <div className="flex gap-2 flex-wrap">
                {scopeEntries.map(([scope, count]) => (
                  <span key={scope} className="text-[9px] px-2 py-0.5 rounded border border-slate-700 text-slate-400">
                    {scope}: {count}
                  </span>
                ))}
              </div>
            </div>
          )}

          <QuadrantMap
            pi={pi_diag.pi_final}
            gamma={gamma_diag.gamma}
            quadrant={gamma_diag.quadrant || ""}
          />
        </div>
      )}
    </div>
  );
}

export default function ILOAnalyzerConsole() {
  const [claim, setClaim]             = useState("");
  const [loading, setLoading]         = useState(false);
  const [phaseIndex, setPhaseIndex]   = useState(0);
  const [runningPi, setRunningPi]     = useState(null);
  const [verdict, setVerdict]         = useState(null);
  const [error, setError]             = useState(null);
  const [tab, setTab]                 = useState("verdict");
  const [reportLoading, setReportLoading] = useState(false);
  const [report, setReport]           = useState(null);
  const [reportError, setReportError] = useState(null);
  const phaseTimer                    = useRef(null);

  const generateReport = async () => {
    if (!claim.trim() || reportLoading) return;
    setReportLoading(true);
    setReportError(null);
    setReport(null);
    setTab("report");
    try {
      const res = await fetch(`${API_BASE}/report`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ claim, fetch_cdx: true }),
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data = await res.json();
      setReport(data);
    } catch (err) {
      setReportError(`Report generation failed: ${err.message}`);
    } finally {
      setReportLoading(false);
    }
  };

  const downloadReport = () => {
    if (!report?.markdown) return;
    const blob = new Blob([report.markdown], { type: "text/markdown" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `ilo-report-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

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
      <header className="border-b border-slate-800 pb-4 mb-6">
        <div className="flex justify-between items-start flex-wrap gap-3">
          <div>
            <h1 className="text-lg md:text-xl font-bold tracking-wider text-teal-400">
              CHRONODYNE SYSTEMS // ILO ANALYZER
            </h1>
            <p className="text-[11px] text-slate-500 mt-1">
              v4.1.0 · PPS · STOC · Π · Γ · NOAA Baseline · Wayback CDX
            </p>
          </div>
          <span className="text-[10px] px-2.5 py-1 rounded border border-teal-500/30 bg-teal-950/20 text-teal-400 tracking-wider">
            P4 GATE ACTIVE
          </span>
        </div>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left: Input */}
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
              <button
                onClick={generateReport}
                disabled={reportLoading || !claim.trim()}
                className="w-full bg-purple-800 hover:bg-purple-700 disabled:bg-slate-800 disabled:text-slate-600 text-slate-100 font-bold py-2.5 px-4 rounded text-[11px] uppercase tracking-widest transition-colors cursor-pointer"
              >
                {reportLoading ? "Generating Report..." : "Generate Analyst Report"}
              </button>
              <p className="text-[9px] text-slate-700 text-right">⌘+Enter to execute</p>
            </div>
          </div>

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
              <p className="text-[9px] text-slate-700">CDX + geo queries in progress...</p>
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

              {/* Quadrant badge */}
              {verdict.gamma_diagnostics?.quadrant && (
                <div className={`text-center text-[11px] font-bold tracking-widest py-2 rounded border border-slate-800 ${QUADRANT_COLOR(verdict.gamma_diagnostics.quadrant)}`}>
                  Π/Γ QUADRANT: {verdict.gamma_diagnostics.quadrant}
                </div>
              )}

              {/* WTF factor */}
              {verdict.wtf_factor && !verdict.wtf_factor.toLowerCase().includes("no significant") && (
                <div className="bg-slate-900/50 border border-rose-500/20 border-l-2 border-l-rose-500 rounded p-4">
                  <span className="block text-[10px] uppercase tracking-widest text-rose-500 mb-1.5">⚡ Core Anomaly</span>
                  <p className="text-xs text-slate-300 leading-relaxed">{verdict.wtf_factor}</p>
                </div>
              )}

              {/* Tabs */}
              <div className="flex border-b border-slate-800">
                {["verdict", "physics", "report"].map((t) => (
                  <button key={t} onClick={() => setTab(t)}
                    className={`px-4 py-2 text-[10px] uppercase tracking-widest transition-colors cursor-pointer ${
                      tab === t ? "text-teal-400 border-b-2 border-teal-400 -mb-px" : "text-slate-600 hover:text-slate-400"
                    }`}>
                    {t === "verdict" ? "Verdict Matrix" : t === "physics" ? "Physics Diagnostics" : "Analyst Report"}
                  </button>
                ))}
              </div>

              {/* Verdict tab */}
              {tab === "verdict" && (
                <div className="space-y-4">
                  <div className="bg-slate-900 border border-slate-800 rounded p-5 space-y-4">
                    <div className="px-1 space-y-3">
                      <PiBar value={verdict.pi_diagnostics?.pi_final ?? 0} />
                      <GammaBar value={verdict.gamma_diagnostics?.gamma ?? 0} />
                    </div>
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest border-b border-slate-800 pb-2">
                      System Parameter Assessment
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <MetricCard label="Wildness Profile"
                        value={`Tier ${verdict.wildness_tier} // ${verdict.wildness_label}`}
                        detail={verdict.wildness_justification}
                        accent={WILDNESS_COLOR(verdict.wildness_tier)} />
                      <MetricCard label="Thermodynamic Trend"
                        value={verdict.pps_assessment}
                        detail={verdict.pps_justification} />
                      <MetricCard label="Signal Pattern"
                        value={verdict.signal_pattern}
                        detail={verdict.signal_justification}
                        accent="text-slate-200" />
                      <MetricCard label="Local Credibility"
                        value={verdict.local_credibility}
                        detail={verdict.local_credibility_justification}
                        accent={verdict.local_credibility?.toLowerCase().includes("met") &&
                                !verdict.local_credibility?.toLowerCase().includes("not")
                                  ? "text-emerald-400" : "text-rose-400"} />
                      <MetricCard label="Admissibility Bound"
                        value={verdict.admissibility_bound}
                        detail={verdict.admissibility_justification} />
                      <MetricCard label="Vanish Pattern"
                        value={verdict.vanish_pattern}
                        detail={verdict.vanish_justification}
                        accent="text-slate-300" />
                    </div>

                    {verdict.source_analysis && (
                      <div className="border-t border-slate-800 pt-4 space-y-3">
                        <h5 className="text-[10px] uppercase tracking-widest text-slate-500">Source Matrix</h5>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[10px]">
                          {[
                            ["Diversity",  verdict.source_analysis.source_diversity],
                            ["Trajectory", verdict.source_analysis.coverage_trajectory],
                            ["Earliest",   verdict.source_analysis.earliest_source_found],
                            ["Grassroots", verdict.source_analysis.grassroots_signals],
                          ].map(([label, val]) => (
                            <div key={label}>
                              <span className="block text-slate-600 uppercase mb-1">{label}</span>
                              <span className="text-slate-300 font-bold">{val}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {verdict.what_would_confirm && (
                      <div className="border-t border-slate-800 pt-4">
                        <span className="block text-[10px] uppercase tracking-widest text-slate-600 mb-2">What Would Confirm</span>
                        <p className="text-xs text-slate-400 leading-relaxed">{verdict.what_would_confirm}</p>
                      </div>
                    )}
                  </div>

                  {verdict.anomalous_patterns?.length > 0 && (
                    <div className="bg-slate-900/50 border border-amber-500/20 rounded p-4">
                      <span className="block text-[10px] uppercase tracking-widest text-amber-500 mb-2">Anomalous Patterns</span>
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
                <PhysicsPanel
                  pi_diag={verdict.pi_diagnostics}
                  gamma_diag={verdict.gamma_diagnostics}
                />
              )}

              {/* Report tab */}
              {tab === "report" && (
                <div className="space-y-4">
                  {reportLoading && (
                    <div className="border border-purple-500/20 bg-purple-950/10 rounded p-6 text-center space-y-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse mx-auto" />
                      <p className="text-[10px] uppercase tracking-widest text-purple-400">Gemini Analyst Pass In Progress...</p>
                      <p className="text-[9px] text-slate-600">Assembling diagnostic report · Pattern hypothesis generation · Investigative guidance</p>
                    </div>
                  )}
                  {reportError && (
                    <div className="bg-red-950/20 border border-red-500/30 rounded p-4 text-[11px] text-red-400">
                      <span className="font-bold">[-] REPORT GENERATION FAILED</span>
                      <p className="mt-1 text-red-500/70">{reportError}</p>
                    </div>
                  )}
                  {report && !reportLoading && (
                    <div className="space-y-4">
                      <div className="border border-purple-500/30 bg-purple-950/10 rounded p-5 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] uppercase tracking-widest text-purple-400 font-bold">Analyst Assessment</span>
                          <span className="text-[9px] text-slate-600">{report.analyst?.campaign_type} · {((report.analyst?.campaign_confidence ?? 0) * 100).toFixed(0)}% confidence</span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed">{report.analyst?.executive_summary}</p>
                        {report.analyst?.actor_profile && (
                          <p className="text-[10px] text-slate-500 border-t border-slate-800 pt-2">
                            <span className="text-slate-600 uppercase tracking-wider">Actor Profile: </span>{report.analyst.actor_profile}
                          </p>
                        )}
                      </div>
                      {report.analyst?.pattern_hypotheses?.length > 0 && (
                        <div className="border border-slate-800 rounded p-4 space-y-3">
                          <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Pattern Hypotheses</span>
                          {report.analyst.pattern_hypotheses.map((h, i) => (
                            <div key={i} className="border border-slate-800/60 rounded p-3 space-y-1">
                              <div className="flex justify-between items-start gap-2">
                                <p className="text-xs text-slate-200 font-bold leading-relaxed">{h.hypothesis}</p>
                                <span className="text-[9px] text-purple-400 font-bold flex-shrink-0">{((h.confidence ?? 0) * 100).toFixed(0)}%</span>
                              </div>
                              <p className="text-[9px] text-emerald-600">↑ {h.supporting_evidence}</p>
                              <p className="text-[9px] text-rose-700">↓ {h.contradicting_evidence}</p>
                            </div>
                          ))}
                        </div>
                      )}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {report.analyst?.red_flags?.length > 0 && (
                          <div className="border border-rose-500/20 rounded p-4 space-y-2">
                            <span className="text-[10px] uppercase tracking-widest text-rose-500 font-bold">Red Flags</span>
                            <ul className="space-y-1">
                              {report.analyst.red_flags.map((f, i) => (
                                <li key={i} className="text-[10px] text-slate-400 flex items-start gap-2"><span className="text-rose-600 mt-0.5">›</span>{f}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {report.analyst?.investigative_next_steps?.length > 0 && (
                          <div className="border border-amber-500/20 rounded p-4 space-y-2">
                            <span className="text-[10px] uppercase tracking-widest text-amber-500 font-bold">Next Steps</span>
                            <ol className="space-y-1">
                              {report.analyst.investigative_next_steps.map((s, i) => (
                                <li key={i} className="text-[10px] text-slate-400 flex items-start gap-2"><span className="text-amber-600 flex-shrink-0">{i+1}.</span>{s}</li>
                              ))}
                            </ol>
                          </div>
                        )}
                      </div>
                      {report.analyst?.follow_up_claims?.length > 0 && (
                        <div className="border border-sky-500/20 rounded p-4 space-y-2">
                          <span className="text-[10px] uppercase tracking-widest text-sky-500 font-bold">Follow-Up Claims to Test</span>
                          <ul className="space-y-1">
                            {report.analyst.follow_up_claims.map((c, i) => (
                              <li key={i} className="text-[10px] text-slate-400 flex items-start gap-2"><span className="text-sky-600 mt-0.5">›</span>{c}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {report.analyst?.analyst_notes && (
                        <div className="border border-slate-700/50 rounded p-4">
                          <span className="block text-[10px] uppercase tracking-widest text-slate-600 mb-2">Analyst Notes</span>
                          <p className="text-[10px] text-slate-400 leading-relaxed">{report.analyst.analyst_notes}</p>
                        </div>
                      )}
                      <button
                        onClick={downloadReport}
                        className="w-full border border-purple-500/30 hover:border-purple-400/60 bg-purple-950/10 hover:bg-purple-950/20 text-purple-400 font-bold py-2.5 px-4 rounded text-[11px] uppercase tracking-widest transition-colors cursor-pointer"
                      >
                        Download Full Report (.md)
                      </button>
                    </div>
                  )}
                  {!report && !reportLoading && !reportError && (
                    <div className="text-center py-8 text-slate-600 text-[10px] uppercase tracking-widest">
                      Click "Generate Analyst Report" to run the full investigative analysis.
                    </div>
                  )}
                </div>
              )}
            </div>

          ) : (
            <div className="h-full min-h-64 flex flex-col items-center justify-center border border-dashed border-slate-800 rounded p-12 text-center text-slate-600">
              <div className="w-8 h-8 mb-4 opacity-30 border border-slate-600 rounded flex items-center justify-center">
                <div className="w-2 h-2 bg-teal-500 rounded-full animate-pulse" />
              </div>
              <p className="text-[11px] uppercase tracking-widest">Awaiting Stream Ingestion Target</p>
              <p className="text-[10px] max-w-xs mt-2 opacity-50 leading-relaxed">
                Submit a narrative segment to initialize the cascade. Π and Γ metrics active.
              </p>
            </div>
          )}
        </section>
      </main>

      <footer className="max-w-6xl mx-auto mt-8 pt-4 border-t border-slate-900 flex justify-between items-center flex-wrap gap-2">
        <span className="text-[9px] text-slate-700 uppercase tracking-widest">
          ChronoDyne Systems · PPS · STOC · Π = τobs/τpred(S) · Γ = Hgeo/Hexp(t)
        </span>
        <span className="text-[9px] text-slate-700 uppercase tracking-widest">
          CDX · NOAA Baseline · P4 Gate · v4.2.0
        </span>
        <a
          href="https://github.com/JustMichael-80/ILO-Analyzer"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[9px] text-slate-600 hover:text-teal-400 uppercase tracking-widest transition-colors"
        >
          GitHub ↗
        </a>
      </footer>
    </div>
  );
}
