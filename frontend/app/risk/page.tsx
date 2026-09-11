const settlements = [
  {
    name: "Joshimath",
    score: 91,
    level: "CRITICAL",
    population: "16,709",
    flood: 86,
    landslide: 78,
    upstream: 64,
  },
  {
    name: "Vishnuprayag",
    score: 78,
    level: "HIGH",
    population: "1,245",
    flood: 82,
    landslide: 61,
    upstream: 72,
  },
  {
    name: "Govindghat",
    score: 64,
    level: "MODERATE",
    population: "2,184",
    flood: 67,
    landslide: 58,
    upstream: 49,
  },
  {
    name: "Badrinath",
    score: 58,
    level: "MODERATE",
    population: "1,523",
    flood: 54,
    landslide: 63,
    upstream: 42,
  },
];

const factors = [
  {
    name: "Rainfall",
    value: 84,
    change: "+31%",
    text: "Above normal",
  },
  {
    name: "River level",
    value: 78,
    change: "+18%",
    text: "Rising rapidly",
  },
  {
    name: "Slope susceptibility",
    value: 69,
    change: "High",
    text: "Terrain based",
  },
  {
    name: "Upstream anomaly",
    value: 62,
    change: "Moderate",
    text: "Satellite indicators",
  },
];

export default function RiskPage() {
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
              className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"
            >
              <span>◈</span>
              Upstream Intelligence
            </a>

            <a
              href="/risk"
              className="flex items-center gap-3 rounded-md border border-cyan-400/20 bg-cyan-400/10 px-3 py-2.5 text-sm text-cyan-300"
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
                SYSTEM OPERATIONAL
              </span>
            </div>

            <p className="text-[10px] leading-4 text-slate-500">
              Risk engine processing current corridor data
            </p>

          </div>

        </aside>

        {/* MAIN CONTENT */}
        <section className="flex-1">

          {/* HEADER */}
          <header className="flex h-[68px] items-center justify-between border-b border-[#1c3038] bg-[#0b151b] px-6">

            <div>
              <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">
                Risk Assessment
              </p>

              <h2 className="mt-1 text-lg font-medium">
                Risk Intelligence
              </h2>
            </div>

            <div className="flex items-center gap-5">

              <div className="text-right">
                <p className="text-[10px] text-slate-500">
                  ASSESSMENT TIME
                </p>

                <p className="text-xs text-slate-300">
                  05 Sep 2026 · 16:21 IST
                </p>
              </div>

              <div className="flex items-center gap-2 rounded-md border border-emerald-400/20 bg-emerald-400/5 px-3 py-2">
                <span className="h-2 w-2 rounded-full bg-emerald-400"></span>

                <span className="text-xs text-emerald-300">
                  LIVE
                </span>
              </div>

            </div>

          </header>

          {/* PAGE CONTENT */}
          <div className="p-5">

            {/* TOP SUMMARY */}
            <div className="grid grid-cols-[1.3fr_1fr_1fr_1fr] gap-4">

              {/* OVERALL RISK */}
              <div className="rounded-lg border border-red-400/20 bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Corridor Risk Score
                </p>

                <div className="mt-2 flex items-end gap-3">

                  <span className="text-4xl font-semibold text-red-400">
                    78
                  </span>

                  <span className="mb-1.5 text-xs font-medium text-red-400">
                    HIGH
                  </span>

                </div>

                <div className="mt-4 h-1.5 rounded-full bg-[#1b2930]">
                  <div className="h-full w-[78%] rounded-full bg-red-400"></div>
                </div>

                <p className="mt-3 text-[10px] text-slate-500">
                  Based on current hazard and exposure conditions
                </p>

              </div>

              {/* SETTLEMENTS */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Settlements Monitored
                </p>

                <p className="mt-2 text-3xl font-semibold">
                  24
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  4 currently above moderate risk
                </p>

              </div>

              {/* HIGH RISK */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  High / Critical
                </p>

                <p className="mt-2 text-3xl font-semibold text-orange-400">
                  7
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  Require priority assessment
                </p>

              </div>

              {/* CONFIDENCE */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Model Confidence
                </p>

                <p className="mt-2 text-3xl font-semibold">
                  84%
                </p>

                <p className="mt-3 text-xs text-emerald-400">
                  Good data coverage
                </p>

              </div>

            </div>

            {/* MAP + RISK FACTORS */}
            <div className="mt-5 grid grid-cols-[1fr_340px] gap-5">

              {/* RISK MAP */}
              <div className="overflow-hidden rounded-lg border border-[#1c3038] bg-[#0b171d]">

                <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">

                  <div>
                    <h3 className="text-sm font-medium">
                      Settlement Risk Map
                    </h3>

                    <p className="mt-0.5 text-[10px] text-slate-500">
                      Dynamic risk assessment across the monitored corridor
                    </p>
                  </div>

                  <div className="flex items-center gap-3 text-[10px]">

                    <span className="flex items-center gap-1.5">
                      <i className="h-2 w-2 rounded-full bg-emerald-400"></i>
                      Low
                    </span>

                    <span className="flex items-center gap-1.5">
                      <i className="h-2 w-2 rounded-full bg-yellow-400"></i>
                      Moderate
                    </span>

                    <span className="flex items-center gap-1.5">
                      <i className="h-2 w-2 rounded-full bg-orange-400"></i>
                      High
                    </span>

                    <span className="flex items-center gap-1.5">
                      <i className="h-2 w-2 rounded-full bg-red-400"></i>
                      Critical
                    </span>

                  </div>

                </div>

                {/* MOCK MAP */}
                <div className="relative h-[355px] overflow-hidden bg-[#0a191f]">

                  {/* GRID */}
                  <div
                    className="absolute inset-0 opacity-20"
                    style={{
                      backgroundImage:
                        "linear-gradient(#55727a 1px, transparent 1px), linear-gradient(90deg, #55727a 1px, transparent 1px)",
                      backgroundSize: "42px 42px",
                    }}
                  />

                  {/* TERRAIN */}
                  <svg
                    className="absolute inset-0 h-full w-full opacity-30"
                    viewBox="0 0 900 355"
                    preserveAspectRatio="none"
                  >

                    <path
                      d="M0 90 C120 20 180 150 310 80 S500 40 620 110 S790 180 900 70"
                      fill="none"
                      stroke="#48656d"
                      strokeWidth="1"
                    />

                    <path
                      d="M0 165 C120 90 220 230 340 155 S530 100 680 180 S800 230 900 140"
                      fill="none"
                      stroke="#48656d"
                      strokeWidth="1"
                    />

                    <path
                      d="M0 250 C140 180 230 310 370 235 S570 190 710 270 S820 310 900 225"
                      fill="none"
                      stroke="#48656d"
                      strokeWidth="1"
                    />

                    {/* river */}
                    <path
                      d="M180 0 C210 70 180 120 270 165 C340 205 310 255 405 285 C475 310 520 335 570 355"
                      fill="none"
                      stroke="#22d3ee"
                      strokeWidth="3"
                      opacity="0.5"
                    />

                  </svg>

                  {/* STUDY AREA */}
                  <div className="absolute left-5 top-5 rounded border border-[#31454c] bg-[#081016]/90 px-3 py-2">

                    <p className="text-[9px] text-slate-500">
                      STUDY AREA
                    </p>

                    <p className="mt-1 text-xs text-slate-300">
                      Joshimath → Vishnuprayag
                    </p>

                    <p className="text-xs text-slate-300">
                      → Badrinath
                    </p>

                  </div>

                  {/* JOSHIMATH */}
                  <div className="absolute left-[27%] top-[30%]">

                    <div className="h-5 w-5 rounded-full border-2 border-red-200 bg-red-500 shadow-[0_0_12px_rgba(248,113,113,0.55)]"></div>

                    <p className="mt-1 whitespace-nowrap text-xs font-medium">
                      Joshimath
                    </p>

                    <p className="text-[9px] text-red-400">
                      91 · CRITICAL
                    </p>

                  </div>

                  {/* VISHNUPRAYAG */}
                  <div className="absolute left-[43%] top-[53%]">

                    <div className="h-5 w-5 rounded-full border-2 border-orange-200 bg-orange-400 shadow-[0_0_12px_rgba(251,146,60,0.45)]"></div>

                    <p className="mt-1 whitespace-nowrap text-xs font-medium">
                      Vishnuprayag
                    </p>

                    <p className="text-[9px] text-orange-400">
                      78 · HIGH
                    </p>

                  </div>

                  {/* GOVINDGHAT */}
                  <div className="absolute left-[58%] top-[67%]">

                    <div className="h-4 w-4 rounded-full border-2 border-yellow-100 bg-yellow-400"></div>

                    <p className="mt-1 whitespace-nowrap text-xs font-medium">
                      Govindghat
                    </p>

                    <p className="text-[9px] text-yellow-400">
                      64 · MODERATE
                    </p>

                  </div>

                  {/* BADRINATH */}
                  <div className="absolute right-[17%] top-[28%]">

                    <div className="h-4 w-4 rounded-full border-2 border-yellow-100 bg-yellow-400"></div>

                    <p className="mt-1 whitespace-nowrap text-xs font-medium">
                      Badrinath
                    </p>

                    <p className="text-[9px] text-yellow-400">
                      58 · MODERATE
                    </p>

                  </div>

                  {/* MAP INFO */}
                  <div className="absolute bottom-4 left-4 rounded border border-[#31454c] bg-[#081016]/90 px-3 py-2">

                    <p className="text-[9px] text-slate-600">
                      RISK ENGINE
                    </p>

                    <p className="mt-1 text-[10px] text-emerald-400">
                      ● PROCESSING CURRENT DATA
                    </p>

                  </div>

                  {/* NORTH */}
                  <div className="absolute right-5 top-5 flex h-9 w-9 items-center justify-center rounded border border-[#31454c] bg-[#081016]/80 text-xs text-slate-400">
                    N
                  </div>

                </div>

              </div>

              {/* RISK FACTORS */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920]">

                <div className="border-b border-[#1c3038] px-4 py-3">

                  <h3 className="text-sm font-medium">
                    Risk Factors
                  </h3>

                  <p className="mt-1 text-[10px] text-slate-500">
                    Main inputs affecting current risk
                  </p>

                </div>

                <div className="divide-y divide-[#1c3038]">

                  {factors.map((factor) => (
                    <div
                      key={factor.name}
                      className="p-4"
                    >

                      <div className="flex items-center justify-between">

                        <span className="text-xs text-slate-300">
                          {factor.name}
                        </span>

                        <span className="text-sm font-medium">
                          {factor.value}
                        </span>

                      </div>

                      <div className="mt-3 h-1.5 rounded-full bg-[#1b2930]">

                        <div
                          className={`h-full rounded-full ${
                            factor.value >= 80
                              ? "w-[84%] bg-red-400"
                              : factor.value >= 70
                              ? "w-[78%] bg-orange-400"
                              : "w-[69%] bg-yellow-400"
                          }`}
                        ></div>

                      </div>

                      <div className="mt-2 flex justify-between">

                        <span className="text-[9px] text-slate-600">
                          {factor.text}
                        </span>

                        <span className="text-[9px] text-orange-400">
                          {factor.change}
                        </span>

                      </div>

                    </div>
                  ))}

                </div>

                <div className="m-4 rounded border border-[#253941] bg-[#0a151b] p-3">

                  <p className="text-[9px] uppercase tracking-wider text-slate-600">
                    Assessment
                  </p>

                  <p className="mt-2 text-xs leading-5 text-slate-300">
                    Current conditions indicate elevated multi-hazard
                    exposure across parts of the corridor.
                  </p>

                </div>

              </div>

            </div>

            {/* SETTLEMENT TABLE */}
            <div className="mt-5 rounded-lg border border-[#1c3038] bg-[#0d1920]">

              <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">

                <div>
                  <h3 className="text-sm font-medium">
                    Settlement Risk Assessment
                  </h3>

                  <p className="mt-1 text-[10px] text-slate-500">
                    Hazard scores and population exposure
                  </p>
                </div>

                <button className="rounded border border-[#293d44] px-3 py-1.5 text-[10px] text-slate-400 hover:bg-white/5 hover:text-white">
                  VIEW DETAILS
                </button>

              </div>

              <div className="overflow-x-auto">

                <table className="w-full text-left">

                  <thead className="border-b border-[#1c3038]">

                    <tr className="text-[9px] uppercase tracking-wider text-slate-600">

                      <th className="px-4 py-3 font-medium">
                        Settlement
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Population
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Flood
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Landslide
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Upstream
                      </th>

                      <th className="px-4 py-3 text-right font-medium">
                        Risk Score
                      </th>

                    </tr>

                  </thead>

                  <tbody className="divide-y divide-[#1c3038]">

                    {settlements.map((settlement) => (

                      <tr
                        key={settlement.name}
                        className="hover:bg-white/[0.02]"
                      >

                        <td className="px-4 py-3">

                          <div className="flex items-center gap-3">

                            <span
                              className={`h-2 w-2 rounded-full ${
                                settlement.level === "CRITICAL"
                                  ? "bg-red-400"
                                  : settlement.level === "HIGH"
                                  ? "bg-orange-400"
                                  : "bg-yellow-400"
                              }`}
                            ></span>

                            <span className="text-xs text-slate-200">
                              {settlement.name}
                            </span>

                          </div>

                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {settlement.population}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {settlement.flood}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {settlement.landslide}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {settlement.upstream}
                        </td>

                        <td className="px-4 py-3 text-right">

                          <div className="flex items-center justify-end gap-3">

                            <span
                              className={`text-[9px] ${
                                settlement.level === "CRITICAL"
                                  ? "text-red-400"
                                  : settlement.level === "HIGH"
                                  ? "text-orange-400"
                                  : "text-yellow-400"
                              }`}
                            >
                              {settlement.level}
                            </span>

                            <span className="text-sm font-medium">
                              {settlement.score}
                            </span>

                          </div>

                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            </div>

            {/* FOOTER */}
            <div className="mt-5 flex items-center justify-between border-t border-[#1c3038] pt-4">

              <p className="text-[9px] text-slate-600">
                TRINETRA · Risk Intelligence
              </p>

              <p className="text-[9px] text-slate-600">
                DEMO DATA · Replace with model output
              </p>

            </div>

          </div>

        </section>
      </div>
    </main>
  );
}