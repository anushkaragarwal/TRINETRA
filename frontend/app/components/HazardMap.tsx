type HazardMapProps = {
  title?: string;
  className?: string;
};

export default function HazardMap({
  title = "Hazard map",
  className = "",
}: HazardMapProps) {
  return (
    <div className={`rounded-2xl border border-slate-700 bg-slate-900/80 p-4 ${className}`}>
      <div className="mb-3 text-sm font-semibold tracking-wide text-slate-200 uppercase">
        {title}
      </div>
      <div className="relative h-64 overflow-hidden rounded-xl border border-slate-700 bg-slate-950">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(34,197,94,0.22),transparent_30%),radial-gradient(circle_at_80%_30%,rgba(251,146,60,0.18),transparent_28%),radial-gradient(circle_at_52%_78%,rgba(59,130,246,0.16),transparent_32%)]" />
        <div className="absolute left-[18%] top-[28%] h-3 w-3 rounded-full bg-emerald-400 shadow-[0_0_20px_rgba(52,211,153,0.9)]" />
        <div className="absolute left-[42%] top-[42%] h-3 w-3 rounded-full bg-amber-400 shadow-[0_0_20px_rgba(251,191,36,0.9)]" />
        <div className="absolute left-[64%] top-[26%] h-3 w-3 rounded-full bg-red-400 shadow-[0_0_20px_rgba(248,113,113,0.9)]" />
        <div className="absolute left-[56%] top-[68%] h-3 w-3 rounded-full bg-sky-400 shadow-[0_0_20px_rgba(96,165,250,0.9)]" />
        <div className="absolute inset-0 [background-image:linear-gradient(rgba(148,163,184,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.08)_1px,transparent_1px)] [background-size:24px_24px]" />
      </div>
    </div>
  );
}
