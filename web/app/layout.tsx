// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
import type { Metadata } from "next";
import { I18nProvider } from "@/lib/i18n";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgroTwin — from the sky to the land",
  description:
    "Replay a field's weather history, compare three crop rotations and see how a Scout sensor narrows the range. Illustrative fixture for NASA Space Apps 2026.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl">
      <body>
        <I18nProvider>{children}</I18nProvider>
      </body>
    </html>
  );
}
