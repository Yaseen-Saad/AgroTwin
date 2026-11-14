// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useMemo, useState } from "react";
import { useI18n } from "@/lib/i18n";
import type { Result } from "@/lib/types";

function fill(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => String(values[key] ?? `{${key}}`));
}

async function copyText(text: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "true");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  document.execCommand("copy");
  document.body.removeChild(area);
}

export function FieldCardButton({ result }: { result: Result }) {
  const { t, formatNumber } = useI18n();
  const [state, setState] = useState<"idle" | "copied" | "error">("idle");
  const top = result.rotations.find((rotation) => !rotation.excluded.is_excluded) ?? result.rotations[0];

  const message = useMemo(() => {
    if (!top) {
      return "";
    }
    const profit = top.metrics.profit_per_ha;
    const water = top.metrics.water_use_mm;
    const lines = [
      fill(t("fieldcard.messageTitle"), {
        site: result.site_id,
        mode: t(`mode.labels.${result.mode}`),
      }),
      fill(t("fieldcard.messageProfit"), {
        rotation: top.label,
        p10: formatNumber(profit.p10),
        p90: formatNumber(profit.p90),
        currency: profit.currency ?? "EGP",
        median: formatNumber(profit.median),
        w10: formatNumber(water.p10),
        w90: formatNumber(water.p90),
      }),
      fill(t("fieldcard.messageWorst"), {
        year: top.worst_year.year,
        profit: `${formatNumber(top.worst_year.profit_per_ha)} ${top.worst_year.currency ?? "EGP"}`,
      }),
    ];
    if (result.fusion.used) {
      lines.push(
        fill(t("fieldcard.messageScout"), {
          points: formatNumber(result.fusion.n_points),
          ess: formatNumber(result.fusion.ess, 1),
          with: formatNumber(result.fusion.range_width.with_scout),
          without: formatNumber(result.fusion.range_width.without_scout),
        }),
      );
    }
    lines.push(t("fieldcard.messageNote"));
    return lines.join("\n");
  }, [formatNumber, result, t, top]);

  const copy = async () => {
    try {
      await copyText(message);
      setState("copied");
    } catch {
      setState("error");
    }
  };

  return (
    <section className="card fieldcard-card no-print" aria-labelledby="fieldcard-title">
      <div className="section-head">
        <h2 id="fieldcard-title">{t("fieldcard.title")}</h2>
        <p className="note">{t("fieldcard.note")}</p>
      </div>
      <div className="fieldcard-actions">
        <button type="button" className="button" onClick={copy}>
          {state === "copied" ? t("fieldcard.copied") : t("fieldcard.copy")}
        </button>
        <button type="button" className="button button-quiet" onClick={() => window.print()}>
          {t("fieldcard.print")}
        </button>
        <span className="note" aria-live="polite">
          <span className="num" dir="ltr">
            {message.length}/600
          </span>
        </span>
      </div>
      <pre className="fieldcard-preview">{message}</pre>
      {state === "error" ? <p className="callout callout-warn">{t("scenario.failed")}</p> : null}
    </section>
  );
}
