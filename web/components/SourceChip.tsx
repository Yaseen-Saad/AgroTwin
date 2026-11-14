// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useI18n } from "@/lib/i18n";

export function SourceChip({ source, label }: { source: string; label?: string }) {
  const { t } = useI18n();
  const kind = source.split(":")[0].toLowerCase() || "other";
  const known = ["nasa", "computed", "scout", "quoted", "assumption"].includes(kind);

  return (
    <details className="source-chip-wrap">
      <summary className={`source-chip source-${known ? kind : "other"}`} title={source} dir="ltr">
        {label ?? source}
      </summary>
      <span className="source-detail" dir="auto">
        <span className="source-detail-tag" dir="ltr">
          {source}
        </span>
        <span>{t(`source.${known ? kind : "other"}`)}</span>
      </span>
    </details>
  );
}
