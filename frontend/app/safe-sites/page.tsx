const sites = [
  {
    id: "A",
    name: "Auli Road",
    location: "Joshimath",
    distance: "4.2 km",
    score: 86,
    capacity: 1200,
    available: 980,
    flood: 18,
    landslide: 24,
    access: 91,
    status: "LOW",
    x: "28%",
    y: "38%",
  },
  {
    id: "B",
    name: "Govindghat",
    location: "Govindghat",
    distance: "6.8 km",
    score: 79,
    capacity: 900,
    available: 620,
    flood: 27,
    landslide: 31,
    access: 84,
    status: "LOW",
    x: "49%",
    y: "54%",
  },
  {
    id: "C",
    name: "Pandukeshwar",
    location: "Pandukeshwar",
    distance: "11.5 km",
    score: 72,
    capacity: 760,
    available: 510,
    flood: 34,
    landslide: 38,
    access: 76,
    status: "MODERATE",
    x: "67%",
    y: "66%",
  },
  {
    id: "D",
    name: "Lower Valley",
    location: "Joshimath",
    distance: "5.6 km",
    score: 61,
    capacity: 540,
    available: 310,
    flood: 48,
    landslide: 44,
    access: 69,
    status: "MODERATE",
    x: "14%",
    y: "74%",
  },
];

const selectedSite = sites[0];

