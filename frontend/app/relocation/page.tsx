const relocationOptions = [
  {
    id: "R-01",
    source: "Joshimath",
    destination: "Site A — Auli Road",
    people: 980,
    distance: "4.2 km",
    safetyGain: "+82%",
    capacity: "980 / 1,200",
    cost: "₹18.4 L",
    status: "RECOMMENDED",
  },
  {
    id: "R-02",
    source: "Joshimath",
    destination: "Site B — Govindghat",
    people: 620,
    distance: "6.8 km",
    safetyGain: "+71%",
    capacity: "620 / 900",
    cost: "₹21.7 L",
    status: "ALTERNATIVE",
  },
  {
    id: "R-03",
    source: "Vishnuprayag",
    destination: "Site B — Govindghat",
    people: 420,
    distance: "5.1 km",
    safetyGain: "+64%",
    capacity: "420 / 900",
    cost: "₹14.2 L",
    status: "ALTERNATIVE",
  },
];

export default function RelocationPage() {
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

          </nav>

          {/* RESPONSE */}
          <p className="mb-3 mt-8 px-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-600">
            Response
          </p>

          <nav>
            <a
              href="/relocation"
              className="flex items-center gap-3 rounded-md border border-cyan-400/20 bg-cyan-400/10 px-3 py-2.5 text-sm text-cyan-300"
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
              Relocation optimizer processing current corridor conditions
            </p>

          </div>

        </aside>

        {/* MAIN */}
        <section className="flex-1">

          {/* HEADER */}
          <header className="flex h-[68px] items-center justify-between border-b border-[#1c3038] bg-[#0b151b] px-6">

            <div>
              <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">
                Emergency Response
              </p>

              <h2 className="mt-1 text-lg font-medium">
                Relocation Optimizer
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Risk-aware relocation planning under capacity and access constraints
              </p>
            </div>

            <div className="flex items-center gap-2 rounded-md border border-emerald-400/20 bg-emerald-400/5 px-3 py-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400"></span>

              <span className="text-xs text-emerald-300">
                OPTIMIZER READY
              </span>
            </div>

          </header>

          {/* CONTENT */}
          <div className="p-5">

            {/* SUMMARY CARDS */}
            <div className="grid grid-cols-4 gap-4">

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Settlements Prioritized
                </p>

                <p className="mt-2 text-4xl font-semibold text-cyan-300">
                  7
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  high / critical risk
                </p>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  People Requiring Action
                </p>

                <p className="mt-2 text-4xl font-semibold text-orange-400">
                  2,020
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  across priority settlements
                </p>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Available Capacity
                </p>

                <p className="mt-2 text-4xl font-semibold text-emerald-400">
                  4,210
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  screened safe-site capacity
                </p>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-5">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Recommended Plans
                </p>

                <p className="mt-2 text-4xl font-semibold text-cyan-300">
                  3
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  feasible relocation options
                </p>
              </div>

            </div>

            {/* HERO WORKFLOW */}
            <div className="mt-5 grid grid-cols-[1fr_360px] gap-5">

              {/* RELOCATION FLOW */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920]">

                <div className="flex items-center justify-between border-b border-[#1c3038] px-5 py-4">

                  <div>
                    <h3 className="text-sm font-medium">
                      Relocation Decision Flow
                    </h3>

                    <p className="mt-1 text-[10px] text-slate-500">
                      From vulnerable settlement to screened relocation site
                    </p>
                  </div>

                  <span className="text-[10px] text-emerald-400">
                    PLAN R-01
                  </span>

                </div>

                <div className="p-5">

                  {/* SOURCE */}
                  <div className="rounded-md border border-red-400/20 bg-red-400/5 p-4">

                    <div className="flex items-center justify-between">

                      <div>
                        <p className="text-[9px] uppercase tracking-wider text-red-400">
                          SOURCE SETTLEMENT
                        </p>

                        <h3 className="mt-2 text-xl font-semibold">
                          Joshimath
                        </h3>

                        <p className="mt-1 text-xs text-slate-500">
                          Critical risk · 980 people prioritized
                        </p>
                      </div>

                      <div className="text-right">

                        <p className="text-3xl font-semibold text-red-400">
                          91
                        </p>

                        <p className="text-[9px] text-slate-500">
                          RISK SCORE
                        </p>

                      </div>

                    </div>

                  </div>

                  {/* ARROW */}
                  <div className="flex items-center justify-center py-4">

                    <div className="flex items-center gap-3">

                      <div className="h-px w-12 bg-[#30444c]"></div>

                      <div className="flex h-9 w-9 items-center justify-center rounded-full border border-cyan-400/30 bg-cyan-400/10 text-cyan-300">
                        ↓
                      </div>

                      <div className="h-px w-12 bg-[#30444c]"></div>

                    </div>

                  </div>

                  {/* DESTINATION */}
                  <div className="rounded-md border border-emerald-400/20 bg-emerald-400/5 p-4">

                    <div className="flex items-center justify-between">

                      <div>
                        <p className="text-[9px] uppercase tracking-wider text-emerald-400">
                          RECOMMENDED DESTINATION
                        </p>

                        <h3 className="mt-2 text-xl font-semibold">
                          Site A — Auli Road
                        </h3>

                        <p className="mt-1 text-xs text-slate-500">
                          Low risk · 980 available capacity
                        </p>
                      </div>

                      <div className="text-right">

                        <p className="text-3xl font-semibold text-emerald-400">
                          86
                        </p>

                        <p className="text-[9px] text-slate-500">
                          SAFETY SCORE
                        </p>

                      </div>

                    </div>

                  </div>

                  {/* FLOW FACTORS */}
                  <div className="mt-5 grid grid-cols-4 gap-3">

                    <div className="rounded border border-[#1c3038] bg-[#0a151b] p-3">
                      <p className="text-[9px] text-slate-600">
                        SAFETY GAIN
                      </p>

                      <p className="mt-1 text-sm font-medium text-emerald-400">
                        +82%
                      </p>
                    </div>

                    <div className="rounded border border-[#1c3038] bg-[#0a151b] p-3">
                      <p className="text-[9px] text-slate-600">
                        DISTANCE
                      </p>

                      <p className="mt-1 text-sm font-medium">
                        4.2 km
                      </p>
                    </div>

                    <div className="rounded border border-[#1c3038] bg-[#0a151b] p-3">
                      <p className="text-[9px] text-slate-600">
                        CAPACITY
                      </p>

                      <p className="mt-1 text-sm font-medium">
                        980 / 1,200
                      </p>
                    </div>

                    <div className="rounded border border-[#1c3038] bg-[#0a151b] p-3">
                      <p className="text-[9px] text-slate-600">
                        EST. COST
                      </p>

                      <p className="mt-1 text-sm font-medium">
                        ₹18.4 L
                      </p>
                    </div>

                  </div>

                </div>

              </div>

              {/* OPTIMIZATION CRITERIA */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920]">

                <div className="border-b border-[#1c3038] px-4 py-4">

                  <h3 className="text-sm font-medium">
                    Optimization Criteria
                  </h3>

                  <p className="mt-1 text-[10px] text-slate-500">
                    Factors used to rank feasible relocation plans
                  </p>

                </div>

                <div className="space-y-5 p-5">

                  <div>
                    <div className="flex justify-between">
                      <span className="text-xs text-slate-300">
                        Safety improvement
                      </span>

                      <span className="text-xs text-cyan-300">
                        40%
                      </span>
                    </div>

                    <div className="mt-2 h-1.5 rounded-full bg-[#1b2930]">
                      <div className="h-full w-[40%] rounded-full bg-cyan-400"></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between">
                      <span className="text-xs text-slate-300">
                        Site capacity
                      </span>

                      <span className="text-xs text-cyan-300">
                        25%
                      </span>
                    </div>

                    <div className="mt-2 h-1.5 rounded-full bg-[#1b2930]">
                      <div className="h-full w-[25%] rounded-full bg-cyan-400"></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between">
                      <span className="text-xs text-slate-300">
                        Accessibility
                      </span>

                      <span className="text-xs text-cyan-300">
                        15%
                      </span>
                    </div>

                    <div className="mt-2 h-1.5 rounded-full bg-[#1b2930]">
                      <div className="h-full w-[15%] rounded-full bg-cyan-400"></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between">
                      <span className="text-xs text-slate-300">
                        Distance
                      </span>

                      <span className="text-xs text-cyan-300">
                        10%
                      </span>
                    </div>

                    <div className="mt-2 h-1.5 rounded-full bg-[#1b2930]">
                      <div className="h-full w-[10%] rounded-full bg-cyan-400"></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between">
                      <span className="text-xs text-slate-300">
                        Estimated cost
                      </span>

                      <span className="text-xs text-cyan-300">
                        10%
                      </span>
                    </div>

                    <div className="mt-2 h-1.5 rounded-full bg-[#1b2930]">
                      <div className="h-full w-[10%] rounded-full bg-cyan-400"></div>
                    </div>
                  </div>

                  <div className="rounded border border-cyan-400/20 bg-cyan-400/5 p-3">

                    <p className="text-[9px] uppercase tracking-wider text-cyan-300">
                      Constraint Check
                    </p>

                    <p className="mt-2 text-xs leading-5 text-slate-400">
                      Destination capacity, safety threshold, road access and
                      population demand must all be satisfied.
                    </p>

                  </div>

                </div>

              </div>

            </div>

            {/* RELOCATION OPTIONS TABLE */}
            <div className="mt-5 rounded-lg border border-[#1c3038] bg-[#0d1920]">

              <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-4">

                <div>
                  <h3 className="text-sm font-medium">
                    Recommended Relocation Plans
                  </h3>

                  <p className="mt-1 text-[10px] text-slate-500">
                    Ranked options based on safety, capacity, access, distance and cost
                  </p>
                </div>

                <button className="rounded border border-[#293d44] px-3 py-1.5 text-[10px] text-slate-400 hover:bg-white/5 hover:text-white">
                  RECALCULATE
                </button>

              </div>

              <div className="overflow-x-auto">

                <table className="w-full text-left">

                  <thead className="border-b border-[#1c3038]">

                    <tr className="text-[9px] uppercase tracking-wider text-slate-600">

                      <th className="px-4 py-3 font-medium">
                        Plan
                      </th>

                      <th className="px-4 py-3 font-medium">
                        From
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Destination
                      </th>

                      <th className="px-4 py-3 font-medium">
                        People
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Distance
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Safety Gain
                      </th>

                      <th className="px-4 py-3 font-medium">
                        Cost
                      </th>

                      <th className="px-4 py-3 text-right font-medium">
                        Status
                      </th>

                    </tr>

                  </thead>

                  <tbody className="divide-y divide-[#1c3038]">

                    {relocationOptions.map((option) => (

                      <tr
                        key={option.id}
                        className="hover:bg-white/[0.02]"
                      >

                        <td className="px-4 py-3 text-xs font-medium text-cyan-300">
                          {option.id}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-300">
                          {option.source}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-300">
                          {option.destination}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {option.people.toLocaleString()}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {option.distance}
                        </td>

                        <td className="px-4 py-3 text-xs text-emerald-400">
                          {option.safetyGain}
                        </td>

                        <td className="px-4 py-3 text-xs text-slate-400">
                          {option.cost}
                        </td>

                        <td className="px-4 py-3 text-right">

                          <span
                            className={`rounded px-2 py-1 text-[9px] ${
                              option.status === "RECOMMENDED"
                                ? "bg-emerald-400/10 text-emerald-400"
                                : "bg-yellow-400/10 text-yellow-400"
                            }`}
                          >
                            {option.status}
                          </span>

                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            </div>

            {/* HOW IT WORKS */}
            <div className="mt-5 grid grid-cols-3 gap-4">

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  01 · Prioritize
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  Identify settlements where current risk and population
                  exposure require relocation planning.
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  02 · Match
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  Match people to screened sites while respecting sustainable
                  capacity, accessibility and safety constraints.
                </p>

              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">

                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  03 · Recalculate
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  If a destination becomes unsafe or unavailable, generate a
                  new feasible allocation using the latest conditions.
                </p>

              </div>

            </div>

            {/* FOOTER */}
            <div className="mt-5 flex items-center justify-between border-t border-[#1c3038] pt-4">

              <p className="text-[9px] text-slate-600">
                TRINETRA · Risk-Aware Relocation Optimisation
              </p>

              <p className="text-[9px] text-slate-600">
                DEMO DATA · Replace with optimizer output
              </p>

            </div>

          </div>

        </section>

      </div>
    </main>
  );
}