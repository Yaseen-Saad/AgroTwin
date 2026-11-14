// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useState } from "react";
import { useI18n } from "@/lib/i18n";

interface Site {
  id: string;
  nameKey: string;
  lon: number;
  lat: number;
  active: boolean;
  labelDx: number;
  labelDy: number;
}

const SITES: Site[] = [
  {
    id: "delta_01",
    nameKey: "map.delta",
    lon: 31.04,
    lat: 31.38,
    active: true,
    labelDx: 10,
    labelDy: -10,
  },
  {
    id: "matruh_01",
    nameKey: "map.matruh",
    lon: 31.35,
    lat: 27.24,
    active: false,
    labelDx: 10,
    labelDy: 20,
  },
  {
    id: "sevilla_01",
    nameKey: "map.seville",
    lon: -5.98,
    lat: 37.39,
    active: false,
    labelDx: 10,
    labelDy: -10,
  },
];

const LON_MIN = -8;
const LON_MAX = 40;
const LAT_MIN = 25;
const LAT_MAX = 40;
const PAD = 28;
const WIDTH = 360;
const HEIGHT = 180;

function project(lon: number, lat: number): { x: number; y: number } {
  return {
    x: PAD + ((lon - LON_MIN) / (LON_MAX - LON_MIN)) * (WIDTH - PAD * 2),
    y: PAD + ((LAT_MAX - lat) / (LAT_MAX - LAT_MIN)) * (HEIGHT - PAD * 2),
  };
}

export function SiteMap() {
  const { t } = useI18n();
  const [selected, setSelected] = useState("delta_01");
  const selectedSite = SITES.find((site) => site.id === selected) ?? SITES[0];

  return (
    <section className="card map-card" aria-labelledby="map-title">
      <div className="section-head">
        <h2 id="map-title">{t("map.title")}</h2>
      </div>
      <svg
        className="site-map"
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        role="img"
        aria-label={t("map.note")}
      >
        <defs>
          <pattern id="map-grid" width="24" height="24" patternUnits="userSpaceOnUse">
            <path d="M 24 0 L 0 0 0 24" fill="none" stroke="currentColor" strokeOpacity="0.12" />
          </pattern>
        </defs>
        <rect x="0" y="0" width={WIDTH} height={HEIGHT} className="map-sea" rx="12" />
        <rect x="0" y="0" width={WIDTH} height={HEIGHT} fill="url(#map-grid)" rx="12" />
        <path
          d="M 0 74 C 55 66, 105 78, 155 70 S 245 58, 300 68 S 340 74, 360 70"
          className="map-coast"
          fill="none"
        />
        <text x={WIDTH - 14} y={22} textAnchor="end" className="map-axis">
          {t("map.sea")}
        </text>
        {SITES.map((site) => {
          const { x, y } = project(site.lon, site.lat);
          const classes = [
            "map-site",
            site.active ? "map-site-active" : "",
            selected === site.id ? "map-site-selected" : "",
          ]
            .filter(Boolean)
            .join(" ");
          return (
            <g
              key={site.id}
              className={classes}
              role="button"
              tabIndex={0}
              aria-pressed={selected === site.id}
              aria-label={`${t(site.nameKey)} — ${site.active ? t("map.active") : t("map.pending")}`}
              onClick={() => setSelected(site.id)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  setSelected(site.id);
                }
              }}
            >
              {site.active ? <circle cx={x} cy={y} r="12" className="map-ring" /> : null}
              <circle cx={x} cy={y} r={site.active ? 5 : 4} className="map-marker" />
              <text
                x={x + site.labelDx}
                y={y + site.labelDy}
                textAnchor={site.lon > 0 ? "end" : "start"}
                className="map-label"
              >
                {t(site.nameKey)}
              </text>
              <text
                x={x + site.labelDx}
                y={y + site.labelDy + 13}
                textAnchor={site.lon > 0 ? "end" : "start"}
                className="map-status"
              >
                {site.active ? t("map.active") : t("map.pending")}
              </text>
              <title>{`${t(site.nameKey)} (${site.lat.toFixed(2)}, ${site.lon.toFixed(2)})`}</title>
            </g>
          );
        })}
      </svg>
      <p className="note">{t("map.note")}</p>
      <div className="legend-row">
        <span className="legend-item">
          <span className="legend-dot legend-dot-active" aria-hidden="true" />
          {t("map.active")}
        </span>
        <span className="legend-item">
          <span className="legend-dot" aria-hidden="true" />
          {t("map.pending")}
        </span>
      </div>
      <p className="callout">
        {t("map.selected")}: <strong>{t(selectedSite.nameKey)}</strong>. {t("map.selectedNote")}
      </p>
    </section>
  );
}
