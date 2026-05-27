import { useState, useRef, useEffect } from "react";

const API_BASE = "https://ilo-analyzer.onrender.com";

const PHASES = [
  { label: "Phase 1 // Primary source ingestion",        plain: "Scanning primary sources & official records" },
  { label: "Phase 2 // Local journalism scan",           plain: "Checking local news coverage" },
  { label: "Phase 3 // Deep archive cascade",            plain: "Searching web archives for history" },
  { label: "Phase 4 // Debunking cross-reference",       plain: "Cross-referencing fact-checks" },
  { label: "Phase 5 // Institutional corroboration",     plain: "Checking academic & institutional sources" },
  { label: "Phase 6 // Declassified document archaeology", plain: "Searching FOIA archives & declassified records" },
];

// ── Info popup content ────────────────────────────────────────────────────────

const INFO = {
  pi: {
    title: "Persistence Ratio (Π)",
    plain: "How long has this story been around compared to how long a real story of its complexity would naturally last?",
    detail: "A score near 1.0 means organic — the story lives as long as you'd expect. Much higher means it's being artificially kept alive (bots, coordinated accounts). Much lower means it vanished faster than it should — a sign it may have been suppressed.",
    formula: "Π = time observed ÷ time predicted by information complexity",
    ranges: [
      { label: "< 0.35", color: "#f43f5e", meaning: "ILO Fade — story died unnaturally fast" },
      { label: "0.70 – 1.40", color: "#34d399", meaning: "Organic — normal lifespan" },
      { label: "> 2.50", color: "#fbbf24", meaning: "Artificially maintained — someone is keeping it alive" },
    ],
  },
  gamma: {
    title: "Geographic Spread (Γ)",
    plain: "Did this story spread the way real news spreads — starting local and growing outward — or did it appear everywhere at once?",
    detail: "Real stories start locally and spread outward over days. Coordinated campaigns inject content simultaneously across many regions. Suppressed stories stay stuck locally even when they should spread.",
    formula: "Γ = actual geographic spread ÷ expected spread for a story this age",
    ranges: [
      { label: "< 0.70", color: "#fbbf24", meaning: "Suppression — geographically contained" },
      { label: "0.70 – 1.40", color: "#34d399", meaning: "Organic — natural diffusion pattern" },
      { label: "> 1.40", color: "#f43f5e", meaning: "Coordinated injection — appeared everywhere too fast" },
    ],
  },
  quadrant: {
    title: "Π/Γ Diagnostic Quadrant",
    plain: "Where does this story land on the two-axis map of time vs. geography anomalies?",
    detail: "Combining how long the story has lived (Π) with how it spread geographically (Γ) creates a diagnostic coordinate space. Each quadrant has a distinct meaning.",
    ranges: [
      { label: "Quadrant I (Π high, Γ high)", color: "#f43f5e", meaning: "Confirmed ILO — injected everywhere and kept alive" },
      { label: "Quadrant II (Π high, Γ low)", color: "#fb923c", meaning: "Astroturfed local — manufactured but contained" },
      { label: "Quadrant III (Π low, Γ high)", color: "#fbbf24", meaning: "Viral suppression — spread fast then killed" },
      { label: "Quadrant IV (Π low, Γ low)", color: "#38bdf8", meaning: "Suppressed real event — neither persisting nor spreading" },
      { label: "Center (both organic)", color: "#34d399", meaning: "Organic — normal story, no anomalies" },
    ],
  },
  saddle: {
    title: "Decay Pattern",
    plain: "Is the story fading at the same rate weather forecasts lose accuracy — the natural benchmark for how information decays?",
    detail: "Weather forecast accuracy degrades at a predictable rate (~12% per day). This is used as a physics-grounded baseline for natural information decay. Stories that decay faster, slower, or not at all compared to this baseline are flagged.",
    ranges: [
      { label: "Organic", color: "#34d399", meaning: "Decaying at normal rate" },
      { label: "ILO Fade", color: "#f43f5e", meaning: "Collapsed faster than physics predicts — engineered disappearance" },
      { label: "Artificial Maintenance", color: "#fbbf24", meaning: "Not decaying — being actively kept alive" },
    ],
  },
  wildness: {
    title: "Wildness Tier",
    plain: "How extraordinary is this claim, independent of whether it's true?",
    detail: "Tier 1 is mundane news. Tier 6 is mythological. Higher tiers don't mean false — extraordinary things happen — but they require stronger evidence. The tier calibrates how skeptical to be about the available sourcing.",
    ranges: [
      { label: "Tier 1 — Mundane",      color: "#34d399", meaning: "Ordinary news, low prior skepticism needed" },
      { label: "Tier 2 — Murky",        color: "#38bdf8", meaning: "Ambiguous or contested" },
      { label: "Tier 3 — Mysterious",   color: "#fbbf24", meaning: "Unusual claim, requires good evidence" },
      { label: "Tier 4 — Manufactured", color: "#fb923c", meaning: "Strong ILO indicators present" },
      { label: "Tier 5 — Manic",        color: "#f43f5e", meaning: "Extreme claim, very high burden of proof" },
      { label: "Tier 6 — Mythological", color: "#a855f7", meaning: "Extraordinary claim, extraordinary evidence required" },
    ],
  },
  sourceClasses: {
    title: "Source Classifications",
    plain: "Not all sources are equal. The system grades every source it finds.",
    detail: "Sources are sorted into four classes based on editorial standards, independence, and historical reliability.",
    ranges: [
      { label: "Class A — Primary Sources", color: "#34d399", meaning: "Academic papers, government records, court filings — highest trust" },
      { label: "Class B — Credentialed Media", color: "#38bdf8", meaning: "Reuters, BBC, major newspapers — bias-adjusted but credentialed" },
      { label: "Class C — Volatile/Captured", color: "#fbbf24", meaning: "High-lean outlets — usable but flagged" },
      { label: "Class D — Propagation Nodes", color: "#f43f5e", meaning: "Social media, anonymous platforms — presence raises suspicion, not trust" },
    ],
  },
  ilo: {
    title: "What is an ILO?",
    plain: "An Information Layering Operation — a coordinated campaign to manufacture, amplify, or suppress a narrative.",
    detail: "ILOs are distinguished from organic misinformation by their physics signature: they leave traces in how long a story persists (Π), how it spreads geographically (Γ), and what kind of sources carry it. An organic lie fades naturally. An ILO fights the physics.",
    ranges: [],
  },
  pps: {
    title: "Principle of Persistent Structurization (PPS)",
    plain: "Real information structures adapt and persist naturally. Fake ones need artificial support.",
    detail: "PPS is a proposed extension of thermodynamic law: persistent flow structures (including information) must continuously adapt to survive. A natural story builds diverse sourcing, diffuses geographically, and persists at a predictable rate. An engineered narrative cannot do this — it requires continuous artificial support, which leaves measurable signatures.",
    ranges: [],
  },
  signature: {
    title: "Campaign Signature Match",
    plain: "Does this story's physics fingerprint match any known disinformation campaign pattern?",
    detail: "The system compares the story's 8-dimensional physics vector (Π, Γ, source entropy, complexity, Class D mass, etc.) against a library of known campaign signatures using cosine similarity. A strong match means the story's structure closely resembles a documented operation.",
    ranges: [
      { label: "≥ 0.97 similarity", color: "#f43f5e", meaning: "Strong match — same campaign family" },
      { label: "0.90 – 0.97", color: "#fb923c", meaning: "Probable match — similar mechanics" },
      { label: "0.80 – 0.90", color: "#fbbf24", meaning: "Partial match — shared structural patterns" },
      { label: "< 0.80", color: "#34d399", meaning: "No match — structurally distinct from known campaigns" },
    ],
  },
};

