"use client";

import { useEffect, useMemo, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

type RiskLevel = "CRITICAL" | "HIGH" | "MODERATE" | "LOW" | string;

type TrinetraResponse = {
  project?: string;
  status?: string;
  hazard_score?: number | null;
  risk_level?: RiskLevel | null;
  alert?: boolean;
  components?: {
    river_score?: number | null;
    rainfall_score?: number | null;
    terrain_score?: number | null;
    satellite_products?: number | null;
  };
  data_sources?: {
    river?: string;
    rainfall?: string;
    satellite?: string;
    terrain?: string;
  };
};

type HazardZone = {
  type?: "river" | "rainfall" | "terrain" | string;
  lat?: number | null;
  lon?: number | null;
  hazard_score?: number | null;
  risk_level?: RiskLevel | null;
};

type HazardZonesResponse = {
  status?: string;
  zone_count?: number;
  zones?: HazardZone[];
};

type SettlementRisk = {
  id?: string;
  name?: string;
  latitude?: number | null;
  longitude?: number | null;
  population?: number | null;
  risk_score?: number | null;
  risk_level?: RiskLevel | null;
  hazards?: {
    river?: number | null;
    rainfall?: number | null;
    terrain?: number | null;
  };
  location_source?: string;
};

type SettlementRiskResponse = {
  status?: string;
  count?: number;
  settlements?: SettlementRisk[];
  message?: string;
};

function riskText(level?: string | null) {
  return level || "—";
}

function riskColor(level?: string | null) {
  switch (level) {
    case "CRITICAL":
      return "text-red-400";
    case "HIGH":
      return "text-orange-400";
    case "MODERATE":
      return "text-yellow-400";
    case "LOW":
      return "text-emerald-400";
    default:
      return "text-slate-400";
  }
}

function riskDot(level?: string | null) {
  switch (level) {
    case "CRITICAL":
      return "bg-red-400";
    case "HIGH":
      return "bg-orange-400";
    case "MODERATE":
      return "bg-yellow-400";
    case "LOW":
      return "bg-emerald-400";
    default:
      return "bg-slate-500";
  }
}

function sourceLabel(type?: string) {
  switch (type) {
    case "river":
      return "River";
    case "rainfall":
      return "Rainfall";
    case "terrain":
      return "Terrain";
    default:
      return type || "Hazard";
  }
}

function mapPosition(lat: number, lon: number) {
  // Actual backend study-area bounds:
  // latitude 30.50–30.80 N, longitude 79.40–79.75 E.
  const left = ((lon - 79.4) / 0.35) * 100;
  const top = (1 - (lat - 30.5) / 0.3) * 100;

  return {
    left: `${Math.min(94, Math.max(6, left))}%`,
    top: `${Math.min(84, Math.max(10, top))}%`,
  };
}

function settlementLabelStyle(index: number, lat: number, lon: number) {
  const rawLeft = ((lon - 79.4) / 0.35) * 100;
  const rawTop = (1 - (lat - 30.5) / 0.3) * 100;

  // Real settlements can be very close together. Keep the marker at its
  // actual coordinate, but stagger the label around it so labels stay readable.
  const stack = index % 4;
  const side = index % 2 === 0 ? 1 : -1;

  let x = side * (stack < 2 ? 28 : 42);
  let y = stack < 2 ? -48 : -88;

  // Bottom-clustered settlements need labels above the marker; this prevents
  // the label from being clipped by the map boundary.
  if (rawTop > 62) {
    const bottomStack = index % 6;
    x = bottomStack % 2 === 0 ? 34 : -34;
    y = -(52 + Math.floor(bottomStack / 2) * 48);
  } else if (rawTop < 24) {
    // Near the top edge, place labels below the marker.
    x = rawLeft > 72 ? -34 : 34;
    y = 28 + (index % 2) * 42;
  } else if (rawLeft > 78) {
    x = -118;
  } else if (rawLeft < 18) {
    x = 118;
  }

  return {
    transform: `translate(${x}px, ${y}px)`,
  };
}
function formatScore(value?: number | null) {
  return typeof value === "number" ? value.toFixed(1) : "—";
}

export default function Page() {
  const [trinetraData, setTrinetraData] = useState<TrinetraResponse | null>(
    null,
  );
  const [hazardData, setHazardData] = useState<HazardZonesResponse | null>(
    null,
  );
  const [settlementData, setSettlementData] =
    useState<SettlementRiskResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadDashboard = async (manualRefresh = false) => {
    if (manualRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError("");

    try {
      const [trinetraResponse, hazardResponse, settlementResponse] =
        await Promise.all([
          fetch(`${API_BASE}/api/trinetra`, { cache: "no-store" }),
          fetch(`${API_BASE}/api/hazard-zones`, { cache: "no-store" }),
          fetch(`${API_BASE}/api/risk/settlements?limit=8`, {
            cache: "no-store",
          }),
        ]);

      if (!trinetraResponse.ok) {
        throw new Error(`TRINETRA API returned ${trinetraResponse.status}`);
      }

      if (!hazardResponse.ok) {
        throw new Error(`Hazard Zones API returned ${hazardResponse.status}`);
      }

      if (!settlementResponse.ok) {
        throw new Error(
          `Settlement Risk API returned ${settlementResponse.status}`,
        );
      }

      const trinetra = (await trinetraResponse.json()) as TrinetraResponse;
      const hazards = (await hazardResponse.json()) as HazardZonesResponse;
      const settlements =
        (await settlementResponse.json()) as SettlementRiskResponse;

      setTrinetraData(trinetra);
      setHazardData(hazards);
      setSettlementData(settlements);
    } catch (err) {
      console.error("TRINETRA dashboard error:", err);
      setError(
        "Unable to load live backend data. Check that FastAPI and MongoDB are running.",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const zones = useMemo(() => {
    const raw = Array.isArray(hazardData?.zones) ? hazardData.zones : [];

    return raw
      .filter(
        (zone) =>
          typeof zone.lat === "number" &&
          typeof zone.lon === "number" &&
          typeof zone.hazard_score === "number",
      )
      .sort(
        (a, b) => (b.hazard_score ?? 0) - (a.hazard_score ?? 0),
      )
      .slice(0, 30);
  }, [hazardData]);

  const settlements = useMemo(() => {
    return (Array.isArray(settlementData?.settlements)
      ? settlementData.settlements
      : []
    )
      .filter(
        (settlement) =>
          typeof settlement.name === "string" &&
          typeof settlement.risk_score === "number",
      )
      .sort(
        (a, b) => (b.risk_score ?? 0) - (a.risk_score ?? 0),
      );
  }, [settlementData]);

  const distribution = useMemo(() => {
    const counts = {
      river: 0,
      rainfall: 0,
      terrain: 0,
    };

    zones.forEach((zone) => {
      if (zone.type === "river") counts.river += 1;
      if (zone.type === "rainfall") counts.rainfall += 1;
      if (zone.type === "terrain") counts.terrain += 1;
    });

    const total = counts.river + counts.rainfall + counts.terrain;

    return [
      {
        label: "River",
        count: counts.river,
        percentage: total ? Math.round((counts.river / total) * 100) : 0,
        bar: "bg-cyan-400",
      },
      {
        label: "Rainfall",
        count: counts.rainfall,
        percentage: total ? Math.round((counts.rainfall / total) * 100) : 0,
        bar: "bg-purple-400",
      },
      {
        label: "Terrain",
        count: counts.terrain,
        percentage: total ? Math.round((counts.terrain / total) * 100) : 0,
        bar: "bg-orange-400",
      },
    ];
  }, [zones]);

  const corridorRisk = trinetraData?.hazard_score ?? null;
  const riskLevel = trinetraData?.risk_level ?? null;
  const rainfallScore = trinetraData?.components?.rainfall_score ?? null;
  const riverScore = trinetraData?.components?.river_score ?? null;
  const terrainScore = trinetraData?.components?.terrain_score ?? null;
  const satelliteProducts =
    trinetraData?.components?.satellite_products ?? null;
  const activeAlert = trinetraData?.alert === true;

  return (
    <main className="min-h-screen bg-[#081016] text-white">
      <div className="flex min-h-screen">
        {/* SIDEBAR */}
        <aside className="flex w-[230px] shrink-0 flex-col border-r border-[#1c3038] bg-[#0b151b] px-4 py-5">
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
                <span
                  className={`h-2 w-2 rounded-full ${
                    error ? "bg-red-400" : "bg-emerald-400"
                  }`}
                ></span>
                <span
                  className={`text-xs ${
                    error ? "text-red-300" : "text-emerald-300"
                  }`}
                >
                  {error ? "CHECK CONNECTION" : "SYSTEM OPERATIONAL"}
                </span>
              </div>

              <p className="text-[10px] leading-4 text-slate-500">
                Monitoring TRINETRA hazard intelligence for the configured
                study area
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

            <div className="flex items-center gap-4">
              <button
                onClick={() => loadDashboard(true)}
                disabled={refreshing}
                className="rounded-md border border-[#293d44] px-3 py-2 text-[10px] text-slate-400 transition hover:bg-white/5 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                {refreshing ? "REFRESHING..." : "REFRESH"}
              </button>

              <div className="text-right">
                <p className="text-[10px] text-slate-500">BACKEND STATUS</p>
                <p className="text-xs text-slate-300">
                  {loading
                    ? "Loading..."
                    : error
                      ? "Connection unavailable"
                      : "FastAPI connected"}
                </p>
              </div>

              <div
                className={`flex items-center gap-2 rounded-md border px-3 py-2 ${
                  error
                    ? "border-red-400/20 bg-red-400/5"
                    : "border-emerald-400/20 bg-emerald-400/5"
                }`}
              >
                <span
                  className={`h-2 w-2 rounded-full ${
                    error ? "bg-red-400" : "bg-emerald-400"
                  }`}
                ></span>
                <span
                  className={`text-xs ${
                    error ? "text-red-300" : "text-emerald-300"
                  }`}
                >
                  {error ? "OFFLINE" : loading ? "CONNECTING" : "LIVE"}
                </span>
              </div>
            </div>
          </header>

          {/* CONTENT */}
          <div className="p-5">
            {error && (
              <div className="mb-4 rounded-md border border-red-400/20 bg-red-400/5 px-4 py-3 text-xs text-red-300">
                {error}
              </div>
            )}

            {/* KPI ROW */}
            <div className="grid grid-cols-4 gap-4">
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Overall Corridor Risk
                </p>

                <div className="mt-2 flex items-end gap-2">
                  <span className={`text-3xl font-semibold ${riskColor(riskLevel)}`}>
                    {loading ? "--" : formatScore(corridorRisk)}
                  </span>

                  <span
                    className={`mb-1 text-xs ${riskColor(riskLevel)}`}
                  >
                    {loading ? "LOADING" : riskText(riskLevel)}
                  </span>
                </div>

                <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-[#1b2930]">
                  <div
                    className={`h-full rounded-full ${
                      riskLevel === "CRITICAL"
                        ? "bg-red-400"
                        : riskLevel === "HIGH"
                          ? "bg-orange-400"
                          : riskLevel === "MODERATE"
                            ? "bg-yellow-400"
                            : "bg-emerald-400"
                    }`}
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(0, corridorRisk ?? 0),
                      )}%`,
                    }}
                  ></div>
                </div>

                <p className="mt-3 text-[10px] text-slate-500">
                  Backend multi-hazard score
                </p>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Rainfall Risk Score
                </p>

                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-semibold">
                    {loading ? "--" : formatScore(rainfallScore)}
                  </span>
                  <span className="mb-1 text-xs text-slate-500">/ 100</span>
                </div>

                <p className="mt-3 text-xs text-slate-500">
                  Processed rainfall hazard input
                </p>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  River Risk Score
                </p>

                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-semibold">
                    {loading ? "--" : formatScore(riverScore)}
                  </span>
                  <span className="mb-1 text-xs text-slate-500">/ 100</span>
                </div>

                <p className="mt-3 text-xs text-slate-500">
                  Processed river hazard input
                </p>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">
                  Terrain Risk Score
                </p>

                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-semibold">
                    {loading ? "--" : formatScore(terrainScore)}
                  </span>
                  <span className="mb-1 text-xs text-slate-500">/ 100</span>
                </div>

                <p className="mt-3 text-xs text-slate-500">
                  DEM-derived terrain hazard input
                </p>
              </div>
            </div>

            {/* MAP + ALERTS */}
            <div className="mt-5 grid grid-cols-[1fr_330px] gap-5">
              {/* MAP */}
              <div className="overflow-hidden rounded-lg border border-[#1c3038] bg-[#0b171d]">
                <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">
                  <div>
                    <h3 className="text-sm font-medium">Live Hazard Map</h3>
                    <p className="mt-0.5 text-[10px] text-slate-500">
                      Named settlement risk + hazard observations
                    </p>
                  </div>

                  <div className="flex items-center gap-3 text-[10px]">
                    <span className="flex items-center gap-1.5">
                      <i className="h-2 w-2 rounded-full bg-red-400"></i>
                      Critical settlement
                    </span>

                    <span className="flex items-center gap-1.5">
                      <i className="h-2 w-2 rounded-full bg-orange-400"></i>
                      High settlement
                    </span>

                    <span className="flex items-center gap-1.5">
                      <i className="h-2 w-2 rounded-full bg-yellow-400"></i>
                      Moderate settlement
                    </span>

                    <span className="flex items-center gap-1.5 text-slate-500">
                      <i className="h-1.5 w-1.5 rounded-full bg-slate-400"></i>
                      Hazard observation
                    </span>
                  </div>
                </div>

                <div className="relative h-[430px] overflow-hidden bg-[#0b1a20]">
                  {/* grid */}
                  <div
                    className="absolute inset-0 opacity-20"
                    style={{
                      backgroundImage:
                        "linear-gradient(#55727a 1px, transparent 1px), linear-gradient(90deg, #55727a 1px, transparent 1px)",
                      backgroundSize: "45px 45px",
                    }}
                  />

                  {/* subtle terrain illustration only as background texture */}
                  <svg
                    className="absolute inset-0 h-full w-full opacity-20"
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
                  </svg>

                  {/* Study area */}
                  <div className="absolute left-5 top-5 rounded border border-[#31454c] bg-[#081016]/80 px-3 py-2 backdrop-blur-sm">
                    <p className="text-[10px] text-slate-500">STUDY AREA</p>
                    <p className="mt-1 text-xs text-slate-200">
                      30.50°N — 30.80°N
                    </p>
                    <p className="text-xs text-slate-200">
                      79.40°E — 79.75°E
                    </p>
                  </div>

                  {/* Named settlement risk markers. The marker stays at the real
                      coordinate; labels are staggered to avoid collisions. */}
                  {settlements.slice(0, 8).map((settlement, index) => {
                    if (
                      typeof settlement.latitude !== "number" ||
                      typeof settlement.longitude !== "number"
                    ) {
                      return null;
                    }

                    const position = mapPosition(
                      settlement.latitude,
                      settlement.longitude,
                    );

                    return (
                      <div
                        key={settlement.id || `${settlement.name}-${index}`}
                        className="absolute z-20"
                        style={position}
                        title={`${settlement.name} · ${formatScore(
                          settlement.risk_score,
                        )} · ${riskText(settlement.risk_level)}`}
                      >
                        <div className="relative -translate-x-1/2 -translate-y-1/2">
                          <div
                            className={`relative z-20 h-4 w-4 rounded-full border-2 border-white/80 ${riskDot(
                              settlement.risk_level,
                            )} shadow-[0_0_16px_rgba(248,113,113,0.55)]`}
                          ></div>

                          <div
                            className="pointer-events-none absolute left-1/2 top-1/2 z-10 h-px w-5 bg-slate-500/70"
                            style={{
                              transform:
                                index % 2 === 0
                                  ? "translate(2px, -26px) rotate(-45deg)"
                                  : "translate(-22px, -26px) rotate(45deg)",
                              transformOrigin: "left center",
                            }}
                          ></div>

                          <div
                            className="absolute left-1/2 top-1/2 z-30 min-w-[86px] -translate-x-1/2 whitespace-nowrap rounded border border-[#31454c] bg-[#081016]/95 px-2.5 py-1.5 shadow-lg backdrop-blur-sm"
                            style={settlementLabelStyle(
                              index,
                              settlement.latitude,
                              settlement.longitude,
                            )}
                          >
                            <p className="text-[10px] font-medium text-white">
                              {settlement.name}
                            </p>
                            <p
                              className={`text-[9px] ${riskColor(
                                settlement.risk_level,
                              )}`}
                            >
                              {riskText(settlement.risk_level)} · {formatScore(
                                settlement.risk_score,
                              )}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                  {/* API hazard observations */}
                  {zones.map((zone, index) => {
                    const position = mapPosition(zone.lat!, zone.lon!);

                    return (
                      <div
                        key={`${zone.type}-${zone.lat}-${zone.lon}-${index}`}
                        className="absolute z-10"
                        style={position}
                        title={`${sourceLabel(zone.type)} · ${formatScore(
                          zone.hazard_score,
                        )} · ${riskText(zone.risk_level)}`}
                      >
                        <div className="relative -translate-x-1/2 -translate-y-1/2">
                          <div
                            className={`h-2.5 w-2.5 rounded-full border border-white/40 opacity-80 ${riskDot(
                              zone.risk_level,
                            )} shadow-[0_0_12px_rgba(34,211,238,0.25)]`}
                          ></div>
                        </div>
                      </div>
                    );
                  })}

                  {zones.length === 0 && !loading && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="rounded-md border border-[#31454c] bg-[#081016]/90 px-4 py-3 text-center">
                        <p className="text-xs text-slate-300">
                          No georeferenced hazard zones available
                        </p>
                        <p className="mt-1 text-[10px] text-slate-600">
                          Check the /api/hazard-zones response
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="absolute right-5 top-5 flex h-9 w-9 items-center justify-center rounded border border-[#31454c] bg-[#081016]/70 text-xs text-slate-400">
                    N
                  </div>

                  <div className="absolute bottom-5 left-5 rounded border border-[#31454c] bg-[#081016]/90 px-3 py-2 text-[10px] text-slate-500">
                    {loading
                      ? "LOADING HAZARD ZONES..."
                      : `${zones.length} mapped observations`}
                  </div>
                </div>
              </div>

              {/* ALERT / ENGINE PANEL */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920]">
                <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">
                  <h3 className="text-sm font-medium">Risk Engine Status</h3>

                  <span
                    className={`rounded-full px-2 py-1 text-[10px] ${
                      activeAlert
                        ? "bg-red-400/10 text-red-400"
                        : "bg-emerald-400/10 text-emerald-400"
                    }`}
                  >
                    {loading
                      ? "LOADING"
                      : activeAlert
                        ? "ALERT"
                        : "NO ACTIVE ALERT"}
                  </span>
                </div>

                <div className="p-4">
                  <div className="rounded-md border border-[#263941] bg-[#0a151b] p-4">
                    <div className="flex items-center gap-2">
                      <span
                        className={`h-2 w-2 rounded-full ${
                          activeAlert ? "bg-red-400" : "bg-emerald-400"
                        }`}
                      ></span>
                      <span
                        className={`text-[10px] font-semibold tracking-wider ${
                          activeAlert
                            ? "text-red-400"
                            : "text-emerald-400"
                        }`}
                      >
                        {loading
                          ? "PROCESSING"
                          : activeAlert
                            ? "RISK ALERT ACTIVE"
                            : "MONITORING"}
                      </span>
                    </div>

                    <p className="mt-3 text-sm font-medium text-slate-200">
                      {loading
                        ? "Calculating current hazard state..."
                        : activeAlert
                          ? `${riskText(
                              riskLevel,
                            )} corridor risk condition detected`
                          : "No active corridor alert from the backend"}
                    </p>

                    <p className="mt-2 text-[10px] leading-4 text-slate-500">
                      Alert state is taken directly from the TRINETRA risk
                      endpoint. No fabricated alert records are shown.
                    </p>
                  </div>

                  <div className="mt-4 space-y-3">
                    <div className="flex items-center justify-between border-b border-[#1c3038] pb-3">
                      <span className="text-xs text-slate-400">
                        Risk level
                      </span>
                      <span className={`text-xs ${riskColor(riskLevel)}`}>
                        {loading ? "—" : riskText(riskLevel)}
                      </span>
                    </div>

                    <div className="flex items-center justify-between border-b border-[#1c3038] pb-3">
                      <span className="text-xs text-slate-400">
                        Hazard-zone records
                      </span>
                      <span className="text-xs text-slate-200">
                        {loading
                          ? "—"
                          : hazardData?.zone_count ??
                            hazardData?.zones?.length ??
                            0}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-400">
                        Sentinel-1 products
                      </span>
                      <span className="text-xs text-slate-200">
                        {loading
                          ? "—"
                          : satelliteProducts ?? "—"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* BOTTOM SECTION */}
            <div className="mt-5 grid grid-cols-2 gap-5">
              {/* HIGHEST RISK SETTLEMENTS */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920]">
                <div className="border-b border-[#1c3038] px-4 py-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium">
                        Highest Risk Settlements
                      </h3>
                      <p className="mt-1 text-[10px] text-slate-500">
                        Settlement-level risk from the backend risk endpoint
                      </p>
                    </div>
                    <span className="text-[10px] text-slate-600">
                      {loading ? "—" : `${settlements.length} shown`}
                    </span>
                  </div>
                </div>

                <div className="p-4">
                  {settlements.length > 0 ? (
                    settlements.map((settlement, index) => (
                      <div
                        key={settlement.id || settlement.name || index}
                        className="mb-4 last:mb-0"
                      >
                        <div className="mb-1.5 flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <span className="w-4 text-[10px] text-slate-600">
                              {String(index + 1).padStart(2, "0")}
                            </span>
                            <div>
                              <span className="text-xs text-slate-200">
                                {settlement.name}
                              </span>
                              {typeof settlement.population === "number" && (
                                <span className="ml-2 text-[9px] text-slate-600">
                                  pop. {settlement.population.toLocaleString()}
                                </span>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <span
                              className={`text-[9px] ${riskColor(
                                settlement.risk_level,
                              )}`}
                            >
                              {riskText(settlement.risk_level)}
                            </span>
                            <span className="w-8 text-right text-xs font-medium">
                              {formatScore(settlement.risk_score)}
                            </span>
                          </div>
                        </div>

                        <div className="ml-7 h-1.5 rounded-full bg-[#1b2930]">
                          <div
                            className={`h-full rounded-full ${
                              settlement.risk_level === "CRITICAL"
                                ? "bg-red-400"
                                : settlement.risk_level === "HIGH"
                                  ? "bg-orange-400"
                                  : settlement.risk_level === "MODERATE"
                                    ? "bg-yellow-400"
                                    : "bg-emerald-400"
                            }`}
                            style={{
                              width: `${Math.min(
                                100,
                                Math.max(0, settlement.risk_score ?? 0),
                              )}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="rounded-md border border-[#263941] bg-[#0a151b] p-4">
                      <p className="text-xs text-slate-400">
                        {loading
                          ? "Loading settlement risk..."
                          : settlementData?.message ||
                            "No settlement-level risk records are available."}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* HAZARD SIGNAL DISTRIBUTION */}
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920]">
                <div className="border-b border-[#1c3038] px-4 py-3">
                  <h3 className="text-sm font-medium">
                    Hazard Signal Distribution
                  </h3>
                  <p className="mt-1 text-[10px] text-slate-500">
                    Distribution of georeferenced observations returned by the hazard-zone API
                  </p>
                </div>

                <div className="space-y-5 p-5">
                  {distribution.map((item) => (
                    <div key={item.label}>
                      <div className="mb-2 flex justify-between">
                        <span className="text-xs text-slate-300">
                          {item.label}
                        </span>
                        <span className="text-xs text-slate-500">
                          {item.count} records · {item.percentage}%
                        </span>
                      </div>

                      <div className="h-2 rounded-full bg-[#1b2930]">
                        <div
                          className={`h-full rounded-full ${item.bar}`}
                          style={{ width: `${item.percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}

                  <div className="mt-3 border-t border-[#1c3038] pt-4">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] uppercase tracking-wider text-slate-600">
                        Risk method
                      </span>
                      <span className="text-right text-[10px] text-slate-400">
                        70% hydro + 30% terrain
                      </span>
                    </div>
                    <p className="mt-2 text-[9px] leading-4 text-slate-600">
                      Settlement risk applies the same hydro-terrain weighting used by the corridor risk engine to the available settlement-linked observations.
                    </p>
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
                Live data from TRINETRA FastAPI backend
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}


