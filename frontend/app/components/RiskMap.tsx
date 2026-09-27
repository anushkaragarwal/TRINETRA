"use client";

import { MapContainer, TileLayer, CircleMarker, Popup, Rectangle } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const LEVEL_COLORS: Record<string, string> = {
  CRITICAL: "#f87171",
  HIGH: "#fb923c",
  MODERATE: "#facc15",
  LOW: "#34d399",
};

function colorFor(level?: string | null) {
  return LEVEL_COLORS[level ?? ""] ?? "#94a3b8";
}

export interface RiskMapPoint {
  settlement: Record<string, unknown>;
  lat: number;
  lon: number;
  level: string;
  score: number | null;
  name: string;
}

interface RiskMapProps {
  points: RiskMapPoint[];
  onPointClick?: (settlement: Record<string, unknown>) => void;
}

export default function RiskMap({ points, onPointClick }: RiskMapProps) {
  return (
    <MapContainer
      center={[30.65, 79.57]}
      zoom={10}
      style={{ height: "355px", width: "100%" }}
      className="bg-[#0a191f]"
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />

      <Rectangle
        bounds={[[30.5, 79.4], [30.8, 79.75]]}
        pathOptions={{ color: "#55D6BE", weight: 1, fillOpacity: 0 }}
      />

      {points.map((point, index) => (
        <CircleMarker
          key={index}
          center={[point.lat, point.lon]}
          radius={9}
          pathOptions={{
            color: colorFor(point.level),
            fillColor: colorFor(point.level),
            fillOpacity: 0.9,
            weight: 2,
          }}
          eventHandlers={{ click: () => onPointClick?.(point.settlement) }}
        >
          <Popup>
            <b>{point.name}</b>
            <br />
            Risk: {point.score?.toFixed?.(1) ?? "—"} — {point.level}
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}