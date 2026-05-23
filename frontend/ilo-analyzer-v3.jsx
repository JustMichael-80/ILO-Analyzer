import { useState, useRef } from "react";

const PHASES = [
  { label: "Phase 1: Sifting primary source reports", max: 3 },
  { label: "Phase 2: Scanning local news and grassroots journalism", max: 3 },
  { label: "Phase 3: Deep advanced cascade mapping on historic archives", max: 5 },
  { label: "Phase 4: Cross-referencing debunking and verification signals", max: 3 },
  { label: "Phase 5: Institutional corroboration and research scan", max: 3 },
];

const VERDICT_STYLE = (verdict = "") => {
  if (verdict.includes("Clean")) return { border: "border-emerald-500/40", bg: "bg-emerald-950/20", text: "text-emerald-400", bar: "#34d399" };
  if (verdict.includes("Suppression") || verdict.includes("Suppressed")) return { border: "border-amber-500/40", bg: "bg-amber-950/20", text: "text-amber-400", bar: "#fbbf24" };
  if (verdict.includes("Anomalous")) return { border: "border-cyan-500/40", bg: "bg-cyan-950/20", text: "text-cyan-400", bar: "#22d3ee" };
  return { border: "border-rose-500/40", bg: "bg-rose-950/20", text: "text-rose-400", bar: "#f43f5e" };
};

const TIER_COLOR = (tier) => {
  const map = { 1: "text-emerald-400", 2: "text-sky-400", 3: "text-yellow-400", 4: "text-orange-400", 5: "text-rose-400", 6: "text-purple-400" };
  return map[tier] || "text-teal-400";
};

function MetricCard({ label, value, detail, accent = "text-teal-400" }) {
  return (
    <div className="bg-slate-950 p-3 rounded border border-slate-800/60 space-y-1">
      <span className="block text-[10px] uppercase tracking-widest text-slate-500">{label}</span>
      <span className={`text-sm font-bold ${accent}`}>{value}</span>
      {detail && <p className="text-xs text-slate-400 leading-relaxed">{detail}</p>}
    </div>
  );
}

function PiBar({ value }) {
  const color = value > 0.6 ? "#34d399" : value > 0.3 ? "#fbbf24" : "#f43f5e";
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[10px] text-slate-500 uppercase tracking-widest">
        <span>Persistence Ratio (Π)</span>
        <span style={{ color }} className="font-bold">{value.toFixed(4)}</span>
      </div>
      <div className="h-1.5 bg-slate-800 rounded overflow-hidden">
        <div
          className="h-full rounded transition-all duration-700"
          style={{ width: `${Math.min(value * 100, 100)}%`, background: color, boxShadow: `0 0 8px ${color}88` }}
        />
      </div>
    </div>
  );
}

