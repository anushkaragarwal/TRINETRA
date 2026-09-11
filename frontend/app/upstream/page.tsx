const upstreamSites = [
  {
    name: "Upper Alaknanda",
    type: "River",
    status: "WATCH",
    value: "Rising",
    change: "+18%",
  },
  {
    name: "Dhauliganga Catchment",
    type: "Catchment",
    status: "NORMAL",
    value: "Stable",
    change: "-2%",
  },
  {
    name: "Glacial Lake Zone",
    type: "Water body",
    status: "WATCH",
    value: "Change detected",
    change: "+7%",
  },
  {
    name: "Badrinath Upper Basin",
    type: "Terrain",
    status: "NORMAL",
    value: "Stable",
    change: "0%",
  },
];

const indicators = [
  {
    name: "River / Water Change",
    score: 72,
    description: "Above recent baseline",
  },
  {
    name: "Satellite Surface Change",
    score: 61,
    description: "Moderate anomaly",
  },
  {
    name: "Rainfall Upstream",
    score: 68,
    description: "Elevated conditions",
  },
  {
    name: "Glacial Lake Change",
    score: 43,
    description: "Low-moderate signal",
  },
];

export default function UpstreamPage() {
  return (
    <main className="min-h-screen bg-[#081016] text-white">
      <div className="flex min-h-screen">

        {/* SIDEBAR */}
        <aside className="w-[230px] shrink-0 border-r border-[#1c3038] bg-[#0b151b] px-4 py-5">

          <div className="mb-8 px-2">
            <div className="flex items-center gap-3">

              <div className="flex h-9 w-9 items-center justify-center rounded-md border border-cyan-400/40 bg-cyan-400/10 text-sm font-bold text-cyan-300">
                T
              </div>

              <div>
                <h1 className="text-[18px] font-semibold tracking-[0.18em]">
                  TRINETRA
                </h1>

                <p className="text-[9px] uppercase tracking-[0.18em] text-slate-500">
                  Terrain Intelligence
                </p>
              </div>

            </div>
          </div>

          <p className="mb-3 px-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-600">
            Monitoring
          </p>

          <nav className="space-y-1">

            <a
              href="/"
              className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"
            >
              <span>⌂</span>
              Command Center
            </a>

            <a
              href="/upstream"
              className="flex items-center gap-3 rounded-md border border-cyan-400/20 bg-cyan-400/10 px-3 py-2.5 text-sm text-cyan-300"
            >
              <span>◈</span>
              Upstream Intelligence
            </a>

            <a
              href="/risk"
              className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"
            >
              <span>◆</span>
              Risk Intelligence
            </a>

            <a
              href="/safe-sites"
              className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"
            >
              <span>⌂</span>
              Safe Sites
            </a>

            <a
              href="/relocation"
              className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"
            >
              <span>⇄</span>
              Relocation
            </a>

          </nav>

          <p className="mb-3 mt-8 px-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-600">
            System
          </p>

          <nav>
            <a
              href="/data-sources"
              className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"
            >
              <span>▣</span>
              Data Sources
            </a>
          </nav>

          <div className="mt-12 rounded-md border border-[#1c3038] bg-[#0e1b22] p-3">

            <div className="mb-2 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400"></span>

              <span className="text-xs text-emerald-300">
                SATELLITE LINK ACTIVE
              </span>
            </div>

            <p className="text-[10px] leading-4 text-slate-500">
              Monitoring upstream terrain and water-body indicators
            </p>

          </div>

        </aside>

        {/* MAIN */}
        <section className="flex-1">

          {/* HEADER */}
          <header className="flex h-[68px] items-center justify-between border-b border-[#1c3038] bg-[#0b151b] px-6">

            <div>
              <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">
                Satellite & Hydrological Monitoring
              </p>

              <h2 className="mt-1 text-lg font-medium">
                Upstream Intelligence
              </h2>
            </div>

            <div className="flex items-center gap-5">

              <div className="text-right">
                <p className="text-[10px] text-slate-500">
                  LAST UPDATE
                </p>

                <p className="text-xs text-slate-300">
                  05 Sep 2026 · 16:18 IST
                </p>
              </div>

              <div className="flex items-center gap-2 rounded-md border border-emerald-400/20 bg-emerald-400/5 px-3 py-2">
                <span className="h-2 w-2 rounded-full bg-emerald-400"></span>

                <span className="text-xs text-emerald-300">
                  MONITORING
                </span>
              </div>

            </div>

          </header>

          <div className="p-5">

            {/* TOP CARDS */}
            <div className="grid grid-cols-4 gap-4">

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Upstream Sites
                </p>

                <p className="mt-2 text-3xl font-semibold">
                  18
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  River, terrain and water-body zones
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Active Signals
                </p>

                <p className="mt-2 text-3xl font-semibold text-orange-400">
                  5
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  Require additional assessment
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  SAR Coverage
                </p>

                <p className="mt-2 text-3xl font-semibold">
                  96%
                </p>

                <p className="mt-3 text-xs text-emerald-400">
                  Cloud-independent monitoring
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Anomaly Index
                </p>

                <p className="mt-2 text-3xl font-semibold text-yellow-400">
                  62
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  Moderate upstream signal
                </p>

              </div>

            </div>

            {/* SATELLITE PANEL + SIGNALS */}
            <div className="mt-5 grid grid-cols-[1fr_340px] gap-5">

              {/* SATELLITE VIEW */}
              <div className="overflow-hidden rounded-lg border border-[#1c3038] bg-[#0b171d]">

                <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">

                  <div>
                    <h3 className="text-sm font-medium">
                      Upstream Monitoring View
                    </h3>

                    <p className="mt-0.5 text-[10px] text-slate-500">
                      Sentinel-derived terrain and water-body indicators
                    </p>
                  </div>

                  <div className="flex gap-2">

                    <button className="rounded border border-cyan-400/30 bg-cyan-400/10 px-3 py-1.5 text-[10px] text-cyan-300">
                      SAR
                    </button>

                    <button className="rounded border border-[#293d44] px-3 py-1.5 text-[10px] text-slate-500">
                      OPTICAL
                    </button>

                  </div>

                </div>

                <div className="relative h-[355px] overflow-hidden bg-[#101d20]">

                  {/* GRID */}
                  <div
                    className="absolute inset-0 opacity-20"
                    style={{
                      backgroundImage:
                        "linear-gradient(#55727a 1px, transparent 1px), linear-gradient(90deg, #55727a 1px, transparent 1px)",
                      backgroundSize: "40px 40px",
                    }}
                  />

                  {/* TERRAIN */}
                  <svg
                    className="absolute inset-0 h-full w-full"
                    viewBox="0 0 900 355"
                    preserveAspectRatio="none"
                  >

                    <path
                      d="M0 280 L100 210 L170 245 L250 110 L330 180 L410 70 L490 150 L570 55 L650 140 L730 80 L810 175 L900 100 L900 355 L0 355 Z"
                      fill="#18292c"
                    />

                    <path
                      d="M0 280 L100 210 L170 245 L250 110 L330 180 L410 70 L490 150 L570 55 L650 140 L730 80 L810 175 L900 100"
                      fill="none"
                      stroke="#4a6469"
                      strokeWidth="2"
                    />

                    {/* river */}
                    <path
                      d="M580 0 C540 65 620 90 570 145 C520 200 590 230 530 275 C480 315 500 340 460 355"
                      fill="none"
                      stroke="#22d3ee"
                      strokeWidth="4"
                      opacity="0.65"
                    />

                    {/* anomaly zone */}
                    <path
                      d="M230 120 C270 85 330 100 355 145 C335 185 285 190 245 165 Z"
                      fill="#f97316"
                      opacity="0.22"
                    />

                    <path
                      d="M550 60 C600 40 650 70 665 110 C640 140 590 135 555 110 Z"
                      fill="#facc15"
                      opacity="0.18"
                    />

                  </svg>

                  {/* LABELS */}
                  <div className="absolute left-[25%] top-[28%]">

                    <div className="flex items-center gap-2">

                      <span className="h-3 w-3 rounded-full bg-orange-400 shadow-[0_0_10px_rgba(251,146,60,0.7)]"></span>

                      <span className="text-xs font-medium">
                        Terrain anomaly
                      </span>

                    </div>

                    <p className="ml-5 text-[9px] text-orange-400">
                      MODERATE SIGNAL
                    </p>

                  </div>

                  <div className="absolute left-[61%] top-[20%]">

                    <div className="flex items-center gap-2">

                      <span className="h-3 w-3 rounded-full bg-yellow-400"></span>

                      <span className="text-xs font-medium">
                        Water-body change
                      </span>

                    </div>

                    <p className="ml-5 text-[9px] text-yellow-400">
                      WATCH
                    </p>

                  </div>

                  <div className="absolute bottom-5 left-5 rounded border border-[#31454c] bg-[#081016]/90 px-3 py-2">

                    <p className="text-[9px] text-slate-600">
                      CURRENT LAYER
                    </p>

                    <p className="mt-1 text-[10px] text-cyan-300">
                      SENTINEL-1 · SAR BACKSCATTER
                    </p>

                  </div>

                  <div className="absolute right-5 top-5 rounded border border-[#31454c] bg-[#081016]/90 px-3 py-2">

                    <p className="text-[9px] text-slate-600">
                      AOI
                    </p>

                    <p className="mt-1 text-[10px] text-slate-300">
                      30.50–30.80° N
                    </p>

                    <p className="text-[10px] text-slate-300">
                      79.40–79.75° E
                    </p>

                  </div>

                </div>

              </div>

              {/* SIGNAL PANEL */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920]">

                <div className="border-b border-[#1c3038] px-4 py-3">

                  <h3 className="text-sm font-medium">
                    Upstream Indicators
                  </h3>

                  <p className="mt-1 text-[10px] text-slate-500">
                    Current signals from monitored sources
                  </p>

                </div>

                <div className="divide-y divide-[#1c3038]">

                  {indicators.map((indicator) => (
                    <div
                      key={indicator.name}
                      className="p-4"
                    >

                      <div className="flex items-center justify-between">

                        <span className="text-xs text-slate-300">
                          {indicator.name}
                        </span>

                        <span className="text-sm font-medium">
                          {indicator.score}
                        </span>

                      </div>

                      <div className="mt-3 h-1.5 rounded-full bg-[#1b2930]">

                        <div
                          className={`h-full rounded-full ${
                            indicator.score >= 70
                              ? "w-[72%] bg-orange-400"
                              : indicator.score >= 55
                              ? "w-[61%] bg-yellow-400"
                              : "w-[43%] bg-emerald-400"
                          }`}
                        ></div>

                      </div>

                      <p className="mt-2 text-[9px] text-slate-600">
                        {indicator.description}
                      </p>

                    </div>
                  ))}

                </div>

              </div>

            </div>

            {/* SITE TABLE */}
            <div className="mt-5 rounded-lg border border-[#1c3038] bg-[#0d1920]">

              <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">

                <div>
                  <h3 className="text-sm font-medium">
                    Monitored Upstream Zones
                  </h3>

                  <p className="mt-1 text-[10px] text-slate-500">
                    Recent changes detected across the upstream area
                  </p>
                </div>

                <button className="rounded border border-[#293d44] px-3 py-1.5 text-[10px] text-slate-400 hover:bg-white/5 hover:text-white">
                  VIEW ALL
                </button>

              </div>

              <table className="w-full text-left">

                <thead className="border-b border-[#1c3038]">

                  <tr className="text-[9px] uppercase tracking-wider text-slate-600">

                    <th className="px-4 py-3 font-medium">
                      Monitoring Zone
                    </th>

                    <th className="px-4 py-3 font-medium">
                      Type
                    </th>

                    <th className="px-4 py-3 font-medium">
                      Current Signal
                    </th>

                    <th className="px-4 py-3 font-medium">
                      Change
                    </th>

                    <th className="px-4 py-3 font-medium">
                      Status
                    </th>

                  </tr>

                </thead>

                <tbody className="divide-y divide-[#1c3038]">

                  {upstreamSites.map((site) => (

                    <tr
                      key={site.name}
                      className="hover:bg-white/[0.02]"
                    >

                      <td className="px-4 py-3 text-xs text-slate-200">
                        {site.name}
                      </td>

                      <td className="px-4 py-3 text-xs text-slate-500">
                        {site.type}
                      </td>

                      <td className="px-4 py-3 text-xs text-slate-300">
                        {site.value}
                      </td>

                      <td className="px-4 py-3 text-xs text-slate-400">
                        {site.change}
                      </td>

                      <td className="px-4 py-3">

                        <span
                          className={`text-[9px] font-medium ${
                            site.status === "WATCH"
                              ? "text-orange-400"
                              : "text-emerald-400"
                          }`}
                        >
                          ● {site.status}
                        </span>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

            {/* BOTTOM INFO */}
            <div className="mt-5 grid grid-cols-3 gap-4">

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[9px] uppercase tracking-wider text-slate-600">
                  Satellite
                </p>

                <p className="mt-2 text-xs text-slate-300">
                  Sentinel-1 SAR
                </p>

                <p className="mt-1 text-[10px] text-slate-600">
                  Useful for cloud-independent surface monitoring
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[9px] uppercase tracking-wider text-slate-600">
                  Optical
                </p>

                <p className="mt-2 text-xs text-slate-300">
                  Sentinel-2
                </p>

                <p className="mt-1 text-[10px] text-slate-600">
                  Used for vegetation and water-body change
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[9px] uppercase tracking-wider text-slate-600">
                  Interpretation
                </p>

                <p className="mt-2 text-xs text-slate-300">
                  Indicator / anomaly analysis
                </p>

                <p className="mt-1 text-[10px] text-slate-600">
                  Signals require model and ground-data validation
                </p>

              </div>

            </div>

            {/* FOOTER */}
            <div className="mt-5 flex items-center justify-between border-t border-[#1c3038] pt-4">

              <p className="text-[9px] text-slate-600">
                TRINETRA · Upstream Intelligence
              </p>

              <p className="text-[9px] text-slate-600">
                DEMO DATA · Replace with satellite pipeline
              </p>

            </div>

          </div>

        </section>
      </div>
    </main>
  );
}