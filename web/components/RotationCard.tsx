// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useI18n } from "@/lib/i18n";
import type { LowHighMetric, RangeMetric, Rotation } from "@/lib/types";
import { SourceChip } from "./SourceChip";

export interface MetricDomain {
  min: number;
  max: number;
}

export type MetricDomains = Record<
  "water" | "deficit" | "bare" | "erosion" | "profit",
  MetricDomain
>;

function domainFor(values: number[]): MetricDomain {
  const min = Math.min(...values);
  const max = Math.max(...values);
  return { min, max: max === min ? min + 1 : max };
}

export function buildDomains(rotations: Rotation[]): MetricDomains {
  return {
    water: domainFor(rotations.flatMap((r) => [r.metrics.water_use_mm.p10, r.metrics.water_use_mm.p90])),
    deficit: domainFor(rotations.flatMap((r) => [r.metrics.deficit_days.p10, r.metrics.deficit_days.p90])),
    bare: domainFor(rotations.flatMap((r) => [r.metrics.bare_days.p10, r.metrics.bare_days.p90])),
    erosion: domainFor(rotations.flatMap((r) => [r.metrics.erosion_index.p10, r.metrics.erosion_index.p90])),
    profit: domainFor(rotations.flatMap((r) => [r.metrics.profit_per_ha.p10, r.metrics.profit_per_ha.p90])),
  };
}

function clamp(value: number): number {
  return Math.max(0, Math.min(100, value));
}

function pct(value: number, domain: MetricDomain): number {
  return ((value - domain.min) / (domain.max - domain.min)) * 100;
}

function RangeBar({
  label,
  metric,
  domain,
  unit,
}: {
  label: string;
  metric: RangeMetric;
  domain: MetricDomain;
  unit: string;
}) {
  const { t, formatNumber } = useI18n();
  const left = clamp(pct(metric.p10, domain));
  const right = clamp(pct(metric.p90, domain));
  const width = Math.max(right - left, 2);
  const median = clamp(pct(metric.median, domain));

  return (
    <div className="metric-block">
      <div className="metric-head">
        <span>{label}</span>
        <SourceChip source={metric.source} />
      </div>
      <div
        className="range-track"
        role="img"
        dir="ltr"
        aria-label={`${label}: ${formatNumber(metric.p10)}–${formatNumber(metric.p90)} ${unit}, ${t("metrics.median")} ${formatNumber(metric.median)}`}
      >
        <span className="range-band" style={{ insetInlineStart: `${left}%`, width: `${width}%` }} />
        <span className="range-median" style={{ insetInlineStart: `${median}%` }} />
      </div>
      <div className="range-values num" dir="ltr">
        <span>{formatNumber(metric.p10)}</span>
        <strong>{formatNumber(metric.median)}</strong>
        <span>{formatNumber(metric.p90)}</span>
        <span className="metric-unit">{unit}</span>
      </div>
    </div>
  );
}

function LowHighBar({
  label,
  metric,
  unit,
}: {
  label: string;
  metric: LowHighMetric;
  unit: string;
}) {
  const { formatNumber } = useI18n();
  return (
    <div className="metric-block">
      <div className="metric-head">
        <span>{label}</span>
        <SourceChip source={metric.source} />
      </div>
      <div className="range-track range-track-static" aria-hidden="true">
        <span className="range-band range-band-full" />
      </div>
      <div className="range-values num" dir="ltr">
        <span>{formatNumber(metric.low)}</span>
        <strong>–</strong>
        <span>{formatNumber(metric.high)}</span>
        <span className="metric-unit">{unit}</span>
      </div>
    </div>
  );
}

function ListBlock({ title, items, tone }: { title: string; items: string[]; tone?: "warn" }) {
  if (!items.length) {
    return null;
  }
  return (
    <div className={`list-block${tone ? ` list-${tone}` : ""}`}>
      <h4>{title}</h4>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export function RotationCard({
  rotation,
  domains,
}: {
  rotation: Rotation;
  domains: MetricDomains;
}) {
  const { t, formatNumber, formatPercent } = useI18n();
  const profit = rotation.metrics.profit_per_ha;

  return (
    <article className={`card rotation-card${rotation.excluded.is_excluded ? " is-excluded" : ""}`}>
      <header className="rotation-head">
        <div>
          <h3>{rotation.label}</h3>
          <div className="rotation-worst">
            {t("rotations.worst")}: {rotation.worst_year.year} ·{" "}
            <span className="num" dir="ltr">
              {formatNumber(rotation.worst_year.profit_per_ha)} {rotation.worst_year.currency ?? ""}
            </span>{" "}
            <SourceChip source={rotation.worst_year.source} />
          </div>
        </div>
        {rotation.excluded.is_excluded ? (
          <span className="pill pill-warn">{t("rotations.excluded")}</span>
        ) : null}
      </header>

      {rotation.excluded.is_excluded && rotation.excluded.reasons.length ? (
        <ul className="excluded-reasons">
          {rotation.excluded.reasons.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      ) : null}

      <div className="metric-grid">
        <RangeBar
          label={t("metrics.water")}
          metric={rotation.metrics.water_use_mm}
          domain={domains.water}
          unit={t("metrics.mmPerYear")}
        />
        <RangeBar
          label={t("metrics.deficit")}
          metric={rotation.metrics.deficit_days}
          domain={domains.deficit}
          unit={t("metrics.daysPerYear")}
        />
        <RangeBar
          label={t("metrics.bare")}
          metric={rotation.metrics.bare_days}
          domain={domains.bare}
          unit={t("metrics.daysPerYear")}
        />
        <RangeBar
          label={t("metrics.erosion")}
          metric={rotation.metrics.erosion_index}
          domain={domains.erosion}
          unit=""
        />
        <LowHighBar
          label={t("metrics.nCredit")}
          metric={rotation.metrics.n_credit_kg_ha}
          unit={t("metrics.kgPerHa")}
        />
        <RangeBar
          label={t("metrics.profit")}
          metric={profit}
          domain={domains.profit}
          unit={`${profit.currency ?? "EGP"}/${t("metrics.perHa")}`}
        />
      </div>

      <div className="loss-line">
        <strong className="num" dir="ltr">
          {formatPercent(rotation.loss_year_share.value)}
        </strong>{" "}
        {t("rotations.lossShare")} <SourceChip source={rotation.loss_year_share.source} />
      </div>

      <div className="list-grid">
        <ListBlock title={t("rotations.evidence")} items={rotation.evidence} />
        <ListBlock title={t("rotations.benefits")} items={rotation.benefits} />
        <ListBlock title={t("rotations.gaps")} items={rotation.gaps} />
        <ListBlock title={t("rotations.flags")} items={rotation.review_flags} tone="warn" />
      </div>
    </article>
  );
}
