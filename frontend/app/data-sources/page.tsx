const sources = [
  {
    source: "Sentinel-1 SAR",
    provider: "Copernicus / ESA",
    type: "Satellite",
    update: "5–12 days",
    coverage: "Corridor AOI",
    status: "AVAILABLE",
    use: "Surface disturbance, water-body change, terrain anomaly",
  },
  {
    source: "Sentinel-2",
    provider: "Copernicus / ESA",
    type: "Satellite",
    update: "5 days",
    coverage: "Corridor AOI",
    status: "AVAILABLE",
    use: "Vegetation, water and land-cover change",
  },
  {
    source: "SRTM DEM",
    provider: "NASA / USGS",
    type: "Terrain",
    update: "Static",
    coverage: "30 m",
    status: "AVAILABLE",
    use: "Elevation, slope, drainage and terrain features",
  },
  {
    source: "NRSC Landslide Atlas",
    provider: "ISRO / NRSC",
    type: "Historical",
    update: "Periodic",
    coverage: "India",
    status: "AVAILABLE",
    use: "Historical landslide inventory and model labels",
  },
  {
    source: "CHIRPS Rainfall",
    provider: "Climate Hazards Center",
    type: "Rainfall",
    update: "Daily",
    coverage: "0.05°",
    status: "AVAILABLE",
    use: "Rainfall accumulation and anomaly features",
  },
  {
    source: "CWC River Telemetry",
    provider: "Central Water Commission",
    type: "Hydrology",
    update: "Hourly",
    coverage: "Stations",
    status: "CONNECTED",
    use: "River level, discharge and rate-of-rise indicators",
  },
  {
    source: "NRSC Historical Flood",
    provider: "ISRO / NRSC",
    type: "Historical",
    update: "Periodic",
    coverage: "India",
    status: "AVAILABLE",
    use: "Historical flood inundation and exposure analysis",
  },
  {
    source: "Glacial Lake Atlas",
    provider: "ISRO / NRSC",
    type: "Inventory",
    update: "Baseline",
    coverage: "Himalayan region",
    status: "AVAILABLE",
    use: "Glacial lake baseline and upstream anomaly analysis",
  },
  {
    source: "ESA WorldCover",
    provider: "ESA / Copernicus",
    type: "Land Cover",
    update: "Annual",
    coverage: "10 m",
    status: "AVAILABLE",
    use: "Land-use and suitability screening",
  },
  {
    source: "Census 2011",
    provider: "Government of India",
    type: "Population",
    update: "Historical",
    coverage: "Village level",
    status: "AVAILABLE",
    use: "Population, households and vulnerability indicators",
  },
  {
    source: "OpenStreetMap",
    provider: "OpenStreetMap",
    type: "Infrastructure",
    update: "Variable",
    coverage: "Corridor",
    status: "AVAILABLE",
    use: "Roads, bridges and accessibility analysis",
  },
  {
    source: "WorldPop",
    provider: "WorldPop",
    type: "Population Grid",
    update: "Annual",
    coverage: "100 m",
    status: "AVAILABLE",
    use: "Spatial population distribution",
  },
];

const pipeline = [
  {
    step: "01",
    title: "Acquire",
    description: "Collect satellite, terrain, rainfall, hydrology and exposure data.",
  },
  {
    step: "02",
    title: "Validate",
    description: "Check coverage, timestamps, missing values and spatial consistency.",
  },
  {
    step: "03",
    title: "Transform",
    description: "Generate terrain, rainfall, water-change and anomaly features.",
  },
  {
    step: "04",
    title: "Model",
    description: "Feed validated features into hazard and settlement risk models.",
  },
  {
    step: "05",
    title: "Decide",
    description: "Use risk, capacity and infrastructure data for response planning.",
  },
];

