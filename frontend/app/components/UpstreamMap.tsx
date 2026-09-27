"use client";

import { MapContainer, TileLayer, CircleMarker, Popup, Rectangle } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export interface RiverPoint {
  Station?: string;
  Latitude?: number | null;
  Longitude?: number | null;
  hybrid_hazard_score?: number | null;
  hybrid_risk_category?: string | null;
  risk_category?: string | null;
}

export interface TerrainPoint {
  cell_id?: string;
  lat?: number | null;
  lon?: number | null;
  terrain_hazard_score?: number | null;
  terrain_hazard_level?: string | null;
}

const LEVEL_COLORS: Record<string, string> = {
  CRITICAL: "#f87171",
  HIGH: "#fb923c",
  MODERATE: "#facc15",
  LOW: "#34d399",
};

function colorFor(level?: string | null) {
  return LEVEL_COLORS[level ?? ""] ?? "#22d3ee";
}

interface UpstreamMapProps {
  riverPoints: RiverPoint[];
  terrainPoints: TerrainPoint[];
  showTerrain?: boolean;
  onRiverClick?: (point: RiverPoint) => void;
  onTerrainClick?: (point: TerrainPoint) => void;
}

export default function UpstreamMap({
  riverPoints,
  terrainPoints,
  showTerrain = true,
  onRiverClick,
  onTerrainClick,
}: UpstreamMapProps) {
  return (
    <MapContainer
      center={[30.65, 79.57]}
      zoom={10}
      style={{ height: "355px", width: "100%" }}
      className="bg-[#101d20]"
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />

      <Rectangle
        bounds={[[30.5, 79.4], [30.8, 79.75]]}
        pathOptions={{ color: "#55D6BE", weight: 1, fillOpacity: 0 }}
      />

      {riverPoints.map((river, index) => {
        if (typeof river.Latitude !== "number" || typeof river.Longitude !== "number") {
          return null;
        }
        const level = river.hybrid_risk_category || river.risk_category;
        return (
          <CircleMarker
            key={`river-${index}`}
            center={[river.Latitude, river.Longitude]}
            radius={7}
            pathOptions={{
              color: colorFor(level),
              fillColor: colorFor(level),
              fillOpacity: 0.85,
              weight: 2,
            }}
            eventHandlers={{ click: () => onRiverClick?.(river) }}
          >
            <Popup>
              <b>{river.Station || "River station"}</b>
              <br />
              Score: {river.hybrid_hazard_score?.toFixed?.(1) ?? "—"}
              <br />
              Level: {level || "—"}
            </Popup>
          </CircleMarker>
        );
      })}

      {showTerrain &&
        terrainPoints.map((point, index) => {
          if (typeof point.lat !== "number" || typeof point.lon !== "number") {
            return null;
          }
          return (
            <CircleMarker
              key={`terrain-${point.cell_id || index}`}
              center={[point.lat, point.lon]}
              radius={4}
              pathOptions={{
                color: "#fde047",
                fillColor: "#fde047",
                fillOpacity: 0.6,
                weight: 1,
              }}
              eventHandlers={{ click: () => onTerrainClick?.(point) }}
            >
              <Popup>
                Terrain score: {point.terrain_hazard_score?.toFixed?.(1) ?? "—"}
                <br />
                Level: {point.terrain_hazard_level || "—"}
              </Popup>
            </CircleMarker>
          );
        })}
    </MapContainer>
  );
}