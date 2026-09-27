"use client";

import { MapContainer, TileLayer, CircleMarker, Popup, Rectangle } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const STATUS_COLORS: Record<string, string> = {
  HIGH_SUITABILITY: "#34d399",
  MEDIUM_SUITABILITY: "#facc15",
  LOW_SUITABILITY: "#94a3b8",
};

function colorFor(status?: string | null) {
  return STATUS_COLORS[status ?? ""] ?? "#94a3b8";
}

export interface SafeSitePoint {
  site: Record<string, unknown>;
  lat: number;
  lon: number;
  id: string | number | null | undefined;
  status?: string | null;
  score: number | null;
  title: string;
  location: string;
}

interface SafeSitesMapProps {
  points: SafeSitePoint[];
  selectedId: string | number | null;
  onSelect?: (id: string | number | null | undefined) => void;
}

export default function SafeSitesMap({
  points,
  selectedId,
  onSelect,
}: SafeSitesMapProps) {
  return (
    <MapContainer
      center={[30.65, 79.57]}
      zoom={10}
      style={{ height: "680px", width: "100%" }}
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

      {points.map((point, index) => {
        const isSelected = String(point.id) === String(selectedId);
        return (
          <CircleMarker
            key={`${point.id}-${index}`}
            center={[point.lat, point.lon]}
            radius={isSelected ? 11 : 7}
            pathOptions={{
              color: isSelected ? "#ffffff" : colorFor(point.status),
              fillColor: colorFor(point.status),
              fillOpacity: 0.9,
              weight: isSelected ? 3 : 1.5,
            }}
            eventHandlers={{ click: () => onSelect?.(point.id) }}
          >
            <Popup>
              <b>{point.title}</b>
              <br />
              {point.location}
              <br />
              Score: {point.score?.toFixed?.(1) ?? "—"} — {point.status || "UNKNOWN"}
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}