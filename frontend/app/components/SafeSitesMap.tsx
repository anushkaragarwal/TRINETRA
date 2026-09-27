type SafeSitesMapProps = {
  title?: string;
  className?: string;
};

export default function SafeSitesMap({
  title = "Safe sites",
  className = "",
}: SafeSitesMapProps) {
  return (
    <div className={`rounded-2xl border border-slate-700 bg-slate-900/80 p-4 ${className}`}>
      <div className="mb-3 text-sm font-semibold tracking-wide text-slate-200 uppercase">
        {title}
      </div>
      <div className="relative h-64 overflow-hidden rounded-xl border border-slate-700 bg-slate-950">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_35%,rgba(16,185,129,0.2),transparent_28%),radial-gradient(circle_at_75%_30%,rgba(59,130,246,0.16),transparent_25%)]" />
        <div className="absolute left-[28%] top-[38%] h-4 w-4 rounded-full bg-emerald-400 shadow-[0_0_22px_rgba(52,211,153,0.9)]" />
        <div className="absolute left-[46%] top-[28%] h-4 w-4 rounded-full bg-emerald-500 shadow-[0_0_22px_rgba(16,185,129,0.9)]" />
        <div className="absolute left-[62%] top-[56%] h-4 w-4 rounded-full bg-sky-400 shadow-[0_0_22px_rgba(56,189,248,0.9)]" />
        <div className="absolute left-[76%] top-[40%] h-4 w-4 rounded-full bg-lime-400 shadow-[0_0_22px_rgba(163,230,53,0.9)]" />
        <div className="absolute inset-0 [background-image:linear-gradient(rgba(148,163,184,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.08)_1px,transparent_1px)] [background-size:22px_22px]" />
      </div>
    </div>
  );
}
