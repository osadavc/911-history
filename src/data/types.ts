import type { CarDef } from "@/lib/car/types";

export type PaintColor = {
  name: string;
  code?: string;
  hex: string;
  type: "solid" | "metallic" | "special";
};

/** Numeric specs are null where the research found no documented figure. */
export type Specs = {
  engine: string;
  powerPs: number | null;
  torqueNm: number | null;
  /** 0–100 km/h in seconds. */
  zeroTo100: number | null;
  topSpeedKmh: number | null;
  weightKg: number | null;
};

export type Stop = {
  id: string;
  /** Scrubber label, usually the introduction year. */
  year: number;
  name: string;
  /** Internal code / series, e.g. "901", "G-series", "992.2". */
  code: string;
  /** Production span, e.g. "1964–1968". */
  span: string;
  summary: string;
  specs: Specs;
  colors: PaintColor[];
  /** Index of the colour shown first (the era's signature colour). */
  signature: number;
  car: CarDef;
};
