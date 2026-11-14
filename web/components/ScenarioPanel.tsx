// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useEffect, useState } from "react";
import { diagnose } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { Result, Scenario } from "@/lib/types";

export function ScenarioPanel({
  result,
  onResult,
}: {
  result: Result;
  onResult: (result: Result) => void;
}) {
  const { t, formatNumber } = useI18n();
  const [scenario, setScenario] = useState<Scenario>(result.scenario);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<"idle" | "applied" | "failed">("idle");

  useEffect(() => {
    setScenario(result.scenario);
  }, [result]);

  const update = (key: keyof Scenario, value: number) => {
    setScenario((current) => ({ ...current, [key]: value }));
    setMessage("idle");
  };

  const apply = async () => {
    setBusy(true);
    setMessage("idle");
    try {
      const next = await diagnose(
        result.site_id,
        scenario,
        result.rotations.map((rotation) => rotation.rotation_id),
      );
      onResult(next);
      setMessage("applied");
    } catch {
      setMessage("failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="card scenario-card" aria-labelledby="scenario-title">
      <div className="section-head">
        <h2 id="scenario-title">{t("scenario.title")}</h2>
        <p className="note">{t("scenario.subtitle")}</p>
      </div>

      <div className="sliders">
        <label className="slider-row">
          <span className="slider-label">
            {t("scenario.rain")}
            <strong className="num" dir="ltr">
              ×{formatNumber(scenario.rain_mult, 2)}
            </strong>
          </span>
          <input
            type="range"
            min="0.5"
            max="1.5"
            step="0.05"
            value={scenario.rain_mult}
            onChange={(event) => update("rain_mult", Number(event.target.value))}
          />
        </label>
        <label className="slider-row">
          <span className="slider-label">
            {t("scenario.temp")}
            <strong className="num" dir="ltr">
              {scenario.temp_offset_c >= 0 ? "+" : ""}
              {formatNumber(scenario.temp_offset_c, 1)} °C
            </strong>
          </span>
          <input
            type="range"
            min="-3"
            max="3"
            step="0.5"
            value={scenario.temp_offset_c}
            onChange={(event) => update("temp_offset_c", Number(event.target.value))}
          />
        </label>
        <label className="slider-row">
          <span className="slider-label">
            {t("scenario.price")}
            <strong className="num" dir="ltr">
              ×{formatNumber(scenario.price_mult, 2)}
            </strong>
          </span>
          <input
            type="range"
            min="0.5"
            max="1.5"
            step="0.05"
            value={scenario.price_mult}
            onChange={(event) => update("price_mult", Number(event.target.value))}
          />
        </label>
      </div>

      <div className="scenario-actions no-print">
        <button type="button" className="button" onClick={apply} disabled={busy}>
          {busy ? t("scenario.applying") : t("scenario.apply")}
        </button>
      </div>

      <p className="callout">{t("scenario.fixtureNote")}</p>
      {message === "failed" ? <p className="callout callout-warn">{t("scenario.failed")}</p> : null}
    </section>
  );
}
