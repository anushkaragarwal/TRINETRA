"use client";

import { MapContainer, TileLayer, CircleMarker, Popup, Rectangle } from "react-leaflet";
import "leaflet/dist/leaflet.css";

type RiskLevel = "CRITICAL" | "HIGH" | "MODERATE" | "LOW" | string;

const RISK_COLORS: Record<string, string> = {
  CRITICAL: "#f87171",
  HIGH: "#fb923c",
  MODERATE: "#facc15",
  LOW: "#34d399",
};

const ZONE_COLORS: Record<string, string> = {
  river: "#22d3ee",
  rainfall: "#c084fc",
  terrain: "#fb923c",
  landslide: "#f87171",
};

export interface HazardZone {
  type?: string;
  lat?: number | null;
  lon?: number | null;
  hazard_score?: number | null;
  risk_level?: RiskLevel | null;
}

export interface SettlementRisk {
  id?: string;
  name?: string;
  latitude?: number | null;
  longitude?: number | null;
  population?: number | null;
  risk_score?: number | null;
  risk_level?: RiskLevel | null;
}

interface HazardMapProps {
  zones: HazardZone[];
  settlements: SettlementRisk[];
  onZoneClick?: (zone: HazardZone) => void;
  onSettlementClick?: (settlement: SettlementRisk) => void;
}

export default function HazardMap({
  zones,
  settlements,
  onZoneClick,
  onSettlementClick,
}: HazardMapProps) {
  return (
    <MapContainer
      center={[30.65, 79.57]}
      zoom={10}
      style={{ height: "430px", width: "100%" }}
      className="bg-[#0b1a20]"
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />

      <Rectangle
        bounds={[[30.5, 79.4], [30.8, 79.75]]}
        pathOptions={{ color: "#55D6BE", weight: 1, fillOpacity: 0 }}
      />

      {zones.map((z, i) => {
        if (typeof z.lat !== "number" || typeof z.lon !== "number") return null;
        return (
          <CircleMarker
            key={`zone-${z.type}-${i}`}
            center={[z.lat, z.lon]}
            radius={4}
            pathOptions={{
              color: ZONE_COLORS[z.type ?? ""] ?? "#94a3b8",
              fillColor: ZONE_COLORS[z.type ?? ""] ?? "#94a3b8",
              fillOpacity: 0.55,
              weight: 1,
            }}
            eventHandlers={{ click: () => onZoneClick?.(z) }}
          >
            <Popup>
              <b>{z.type}</b><br />
              Score: {z.hazard_score?.toFixed(1)} — {z.risk_level}
            </Popup>
          </CircleMarker>
        );
      })}

      {settlements.map((s, i) => {
        if (typeof s.latitude !== "number" || typeof s.longitude !== "number") return null;
        return (
          <CircleMarker
            key={s.id ?? `${s.name}-${i}`}
            center={[s.latitude, s.longitude]}
            radius={9}
            pathOptions={{
              color: RISK_COLORS[s.risk_level ?? ""] ?? "#94a3b8",
              fillColor: RISK_COLORS[s.risk_level ?? ""] ?? "#94a3b8",
              fillOpacity: 0.9,
              weight: 2,
            }}
            eventHandlers={{ click: () => onSettlementClick?.(s) }}
          >
            <Popup>
              <b>{s.name}</b><br />
              Risk: {s.risk_score?.toFixed(1)} — {s.risk_level}<br />
              Population: {s.population ?? "—"}
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}