// ── Style helpers ─────────────────────────────────────────────────────────────

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
  organic:    { text: "text-emerald-400", label: "ORGANIC DECAY",             plain: "Fading naturally" },
  ilo_fade:   { text: "text-rose-400",    label: "ILO FADE ⚠",               plain: "Collapsed unnaturally fast" },
  maintained: { text: "text-amber-400",   label: "ARTIFICIAL MAINTENANCE ⚠", plain: "Being kept alive artificially" },
  no_data:    { text: "text-slate-500",   label: "NO DATA",                   plain: "Insufficient data" },
}[c] || { text: "text-slate-500", label: "UNKNOWN", plain: "Unknown" });

const VELOCITY_STYLE = (v) => ({
  organic:          { text: "text-emerald-400", label: "ORGANIC DIFFUSION",  plain: "Spread naturally" },
  fast_injection:   { text: "text-rose-400",    label: "FAST INJECTION ⚠",  plain: "Appeared everywhere at once" },
  slow_suppression: { text: "text-amber-400",   label: "SUPPRESSION SIGNAL ⚠", plain: "Contained — failed to spread" },
}[v] || { text: "text-slate-500", label: "UNKNOWN", plain: "Unknown" });

const QUADRANT_COLOR = (q = "") => {
  if (q.includes("I —"))  return "text-rose-400";
  if (q.includes("II"))   return "text-orange-400";
  if (q.includes("III"))  return "text-amber-400";
  if (q.includes("IV"))   return "text-sky-400";
  return "text-emerald-400";
};

const MATCH_TIER_STYLE = (tier) => ({
  strong:   { color: "#f43f5e", label: "STRONG MATCH" },
  probable: { color: "#fb923c", label: "PROBABLE MATCH" },
  partial:  { color: "#fbbf24", label: "PARTIAL MATCH" },
  none:     { color: "#475569", label: "NO MATCH" },
}[tier] || { color: "#475569", label: "UNKNOWN" });

// ── Info Popup ────────────────────────────────────────────────────────────────

