type RiskMapProps = {
  title?: string;
  className?: string;
};

export default function RiskMap({
  title = "Risk map",
  className = "",
}: RiskMapProps) {
  return (
    <div className={`rounded-2xl border border-slate-700 bg-slate-900/80 p-4 ${className}`}>
      <div className="mb-3 text-sm font-semibold tracking-wide text-slate-200 uppercase">
        {title}
      </div>
      <div className="relative h-64 overflow-hidden rounded-xl border border-slate-700 bg-slate-950">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_25%,rgba(248,113,113,0.16),transparent_30%),radial-gradient(circle_at_70%_35%,rgba(251,146,60,0.18),transparent_28%),radial-gradient(circle_at_52%_75%,rgba(234,179,8,0.12),transparent_32%)]" />
        <div className="absolute left-[20%] top-[24%] h-4 w-4 rounded-full bg-red-500 shadow-[0_0_24px_rgba(239,68,68,0.9)]" />
        <div className="absolute left-[35%] top-[48%] h-4 w-4 rounded-full bg-orange-500 shadow-[0_0_24px_rgba(249,115,22,0.9)]" />
        <div className="absolute left-[58%] top-[34%] h-4 w-4 rounded-full bg-yellow-400 shadow-[0_0_24px_rgba(250,204,21,0.9)]" />
        <div className="absolute left-[72%] top-[60%] h-4 w-4 rounded-full bg-emerald-500 shadow-[0_0_24px_rgba(16,185,129,0.9)]" />
        <div className="absolute inset-0 [background-image:linear-gradient(rgba(148,163,184,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.08)_1px,transparent_1px)] [background-size:22px_22px]" />
      </div>
    </div>
  );
}
