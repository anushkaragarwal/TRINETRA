"use client";

import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";

const SafeSitesMap = dynamic(() => import("../components/SafeSitesMap"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[680px] items-center justify-center text-xs text-slate-500">
      Loading map…
    </div>
  ),
});

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

type SafeSite = {
  site_id?: string | number;
  site_name?: string;
  name?: string;
  latitude?: number | null;
  longitude?: number | null;
  safe_site_score?: number | null;
  site_status?: string | null;
  available_capacity?: number | null;
  district?: string | null;
  village?: string | null;
  location?: string | null;
};

type SafeSitesResponse = {
  status?: string;
  count?: number;
  total_count?: number;
  sites?: SafeSite[];
  summary?: {
    total_sites?: number;
    high_suitability_sites?: number;
    medium_suitability_sites?: number;
    low_suitability_sites?: number;
    total_available_capacity?: number;
    best_safety_score?: number | null;
    mapped_sites?: number;
  };
};

function statusColor(status?: string | null) {
  switch (status) {
    case "HIGH_SUITABILITY":
      return "text-emerald-400";
    case "MEDIUM_SUITABILITY":
      return "text-yellow-400";
    case "LOW_SUITABILITY":
      return "text-orange-400";
    default:
      return "text-slate-400";
  }
}

function formatScore(value?: number | null) {
  return typeof value === "number" ? value.toFixed(1) : "—";
}

