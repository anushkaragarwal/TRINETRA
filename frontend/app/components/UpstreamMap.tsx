type UpstreamMapProps = {
  title?: string;
  className?: string;
};

export default function UpstreamMap({
  title = "Upstream map",
  className = "",
}: UpstreamMapProps) {
  return (
    <div className={`rounded-2xl border border-slate-700 bg-slate-900/80 p-4 ${className}`}>
      <div className="mb-3 text-sm font-semibold tracking-wide text-slate-200 uppercase">
        {title}
      </div>
      <div className="relative h-64 overflow-hidden rounded-xl border border-slate-700 bg-slate-950">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(56,189,248,0.2),transparent_28%),radial-gradient(circle_at_70%_55%,rgba(34,197,94,0.18),transparent_30%)]" />
        <div className="absolute left-[24%] top-[36%] h-4 w-4 rounded-full bg-sky-400 shadow-[0_0_24px_rgba(56,189,248,0.9)]" />
        <div className="absolute left-[48%] top-[42%] h-4 w-4 rounded-full bg-cyan-400 shadow-[0_0_24px_rgba(34,211,238,0.9)]" />
        <div className="absolute left-[64%] top-[56%] h-4 w-4 rounded-full bg-emerald-400 shadow-[0_0_24px_rgba(52,211,153,0.9)]" />
        <div className="absolute left-[74%] top-[28%] h-4 w-4 rounded-full bg-violet-400 shadow-[0_0_24px_rgba(167,139,250,0.9)]" />
        <div className="absolute inset-0 [background-image:linear-gradient(rgba(148,163,184,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.08)_1px,transparent_1px)] [background-size:22px_22px]" />
      </div>
    </div>
  );
}