export default function ILOAnalyzerConsole() {
  const [claim, setClaim] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentPhase, setCurrentPhase] = useState("");
  const [phaseIndex, setPhaseIndex] = useState(0);
  const [runningPi, setRunningPi] = useState(null);
  const [verdict, setVerdict] = useState(null);
  const [error, setError] = useState(null);
  const phaseTimer = useRef(null);

  const simulatePhases = () => {
    let idx = 0;
    setPhaseIndex(0);
    setCurrentPhase(PHASES[0].label + ` (Max Results: ${PHASES[0].max})...`);
    setRunningPi(null);

    phaseTimer.current = setInterval(() => {
      idx++;
      if (idx < PHASES.length) {
        setPhaseIndex(idx);
        setCurrentPhase(PHASES[idx].label + ` (Max Results: ${PHASES[idx].max})...`);
        setRunningPi(parseFloat((Math.random() * 0.4 + 0.05).toFixed(2)));
      } else {
        clearInterval(phaseTimer.current);
        setCurrentPhase("Passing matrices to P4 Gate for schema validation...");
      }
    }, 1800);
  };

  const executeAnalysis = async () => {
    if (!claim.trim() || loading) return;

    setLoading(true);
    setError(null);
    setVerdict(null);
    simulatePhases();

    try {
      // Connects directly to your local engine server gateway
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ claim: claim })
      });

      if (!response.ok) throw new Error(`Server returned status: ${response.status}`);

      const parsed = await response.json();
      clearInterval(phaseTimer.current);

      setRunningPi(parsed.ilo_probability / 100);
      setVerdict(parsed);
    } catch (err) {
      clearInterval(phaseTimer.current);
      setError(`Pipeline collapsed: ${err.message}`);
    } finally {
      setLoading(false);
      setCurrentPhase("");
      setPhaseIndex(0);
    }
  };

  const vs = VERDICT_STYLE(verdict?.verdict);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-mono p-4 md:p-6 selection:bg-teal-500 selection:text-slate-950">
      <header className="border-b border-slate-800 pb-4 mb-6">
        <div className="flex justify-between items-start flex-wrap gap-3">
          <div>
            <h1 className="text-lg md:text-xl font-bold tracking-wider text-teal-400">CHRONODYNE SYSTEMS // ILO ANALYZER</h1>
            <p className="text-[11px] text-slate-500 mt-1">Sieve Module v2.0 // Powered by the Principle of Persistent Structurization</p>
          </div>
          <div>
            <span className="text-[10px] px-2.5 py-1 rounded border border-teal-500/30 bg-teal-950/20 text-teal-400 tracking-wider">
              P4 NATIVE GATE SECURE
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-1 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded p-5 shadow-xl">
            <h2 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-4">Ingestion Interface</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-[10px] text-slate-500 uppercase tracking-wider mb-2">Target Flux String / Claim</label>
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
                {loading ? "Sifting Cascade..." : "Execute Triage Sieve"}
              </button>
            </div>
          </div>

          {loading && (
            <div className="bg-slate-900/50 border border-teal-500/20 rounded p-4 text-xs space-y-3">
              <div className="text-teal-400 font-bold uppercase tracking-widest text-[10px]">Live Cascade Logs</div>
              <div className="space-y-1.5">
                {PHASES.map((p, i) => (
                  <div key={i} className={`flex items-center gap-2 text-[10px] ${i <= phaseIndex ? "text-slate-300" : "text-slate-700"}`}>
                    <span className={`w-1 h-1 rounded-full ${i < phaseIndex ? "bg-teal-500" : i === phaseIndex ? "bg-teal-400 animate-pulse" : "bg-slate-700"}`} />
                    {p.label}
                  </div>
                ))}
              </div>
              {runningPi !== null && <div className="border-t border-slate-800 pt-3"><PiBar value={runningPi} /></div>}
            </div>
          )}

          {error && (
            <div className="bg-red-950/20 border border-red-500/30 rounded p-4 text-[11px] text-red-400">
              <span className="font-bold">[-] PIPELINE COLLAPSE</span>
              <p className="mt-1 text-red-500/70">{error}</p>
            </div>
          )}
        </section>

        <section className="lg:col-span-2">
          {verdict ? (
            <div className="space-y-4">
              <div className={`border ${vs.border} ${vs.bg} p-5 rounded flex items-center justify-between gap-4 flex-wrap`}>
                <div>
                  <span className={`text-[10px] uppercase font-bold tracking-widest opacity-60 ${vs.text}`}>Diagnostic Decision</span>
                  <h3 className={`text-xl font-black uppercase tracking-tight mt-0.5 ${vs.text}`}>{verdict.verdict}</h3>
                  <p className="text-xs text-slate-400 mt-2 max-w-md leading-relaxed">{verdict.verdict_summary}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <span className={`text-[10px] uppercase font-bold tracking-widest opacity-60 ${vs.text}`}>ILO Probability</span>
                  <p className={`text-4xl font-black mt-0.5 ${vs.text}`}>{verdict.ilo_probability}<span className="text-lg opacity-50">%</span></p>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded p-5 space-y-4">
                <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest border-b border-slate-800 pb-2">System Parameter Assessment</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <MetricCard label="Wildness Profile" value={`Tier ${verdict.wildness_tier} // ${verdict.wildness_label}`} detail={verdict.wildness_justification} accent={TIER_COLOR(verdict.wildness_tier)} />
                  <MetricCard label="Thermodynamic Trend" value={verdict.pps_assessment} detail={verdict.pps_justification} />
                  <MetricCard label="Signal Pattern" value={verdict.signal_pattern} detail={verdict.signal_justification} accent="text-slate-200" />
                  <MetricCard label="Local Credibility" value={verdict.local_credibility} detail={verdict.local_credibility_justification} accent={verdict.local_credibility === "Threshold Met" ? "text-emerald-400" : "text-rose-400"} />
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full min-h-64 flex flex-col items-center justify-center border border-dashed border-slate-800 rounded p-12 text-center text-slate-600">
              <p className="text-[11px] uppercase tracking-widest">Awaiting Stream Ingestion Target</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