export default function SafeSitesPage() {
  const [sites, setSites] = useState<SafeSite[]>([]);
  const [summary, setSummary] = useState<SafeSitesResponse["summary"] | null>(null);
  const [selectedId, setSelectedId] = useState<string | number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadSites = async () => {
      setLoading(true);
      setError("");

      try {
        const response = await fetch(`${API_BASE}/api/safe-sites?limit=2000`, {
          cache: "no-store",
        });

        if (!response.ok) {
          throw new Error(`Request failed with ${response.status}`);
        }

        const data = (await response.json()) as SafeSitesResponse;
        const mappedSites = Array.isArray(data.sites) ? data.sites : [];
        setSites(mappedSites);
        setSummary(data.summary || null);
        if (mappedSites[0]) {
          setSelectedId(mappedSites[0].site_id ?? mappedSites[0].site_name ?? null);
        }
      } catch (err) {
        console.error("Safe sites load error:", err);
        setError("Unable to load safe-site data. The backend is currently returning no mapped site records.");
      } finally {
        setLoading(false);
      }
    };

    loadSites();
  }, []);

  const mapPoints = useMemo(
    () =>
      sites
        .filter(
          (site) =>
            typeof site.latitude === "number" &&
            typeof site.longitude === "number" &&
            Number.isFinite(site.latitude) &&
            Number.isFinite(site.longitude),
        )
        .map((site) => ({
          site,
          lat: Number(site.latitude),
          lon: Number(site.longitude),
          id: site.site_id ?? site.site_name ?? site.name ?? `${site.latitude}-${site.longitude}`,
          status: site.site_status,
          score: site.safe_site_score ?? null,
          title: site.site_name || site.name || "Safe site",
          location: site.location || site.village || site.district || "Chamoli corridor",
        })),
    [sites],
  );

  const selectedSite = sites.find(
    (site) =>
      (site.site_id ?? site.site_name ?? site.name ?? `${site.latitude}-${site.longitude}`) === selectedId,
  );

  return (
    <main className="min-h-screen bg-[#081016] text-white">
      <div className="flex min-h-screen">
        <aside className="flex w-[230px] shrink-0 flex-col border-r border-[#1c3038] bg-[#0b151b] px-4 py-5">
          <div className="mb-8 px-2">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-md border border-cyan-400/40 bg-cyan-400/10 text-sm font-bold text-cyan-300">T</div>
              <div>
                <h1 className="text-[18px] font-semibold tracking-[0.18em]">TRINETRA</h1>
                <p className="text-[9px] uppercase tracking-[0.18em] text-slate-500">Terrain Intelligence</p>
              </div>
            </div>
          </div>

          <nav className="space-y-1">
            <a href="/" className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"><span>⌂</span>Command Center</a>
            <a href="/upstream" className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"><span>◈</span>Upstream Intelligence</a>
            <a href="/risk" className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"><span>◆</span>Risk Intelligence</a>
            <a href="/safe-sites" className="flex items-center gap-3 rounded-md border border-cyan-400/20 bg-cyan-400/10 px-3 py-2.5 text-sm text-cyan-300"><span>⌂</span>Safe Sites</a>
            <a href="/relocation" className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"><span>⇄</span>Relocation</a>
          </nav>

          <div className="mt-auto pt-12 rounded-md border border-[#1c3038] bg-[#0e1b22] p-3">
            <div className="mb-2 flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${error ? "bg-red-400" : "bg-emerald-400"}`}></span>
              <span className={`text-xs ${error ? "text-red-300" : "text-emerald-300"}`}>{error ? "DATA WARNING" : "SITE FEED OK"}</span>
            </div>
            <p className="text-[10px] leading-4 text-slate-500">
              Safe-site screening is refreshed from the operational TRINETRA backend and fallback outputs when needed.
            </p>
          </div>
        </aside>

        <section className="flex-1">
          <header className="flex h-[68px] items-center justify-between border-b border-[#1c3038] bg-[#0b151b] px-6">
            <div>
              <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">Response Planning</p>
              <h2 className="mt-1 text-lg font-medium">Safe Site Screening</h2>
            </div>
            <div className="flex items-center gap-2 rounded-md border border-emerald-400/20 bg-emerald-400/5 px-3 py-2">
              <span className={`h-2 w-2 rounded-full ${loading ? "bg-yellow-400" : error ? "bg-red-400" : "bg-emerald-400"}`}></span>
              <span className={`text-xs ${loading ? "text-yellow-300" : error ? "text-red-300" : "text-emerald-300"}`}>
                {loading ? "LOADING" : error ? "WARNING" : "LIVE"}
              </span>
            </div>
          </header>

          <div className="p-5">
            {error && (
              <div className="mb-4 rounded-md border border-red-400/20 bg-red-400/5 px-4 py-3 text-xs text-red-300">
                {error}
              </div>
            )}

            <div className="grid grid-cols-4 gap-4">
              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">Total Sites</p>
                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-semibold text-cyan-300">{loading ? "—" : summary?.total_sites ?? sites.length}</span>
                </div>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">High Suitability</p>
                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-semibold text-emerald-400">{loading ? "—" : summary?.high_suitability_sites ?? 0}</span>
                </div>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">Total Capacity</p>
                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-semibold text-orange-400">{loading ? "—" : (summary?.total_available_capacity ?? 0).toLocaleString()}</span>
                </div>
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">Best Score</p>
                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-semibold text-yellow-400">{loading ? "—" : formatScore(summary?.best_safety_score ?? null)}</span>
                </div>
              </div>
            </div>

            <div className="mt-5 grid grid-cols-[1fr_330px] gap-5">
              <div className="overflow-hidden rounded-lg border border-[#1c3038] bg-[#0b171d]">
                <div className="flex items-center justify-between border-b border-[#1c3038] px-4 py-3">
                  <div>
                    <h3 className="text-sm font-medium">Safe Site Map</h3>
                    <p className="mt-0.5 text-[10px] text-slate-500">Settlement screening and suitability overlay</p>
                  </div>
                  <span className="text-[10px] text-slate-400">{mapPoints.length} mapped</span>
                </div>

                {mapPoints.length > 0 ? (
                  <SafeSitesMap
                    points={mapPoints}
                    selectedId={selectedId}
                    onSelect={(id) => setSelectedId(id ?? null)}
                  />
                ) : (
                  <div className="flex h-[680px] items-center justify-center bg-[#0b171d] text-sm text-slate-400">
                    {loading ? "Loading safe-site data..." : "No safe-site coordinates are currently available."}
                  </div>
                )}
              </div>

              <div className="rounded-lg border border-[#1c3038] bg-[#0d1920] p-4">
                <h3 className="text-sm font-medium">Selected Site</h3>
                {selectedSite ? (
                  <div className="mt-4 space-y-3 text-xs">
                    <div className="rounded-md border border-[#263941] bg-[#0a151b] p-3">
                      <div className="flex items-center justify-between gap-3">
                        <span className="text-sm font-semibold text-white">{selectedSite.site_name || selectedSite.name || "Unnamed site"}</span>
                        <span className={`text-[10px] ${statusColor(selectedSite.site_status)}`}>
                          {selectedSite.site_status || "UNKNOWN"}
                        </span>
                      </div>

                      <div className="mt-3 space-y-2 text-[11px] text-slate-300">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-500">Site score</span>
                          <span className="text-cyan-300">{formatScore(selectedSite.safe_site_score)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-slate-500">Capacity</span>
                          <span>{selectedSite.available_capacity ?? 0}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-slate-500">Latitude</span>
                          <span>{selectedSite.latitude?.toFixed(5) ?? "—"}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-slate-500">Longitude</span>
                          <span>{selectedSite.longitude?.toFixed(5) ?? "—"}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="mt-4 rounded-md border border-[#263941] bg-[#0a151b] p-3 text-xs text-slate-400">
                    Select a site on the map to view detailed screening information.
                  </div>
                )}

                <div className="mt-5 space-y-3 border-t border-[#1c3038] pt-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">High suitability</span>
                    <span className="text-xs text-slate-200">{summary?.high_suitability_sites ?? 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Medium suitability</span>
                    <span className="text-xs text-slate-200">{summary?.medium_suitability_sites ?? 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Low suitability</span>
                    <span className="text-xs text-slate-200">{summary?.low_suitability_sites ?? 0}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}