export default function SafeSitesPage() {
  return (
    <main className="min-h-screen bg-[#081016] text-white">
      <div className="flex min-h-screen">

        {/* SIDEBAR */}
        <aside className="w-[230px] shrink-0 border-r border-[#1c3038] bg-[#0b151b] px-4 py-5">

          {/* BRAND */}
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

          {/* MONITORING */}
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
              className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"
            >
              <span>◆</span>
              Risk Intelligence
            </a>

            <a
              href="/safe-sites"
              className="flex items-center gap-3 rounded-md border border-cyan-400/20 bg-cyan-400/10 px-3 py-2.5 text-sm text-cyan-300"
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

          {/* SYSTEM */}
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

          {/* STATUS CARD */}
          <div className="mt-12 rounded-md border border-[#1c3038] bg-[#0e1b22] p-3">

            <div className="mb-2 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400"></span>

              <span className="text-xs text-emerald-300">
                SYSTEM OPERATIONAL
              </span>
            </div>

            <p className="text-[10px] leading-4 text-slate-500">
              Safe-site screening engine processing current corridor data
            </p>

          </div>

        </aside>

        {/* MAIN CONTENT */}
        <section className="flex-1">

          {/* HEADER */}
          <header className="flex h-[68px] items-center justify-between border-b border-[#1c3038] bg-[#0b151b] px-6">

            <div>
              <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">
                Site Assessment
              </p>

              <h2 className="mt-1 text-lg font-medium">
                Safe Sites & Capacity
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Safer land identification and realistic carrying capacity
              </p>
            </div>

            <div className="flex items-center gap-5">

              <div className="flex items-center gap-2 rounded-md border border-emerald-400/20 bg-emerald-400/5 px-3 py-2">
                <span className="h-2 w-2 rounded-full bg-emerald-400"></span>

                <span className="text-xs text-emerald-300">
                  SCREENING ENGINE ACTIVE
                </span>
              </div>

            </div>

          </header>

          {/* PAGE CONTENT */}
          <div className="p-5">

            {/* TOP SUMMARY */}
            <div className="grid grid-cols-4 gap-4">

              {/* CANDIDATE SITES */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Candidate Sites
                </p>

                <p className="mt-2 text-4xl font-semibold text-cyan-300">
                  14
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  within study corridor
                </p>

              </div>

              {/* LOW RISK */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Low-Risk Sites
                </p>

                <p className="mt-2 text-4xl font-semibold text-emerald-400">
                  6
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  passed hazard screening
                </p>

              </div>

              {/* CAPACITY */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Estimated Capacity
                </p>

                <p className="mt-2 text-4xl font-semibold text-cyan-300">
                  4,210
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  people across screened sites
                </p>

              </div>

              {/* BEST SCORE */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Best Safety Score
                </p>

                <p className="mt-2 text-4xl font-semibold text-cyan-300">
                  86
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  Site A — Auli Road
                </p>

              </div>

            </div>

            {/* MAP + SELECTED SITE */}
            <div className="mt-5 grid grid-cols-[1fr_390px] gap-5">

              {/* MAP */}
              <div className="overflow-hidden rounded-lg border border-[#1c3038] bg-[#0b171d]">

                <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">

                  <div>
                    <h3 className="text-sm font-medium">
                      Candidate Site Screening Map
                    </h3>

                    <p className="mt-0.5 text-[10px] text-slate-500">
                      Hazard-screened locations across the monitored corridor
                    </p>
                  </div>

                  <span className="text-[10px] text-slate-500">
                    14 SITES
                  </span>

                </div>

                {/* MOCK MAP */}
                <div className="relative h-[390px] overflow-hidden bg-[#0a191f]">

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
                    viewBox="0 0 900 390"
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

                    <path
                      d="M0 335 C130 260 230 390 380 315 S570 270 720 350 S830 390 900 305"
                      fill="none"
                      stroke="#48656d"
                      strokeWidth="1"
                    />

                    {/* RIVER */}
                    <path
                      d="M720 0 C680 80 720 120 650 170 C590 215 620 260 540 300 C480 330 450 360 410 390"
                      fill="none"
                      stroke="#22d3ee"
                      strokeWidth="3"
                      opacity="0.5"
                    />

                    {/* ACCESS ROAD */}
                    <path
                      d="M110 390 C220 330 300 300 400 270 C520 235 620 205 760 170"
                      fill="none"
                      stroke="#c49b4a"
                      strokeWidth="2"
                      strokeDasharray="8 7"
                      opacity="0.6"
                    />

                  </svg>

                  {/* STUDY AREA */}
                  <div className="absolute right-5 top-5 rounded border border-[#31454c] bg-[#081016]/90 px-3 py-2">

                    <p className="text-[9px] text-slate-500">
                      AOI
                    </p>

                    <p className="mt-1 text-[10px] text-slate-300">
                      30.50–30.80°N / 79.40–79.75°E
                    </p>

                  </div>

                  {/* SITE MARKERS */}
                  {sites.map((site) => (
                    <div
                      key={site.id}
                      className="absolute"
                      style={{
                        left: site.x,
                        top: site.y,
                      }}
                    >

                      <div
                        className={`flex h-12 w-12 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border-2 text-sm font-semibold ${
                          site.id === "A"
                            ? "border-emerald-400 bg-[#0b2926] text-emerald-300 shadow-[0_0_18px_rgba(52,211,153,0.25)]"
                            : site.status === "LOW"
                            ? "border-emerald-400 bg-[#0b2926] text-emerald-300"
                            : "border-yellow-400 bg-[#302b0b] text-yellow-300"
                        }`}
                      >
                        {site.id}
                      </div>

                      <p className="mt-1 -translate-x-1/2 whitespace-nowrap text-[9px] uppercase tracking-wider text-slate-400">
                        {site.name}
                      </p>

                    </div>
                  ))}

                  {/* MAP INFO */}
                  <div className="absolute bottom-4 left-4 rounded border border-[#31454c] bg-[#081016]/90 px-3 py-2">

                    <p className="text-[9px] text-slate-600">
                      SCREENING ENGINE
                    </p>

                    <p className="mt-1 text-[10px] text-emerald-400">
                      ● HAZARD FILTER ACTIVE
                    </p>

                  </div>

                  {/* NORTH */}
                  <div className="absolute right-5 bottom-5 flex h-9 w-9 items-center justify-center rounded border border-[#31454c] bg-[#081016]/80 text-xs text-slate-400">
                    N
                  </div>

                </div>

              </div>

              {/* SELECTED SITE */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920]">

                <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">

                  <h3 className="text-sm font-medium">
                    Selected Site
                  </h3>

                  <span className="text-[10px] text-emerald-400">
                    LOW
                  </span>

                </div>

                <div className="p-5">

                  <h2 className="text-2xl font-semibold">
                    Site A — Auli Road
                  </h2>

                  <p className="mt-2 text-xs text-slate-500">
                    Joshimath · 4.2 km from corridor
                  </p>

                  {/* SCORE */}
                  <div className="mt-6 flex items-center gap-5">

                    <div className="flex h-[118px] w-[118px] items-center justify-center rounded-full border-[7px] border-emerald-400">

                      <div className="text-center">
                        <p className="text-3xl font-semibold">
                          86
                        </p>

                        <p className="text-[9px] text-slate-500">
                          / 100
                        </p>
                      </div>

                    </div>

                    <div>
                      <p className="text-[10px] text-slate-500">
                        OVERALL SAFETY SCORE
                      </p>

                      <p className="mt-2 text-sm font-medium text-emerald-400">
                        Suitable for detailed assessment
                      </p>
                    </div>

                  </div>

                  {/* CAPACITY */}
                  <div className="mt-7 border-t border-[#1c3038] pt-5">

                    <p className="text-[10px] uppercase tracking-wider text-slate-500">
                      Sustainable Capacity
                    </p>

                    <div className="mt-2 flex items-end justify-between">

                      <p className="text-3xl font-semibold">
                        1,200
                      </p>

                      <p className="text-xs text-emerald-400">
                        980 available
                      </p>

                    </div>

                    <div className="mt-3 h-2 rounded-full bg-[#1b2930]">

                      <div className="h-full w-[82%] rounded-full bg-cyan-400"></div>

                    </div>

                    <div className="mt-2 flex justify-between text-[9px] text-slate-600">
                      <span>Current allocation</span>
                      <span>Maximum sustainable capacity</span>
                    </div>

                  </div>

                  {/* SITE FACTORS */}
                  <div className="mt-6 border-t border-[#1c3038] pt-5">

                    <p className="text-[10px] uppercase tracking-wider text-slate-500">
                      Screening Factors
                    </p>

                    <div className="mt-4 space-y-4">

                      {/* FLOOD */}
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-300">
                            Flood exposure
                          </span>

                          <span className="text-xs text-emerald-400">
                            18
                          </span>
                        </div>

                        <div className="mt-2 h-1.5 rounded-full bg-[#1b2930]">
                          <div className="h-full w-[18%] rounded-full bg-emerald-400"></div>
                        </div>
                      </div>

                      {/* LANDSLIDE */}
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-300">
                            Landslide susceptibility
                          </span>

                          <span className="text-xs text-emerald-400">
                            24
                          </span>
                        </div>

                        <div className="mt-2 h-1.5 rounded-full bg-[#1b2930]">
                          <div className="h-full w-[24%] rounded-full bg-emerald-400"></div>
                        </div>
                      </div>

                      {/* ACCESS */}
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-300">
                            Road accessibility
                          </span>

                          <span className="text-xs text-cyan-300">
                            91
                          </span>
                        </div>

                        <div className="mt-2 h-1.5 rounded-full bg-[#1b2930]">
                          <div className="h-full w-[91%] rounded-full bg-cyan-400"></div>
                        </div>
                      </div>

                    </div>

                  </div>

                  {/* RECOMMENDATION */}
                  <div className="mt-6 rounded border border-emerald-400/20 bg-emerald-400/5 p-3">

                    <p className="text-[9px] uppercase tracking-wider text-emerald-400">
                      Screening Recommendation
                    </p>

                    <p className="mt-2 text-xs leading-5 text-slate-300">
                      Site passes preliminary hazard screening and can be
                      considered for detailed ground verification.
                    </p>

                  </div>

                </div>

              </div>

            </div>

            {/* SITE TABLE */}
            <div className="mt-5 rounded-lg border border-[#1c3038] bg-[#0d1920]">

              <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">

                <div>
                  <h3 className="text-sm font-medium">
                    Candidate Site Assessment
                  </h3>

                  <p className="mt-1 text-[10px] text-slate-500">
                    Safety, hazard exposure and capacity comparison
                  </p>
                </div>

                <button className="rounded border border-[#293d44] px-3 py-1.5 text-[10px] text-slate-400 hover:bg-white/5 hover:text-white">
                  VIEW ALL SITES
                </button>

              </div>

              <div className="overflow-x-auto">

                <table className="w-full text-left">

                  <thead className="border-b border-[#1c3038]">

                    <tr className="text-[9px] uppercase tracking-wider text-slate-600">

                      <th className="px-4 py-3 font-medium">
                        Site
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Location
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Flood
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Landslide
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Capacity
                      </th>

                      <th className="px-4 py-3 text-right font-medium">
                        Safety Score
                      </th>

                    </tr>

                  </thead>

                  <tbody className="divide-y divide-[#1c3038]">

                    {sites.map((site) => (

                      <tr
                        key={site.id}
                        className="hover:bg-white/[0.02]"
                      >

                        <td className="px-4 py-3">

                          <div className="flex items-center gap-3">

                            <span
                              className={`flex h-7 w-7 items-center justify-center rounded-full border text-[10px] font-semibold ${
                                site.status === "LOW"
                                  ? "border-emerald-400/40 bg-emerald-400/10 text-emerald-400"
                                  : "border-yellow-400/40 bg-yellow-400/10 text-yellow-400"
                              }`}
                            >
                              {site.id}
                            </span>

                            <span className="text-xs text-slate-200">
                              {site.name}
                            </span>

                          </div>

                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {site.location}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {site.flood}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {site.landslide}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {site.capacity.toLocaleString()}
                        </td>

                        <td className="px-4 py-3 text-right">

                          <div className="flex items-center justify-end gap-3">

                            <span
                              className={`text-[9px] ${
                                site.status === "LOW"
                                  ? "text-emerald-400"
                                  : "text-yellow-400"
                              }`}
                            >
                              {site.status}
                            </span>

                            <span className="text-sm font-medium">
                              {site.score}
                            </span>

                          </div>

                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            </div>

            {/* CAPACITY LOGIC */}
            <div className="mt-5 grid grid-cols-3 gap-4">

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Hazard Screening
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  High flood, landslide and upstream hazard zones are excluded
                  before capacity estimation.
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Infrastructure
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  Road access, water availability and essential facilities
                  influence the usable capacity of each site.
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Sustainable Capacity
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  Capacity represents a planning estimate rather than simply
                  the maximum number of people that can physically fit.
                </p>

              </div>

            </div>

            {/* FOOTER */}
            <div className="mt-5 flex items-center justify-between border-t border-[#1c3038] pt-4">

              <p className="text-[9px] text-slate-600">
                TRINETRA · Safe Sites & Capacity
              </p>

              <p className="text-[9px] text-slate-600">
                DEMO DATA · Replace with screening output
              </p>

            </div>

          </div>

        </section>

      </div>
    </main>
  );
}