function InfoPopup({ infoKey, children }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const info = INFO[infoKey];
  if (!info) return children;

  useEffect(() => {
    if (!open) return;
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  return (
    <span className="relative inline-flex items-center gap-1" ref={ref}>
      {children}
      <button
        onClick={() => setOpen(!open)}
        className="inline-flex items-center justify-center w-3.5 h-3.5 rounded-full border border-slate-600 text-slate-500 hover:border-teal-500 hover:text-teal-400 transition-colors cursor-pointer text-[8px] font-bold leading-none flex-shrink-0"
        aria-label={`Info: ${info.title}`}
      >?</button>
      {open && (
        <div className="absolute z-50 left-0 top-6 w-72 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl p-4 space-y-3"
             style={{ boxShadow: "0 0 30px #00000088" }}>
          <div className="flex justify-between items-start gap-2">
            <span className="text-[11px] font-bold text-teal-400 uppercase tracking-wider">{info.title}</span>
            <button onClick={() => setOpen(false)} className="text-slate-600 hover:text-slate-400 text-xs cursor-pointer">✕</button>
          </div>
          <p className="text-xs text-slate-200 leading-relaxed font-medium">{info.plain}</p>
          <p className="text-[10px] text-slate-400 leading-relaxed border-t border-slate-800 pt-2">{info.detail}</p>
          {info.formula && (
            <p className="text-[9px] font-mono text-slate-500 bg-slate-950 rounded px-2 py-1">{info.formula}</p>
          )}
          {info.ranges.length > 0 && (
            <div className="space-y-1 border-t border-slate-800 pt-2">
              {info.ranges.map((r, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded flex-shrink-0" style={{ color: r.color, border: `1px solid ${r.color}44`, background: `${r.color}11` }}>{r.label}</span>
                  <span className="text-[9px] text-slate-500 leading-tight pt-0.5">{r.meaning}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </span>
  );
}

// ── Metric bar with info ──────────────────────────────────────────────────────

function PiBar({ value = 0 }) {
  const v = Number(value) || 0;
  const color =
    v >= 0.70 && v <= 1.40 ? "#34d399" :
    v < 0.35               ? "#f43f5e" :
    v > 2.50               ? "#fbbf24" :
    v < 0.70               ? "#fb923c" : "#22d3ee";
  const pct = Math.min((Math.min(v, 3) / 3) * 100, 100);
  const plainLabel = v >= 0.70 && v <= 1.40 ? "Normal lifespan" : v < 0.35 ? "Vanished unnaturally fast" : v > 2.50 ? "Being kept alive" : v < 0.70 ? "Fading faster than expected" : "Persisting longer than expected";

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-end">
        <InfoPopup infoKey="pi">
          <span className="text-[10px] uppercase tracking-widest text-slate-500">Persistence Ratio Π</span>
        </InfoPopup>
        <div className="text-right">
          <span className="font-black text-xl tabular-nums" style={{ color }}>{v.toFixed(4)}</span>
          <span className="block text-[9px] text-slate-500">{plainLabel}</span>
        </div>
      </div>
      <div className="relative h-2 bg-slate-800 rounded overflow-hidden">
        <div className="absolute h-full bg-emerald-900/40 rounded"
             style={{ left: `${(0.70/3)*100}%`, width: `${((1.40-0.70)/3)*100}%` }} />
        <div className="absolute h-full rounded transition-all duration-700"
             style={{ width: `${pct}%`, background: color, boxShadow: `0 0 10px ${color}88` }} />
      </div>
      <div className="flex justify-between text-[9px] text-slate-700 uppercase tracking-wider">
        <span>Vanished fast</span>
        <span className="text-emerald-800">Normal zone</span>
        <span>Kept alive</span>
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
  const plainLabel = v >= 0.70 && v <= 1.40 ? "Spread naturally" : v > 1.40 ? "Appeared everywhere at once" : "Geographically suppressed";

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-end">
        <InfoPopup infoKey="gamma">
          <span className="text-[10px] uppercase tracking-widest text-slate-500">Geographic Spread Γ</span>
        </InfoPopup>
        <div className="text-right">
          <span className="font-black text-xl tabular-nums" style={{ color }}>{v.toFixed(4)}</span>
          <span className="block text-[9px] text-slate-500">{plainLabel}</span>
        </div>
      </div>
      <div className="relative h-2 bg-slate-800 rounded overflow-hidden">
        <div className="absolute h-full bg-emerald-900/40 rounded"
             style={{ left: `${(0.70/3)*100}%`, width: `${((1.40-0.70)/3)*100}%` }} />
        <div className="absolute h-full rounded transition-all duration-700"
             style={{ width: `${pct}%`, background: color, boxShadow: `0 0 10px ${color}88` }} />
      </div>
      <div className="flex justify-between text-[9px] text-slate-700 uppercase tracking-wider">
        <span>Suppressed</span>
        <span className="text-emerald-800">Normal zone</span>
        <span>Coordinated injection</span>
      </div>
    </div>
  );
}

// ── Π/Γ Coordinate Plot ───────────────────────────────────────────────────────

function CoordinatePlot({ pi = 0, gamma = 0 }) {
  const piV  = Math.min(Number(pi)    || 0, 4);
  const gamV = Math.min(Number(gamma) || 0, 4);

  // Map to SVG space: 0→4 maps to padding→(size-padding)
  const SIZE = 200;
  const PAD  = 28;
  const PLOT = SIZE - PAD * 2;

  const toX = (g) => PAD + (Math.min(g, 4) / 4) * PLOT;
  const toY = (p) => SIZE - PAD - (Math.min(p, 4) / 4) * PLOT;

  const dotX = toX(gamV);
  const dotY = toY(piV);

  // Organic zone boundaries
  const ox1 = toX(0.70); const ox2 = toX(1.40);
  const oy2 = toY(0.70); const oy1 = toY(1.40);

  const quadrantColor = (p, g) => {
    if (p > 1.40 && g > 1.40) return "#f43f5e22";
    if (p > 1.40 && g < 0.70) return "#fb923c22";
    if (p < 0.70 && g > 1.40) return "#fbbf2422";
    if (p < 0.70 && g < 0.70) return "#38bdf822";
    return "transparent";
  };

  const dotColor =
    piV >= 0.70 && piV <= 1.40 && gamV >= 0.70 && gamV <= 1.40 ? "#34d399" :
    piV > 1.40 && gamV > 1.40 ? "#f43f5e" :
    piV > 1.40 && gamV < 0.70 ? "#fb923c" :
    piV < 0.70 && gamV > 1.40 ? "#fbbf24" :
    piV < 0.70 && gamV < 0.70 ? "#38bdf8" : "#94a3b8";

  return (
    <div className="space-y-2">
      <InfoPopup infoKey="quadrant">
        <span className="text-[10px] uppercase tracking-widest text-slate-500">Π/Γ Diagnostic Space</span>
      </InfoPopup>
      <svg width={SIZE} height={SIZE} className="w-full max-w-[220px] mx-auto block">
        {/* Quadrant fills */}
        <rect x={PAD}   y={PAD}   width={ox1-PAD}      height={oy1-PAD}       fill="#fb923c11" />
        <rect x={ox2}   y={PAD}   width={SIZE-PAD-ox2} height={oy1-PAD}       fill="#f43f5e11" />
        <rect x={PAD}   y={oy2}   width={ox1-PAD}      height={SIZE-PAD-oy2}  fill="#38bdf811" />
        <rect x={ox2}   y={oy2}   width={SIZE-PAD-ox2} height={SIZE-PAD-oy2}  fill="#fbbf2411" />
        {/* Organic zone */}
        <rect x={ox1} y={oy1} width={ox2-ox1} height={oy2-oy1} fill="#34d39914" stroke="#34d39930" strokeWidth="0.5" />
        {/* Grid lines */}
        <line x1={ox1} y1={PAD} x2={ox1} y2={SIZE-PAD} stroke="#1e293b" strokeWidth="0.5" />
        <line x1={ox2} y1={PAD} x2={ox2} y2={SIZE-PAD} stroke="#1e293b" strokeWidth="0.5" />
        <line x1={PAD} y1={oy1} x2={SIZE-PAD} y2={oy1} stroke="#1e293b" strokeWidth="0.5" />
        <line x1={PAD} y1={oy2} x2={SIZE-PAD} y2={oy2} stroke="#1e293b" strokeWidth="0.5" />
        {/* Axes */}
        <line x1={PAD} y1={SIZE-PAD} x2={SIZE-PAD} y2={SIZE-PAD} stroke="#334155" strokeWidth="0.8" />
        <line x1={PAD} y1={PAD}      x2={PAD}      y2={SIZE-PAD} stroke="#334155" strokeWidth="0.8" />
        {/* Axis labels */}
        <text x={SIZE/2} y={SIZE-4} textAnchor="middle" fill="#475569" fontSize="8" fontFamily="monospace">Γ (geographic spread)</text>
        <text x={10} y={SIZE/2} textAnchor="middle" fill="#475569" fontSize="8" fontFamily="monospace" transform={`rotate(-90, 10, ${SIZE/2})`}>Π (lifespan)</text>
        {/* Quadrant labels */}
        <text x={PAD+4}   y={PAD+10}   fill="#fb923c" fontSize="7" fontFamily="monospace" opacity="0.6">II</text>
        <text x={SIZE-PAD-12} y={PAD+10} fill="#f43f5e" fontSize="7" fontFamily="monospace" opacity="0.6">I</text>
        <text x={PAD+4}   y={SIZE-PAD-6} fill="#38bdf8" fontSize="7" fontFamily="monospace" opacity="0.6">IV</text>
        <text x={SIZE-PAD-14} y={SIZE-PAD-6} fill="#fbbf24" fontSize="7" fontFamily="monospace" opacity="0.6">III</text>
        {/* Organic label */}
        <text x={(ox1+ox2)/2} y={(oy1+oy2)/2+3} textAnchor="middle" fill="#34d399" fontSize="6" fontFamily="monospace" opacity="0.7">organic</text>
        {/* Current point */}
        <circle cx={dotX} cy={dotY} r="5" fill={dotColor} opacity="0.25" />
        <circle cx={dotX} cy={dotY} r="3" fill={dotColor} />
        <circle cx={dotX} cy={dotY} r="3" fill="none" stroke={dotColor} strokeWidth="1.5" opacity="0.6" />
      </svg>
    </div>
  );
}

// ── Quadrant grid ─────────────────────────────────────────────────────────────

function QuadrantGrid({ pi = 0, gamma = 0, quadrant = "" }) {
  const piV   = Number(pi)    || 0;
  const gamV  = Number(gamma) || 0;
  const piHigh  = piV  > 1.40; const piLow   = piV  < 0.70;
  const gamHigh = gamV > 1.40; const gamLow  = gamV < 0.70;
  const isOrganic = !piHigh && !piLow && !gamHigh && !gamLow;

  const cells = [
    { label: "I — Confirmed ILO",     plain: "Injected & kept alive",    active: piHigh && gamHigh, color: "#f43f5e" },
    { label: "III — Viral Suppression",plain: "Spread fast, then killed", active: piLow  && gamHigh, color: "#fbbf24" },
    { label: "II — Astroturfed Local", plain: "Manufactured, contained",  active: piHigh && gamLow,  color: "#fb923c" },
    { label: "IV — Suppressed Event",  plain: "Real but buried",          active: piLow  && gamLow,  color: "#38bdf8" },
  ];

  return (
    <div className="space-y-2">
      <div className="grid grid-cols-2 gap-1">
        {cells.map((cell, i) => (
          <div key={i} className="rounded p-2 border text-center transition-all"
               style={{
                 borderColor: cell.active ? cell.color : "#1e293b",
                 background:  cell.active ? `${cell.color}22` : "#0f172a",
                 boxShadow:   cell.active ? `0 0 12px ${cell.color}44` : "none",
               }}>
            <p className="text-[9px] uppercase tracking-wider leading-tight" style={{ color: cell.active ? cell.color : "#475569" }}>{cell.label}</p>
            <p className="text-[8px] mt-0.5" style={{ color: cell.active ? `${cell.color}cc` : "#334155" }}>{cell.plain}</p>
          </div>
        ))}
      </div>
      {isOrganic && (
        <div className="text-center text-[10px] text-emerald-400 font-bold tracking-widest">● ORGANIC — No anomalies detected</div>
      )}
    </div>
  );
}

// ── Metric card ───────────────────────────────────────────────────────────────

function MetricCard({ label, value, detail, plain, accent = "text-teal-400", infoKey }) {
  return (
    <div className="bg-slate-950 p-3 rounded border border-slate-800/60 space-y-1">
      <span className="block text-[10px] uppercase tracking-widest text-slate-500">
        {infoKey ? <InfoPopup infoKey={infoKey}>{label}</InfoPopup> : label}
      </span>
      <span className={`text-sm font-bold ${accent}`}>{value}</span>
      {plain && <p className="text-[10px] text-slate-500 italic">{plain}</p>}
      {detail && <p className="text-xs text-slate-400 leading-relaxed pt-1 border-t border-slate-900 mt-1">{detail}</p>}
    </div>
  );
}

// ── Source class badge ────────────────────────────────────────────────────────

function SourceClassBar({ classA = 0, classD = 0, total = 0 }) {
  const other = Math.max(0, total - classA - classD);
  return (
    <div className="space-y-2">
      <InfoPopup infoKey="sourceClasses">
        <span className="text-[10px] uppercase tracking-widest text-slate-500">Source Breakdown ({total} sources found)</span>
      </InfoPopup>
      <div className="flex gap-2 flex-wrap">
        <span className="text-[10px] px-2 py-1 rounded border border-emerald-500/30 bg-emerald-950/20 text-emerald-400">
          {classA} primary sources
        </span>
        {classD > 0 && (
          <span className="text-[10px] px-2 py-1 rounded border border-rose-500/30 bg-rose-950/20 text-rose-400">
            {classD} propagation nodes ⚠
          </span>
        )}
        {other > 0 && (
          <span className="text-[10px] px-2 py-1 rounded border border-slate-700 text-slate-400">
            {other} media sources
          </span>
        )}
      </div>
      {classA === 0 && (
        <p className="text-[9px] text-rose-500/70">No verified primary sources found — credibility threshold not met</p>
      )}
      {classD > classA && classD > 0 && (
        <p className="text-[9px] text-amber-500/70">More propagation nodes than primary sources — ILO distribution signature</p>
      )}
    </div>
  );
}

// ── Signature match panel ─────────────────────────────────────────────────────

function SignaturePanel({ signatureResult }) {
  if (!signatureResult) return (
    <div className="text-slate-600 text-[10px] text-center py-4">No signature data available.</div>
  );

  const { matches = [], best_match, best_similarity, campaign_family, library_interpretation } = signatureResult;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <InfoPopup infoKey="signature">
          <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Campaign Signature Match</span>
        </InfoPopup>
        {best_match && (
          <span className="text-[9px] font-bold px-2 py-0.5 rounded"
                style={{ color: MATCH_TIER_STYLE(best_match.match_tier).color, border: `1px solid ${MATCH_TIER_STYLE(best_match.match_tier).color}44`, background: `${MATCH_TIER_STYLE(best_match.match_tier).color}11` }}>
            {MATCH_TIER_STYLE(best_match.match_tier).label}
          </span>
        )}
      </div>

      {best_match ? (
        <>
          <div className="bg-slate-950 border border-slate-800 rounded p-3 space-y-2">
            <div className="flex justify-between items-start gap-2">
              <div>
                <p className="text-xs font-bold text-slate-200">{best_match.campaign_type}</p>
                <p className="text-[9px] text-slate-500">{best_match.benchmark_id} · sim = {best_match.similarity.toFixed(4)}</p>
              </div>
              <span className="text-[9px] text-slate-600 flex-shrink-0">{best_match.quadrant}</span>
            </div>
            <p className="text-[10px] text-slate-400 leading-relaxed border-l-2 border-teal-500/20 pl-2">{best_match.description}</p>
          </div>

          {matches.length > 1 && (
            <div className="space-y-1">
              <span className="text-[9px] uppercase tracking-widest text-slate-700">Other matches</span>
              {matches.slice(1).map((m, i) => (
                <div key={i} className="flex justify-between items-center bg-slate-950 rounded px-2 py-1.5 text-[9px]">
                  <span className="text-slate-500 truncate mr-2">{m.campaign_type}</span>
                  <span className="font-bold flex-shrink-0" style={{ color: MATCH_TIER_STYLE(m.match_tier).color }}>{m.similarity.toFixed(4)}</span>
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <div className="bg-slate-950 border border-slate-800 rounded p-3">
          <p className="text-[10px] text-emerald-400 font-bold">No known campaign match</p>
          <p className="text-[9px] text-slate-500 mt-1">Physics signature is structurally distinct from all known ILO archetypes. This is either an organic signal or a novel campaign pattern not yet in the library.</p>
        </div>
      )}

      <p className="text-[9px] text-slate-600 leading-relaxed border-t border-slate-800 pt-2">{library_interpretation}</p>
    </div>
  );
}

// ── Physics panel ─────────────────────────────────────────────────────────────

function PhysicsPanel({ pi_diag, gamma_diag, signatureResult }) {
  if (!pi_diag) return (
    <div className="text-slate-600 text-[10px] text-center py-8">No physics data available.</div>
  );

  const saddle      = SADDLE_STYLE(pi_diag.saddle_point?.classification);
  const scopeDist   = gamma_diag?.scope_distribution ?? {};
  const velocity    = VELOCITY_STYLE(gamma_diag?.diffusion_velocity);
  const scopeEntries = Object.entries(scopeDist);
  const scopeRankLabel = ["local","national","international","global"][gamma_diag?.max_scope_rank ?? 1] ?? "unknown";

  return (
    <div className="space-y-4">

      {/* Π block */}
      <div className="border border-slate-700/50 rounded bg-slate-950 p-4 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
          <div className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
          <InfoPopup infoKey="pi">
            <span className="text-[10px] uppercase tracking-widest text-teal-400 font-bold">Persistence Ratio (Π) — How long has this story lived?</span>
          </InfoPopup>
        </div>
        <PiBar value={pi_diag.pi_final} />
        <p className="text-[10px] text-slate-400 leading-relaxed border-l-2 border-teal-500/30 pl-3">
          {pi_diag.pi_interpretation || ""}
        </p>
        <div className="grid grid-cols-2 gap-2 text-[10px]">
          {[
            ["Time observed",     `${pi_diag.tau_observed_days ?? 0}d`,          "Days the story has been indexed online"],
            ["Time predicted",    `${pi_diag.tau_predicted_days ?? 0}d`,          "Days it should last given its complexity"],
            ["Source entropy (S)", (pi_diag.S ?? 0).toFixed(4),                   "Diversity of sources citing this story"],
            ["System complexity",  (pi_diag.E ?? 0).toFixed(4),                   "Total trust-weighted source weight"],
          ].map(([label, val, tip]) => (
            <div key={label} className="flex justify-between bg-slate-900 rounded px-2 py-1.5 group relative">
              <span className="text-slate-600 uppercase tracking-wider">{label}</span>
              <span className="text-slate-300 font-bold tabular-nums">{val}</span>
            </div>
          ))}
        </div>
        {pi_diag.saddle_point && (
          <div className="border border-slate-800 rounded p-3 space-y-1.5">
            <div className="flex justify-between items-center">
              <InfoPopup infoKey="saddle">
                <span className="text-[9px] uppercase tracking-widest text-slate-600">Decay Pattern vs. Weather Baseline</span>
              </InfoPopup>
              <div className="text-right">
                <span className={`text-[10px] font-bold ${saddle.text}`}>{saddle.label}</span>
                <span className={`block text-[9px] ${saddle.text} opacity-60`}>{saddle.plain}</span>
              </div>
            </div>
            {pi_diag.saddle_point.delta != null && (
              <div className="flex gap-4 text-[9px] text-slate-600 flex-wrap">
                <span>λ observed = {(pi_diag.saddle_point.lambda_observed ?? 0).toFixed(4)}/day</span>
                <span>λ weather = {(pi_diag.saddle_point.lambda_weather ?? 0).toFixed(4)}/day</span>
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
            <InfoPopup infoKey="gamma">
              <span className="text-[10px] uppercase tracking-widest text-purple-400 font-bold">Geographic Spread (Γ) — How did it diffuse?</span>
            </InfoPopup>
          </div>
          <GammaBar value={gamma_diag.gamma} />
          <p className="text-[10px] text-slate-400 leading-relaxed border-l-2 border-purple-500/30 pl-3">
            {gamma_diag.gamma_interpretation || ""}
          </p>
          <div className="grid grid-cols-2 gap-2 text-[10px]">
            {[
              ["Geographic entropy",  (gamma_diag.h_geographic ?? 0).toFixed(4)],
              ["Expected entropy",    (gamma_diag.h_expected   ?? 0).toFixed(4)],
              ["Highest scope seen",  scopeRankLabel],
            ].map(([label, val]) => (
              <div key={label} className="flex justify-between bg-slate-900 rounded px-2 py-1.5">
                <span className="text-slate-600 uppercase tracking-wider">{label}</span>
                <span className="text-slate-300 font-bold tabular-nums">{val}</span>
              </div>
            ))}
            <div className="flex justify-between bg-slate-900 rounded px-2 py-1.5">
              <span className="text-slate-600 uppercase tracking-wider">Spread pattern</span>
              <div className="text-right">
                <span className={`font-bold text-[10px] ${velocity.text}`}>{velocity.plain}</span>
              </div>
            </div>
          </div>

          {scopeEntries.length > 0 && (
            <div className="border border-slate-800 rounded p-3 space-y-2">
              <span className="text-[9px] uppercase tracking-widest text-slate-600">Sources by geographic scope</span>
              <div className="flex gap-2 flex-wrap">
                {scopeEntries.map(([scope, count]) => (
                  <span key={scope} className="text-[9px] px-2 py-0.5 rounded border border-slate-700 text-slate-400">
                    {scope}: {count}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <CoordinatePlot pi={pi_diag.pi_final} gamma={gamma_diag.gamma} />
            <QuadrantGrid pi={pi_diag.pi_final} gamma={gamma_diag.gamma} quadrant={gamma_diag.quadrant || ""} />
          </div>
        </div>
      )}

      {/* Signature library */}
      {signatureResult && (
        <div className="border border-slate-700/50 rounded bg-slate-950 p-4 space-y-3">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            <span className="text-[10px] uppercase tracking-widest text-amber-400 font-bold">Known Campaign Pattern Match</span>
          </div>
          <SignaturePanel signatureResult={signatureResult} />
        </div>
      )}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function ILOAnalyzerConsole() {
  const [claim, setClaim]               = useState("");
  const [loading, setLoading]           = useState(false);
  const [phaseIndex, setPhaseIndex]     = useState(0);
  const [runningPi, setRunningPi]       = useState(null);
  const [verdict, setVerdict]           = useState(null);
  const [error, setError]               = useState(null);
  const [tab, setTab]                   = useState("verdict");
  const [reportLoading, setReportLoading] = useState(false);
  const [report, setReport]             = useState(null);
  const [reportError, setReportError]   = useState(null);
  const [showTechLabels, setShowTechLabels] = useState(false);
  const [showSources, setShowSources]   = useState(true);
  const phaseTimer                      = useRef(null);

  const generateReport = async () => {
    if (!claim.trim() || reportLoading) return;
    setReportLoading(true);
    setReportError(null);
    setReport(null);
    setTab("report");
    try {
      const res = await fetch(`${API_BASE}/report`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ claim, fetch_cdx: true }),
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      setReport(await res.json());
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
    a.href = url; a.download = `ilo-report-${Date.now()}.md`; a.click();
    URL.revokeObjectURL(url);
  };

  const simulatePhases = () => {
    let idx = 0;
    setPhaseIndex(0); setRunningPi(null);
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
    setLoading(true); setError(null); setVerdict(null); setTab("verdict");
    simulatePhases();
    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ claim, fetch_cdx: true }),
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
      setLoading(false); setPhaseIndex(0);
    }
  };

  const vs = VERDICT_STYLE(verdict?.verdict || "");

  // Plain-language verdicts
  const verdictPlain = (v = "") => {
    const vl = v.toLowerCase();
    if (vl.includes("clean"))       return "This appears to be a legitimate story with no significant anomalies.";
    if (vl.includes("confirmed"))   return "Strong physics evidence of a coordinated disinformation operation.";
    if (vl.includes("probable"))    return "Multiple indicators suggest this story is not organic.";
    if (vl.includes("likely"))      return "Several anomalies are consistent with a coordinated operation.";
    if (vl.includes("suppression")) return "Evidence suggests a real story is being artificially suppressed.";
    if (vl.includes("anomalous"))   return "Unusual patterns detected — does not fit organic or known ILO profiles.";
    if (vl.includes("insufficient"))return "Not enough data to reach a confident conclusion.";
    return "";
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-mono p-4 md:p-6 selection:bg-teal-500 selection:text-slate-950">
      <header className="border-b border-slate-800 pb-4 mb-6">
        <div className="flex justify-between items-start flex-wrap gap-3">
          <div>
            <h1 className="text-lg md:text-xl font-bold tracking-wider text-teal-400">
              CHRONODYNE SYSTEMS // ILO ANALYZER
            </h1>
            <p className="text-[11px] text-slate-500 mt-1">
              v4.3.0 · Physics-grounded disinformation detection
            </p>
          </div>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <span className="text-[9px] uppercase tracking-wider text-slate-600">Technical labels</span>
              <div className={`w-8 h-4 rounded-full transition-colors relative ${showTechLabels ? "bg-teal-600" : "bg-slate-700"}`}
                   onClick={() => setShowTechLabels(!showTechLabels)}>
                <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-slate-300 transition-transform ${showTechLabels ? "translate-x-4" : "translate-x-0.5"}`} />
              </div>
            </label>
            <span className="text-[10px] px-2.5 py-1 rounded border border-teal-500/30 bg-teal-950/20 text-teal-400 tracking-wider">
              P4 GATE ACTIVE
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-6">

        {/* Left: Input */}
        <section className="lg:col-span-1 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded p-5 shadow-xl">
            <h2 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-1">
              Claim Analysis
            </h2>
            <p className="text-[10px] text-slate-600 mb-4">Enter any news claim, rumor, or narrative to analyze.</p>
            <div className="space-y-4">
              <textarea
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter" && e.metaKey) executeAnalysis(); }}
                placeholder={'e.g. "The government is hiding evidence of UFOs in Nevada."'}
                className="w-full h-32 bg-slate-950 border border-slate-800 rounded p-3 text-sm text-slate-200 focus:outline-none focus:border-teal-500/60 transition-colors resize-none placeholder-slate-700"
                disabled={loading}
              />
              <button onClick={executeAnalysis} disabled={loading || !claim.trim()}
                className="w-full bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-bold py-2.5 px-4 rounded text-[11px] uppercase tracking-widest transition-colors cursor-pointer">
                {loading ? "Analyzing..." : "Analyze Claim"}
              </button>
              <button onClick={generateReport} disabled={reportLoading || !claim.trim()}
                className="w-full bg-purple-800 hover:bg-purple-700 disabled:bg-slate-800 disabled:text-slate-600 text-slate-100 font-bold py-2.5 px-4 rounded text-[11px] uppercase tracking-widest transition-colors cursor-pointer">
                {reportLoading ? "Generating Report..." : "Generate Full Report"}
              </button>
              <p className="text-[9px] text-slate-700 text-right">⌘+Enter to analyze</p>
            </div>
          </div>

          {/* What this does */}
          <div className="bg-slate-900/40 border border-slate-800/50 rounded p-4 space-y-3">
            <InfoPopup infoKey="ilo">
              <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">How This Works</span>
            </InfoPopup>
            <div className="space-y-2 text-[10px] text-slate-500">
              <div>The system searches 17 sources across 5 phases, then measures two physics signals:</div>
              <div className="space-y-1.5 pl-2 border-l border-slate-800">
                <div><span className="text-teal-400 font-bold">Π</span>{" — How long has the story lived vs. how long it should?"}</div>
                <div><span className="text-purple-400 font-bold">Γ</span>{" — Did it spread like real news, or appear everywhere at once?"}</div>
              </div>
              <div>{"The "}<InfoPopup infoKey="pps"><span className="text-slate-400">physics engine</span></InfoPopup>{" is grounded in thermodynamic law, not opinion."}</div>
            </div>
          </div>

          {loading && (
            <div className="bg-slate-900/50 border border-teal-500/20 rounded p-4 space-y-3">
              <div className="text-teal-400 font-bold uppercase tracking-widest text-[10px] flex items-center gap-2">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
                Live Analysis
              </div>
              <div className="space-y-2">
                {PHASES.map((p, i) => (
                  <div key={i} className={`flex items-start gap-2 text-[10px] transition-colors ${i <= phaseIndex ? "text-slate-300" : "text-slate-700"}`}>
                    <span className={`mt-0.5 w-1 h-1 rounded-full flex-shrink-0 ${i < phaseIndex ? "bg-teal-500" : i === phaseIndex ? "bg-teal-400 animate-pulse" : "bg-slate-700"}`} />
                    {showTechLabels ? p.label : p.plain}
                  </div>
                ))}
              </div>
              {runningPi !== null && (
                <div className="border-t border-slate-800 pt-3">
                  <div className="flex justify-between text-[9px] text-slate-600 mb-1">
                    <span>Persistence estimate (Π)</span>
                    <span className="text-teal-500">{runningPi.toFixed(3)}</span>
                  </div>
                  <div className="h-1 bg-slate-800 rounded overflow-hidden">
                    <div className="h-full bg-teal-500/60 rounded animate-pulse" style={{ width: `${Math.min(runningPi * 33, 100)}%` }} />
                  </div>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="bg-red-950/20 border border-red-500/30 rounded p-4 text-[11px] text-red-400">
              <span className="font-bold">Analysis failed</span>
              <p className="mt-1 text-red-500/70">{error}</p>
            </div>
          )}
        </section>

        {/* Right: Results */}
        <section className="lg:col-span-2 xl:col-span-2">
          {verdict ? (
            <div className="space-y-4">

              {/* Verdict header */}
              <div className={`border ${vs.border} ${vs.bg} p-5 rounded`} style={{ boxShadow: `0 0 24px ${vs.glow}` }}>
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div className="flex-1">
                    <span className={`text-[10px] uppercase font-bold tracking-widest opacity-60 ${vs.text}`}>
                      {showTechLabels ? "Diagnostic Decision" : "Verdict"}
                    </span>
                    <h3 className={`text-xl font-black uppercase tracking-tight mt-0.5 ${vs.text}`}>
                      {verdict.verdict}
                    </h3>
                    <p className="text-sm text-slate-300 mt-1 font-medium leading-snug">
                      {verdictPlain(verdict.verdict)}
                    </p>
                    <p className="text-xs text-slate-400 mt-1.5 max-w-md leading-relaxed">
                      {verdict.verdict_summary}
                    </p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className={`text-[10px] uppercase font-bold tracking-widest opacity-60 ${vs.text}`}>
                      {showTechLabels ? "ILO Probability" : "Manipulation likelihood"}
                    </span>
                    <p className={`text-4xl font-black mt-0.5 ${vs.text}`}>
                      {verdict.ilo_probability}<span className="text-lg opacity-50">%</span>
                    </p>
                  </div>
                </div>
              </div>

              {/* Quick signal bar */}
              <div className="bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
                <PiBar value={verdict.pi_diagnostics?.pi_final ?? 0} />
                <GammaBar value={verdict.gamma_diagnostics?.gamma ?? 0} />
              </div>

              {/* WTF factor */}
              {verdict.wtf_factor && !verdict.wtf_factor.toLowerCase().includes("no significant") && (
                <div className="bg-slate-900/50 border border-rose-500/20 border-l-2 border-l-rose-500 rounded p-4">
                  <span className="block text-[10px] uppercase tracking-widest text-rose-500 mb-1.5">⚡ Key Anomaly</span>
                  <p className="text-xs text-slate-300 leading-relaxed">{verdict.wtf_factor}</p>
                </div>
              )}

              {/* Source breakdown */}
              <div className="bg-slate-900 border border-slate-800 rounded p-4">
                <SourceClassBar
                  classA={verdict.pi_diagnostics?.class_a_count ?? 0}
                  classD={verdict.pi_diagnostics?.class_d_count ?? 0}
                  total={verdict.pi_diagnostics?.node_count ?? 0}
                />
              </div>

              {/* Tabs */}
              <div className="flex border-b border-slate-800">
                {["verdict", "physics", "report"].map((t) => (
                  <button key={t} onClick={() => setTab(t)}
                    className={`px-4 py-2 text-[10px] uppercase tracking-widest transition-colors cursor-pointer ${
                      tab === t ? "text-teal-400 border-b-2 border-teal-400 -mb-px" : "text-slate-600 hover:text-slate-400"
                    }`}>
                    {t === "verdict" ? "Summary" : t === "physics" ? "Physics Deep Dive" : "Full Report"}
                  </button>
                ))}
              </div>

              {/* Verdict tab */}
              {tab === "verdict" && (
                <div className="space-y-4">
                  <div className="bg-slate-900 border border-slate-800 rounded p-5 space-y-4">
                    {/* Quadrant */}
                    {verdict.gamma_diagnostics?.quadrant && (
                      <div>
                        <InfoPopup infoKey="quadrant">
                          <span className="text-[10px] uppercase tracking-widest text-slate-500">Where it lands</span>
                        </InfoPopup>
                        <div className={`text-sm font-bold mt-1 ${QUADRANT_COLOR(verdict.gamma_diagnostics.quadrant)}`}>
                          {verdict.gamma_diagnostics.quadrant}
                        </div>
                      </div>
                    )}

                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest border-b border-slate-800 pb-2">
                      Signal Assessment
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <MetricCard
                        label={showTechLabels ? "Wildness Profile" : "How extraordinary is this claim?"}
                        value={`Tier ${verdict.wildness_tier} — ${verdict.wildness_label}`}
                        plain={showTechLabels ? null : ["", "Ambiguous claim", "Unusual — needs strong evidence", "Manipulation indicators present", "Extreme claim, high burden of proof", "Extraordinary claim"][verdict.wildness_tier] || ""}
                        detail={verdict.wildness_justification}
                        accent={WILDNESS_COLOR(verdict.wildness_tier)}
                        infoKey="wildness"
                      />
                      <MetricCard
                        label={showTechLabels ? "Thermodynamic Trend" : "Is this story structurizing or dissolving?"}
                        value={verdict.pps_assessment}
                        plain={showTechLabels ? null : { "Structurizing": "Growing stronger and more organized", "Entropifying": "Breaking down naturally", "Hard Cutoff Detected": "Stopped abruptly — suspicious", "Unknown": "Cannot determine" }[verdict.pps_assessment] || ""}
                        detail={verdict.pps_justification}
                        infoKey="pps"
                      />
                      <MetricCard
                        label={showTechLabels ? "Signal Pattern" : "What type of signal is this?"}
                        value={verdict.signal_pattern}
                        plain={showTechLabels ? null : {
                          "True Signal": "Looks like real news",
                          "ILO Laundered": "Appears to have been injected via legitimate-looking sources",
                          "Narrative Spent": "Once active campaign, now fading",
                          "Suppressed Real Event": "Real event being buried",
                          "Anomalous Pattern": "Doesn't fit known patterns",
                          "Insufficient Data": "Not enough data",
                        }[verdict.signal_pattern] || ""}
                        detail={verdict.signal_justification}
                        accent="text-slate-200"
                      />
                      <MetricCard
                        label={showTechLabels ? "Local Credibility" : "Any verified primary sources?"}
                        value={verdict.local_credibility}
                        plain={showTechLabels ? null : verdict.local_credibility?.includes("Not Met") ? "No verified primary sources found" : "At least one verified primary source exists"}
                        detail={verdict.local_credibility_justification}
                        accent={verdict.local_credibility?.toLowerCase().includes("met") && !verdict.local_credibility?.toLowerCase().includes("not") ? "text-emerald-400" : "text-rose-400"}
                        infoKey="sourceClasses"
                      />
                      <MetricCard
                        label={showTechLabels ? "Admissibility Bound" : "Does the evidence stay within physics limits?"}
                        value={verdict.admissibility_bound}
                        plain={showTechLabels ? null : { "Within Bound": "Evidence is internally consistent", "Bound Violated": "Evidence contradicts physics prediction", "Approaching Limit": "Nearing anomalous territory" }[verdict.admissibility_bound] || ""}
                        detail={verdict.admissibility_justification}
                      />
                      <MetricCard
                        label={showTechLabels ? "Vanish Pattern" : "How is this story ending?"}
                        value={verdict.vanish_pattern}
                        plain={showTechLabels ? null : {
                          "Natural Taper": "Fading organically",
                          "ILO Fade": "Collapsed unnaturally — possibly suppressed",
                          "Hard Cutoff": "Stopped abruptly",
                          "Still Active": "Still circulating",
                          "Unknown": "Cannot determine",
                        }[verdict.vanish_pattern] || ""}
                        detail={verdict.vanish_justification}
                        accent="text-slate-300"
                        infoKey="saddle"
                      />
                    </div>

                    {verdict.source_analysis && (
                      <div className="border-t border-slate-800 pt-4 space-y-3">
                        <h5 className="text-[10px] uppercase tracking-widest text-slate-500">Source Profile</h5>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[10px]">
                          {[
                            ["Source variety",   verdict.source_analysis.source_diversity],
                            ["Coverage trend",   verdict.source_analysis.coverage_trajectory],
                            ["Earliest signal",  verdict.source_analysis.earliest_source_found],
                            ["Grassroots signs", verdict.source_analysis.grassroots_signals],
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
                        <span className="block text-[10px] uppercase tracking-widest text-slate-600 mb-2">What would confirm or deny this</span>
                        <p className="text-xs text-slate-400 leading-relaxed">{verdict.what_would_confirm}</p>
                      </div>
                    )}
                  </div>

                  {verdict.anomalous_patterns?.length > 0 && (
                    <div className="bg-slate-900/50 border border-amber-500/20 rounded p-4">
                      <span className="block text-[10px] uppercase tracking-widest text-amber-500 mb-2">Anomalous Patterns Detected</span>
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
                  signatureResult={verdict.signature_result ?? null}
                />
              )}

              {/* Report tab */}
              {tab === "report" && (
                <div className="space-y-4">
                  {reportLoading && (
                    <div className="border border-purple-500/20 bg-purple-950/10 rounded p-6 text-center space-y-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse mx-auto" />
                      <p className="text-[10px] uppercase tracking-widest text-purple-400">Generating analyst report...</p>
                      <p className="text-[9px] text-slate-600">Pattern hypothesis generation · Investigative guidance · Campaign classification</p>
                    </div>
                  )}
                  {reportError && (
                    <div className="bg-red-950/20 border border-red-500/30 rounded p-4 text-[11px] text-red-400">
                      <span className="font-bold">Report generation failed</span>
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
                            <span className="text-slate-600 uppercase tracking-wider">Who likely did this: </span>{report.analyst.actor_profile}
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
                                <span className="text-[9px] text-purple-400 font-bold flex-shrink-0">{((h.confidence ?? 0) * 100).toFixed(0)}% confident</span>
                              </div>
                              <p className="text-[9px] text-emerald-600">↑ Supported by: {h.supporting_evidence}</p>
                              <p className="text-[9px] text-rose-700">↓ Would be ruled out if: {h.contradicting_evidence}</p>
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
                            <span className="text-[10px] uppercase tracking-widest text-amber-500 font-bold">What to investigate next</span>
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
                          <span className="text-[10px] uppercase tracking-widest text-sky-500 font-bold">Related claims worth testing</span>
                          <ul className="space-y-1">
                            {report.analyst.follow_up_claims.map((c, i) => (
                              <li key={i} className="text-[10px] text-slate-400 flex items-start gap-2"><span className="text-sky-600 mt-0.5">›</span>{c}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {report.analyst?.analyst_notes && (
                        <div className="border border-slate-700/50 rounded p-4">
                          <span className="block text-[10px] uppercase tracking-widest text-slate-600 mb-2">Analyst notes</span>
                          <p className="text-[10px] text-slate-400 leading-relaxed">{report.analyst.analyst_notes}</p>
                        </div>
                      )}
                      <button onClick={downloadReport}
                        className="w-full border border-purple-500/30 hover:border-purple-400/60 bg-purple-950/10 hover:bg-purple-950/20 text-purple-400 font-bold py-2.5 px-4 rounded text-[11px] uppercase tracking-widest transition-colors cursor-pointer">
                        Download Full Report (.md)
                      </button>
                    </div>
                  )}
                  {!report && !reportLoading && !reportError && (
                    <div className="text-center py-8 text-slate-600 text-[10px] uppercase tracking-widest">
                      Click "Generate Full Report" to run the complete investigative analysis.
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
              <p className="text-[11px] uppercase tracking-widest">Enter a claim to begin</p>
              <p className="text-[10px] max-w-xs mt-2 opacity-50 leading-relaxed">
                The physics engine will measure persistence, geographic spread, and source structure — then compare against known campaign signatures.
              </p>
            </div>
          )}
        </section>

        {/* Sources sidebar — xl only */}
        <section className="hidden xl:block xl:col-span-1">
          {verdict ? (
            <div className="sticky top-6 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">
                  Source Nodes ({verdict.source_nodes?.length ?? verdict.pi_diagnostics?.node_count ?? 0})
                </span>
                <button
                  onClick={() => setShowSources(!showSources)}
                  className="text-[9px] text-slate-600 hover:text-slate-400 cursor-pointer uppercase tracking-wider"
                >
                  {showSources ? "collapse" : "expand"}
                </button>
              </div>

              {showSources && (
                <div className="space-y-1 max-h-[80vh] overflow-y-auto pr-1">
                  {(verdict.source_nodes ?? []).length > 0 ? (
                    verdict.source_nodes.map((node, i) => {
                      const cls = node.class || "?";
                      const clsColor = {
                        A: { border: "#34d39940", bg: "#34d39908", text: "#34d399", label: "A" },
                        B: { border: "#38bdf840", bg: "#38bdf808", text: "#38bdf8", label: "B" },
                        C: { border: "#fbbf2440", bg: "#fbbf2408", text: "#fbbf24", label: "C" },
                        D: { border: "#f43f5e40", bg: "#f43f5e08", text: "#f43f5e", label: "D" },
                      }[cls] || { border: "#47556940", bg: "#47556908", text: "#475569", label: "?" };

                      const domain = (() => {
                        try { return new URL(node.url).hostname.replace("www.", ""); }
                        catch { return node.url.slice(0, 30); }
                      })();

                      const inverted = node.inverted;
                      const trust = typeof node.trust === "number" ? node.trust.toFixed(2) : "—";
                      const snaps = node.snapshots ?? 0;
                      const tau   = node.tau_days != null ? `${node.tau_days}d` : null;

                      return (
                        <a
                          key={i}
                          href={node.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block rounded border p-2 space-y-1 transition-opacity hover:opacity-80"
                          style={{ borderColor: clsColor.border, background: clsColor.bg }}
                        >
                          <div className="flex items-center justify-between gap-1">
                            <span className="text-[8px] font-bold px-1 rounded flex-shrink-0"
                                  style={{ color: clsColor.text, border: `1px solid ${clsColor.border}` }}>
                              {inverted ? "D⚠" : `Class ${clsColor.label}`}
                            </span>
                            <span className="text-[8px] text-slate-600 tabular-nums">T={trust}</span>
                          </div>
                          <p className="text-[9px] text-slate-400 truncate leading-tight">{domain}</p>
                          {(snaps > 0 || tau) && (
                            <div className="flex gap-2 text-[8px] text-slate-700">
                              {snaps > 0 && <span>{snaps} snapshots</span>}
                              {tau && <span>τ={tau}</span>}
                            </div>
                          )}
                        </a>
                      );
                    })
                  ) : (
                    <div className="text-[9px] text-slate-700 text-center py-4">
                      No node detail data.<br/>Add source_nodes to PPSVerdict.
                    </div>
                  )}
                </div>
              )}

              {/* Class legend */}
              <div className="border border-slate-800 rounded p-2 space-y-1">
                <span className="text-[8px] uppercase tracking-widest text-slate-700">Source classes</span>
                {[
                  { cls: "A", color: "#34d399", label: "Primary — highest trust" },
                  { cls: "B", color: "#38bdf8", label: "Credentialed media" },
                  { cls: "C", color: "#fbbf24", label: "Volatile / captured" },
                  { cls: "D", color: "#f43f5e", label: "Propagation node ⚠" },
                ].map(({ cls, color, label }) => (
                  <div key={cls} className="flex items-center gap-2">
                    <span className="text-[8px] font-bold w-4 text-center" style={{ color }}>{cls}</span>
                    <span className="text-[8px] text-slate-600">{label}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="border border-dashed border-slate-800/50 rounded p-4 text-center text-slate-700 text-[9px] uppercase tracking-widest">
              Sources appear here after analysis
            </div>
          )}
        </section>

        {/* Sources — mobile/lg: collapsible below results */}
        {verdict && (
          <section className="xl:hidden lg:col-span-3">
            <div className="border border-slate-800 rounded p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">
                  Source Nodes ({verdict.source_nodes?.length ?? verdict.pi_diagnostics?.node_count ?? 0})
                </span>
                <button
                  onClick={() => setShowSources(!showSources)}
                  className="text-[9px] text-slate-600 hover:text-slate-400 cursor-pointer uppercase tracking-wider"
                >
                  {showSources ? "▲ collapse" : "▼ expand"}
                </button>
              </div>
              {showSources && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {(verdict.source_nodes ?? []).map((node, i) => {
                    const cls = node.class || "?";
                    const clsColor = {
                      A: { border: "#34d39940", bg: "#34d39908", text: "#34d399" },
                      B: { border: "#38bdf840", bg: "#38bdf808", text: "#38bdf8" },
                      C: { border: "#fbbf2440", bg: "#fbbf2408", text: "#fbbf24" },
                      D: { border: "#f43f5e40", bg: "#f43f5e08", text: "#f43f5e" },
                    }[cls] || { border: "#47556940", bg: "#47556908", text: "#475569" };
                    const domain = (() => {
                      try { return new URL(node.url).hostname.replace("www.", ""); }
                      catch { return node.url.slice(0, 25); }
                    })();
                    return (
                      <a key={i} href={node.url} target="_blank" rel="noopener noreferrer"
                         className="block rounded border p-2 space-y-1 hover:opacity-80 transition-opacity"
                         style={{ borderColor: clsColor.border, background: clsColor.bg }}>
                        <div className="flex items-center justify-between">
                          <span className="text-[8px] font-bold" style={{ color: clsColor.text }}>
                            {node.inverted ? "D ⚠" : `Class ${cls}`}
                          </span>
                          <span className="text-[8px] text-slate-600">T={(node.trust ?? 0).toFixed(2)}</span>
                        </div>
                        <p className="text-[9px] text-slate-400 truncate">{domain}</p>
                      </a>
                    );
                  })}
                </div>
              )}
            </div>
          </section>
        )}

      </main>

      <footer className="max-w-[1600px] mx-auto mt-8 pt-4 border-t border-slate-900 flex justify-between items-center flex-wrap gap-2">
        <span className="text-[9px] text-slate-700 uppercase tracking-widest">
          ChronoDyne Systems · PPS · STOC · Π · Γ · v4.3.0
        </span>
        <a href="https://doi.org/10.6084/m9.figshare.32307087" target="_blank" rel="noopener noreferrer"
           className="text-[9px] text-slate-700 hover:text-teal-400 uppercase tracking-widest transition-colors">
          PPS Paper ↗
        </a>
        <a href="https://github.com/JustMichael-80/ILO-Analyzer" target="_blank" rel="noopener noreferrer"
           className="text-[9px] text-slate-600 hover:text-teal-400 uppercase tracking-widest transition-colors">
          GitHub ↗
        </a>
      </footer>
    </div>
  );
}
