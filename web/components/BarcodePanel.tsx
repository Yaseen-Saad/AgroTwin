// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useState } from "react";
import { useI18n } from "@/lib/i18n";
import type { Rotation } from "@/lib/types";
import { HarvestBarcode } from "./HarvestBarcode";
import { SourceChip } from "./SourceChip";

function DiagnosisTimeline({ rotation }: { rotation: Rotation }) {
  const { t, formatNumber } = useI18n();
  return (
    <div className="timeline-block">
      <div className="timeline-head">
        <h3>{t("timeline.title")}</h3>
        <p className="note">{t("timeline.subtitle")}</p>
      </div>
      <div className="timeline" role="list" aria-label={t("timeline.aria")}>
        {rotation.barcode.map((bar) => (
          <div
            key={bar.year}
            role="listitem"
            className={`timeline-node timeline-${bar.class}${
              bar.year === rotation.worst_year.year ? " is-worst" : ""
            }`}
            title={`${bar.year}: ${formatNumber(bar.profit_per_ha)} ${bar.currency ?? ""}`}
          >
            <span className="timeline-year">{bar.year}</span>
            <span className="timeline-dot" aria-hidden="true" />
            <span className="timeline-profit num" dir="ltr">
              {formatNumber(bar.profit_per_ha)}
            </span>
            <SourceChip source={bar.source} />
          </div>
        ))}
      </div>
    </div>
  );
}

export function BarcodePanel({ rotations }: { rotations: Rotation[] }) {
  const { t, formatNumber } = useI18n();
  const [selected, setSelected] = useState(rotations[0]?.rotation_id ?? "");
  const rotation = rotations.find((item) => item.rotation_id === selected) ?? rotations[0];

  if (!rotation) {
    return null;
  }

  return (
    <section className="card barcode-card" aria-labelledby="barcode-title">
      <div className="section-head section-head-wrap">
        <div>
          <h2 id="barcode-title">{t("barcode.title")}</h2>
          <p className="note">{t("barcode.subtitle")}</p>
        </div>
        <div className="chip-tabs no-print" role="group" aria-label={t("barcode.title")}>
          {rotations.map((item) => (
            <button
              key={item.rotation_id}
              type="button"
              aria-pressed={item.rotation_id === rotation.rotation_id}
              onClick={() => setSelected(item.rotation_id)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
      <div className="barcode-main">
        <div>
          <div className="barcode-meta">
            <strong>{rotation.label}</strong>
            <span className="barcode-worst-label">
              {t("barcode.worst")}: {rotation.worst_year.year} ·{" "}
              <span className="num" dir="ltr">
                {formatNumber(rotation.worst_year.profit_per_ha)} {rotation.worst_year.currency ?? ""}
              </span>
            </span>
            <SourceChip source={rotation.worst_year.source} />
          </div>
          <HarvestBarcode rotation={rotation} />
        </div>
      </div>
      <DiagnosisTimeline rotation={rotation} />
    </section>
  );
}
