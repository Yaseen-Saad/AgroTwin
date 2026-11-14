// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useI18n } from "@/lib/i18n";
import type { Result } from "@/lib/types";
import { SourceChip } from "./SourceChip";

export type Lens = "farmer" | "investor" | "scientist";

const FEDDAN = 0.42;

export function LensPanel({ result, lens }: { result: Result; lens: Lens }) {
  const { t, formatNumber, formatPercent } = useI18n();
  const top = result.rotations.find((rotation) => !rotation.excluded.is_excluded) ?? result.rotations[0];

  if (!top) {
    return null;
  }

  if (lens === "farmer") {
    return (
      <section className="card lens-panel" aria-labelledby="lens-title-farmer">
        <div className="section-head">
          <h2 id="lens-title-farmer">{t("lensPanel.farmerTitle")}</h2>
          <p className="note">{t("lensPanel.perFeddanNote")}</p>
        </div>
        <div className="lens-grid">
          {result.rotations.map((rotation) => {
            const profit = rotation.metrics.profit_per_ha;
            return (
              <div key={rotation.rotation_id} className="lens-card">
                <h3>{rotation.label}</h3>
                <div className="lens-value num" dir="ltr">
                  <span>{formatNumber(profit.p10 * FEDDAN)}</span>
                  <strong>{formatNumber(profit.median * FEDDAN)}</strong>
                  <span>{formatNumber(profit.p90 * FEDDAN)}</span>
                </div>
                <div className="lens-unit">
                  {profit.currency ?? "EGP"}/{t("metrics.perFeddan")} · {t("metrics.range")}{" "}
                  <SourceChip source="computed" /> <SourceChip source={profit.source} />
                </div>
                <div className="note">
                  {t("metrics.water")}:{" "}
                  <span className="num" dir="ltr">
                    {formatNumber(rotation.metrics.water_use_mm.p10)}–
                    {formatNumber(rotation.metrics.water_use_mm.p90)}
                  </span>{" "}
                  {t("metrics.mmPerYear")} <SourceChip source={rotation.metrics.water_use_mm.source} />
                </div>
              </div>
            );
          })}
        </div>
        <div className="list-block list-warn">
          <h4>{t("lensPanel.nextSteps")}</h4>
          <ul>
            {top.review_flags.map((flag) => (
              <li key={flag}>{flag}</li>
            ))}
          </ul>
        </div>
      </section>
    );
  }

  if (lens === "investor") {
    return (
      <section className="card lens-panel" aria-labelledby="lens-title-investor">
        <div className="section-head">
          <h2 id="lens-title-investor">{t("lensPanel.investorTitle")}</h2>
          <p className="note">{t("lensPanel.authoritative")}</p>
        </div>
        <div className="lens-grid">
          {result.rotations.map((rotation) => {
            const profit = rotation.metrics.profit_per_ha;
            const band = profit.p90 - profit.p10;
            return (
              <div key={rotation.rotation_id} className="lens-card">
                <h3>{rotation.label}</h3>
                <div className="lens-line">
                  <span>{t("metrics.profit")}</span>
                  <strong className="num" dir="ltr">
                    {formatNumber(profit.p10)}–{formatNumber(profit.p90)} {profit.currency ?? "EGP"}/
                    {t("metrics.perHa")}
                  </strong>
                  <SourceChip source={profit.source} />
                </div>
                <div className="lens-line">
                  <span>{t("scout.band")}</span>
                  <strong className="num" dir="ltr">
                    {formatNumber(band)} {profit.currency ?? "EGP"}
                  </strong>
                  <SourceChip source="computed" />
                </div>
                <div className="lens-line">
                  <span>{t("metrics.lossShare")}</span>
                  <strong className="num" dir="ltr">
                    {formatPercent(rotation.loss_year_share.value)}
                  </strong>
                  <SourceChip source={rotation.loss_year_share.source} />
                </div>
                <div className="lens-line">
                  <span>{t("metrics.worstYear")}</span>
                  <strong className="num" dir="ltr">
                    {rotation.worst_year.year} · {formatNumber(rotation.worst_year.profit_per_ha)}
                  </strong>
                  <SourceChip source={rotation.worst_year.source} />
                </div>
              </div>
            );
          })}
        </div>
        <p className="note">{t("lensPanel.worstYear")}</p>
      </section>
    );
  }

  return (
    <section className="card lens-panel" aria-labelledby="lens-title-scientist">
      <div className="section-head">
        <h2 id="lens-title-scientist">{t("lensPanel.scientistTitle")}</h2>
        <p className="note">{t("footer.sources")}</p>
      </div>
      <div className="stat-grid">
        <div className="stat">
          <span className="stat-label">{t("scout.ess")}</span>
          <strong className="num" dir="ltr">
            {formatNumber(result.fusion.ess, 1)}
          </strong>
          <SourceChip source="computed" />
        </div>
        <div className="stat">
          <span className="stat-label">{t("scout.sigma")}</span>
          <strong className="num" dir="ltr">
            {formatNumber(result.fusion.sigma_used, 2)}
          </strong>
          <SourceChip source="computed" />
        </div>
        <div className="stat">
          <span className="stat-label">{t("scout.confidence")}</span>
          <strong>
            {t(
              `scout.confidence${
                result.fusion.confidence_label.charAt(0).toUpperCase() +
                result.fusion.confidence_label.slice(1)
              }`,
            )}
          </strong>
        </div>
        <div className="stat">
          <span className="stat-label">{t("scout.points")}</span>
          <strong className="num" dir="ltr">
            {formatNumber(result.fusion.n_points)}
          </strong>
          {result.fusion.scout_run_ids.map((runId) => (
            <SourceChip key={runId} source={`scout:${runId}`} />
          ))}
        </div>
      </div>
      <p className="callout">{t("lensPanel.essNote")}</p>

      <div className="weights-block">
        <h3>{t("lensPanel.weightsNote")}</h3>
        <div className="weights-row">
          {Object.entries(result.fusion.weights_by_year).map(([year, weight]) => (
            <span key={year} className="weight-chip">
              <span className="num" dir="ltr">
                {year}
              </span>
              <strong className="num" dir="ltr">
                {formatNumber(weight, 2)}
              </strong>
            </span>
          ))}
        </div>
      </div>

      <div className="list-grid">
        <div className="list-block">
          <h4>{t("rotations.evidence")}</h4>
          <ul>
            {top.evidence.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="list-block">
          <h4>{t("rotations.gaps")}</h4>
          <ul>
            {top.gaps.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="list-block list-warn">
          <h4>{t("rotations.flags")}</h4>
          <ul>
            {top.review_flags.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      {result.assumptions?.length ? (
        <div className="assumption-row">
          {result.assumptions.map((assumption) => (
            <span key={assumption.id} className="assumption-chip">
              <SourceChip source={`assumption:${assumption.id}`} />
              {assumption.description ? <span>{assumption.description}</span> : null}
            </span>
          ))}
        </div>
      ) : null}
      {result.fusion.notes?.length ? (
        <ul className="compact-list">
          {result.fusion.notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
