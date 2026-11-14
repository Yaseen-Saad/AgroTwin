// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useI18n } from "@/lib/i18n";

export function LocaleToggle() {
  const { locale, setLocale, t } = useI18n();

  return (
    <div className="locale-toggle no-print" role="group" aria-label={t("language.label")}>
      <button
        type="button"
        aria-pressed={locale === "ar"}
        onClick={() => setLocale("ar")}
      >
        {t("language.ar")}
      </button>
      <button
        type="button"
        aria-pressed={locale === "en"}
        onClick={() => setLocale("en")}
      >
        {t("language.en")}
      </button>
    </div>
  );
}
