// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
import type { Result, Scenario } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";
const TIMEOUT_MS = 3500;

async function withTimeout(input: RequestInfo, init: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    return await fetch(input, { ...init, signal: controller.signal, cache: "no-store" });
  } finally {
    clearTimeout(timer);
  }
}

async function parseResult(response: Response): Promise<Result> {
  if (!response.ok) {
    throw new Error(`API ${response.status}`);
  }
  return (await response.json()) as Result;
}

export async function fetchDemoResult(siteId = "delta_01"): Promise<Result> {
  const response = await withTimeout(`${BASE}/demo/${siteId}`, { method: "GET" });
  return parseResult(response);
}

export async function diagnose(
  siteId: string,
  scenario: Scenario,
  rotationIds?: string[],
): Promise<Result> {
  const response = await withTimeout(`${BASE}/diagnose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ site_id: siteId, scenario, rotation_ids: rotationIds }),
  });
  return parseResult(response);
}

export function apiBase(): string {
  return BASE;
}
