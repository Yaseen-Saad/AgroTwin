// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"use client";

import { useI18n } from "@/lib/i18n";
import type { Mode } from "@/lib/types";

export function ModeBadge({ mode, compact = false }: { mode: Mode; compact?: boolean }) {
  const { t } = useI18n();
  const note = t(`mode.notes.${mode}`);

  return (
    <span
      className={`mode-badge mode-${mode.toLowerCase()}${compact ? " mode-compact" : ""}`}
      title={note}
    >
      <span className="mode-dot" aria-hidden="true" />
      <span className="mode-label">{t(`mode.labels.${mode}`)}</span>
      {!compact ? <span className="mode-note">{note}</span> : <span className="sr-only">{note}</span>}
    </span>
  );
}
