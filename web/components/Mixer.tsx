// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useEffect, useMemo, useState } from "react";
import { useI18n } from "@/lib/i18n";
import type { Result, Rotation } from "@/lib/types";
import { SourceChip } from "./SourceChip";

type Weights = Result["ranking"]["weights"];

function normalise(values: number[], higherIsBetter: boolean): Map<string, number> {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min;
  const result = new Map<string, number>();
  values.forEach((value, index) => {
    const base = span === 0 ? 0.5 : (value - min) / span;
    result.set(String(index), higherIsBetter ? base : 1 - base);
  });
  return result;
}

interface Scored {
  rotation: Rotation;
  score: number;
}

function scoreRotations(rotations: Rotation[], weights: Weights): Scored[] {
  const active = rotations.filter((rotation) => !rotation.excluded.is_excluded);
  const water = normalise(
    active.map((rotation) => rotation.metrics.water_use_mm.median),
    false,
  );
  const soil = normalise(
    active.map((rotation) => rotation.metrics.erosion_index.median),
    false,
  );
  const profit = normalise(
    active.map((rotation) => rotation.metrics.profit_per_ha.median),
    true,
  );
  const total = weights.water + weights.soil + weights.profit || 1;
  return active
    .map((rotation, index) => ({
      rotation,
      score:
        (weights.water / total) * (water.get(String(index)) ?? 0) +
        (weights.soil / total) * (soil.get(String(index)) ?? 0) +
        (weights.profit / total) * (profit.get(String(index)) ?? 0),
    }))
    .sort((a, b) => b.score - a.score);
}

export function Mixer({ result }: { result: Result }) {
  const { t, formatNumber } = useI18n();
  const [weights, setWeights] = useState<Weights>(result.ranking.weights);

  useEffect(() => {
    setWeights(result.ranking.weights);
  }, [result]);

  const scored = useMemo(() => scoreRotations(result.rotations, weights), [result.rotations, weights]);
  const total = weights.water + weights.soil + weights.profit || 1;
  const excluded = result.rotations.filter((rotation) => rotation.excluded.is_excluded);
  const tie = scored.length > 1 && Math.abs(scored[0].score - scored[1].score) < 0.02;

  const update = (key: keyof Weights, value: number) => {
    setWeights((current) => ({ ...current, [key]: value }));
  };

  return (
    <section className="card mixer-card" aria-labelledby="mixer-title">
      <div className="section-head">
        <h2 id="mixer-title">{t("mixer.title")}</h2>
        <p className="note">{t("mixer.subtitle")}</p>
      </div>

      <div className="sliders">
        {(Object.keys(weights) as Array<keyof Weights>).map((key) => (
          <label key={key} className="slider-row">
            <span className="slider-label">
              {t(`mixer.${key}`)}
              <strong className="num" dir="ltr">
                {formatNumber((weights[key] / total) * 100)}%
              </strong>
            </span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={weights[key]}
              onChange={(event) => update(key, Number(event.target.value))}
            />
          </label>
        ))}
      </div>

      <div className="mixer-actions no-print">
        <button
          type="button"
          className="button button-quiet"
          onClick={() => setWeights(result.ranking.weights)}
        >
          {t("mixer.reset")}
        </button>
        <span className="note">{t("mixer.preview")}</span>
      </div>

      <div className="mixer-order">
        <h3>{t("mixer.order")}</h3>
        <ol>
          {scored.map((item, index) => (
            <li key={item.rotation.rotation_id}>
              <span className="rank">{index + 1}</span>
              <span className="rank-label">{item.rotation.label}</span>
              <span className="rank-score num" dir="ltr">
                {formatNumber(item.score * 100)}%
              </span>
            </li>
          ))}
        </ol>
        <div className="mixer-source">
          <SourceChip source="computed" />
        </div>
        {tie ? <p className="callout callout-warn">{t("mixer.noWinner")}</p> : null}
        {excluded.length ? (
          <p className="note">
            {t("rotations.excluded")}: {excluded.map((rotation) => rotation.label).join(", ")}
          </p>
        ) : null}
      </div>
    </section>
  );
}
