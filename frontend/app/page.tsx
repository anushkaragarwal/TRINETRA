const alerts = [
  {
    level: "CRITICAL",
    title: "High river rise detected",
    place: "Vishnuprayag",
    time: "08 min ago",
  },
  {
    level: "HIGH",
    title: "Heavy rainfall recorded",
    place: "Joshimath sector",
    time: "21 min ago",
  },
  {
    level: "MODERATE",
    title: "Slope movement detected",
    place: "Badrinath corridor",
    time: "42 min ago",
  },
];

const settlements = [
  { name: "Joshimath", score: 91, level: "CRITICAL" },
  { name: "Vishnuprayag", score: 78, level: "HIGH" },
  { name: "Govindghat", score: 64, level: "MODERATE" },
  { name: "Badrinath", score: 58, level: "MODERATE" },
];

export default function Page() {
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
              className="flex items-center gap-3 rounded-md border border-cyan-400/20 bg-cyan-400/10 px-3 py-2.5 text-sm text-cyan-300"
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

          <div className="mt-auto pt-12">
            <div className="rounded-md border border-[#1c3038] bg-[#0e1b22] p-3">
              <div className="mb-2 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
                <span className="text-xs text-emerald-300">
                  SYSTEM OPERATIONAL
                </span>
              </div>

              <p className="text-[10px] leading-4 text-slate-500">
                Monitoring Joshimath → Vishnuprayag → Badrinath corridor
              </p>
            </div>
          </div>
        </aside>

        {/* MAIN AREA */}
        <section className="flex-1">

          {/* TOP BAR */}
          <header className="flex h-[68px] items-center justify-between border-b border-[#1c3038] bg-[#0b151b] px-6">

            <div>
              <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">
                Disaster Management Control Room
              </p>

              <h2 className="mt-1 text-lg font-medium">
                Corridor Command Center
              </h2>
            </div>

            <div className="flex items-center gap-5">

              <div className="text-right">
                <p className="text-[10px] text-slate-500">
                  LAST UPDATED
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

          {/* CONTENT */}
          <div className="p-5">

            {/* KPI ROW */}
            <div className="grid grid-cols-4 gap-4">

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Overall Corridor Risk
                </p>

                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-semibold text-red-400">
                    78
                  </span>
                  <span className="mb-1 text-xs text-red-400">
                    HIGH
                  </span>
                </div>

                <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-[#1b2930]">
                  <div className="h-full w-[78%] rounded-full bg-red-400"></div>
                </div>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Rainfall · 24h
                </p>

                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-semibold">
                    84
                  </span>
                  <span className="mb-1 text-xs text-slate-500">
                    mm
                  </span>
                </div>

                <p className="mt-3 text-xs text-orange-400">
                  ↑ 31% above normal
                </p>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  River Level
                </p>

                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-semibold">
                    4.82
                  </span>
                  <span className="mb-1 text-xs text-slate-500">
                    m
                  </span>
                </div>

                <p className="mt-3 text-xs text-red-400">
                  ↑ Rising rapidly
                </p>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  People Exposed
                </p>

                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-semibold">
                    38.4K
                  </span>
                </div>

                <p className="mt-3 text-xs text-slate-500">
                  Across monitored settlements
                </p>
              </div>

            </div>

            {/* MAP + ALERTS */}
            <div className="mt-5 grid grid-cols-[1fr_330px] gap-5">

              {/* MAP */}
              <div className="overflow-hidden rounded-lg border border-[#1c3038] bg-[#0b171d]">

                <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">
                  <div>
                    <h3 className="text-sm font-medium">
                      Live Hazard Map
                    </h3>

                    <p className="mt-0.5 text-[10px] text-slate-500">
                      Joshimath — Vishnuprayag — Badrinath
                    </p>
                  </div>

                  <div className="flex items-center gap-3 text-[10px]">
                    <span className="flex items-center gap-1.5">
                      <i className="h-2 w-2 rounded-full bg-red-400"></i>
                      Critical
                    </span>

                    <span className="flex items-center gap-1.5">
                      <i className="h-2 w-2 rounded-full bg-orange-400"></i>
                      High
                    </span>

                    <span className="flex items-center gap-1.5">
                      <i className="h-2 w-2 rounded-full bg-yellow-400"></i>
                      Moderate
                    </span>
                  </div>
                </div>

                {/* MOCK MAP */}
                <div className="relative h-[430px] overflow-hidden bg-[#0b1a20]">

                  {/* grid */}
                  <div className="absolute inset-0 opacity-20"
                    style={{
                      backgroundImage:
                        "linear-gradient(#55727a 1px, transparent 1px), linear-gradient(90deg, #55727a 1px, transparent 1px)",
                      backgroundSize: "45px 45px",
                    }}
                  />

                  {/* terrain lines */}
                  <svg
                    className="absolute inset-0 h-full w-full opacity-30"
                    viewBox="0 0 900 430"
                    preserveAspectRatio="none"
                  >
                    <path
                      d="M0 100 C150 50 180 180 310 110 S520 40 650 120 S780 190 900 80"
                      fill="none"
                      stroke="#48656d"
                      strokeWidth="1"
                    />
                    <path
                      d="M0 170 C120 100 220 250 350 170 S550 100 690 190 S820 250 900 150"
                      fill="none"
                      stroke="#48656d"
                      strokeWidth="1"
                    />
                    <path
                      d="M0 250 C130 180 230 330 370 240 S570 180 700 270 S820 330 900 230"
                      fill="none"
                      stroke="#48656d"
                      strokeWidth="1"
                    />
                    <path
                      d="M0 340 C130 260 250 400 390 320 S570 270 720 350 S820 400 900 310"
                      fill="none"
                      stroke="#48656d"
                      strokeWidth="1"
                    />

                    {/* river */}
                    <path
                      d="M130 0 C190 70 160 120 250 170 C330 215 290 270 390 300 C470 325 510 390 570 430"
                      fill="none"
                      stroke="#22d3ee"
                      strokeWidth="3"
                      opacity="0.55"
                    />
                  </svg>

                  {/* Map label */}
                  <div className="absolute left-5 top-5 rounded border border-[#31454c] bg-[#081016]/80 px-3 py-2 backdrop-blur-sm">
                    <p className="text-[10px] text-slate-500">
                      STUDY AREA
                    </p>
                    <p className="mt-1 text-xs text-slate-200">
                      30.50°N — 30.80°N
                    </p>
                    <p className="text-xs text-slate-200">
                      79.40°E — 79.75°E
                    </p>
                  </div>

                  {/* Joshimath */}
                  <div className="absolute left-[28%] top-[24%]">
                    <div className="relative">
                      <div className="absolute -inset-3 animate-pulse rounded-full bg-red-500/10"></div>
                      <div className="relative h-4 w-4 rounded-full border-2 border-red-300 bg-red-500 shadow-[0_0_18px_rgba(248,113,113,0.7)]"></div>
                    </div>

                    <div className="mt-2 whitespace-nowrap text-xs font-medium">
                      Joshimath
                    </div>

                    <div className="text-[10px] text-red-400">
                      CRITICAL · 91
                    </div>
                  </div>

                  {/* Vishnuprayag */}
                  <div className="absolute left-[43%] top-[47%]">
                    <div className="h-4 w-4 rounded-full border-2 border-orange-300 bg-orange-400 shadow-[0_0_15px_rgba(251,146,60,0.6)]"></div>

                    <div className="mt-2 whitespace-nowrap text-xs font-medium">
                      Vishnuprayag
                    </div>

                    <div className="text-[10px] text-orange-400">
                      HIGH · 78
                    </div>
                  </div>

                  {/* Govindghat */}
                  <div className="absolute left-[57%] top-[63%]">
                    <div className="h-3.5 w-3.5 rounded-full border-2 border-yellow-200 bg-yellow-400"></div>

                    <div className="mt-2 whitespace-nowrap text-xs font-medium">
                      Govindghat
                    </div>

                    <div className="text-[10px] text-yellow-400">
                      MODERATE · 64
                    </div>
                  </div>

                  {/* Badrinath */}
                  <div className="absolute right-[17%] top-[29%]">
                    <div className="h-3.5 w-3.5 rounded-full border-2 border-yellow-200 bg-yellow-400"></div>

                    <div className="mt-2 whitespace-nowrap text-xs font-medium">
                      Badrinath
                    </div>

                    <div className="text-[10px] text-yellow-400">
                      MODERATE · 58
                    </div>
                  </div>

                  {/* North */}
                  <div className="absolute right-5 top-5 flex h-9 w-9 items-center justify-center rounded border border-[#31454c] bg-[#081016]/70 text-xs text-slate-400">
                    N
                  </div>

                  {/* Map controls */}
                  <div className="absolute bottom-5 left-5 flex overflow-hidden rounded border border-[#31454c] bg-[#081016]/90">
                    <button className="px-3 py-2 text-sm text-slate-300 hover:bg-white/5">
                      +
                    </button>
                    <button className="border-l border-[#31454c] px-3 py-2 text-sm text-slate-300 hover:bg-white/5">
                      −
                    </button>
                  </div>

                </div>
              </div>

              {/* ALERT PANEL */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920]">

                <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">
                  <h3 className="text-sm font-medium">
                    Active Alerts
                  </h3>

                  <span className="rounded-full bg-red-400/10 px-2 py-1 text-[10px] text-red-400">
                    3 ACTIVE
                  </span>
                </div>

                <div className="divide-y divide-[#1c3038]">
                  {alerts.map((alert) => (
                    <div
                      key={alert.title}
                      className="p-4"
                    >
                      <div className="flex items-center justify-between">
                        <span
                          className={`text-[9px] font-semibold tracking-wider ${
                            alert.level === "CRITICAL"
                              ? "text-red-400"
                              : alert.level === "HIGH"
                              ? "text-orange-400"
                              : "text-yellow-400"
                          }`}
                        >
                          {alert.level}
                        </span>

                        <span className="text-[9px] text-slate-600">
                          {alert.time}
                        </span>
                      </div>

                      <p className="mt-2 text-xs font-medium text-slate-200">
                        {alert.title}
                      </p>

                      <p className="mt-1 text-[10px] text-slate-500">
                        {alert.place}
                      </p>
                    </div>
                  ))}
                </div>

                <button className="m-4 w-[calc(100%-32px)] rounded border border-[#293d44] py-2 text-[10px] text-slate-400 hover:bg-white/5 hover:text-white">
                  VIEW ALL ALERTS
                </button>
              </div>

            </div>

            {/* BOTTOM SECTION */}
            <div className="mt-5 grid grid-cols-2 gap-5">

              {/* SETTLEMENT RISK */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920]">

                <div className="border-b border-[#1c3038] px-4 py-3">
                  <h3 className="text-sm font-medium">
                    Highest Risk Settlements
                  </h3>

                  <p className="mt-1 text-[10px] text-slate-500">
                    Current settlement-level risk assessment
                  </p>
                </div>

                <div className="p-4">
                  {settlements.map((settlement, index) => (
                    <div
                      key={settlement.name}
                      className="mb-4 last:mb-0"
                    >
                      <div className="mb-1.5 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="w-4 text-[10px] text-slate-600">
                            0{index + 1}
                          </span>

                          <span className="text-xs text-slate-300">
                            {settlement.name}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
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

                          <span className="w-6 text-right text-xs font-medium">
                            {settlement.score}
                          </span>
                        </div>
                      </div>

                      <div className="ml-7 h-1.5 rounded-full bg-[#1b2930]">
                        <div
                          className={`h-full rounded-full ${
                            settlement.level === "CRITICAL"
                              ? "w-[91%] bg-red-400"
                              : settlement.level === "HIGH"
                              ? "w-[78%] bg-orange-400"
                              : "w-[64%] bg-yellow-400"
                          }`}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* HAZARD DISTRIBUTION */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920]">

                <div className="border-b border-[#1c3038] px-4 py-3">
                  <h3 className="text-sm font-medium">
                    Hazard Distribution
                  </h3>

                  <p className="mt-1 text-[10px] text-slate-500">
                    Current contribution to corridor risk
                  </p>
                </div>

                <div className="space-y-5 p-5">

                  <div>
                    <div className="mb-2 flex justify-between">
                      <span className="text-xs text-slate-300">
                        Flood
                      </span>
                      <span className="text-xs text-slate-500">
                        42%
                      </span>
                    </div>

                    <div className="h-2 rounded-full bg-[#1b2930]">
                      <div className="h-full w-[42%] rounded-full bg-cyan-400"></div>
                    </div>
                  </div>

                  <div>
                    <div className="mb-2 flex justify-between">
                      <span className="text-xs text-slate-300">
                        Landslide
                      </span>
                      <span className="text-xs text-slate-500">
                        34%
                      </span>
                    </div>

                    <div className="h-2 rounded-full bg-[#1b2930]">
                      <div className="h-full w-[34%] rounded-full bg-orange-400"></div>
                    </div>
                  </div>

                  <div>
                    <div className="mb-2 flex justify-between">
                      <span className="text-xs text-slate-300">
                        Upstream / GLOF indicators
                      </span>
                      <span className="text-xs text-slate-500">
                        24%
                      </span>
                    </div>

                    <div className="h-2 rounded-full bg-[#1b2930]">
                      <div className="h-full w-[24%] rounded-full bg-purple-400"></div>
                    </div>
                  </div>

                  <div className="mt-3 border-t border-[#1c3038] pt-4">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] uppercase tracking-wider text-slate-600">
                        Risk Engine
                      </span>

                      <span className="flex items-center gap-2 text-[10px] text-emerald-400">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                        PROCESSING
                      </span>
                    </div>
                  </div>

                </div>
              </div>

            </div>

            {/* FOOTER */}
            <div className="mt-5 flex items-center justify-between border-t border-[#1c3038] pt-4">
              <p className="text-[9px] text-slate-600">
                TRINETRA · Terrain Risk Intelligence & Early-warning Network
              </p>

              <p className="text-[9px] text-slate-600">
                DEMO DATA · Replace with live backend feeds
              </p>
            </div>

          </div>
        </section>
      </div>
    </main>
  );
}
