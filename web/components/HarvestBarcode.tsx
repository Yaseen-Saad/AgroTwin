// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useId } from "react";
import { useI18n } from "@/lib/i18n";
import type { Rotation } from "@/lib/types";

const LETTER: Record<string, string> = { green: "G", amber: "A", red: "R" };

export function HarvestBarcode({
  rotation,
  height = 120,
}: {
  rotation: Rotation;
  height?: number;
}) {
  const { t, formatNumber } = useI18n();
  const rawId = useId();
  const uid = rawId.replace(/[^a-zA-Z0-9_-]/g, "");
  const bars = rotation.barcode;
  const max = Math.max(...bars.map((bar) => Math.abs(bar.profit_per_ha)), 1);
  const baseline = 92;
  const usable = 70;
  const width = 360;
  const slot = 42;
  const barWidth = 28;
  const start = 12;

  return (
    <div className="barcode-wrap">
      <svg
        className="barcode"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={`${t("barcode.aria")} — ${rotation.label}`}
      >
        <defs>
          <pattern
            id={`${uid}-green`}
            width="6"
            height="6"
            patternUnits="userSpaceOnUse"
            patternTransform="rotate(45)"
          >
            <line x1="0" y1="0" x2="0" y2="6" className="pattern-green" />
          </pattern>
          <pattern id={`${uid}-amber`} width="6" height="6" patternUnits="userSpaceOnUse">
            <circle cx="3" cy="3" r="1.1" className="pattern-amber" />
          </pattern>
          <pattern id={`${uid}-red`} width="7" height="7" patternUnits="userSpaceOnUse">
            <path d="M0 0 L7 7 M7 0 L0 7" className="pattern-red" />
          </pattern>
        </defs>
        <line x1="0" y1={baseline} x2={width} y2={baseline} className="barcode-baseline" />
        {bars.map((bar, index) => {
          const barHeight = Math.max(8, (Math.abs(bar.profit_per_ha) / max) * usable);
          const x = start + index * slot;
          const y = baseline - barHeight;
          const isWorst = bar.year === rotation.worst_year.year;
          return (
            <g key={bar.year} className={`barcode-stripe stripe-${bar.class}`}>
              <title>
                {`${bar.year}: ${formatNumber(bar.profit_per_ha)} ${bar.currency ?? ""} (${bar.class})`}
              </title>
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={barHeight}
                rx="2"
                className={`bar-base bar-${bar.class}`}
              />
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={barHeight}
                rx="2"
                fill={`url(#${uid}-${bar.class})`}
                className="bar-pattern"
              />
              {isWorst ? (
                <rect
                  x={x - 2}
                  y={y - 2}
                  width={barWidth + 4}
                  height={barHeight + 4}
                  rx="3"
                  className="bar-worst"
                />
              ) : null}
              <text
                x={x + barWidth / 2}
                y={y + barHeight / 2 + 4}
                textAnchor="middle"
                className="bar-letter"
              >
                {LETTER[bar.class]}
              </text>
              <text
                x={x + barWidth / 2}
                y={baseline + 14}
                textAnchor="middle"
                className="bar-year"
              >
                {bar.year}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="barcode-legend">
        <span className="legend-item">
          <span className="swatch swatch-green" aria-hidden="true" /> {t("barcode.legend.green")}
        </span>
        <span className="legend-item">
          <span className="swatch swatch-amber" aria-hidden="true" /> {t("barcode.legend.amber")}
        </span>
        <span className="legend-item">
          <span className="swatch swatch-red" aria-hidden="true" /> {t("barcode.legend.red")}
        </span>
      </div>
    </div>
  );
}