export default function DataSourcesPage() {
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

          {/* SYSTEM */}
          <p className="mb-3 mt-8 px-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-600">
            System
          </p>

          <nav>
            <a
              href="/data-sources"
              className="flex items-center gap-3 rounded-md border border-cyan-400/20 bg-cyan-400/10 px-3 py-2.5 text-sm text-cyan-300"
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
              Data reliability layer monitoring source availability
            </p>

          </div>

        </aside>

        {/* MAIN */}
        <section className="flex-1">

          {/* HEADER */}
          <header className="flex h-[68px] items-center justify-between border-b border-[#1c3038] bg-[#0b151b] px-6">

            <div>
              <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">
                System
              </p>

              <h2 className="mt-1 text-lg font-medium">
                Data Sources
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Source inventory, reliability and feature pipeline
              </p>
            </div>

            <div className="flex items-center gap-4">

              <div className="text-right">
                <p className="text-[9px] uppercase tracking-wider text-slate-600">
                  Primary AOI
                </p>

                <p className="mt-1 text-xs text-slate-400">
                  Joshimath → Vishnuprayag → Badrinath
                </p>
              </div>

              <div className="flex items-center gap-2 rounded-md border border-emerald-400/20 bg-emerald-400/5 px-3 py-2">

                <span className="h-2 w-2 rounded-full bg-emerald-400"></span>

                <span className="text-xs text-emerald-300">
                  DATA LAYER ACTIVE
                </span>

              </div>

            </div>

          </header>

          {/* CONTENT */}
          <div className="p-5">

            {/* SUMMARY */}
            <div className="grid grid-cols-4 gap-4">

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Data Sources
                </p>

                <p className="mt-2 text-4xl font-semibold text-cyan-300">
                  12
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  currently defined
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Available
                </p>

                <p className="mt-2 text-4xl font-semibold text-emerald-400">
                  11
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  accessible for pipeline use
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Connected
                </p>

                <p className="mt-2 text-4xl font-semibold text-cyan-300">
                  1
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  operational telemetry source
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Pipeline Health
                </p>

                <p className="mt-2 text-4xl font-semibold text-emerald-400">
                  94%
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  validation pass rate
                </p>

              </div>

            </div>

            {/* PIPELINE */}
            <div className="mt-5 rounded-lg border border-[#1c3038] bg-[#0d1920]">

              <div className="border-b border-[#1c3038] px-5 py-4">

                <h3 className="text-sm font-medium">
                  TRINETRA Data Pipeline
                </h3>

                <p className="mt-1 text-[10px] text-slate-500">
                  From raw observations to operational decisions
                </p>

              </div>

              <div className="grid grid-cols-5 gap-3 p-5">

                {pipeline.map((item, index) => (

                  <div
                    key={item.step}
                    className="relative rounded-md border border-[#1c3038] bg-[#0a151b] p-4"
                  >

                    <p className="text-[9px] font-semibold text-cyan-400">
                      {item.step}
                    </p>

                    <h4 className="mt-2 text-sm font-medium">
                      {item.title}
                    </h4>

                    <p className="mt-2 text-[10px] leading-5 text-slate-500">
                      {item.description}
                    </p>

                    {index < pipeline.length - 1 && (
                      <span className="absolute -right-3 top-1/2 z-10 text-cyan-400">
                        →
                      </span>
                    )}

                  </div>

                ))}

              </div>

            </div>

            {/* DATA TABLE */}
            <div className="mt-5 rounded-lg border border-[#1c3038] bg-[#0d1920]">

              <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-4">

                <div>
                  <h3 className="text-sm font-medium">
                    Source Registry
                  </h3>

                  <p className="mt-1 text-[10px] text-slate-500">
                    Current source definitions for the TRINETRA corridor
                  </p>
                </div>

                <button className="rounded border border-[#293d44] px-3 py-1.5 text-[10px] text-slate-400 hover:bg-white/5 hover:text-white">
                  REFRESH STATUS
                </button>

              </div>

              <div className="overflow-x-auto">

                <table className="w-full text-left">

                  <thead className="border-b border-[#1c3038]">

                    <tr className="text-[9px] uppercase tracking-wider text-slate-600">

                      <th className="px-4 py-3 font-medium">
                        Source
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Provider
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Type
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Update
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Coverage
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Used For
                      </th>

                      <th className="px-4 py-3 text-right font-medium">
                        Status
                      </th>

                    </tr>

                  </thead>

                  <tbody className="divide-y divide-[#1c3038]">

                    {sources.map((source) => (

                      <tr
                        key={source.source}
                        className="hover:bg-white/[0.02]"
                      >

                        <td className="px-4 py-3">

                          <span className="text-xs font-medium text-slate-200">
                            {source.source}
                          </span>

                        </td>

                        <td className="px-4 py-3 text-xs text-slate-500">
                          {source.provider}
                        </td>

                        <td className="px-4 py-3">

                          <span className="rounded border border-[#293d44] bg-[#101d23] px-2 py-1 text-[9px] text-slate-400">
                            {source.type}
                          </span>

                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {source.update}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {source.coverage}
                        </td>

                        <td className="max-w-[280px] px-4 py-3 text-xs leading-5 text-slate-500">
                          {source.use}
                        </td>

                        <td className="px-4 py-3 text-right">

                          <span
                            className={`rounded px-2 py-1 text-[9px] ${
                              source.status === "CONNECTED"
                                ? "bg-cyan-400/10 text-cyan-300"
                                : "bg-emerald-400/10 text-emerald-400"
                            }`}
                          >
                            {source.status}
                          </span>

                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            </div>

            {/* RELIABILITY */}
            <div className="mt-5 grid grid-cols-3 gap-4">

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Live vs Periodic
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  Sources are classified by actual update behaviour. Only
                  integrated operational feeds are shown as connected.
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Data Validation
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  Timestamp, spatial coverage, missing values and consistency
                  checks are applied before model features are generated.
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Model Readiness
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  Validated observations are transformed into features used by
                  hazard prediction, risk scoring and relocation planning.
                </p>

              </div>

            </div>

            {/* AOI */}
            <div className="mt-5 rounded-lg border border-cyan-400/20 bg-cyan-400/5 p-4">

              <div className="flex items-center justify-between">

                <div>
                  <p className="text-[9px] uppercase tracking-wider text-cyan-300">
                    Primary Study Area
                  </p>

                  <p className="mt-2 text-sm font-medium">
                    Joshimath → Vishnuprayag → Badrinath Corridor
                  </p>

                  <p className="mt-1 text-[10px] text-slate-500">
                    30.50–30.80°N · 79.40–79.75°E
                  </p>
                </div>

                <div className="text-right">

                  <p className="text-[9px] text-slate-600">
                    DATA POLICY
                  </p>

                  <p className="mt-1 text-[10px] text-slate-400">
                    Source status shown separately from model confidence
                  </p>

                </div>

              </div>

            </div>

            {/* FOOTER */}
            <div className="mt-5 flex items-center justify-between border-t border-[#1c3038] pt-4">

              <p className="text-[9px] text-slate-600">
                TRINETRA · Data Reliability Layer
              </p>

              <p className="text-[9px] text-slate-600">
                DEMO DATA · Replace status with actual pipeline telemetry
              </p>

            </div>

          </div>

        </section>

      </div>
    </main>
  );
}