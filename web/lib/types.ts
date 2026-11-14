// AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
export type Mode = "LIVE" | "REPLAY" | "SIMULATED" | "NONE";

export interface Scenario {
  rain_mult: number;
  temp_offset_c: number;
  price_mult: number;
}

export interface RangeMetric {
  p10: number;
  median: number;
  p90: number;
  unit?: string;
  currency?: string;
  source: string;
}

export interface LowHighMetric {
  low: number;
  high: number;
  unit?: string;
  source: string;
}

export interface ValueMetric {
  value: number;
  unit?: string;
  source: string;
}

export interface BarcodeStripe {
  year: number;
  profit_per_ha: number;
  currency?: string;
  class: "green" | "amber" | "red";
  source: string;
}

export interface Rotation {
  rotation_id: string;
  label: string;
  metrics: {
    water_use_mm: RangeMetric;
    deficit_days: RangeMetric;
    bare_days: RangeMetric;
    erosion_index: RangeMetric;
    n_credit_kg_ha: LowHighMetric;
    profit_per_ha: RangeMetric;
    loss_year_share: ValueMetric;
  };
  evidence: string[];
  benefits: string[];
  gaps: string[];
  review_flags: string[];
  barcode: BarcodeStripe[];
  worst_year: {
    year: number;
    profit_per_ha: number;
    currency?: string;
    source: string;
  };
  loss_year_share: ValueMetric;
  excluded: {
    is_excluded: boolean;
    reasons: string[];
  };
}

export interface Fusion {
  used: boolean;
  scout_run_ids: string[];
  n_points: number;
  weights_by_year: Record<string, number>;
  ess: number;
  sigma_used: number;
  range_width: {
    without_scout: number;
    with_scout: number;
    unit: string;
    source: string;
  };
  confidence_label: "low" | "medium" | "high";
  bias_check: {
    n_overlap_days: number;
    mean_gap: number | null;
    applied: boolean;
  };
  notes?: string[];
}

export interface Result {
  schema_version: string;
  version: string;
  site_id: string;
  generated_by: string;
  mode: Mode;
  scenario: Scenario;
  years: number[];
  rotations: Rotation[];
  fusion: Fusion;
  scout_summary: {
    sightings: { healthy: number; diseased: number; unknown: number };
    model: string;
    note: string;
  };
  ranking: {
    weights: { water: number; soil: number; profit: number };
    order: string[];
    tie_band_applied?: boolean;
    notes?: string[];
  };
  assumptions?: Array<{
    id: string;
    description?: string;
    value?: string | number | boolean | null;
    source: string;
    editable: boolean;
  }>;
}
