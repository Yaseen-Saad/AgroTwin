// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import ar from "@/i18n/ar.json";
import en from "@/i18n/en.json";

export type Locale = "ar" | "en";

const dictionaries: Record<Locale, Record<string, unknown>> = {
  ar: ar as Record<string, unknown>,
  en: en as Record<string, unknown>,
};

function lookup(dictionary: Record<string, unknown>, key: string): string {
  const value = key.split(".").reduce<unknown>((node, part) => {
    if (node && typeof node === "object") {
      return (node as Record<string, unknown>)[part];
    }
    return undefined;
  }, dictionary);
  return typeof value === "string" ? value : key;
}

interface I18nValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
  formatNumber: (value: number, digits?: number) => string;
  formatPercent: (value: number) => string;
}

const I18nContext = createContext<I18nValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("ar");

  useEffect(() => {
    const fromQuery = new URLSearchParams(window.location.search).get("lang");
    if (fromQuery === "ar" || fromQuery === "en") {
      setLocaleState(fromQuery);
      return;
    }
    const saved = window.localStorage.getItem("agrotwin.locale");
    if (saved === "ar" || saved === "en") {
      setLocaleState(saved);
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = locale === "ar" ? "rtl" : "ltr";
    window.localStorage.setItem("agrotwin.locale", locale);
  }, [locale]);

  const setLocale = useCallback((next: Locale) => setLocaleState(next), []);

  const t = useCallback(
    (key: string) => lookup(dictionaries[locale], key),
    [locale],
  );

  const formatNumber = useCallback(
    (value: number, digits = 0) =>
      new Intl.NumberFormat(locale === "ar" ? "ar-EG-u-nu-latn" : "en-GB", {
        maximumFractionDigits: digits,
        minimumFractionDigits: 0,
      }).format(value),
    [locale],
  );

  const formatPercent = useCallback(
    (value: number) => `${formatNumber(value * 100, 0)}%`,
    [formatNumber],
  );

  const value = useMemo(
    () => ({ locale, setLocale, t, formatNumber, formatPercent }),
    [locale, setLocale, t, formatNumber, formatPercent],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const value = useContext(I18nContext);
  if (!value) {
    throw new Error("useI18n must be used inside I18nProvider");
  }
  return value;
}
