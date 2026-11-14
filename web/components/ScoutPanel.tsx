// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useI18n } from "@/lib/i18n";
import type { Result } from "@/lib/types";
import { ModeBadge } from "./ModeBadge";
import { SourceChip } from "./SourceChip";

export function ScoutPanel({ result }: { result: Result }) {
  const { t, formatNumber, formatPercent } = useI18n();
  const { fusion, scout_summary: sightings, mode } = result;
  const without = fusion.range_width.without_scout;
  const withScout = fusion.range_width.with_scout;
  const maxBand = Math.max(without, withScout, 1);
  const narrowing = without > 0 ? Math.max(0, 1 - withScout / without) : 0;
  const confidenceKey = `scout.confidence${
    fusion.confidence_label.charAt(0).toUpperCase() + fusion.confidence_label.slice(1)
  }`;

  return (
    <section className="card scout-card" aria-labelledby="scout-title">
      <div className="section-head section-head-wrap">
        <div>
          <h2 id="scout-title">{t("scout.title")}</h2>
          <p className="note">{fusion.used ? t("scout.used") : t("scout.notUsed")}</p>
        </div>
        <ModeBadge mode={mode} compact />
      </div>

      {fusion.scout_run_ids.length ? (
        <div className="chip-row">
          <span className="chip-row-label">{t("scout.runs")}</span>
          {fusion.scout_run_ids.map((runId) => (
            <SourceChip key={runId} source={`scout:${runId}`} />
          ))}
        </div>
      ) : null}

      {fusion.used ? (
        <>
          <div className="stat-grid">
            <div className="stat">
              <span className="stat-label">{t("scout.points")}</span>
              <strong className="num" dir="ltr">
                {formatNumber(fusion.n_points)}
              </strong>
              <SourceChip source="computed" />
            </div>
            <div className="stat">
              <span className="stat-label">{t("scout.ess")}</span>
              <strong className="num" dir="ltr">
                {formatNumber(fusion.ess, 1)}
              </strong>
              <SourceChip source="computed" />
            </div>
            <div className="stat">
              <span className="stat-label">{t("scout.sigma")}</span>
              <strong className="num" dir="ltr">
                {formatNumber(fusion.sigma_used, 2)}
              </strong>
              <SourceChip source="computed" />
            </div>
            <div className="stat">
              <span className="stat-label">{t("scout.confidence")}</span>
              <strong>{t(confidenceKey)}</strong>
              <SourceChip source="computed" />
            </div>
          </div>

          <div className="band-block">
            <div className="band-head">
              <span>{t("scout.band")}</span>
              <span className="pill">
                <span className="num" dir="ltr">
                  {formatPercent(narrowing)}
                </span>{" "}
                {t("scout.narrowing")}
              </span>
            </div>
            <div className="band-row">
              <span className="band-label">{t("scout.without")}</span>
              <div className="band-track" role="img" aria-label={`${t("scout.without")}: ${without}`}>
                <span
                  className="band-fill band-fill-base"
                  style={{ inlineSize: `${(without / maxBand) * 100}%` }}
                />
              </div>
              <span className="num band-value" dir="ltr">
                {formatNumber(without)} {fusion.range_width.unit}
              </span>
            </div>
            <div className="band-row">
              <span className="band-label">{t("scout.with")}</span>
              <div className="band-track" role="img" aria-label={`${t("scout.with")}: ${withScout}`}>
                <span
                  className="band-fill band-fill-scout"
                  style={{ inlineSize: `${(withScout / maxBand) * 100}%` }}
                />
              </div>
              <span className="num band-value" dir="ltr">
                {formatNumber(withScout)} {fusion.range_width.unit}
              </span>
            </div>
            <div className="band-foot">
              <SourceChip source={fusion.range_width.source} />
            </div>
          </div>

          <div className="sightings">
            <span className="stat-label">{t("scout.sightings")}</span>
            <span>
              {t("scout.healthy")}: <strong className="num">{formatNumber(sightings.sightings.healthy)}</strong>
            </span>
            <span>
              {t("scout.diseased")}:{" "}
              <strong className="num">{formatNumber(sightings.sightings.diseased)}</strong>
            </span>
            <span>
              {t("scout.unknown")}: <strong className="num">{formatNumber(sightings.sightings.unknown)}</strong>
            </span>
          </div>
          <p className="note">{t("scout.observation")}</p>
          <p className="note">
            {t("scout.bias")}: {formatNumber(fusion.bias_check.n_overlap_days)}{" "}
            {t("scout.overlapDays")} ·{" "}
            {fusion.bias_check.mean_gap === null
              ? "—"
              : `${formatNumber(fusion.bias_check.mean_gap, 2)} mm`}{" "}
            · {fusion.bias_check.applied ? t("scout.applied") : t("scout.notApplied")}
          </p>
          {fusion.notes?.length ? (
            <ul className="compact-list">
              {fusion.notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          ) : null}
        </>
      ) : (
        <>
          <p className="callout">{t("scout.noData")}</p>
          <div className="sightings">
            <span className="stat-label">{t("scout.sightings")}</span>
            <span>
              {t("scout.healthy")}: <strong className="num">{formatNumber(sightings.sightings.healthy)}</strong>
            </span>
            <span>
              {t("scout.diseased")}:{" "}
              <strong className="num">{formatNumber(sightings.sightings.diseased)}</strong>
            </span>
            <span>
              {t("scout.unknown")}: <strong className="num">{formatNumber(sightings.sightings.unknown)}</strong>
            </span>
          </div>
          <p className="note">{t("scout.observation")}</p>
          <p className="note">{sightings.note}</p>
        </>
      )}
    </section>
  );
}
