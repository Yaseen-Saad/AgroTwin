// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchDemoResult } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { Result } from "@/lib/types";
import { BarcodePanel } from "./BarcodePanel";
import { FieldCardButton } from "./FieldCardButton";
import { LensPanel, type Lens } from "./LensPanel";
import { LocaleToggle } from "./LocaleToggle";
import { Mixer } from "./Mixer";
import { ModeBadge } from "./ModeBadge";
import { RotationCard, buildDomains } from "./RotationCard";
import { ScenarioPanel } from "./ScenarioPanel";
import { ScoutPanel } from "./ScoutPanel";
import { SiteMap } from "./SiteMap";

const LENSES: Lens[] = ["farmer", "investor", "scientist"];

export function Dashboard({ initialResult }: { initialResult: Result }) {
  const { t, formatNumber } = useI18n();
  const [result, setResult] = useState<Result>(initialResult);
  const [lens, setLens] = useState<Lens>("farmer");
  const [source, setSource] = useState<"static" | "api">("static");
  const [loading, setLoading] = useState(true);
  const [offline, setOffline] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setOffline(false);
    try {
      const next = await fetchDemoResult("delta_01");
      setResult(next);
      setSource("api");
    } catch {
      setSource("static");
      setOffline(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const domains = useMemo(() => buildDomains(result.rotations), [result.rotations]);
  const statusText = loading
    ? t("app.loading")
    : source === "api"
      ? t("app.apiConnected")
      : t("app.apiOffline");

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            AT
          </span>
          <div>
            <h1>{t("app.title")}</h1>
            <p>{t("app.tagline")}</p>
          </div>
        </div>
        <div className="topbar-right">
          <ModeBadge mode={result.mode} />
          <span
            className={`status ${source === "api" ? "status-api" : "status-static"}`}
            aria-live="polite"
          >
            <span className="status-dot" aria-hidden="true" />
            {statusText}
          </span>
          <LocaleToggle />
        </div>
      </header>

      <main>
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow">
              {t("app.site")} · <span className="mono">{result.site_id}</span>
            </p>
            <h2 id="hero-title">{t("app.subtitle")}</h2>
          </div>
          <div className="hero-meta">
            <div className="hero-stat">
              <span>{t("app.years")}</span>
              <strong className="num" dir="ltr">
                {formatNumber(result.years.length)}
              </strong>
            </div>
            <div className="hero-stat">
              <span>{t("app.rotations")}</span>
              <strong className="num" dir="ltr">
                {formatNumber(result.rotations.length)}
              </strong>
            </div>
            <div className="hero-stat hero-fixture">
              <span>{t("app.fixture")}</span>
              <code dir="ltr">{result.generated_by}</code>
            </div>
          </div>
        </section>

        {offline ? (
          <div className="banner no-print" role="status">
            <span>{t("app.apiOffline")}</span>
            <button type="button" className="button button-small" onClick={() => void load()}>
              {t("app.retry")}
            </button>
          </div>
        ) : null}

        <nav className="lens-tabs no-print" aria-label={t("lens.title")}>
          <span className="lens-tabs-label">{t("lens.title")}</span>
          {LENSES.map((item) => (
            <button
              key={item}
              type="button"
              aria-pressed={lens === item}
              onClick={() => setLens(item)}
            >
              {t(`lens.${item}`)}
            </button>
          ))}
          <span className="lens-desc">{t(`lens.${lens}Desc`)}</span>
        </nav>

        <div className="grid grid-two">
          <SiteMap />
          <ScoutPanel result={result} />
        </div>

        <BarcodePanel rotations={result.rotations} />

        <section aria-labelledby="rotations-title">
          <div className="section-head section-head-wrap">
            <div>
              <h2 id="rotations-title">{t("rotations.title")}</h2>
              <p className="note">{t("rotations.subtitle")}</p>
            </div>
          </div>
          <div className="grid grid-rotations">
            {result.rotations.map((rotation) => (
              <RotationCard key={rotation.rotation_id} rotation={rotation} domains={domains} />
            ))}
          </div>
        </section>

        <div className="grid grid-two">
          <Mixer result={result} />
          <ScenarioPanel result={result} onResult={setResult} />
        </div>

        <LensPanel result={result} lens={lens} />
        <FieldCardButton result={result} />
      </main>

      <footer className="footer">
        <p>{t("footer.disclaimer")}</p>
        <p>{t("footer.sources")}</p>
        <p>{t("footer.built")}</p>
        <p>{t("footer.ai")}</p>
      </footer>
    </div>
  );
}
