"use client";

import { useEffect, useRef } from "react";
import type { Specs, Stop } from "@/data/types";
import type { TimelineController } from "@/lib/timeline";

type Row = {
  key: keyof Omit<Specs, "engine">;
  label: string;
  unit: string;
  format: (v: number) => string;
};

const ROWS: Row[] = [
  {
    key: "powerPs",
    label: "Power",
    unit: "PS",
    format: (v) => Math.round(v).toString(),
  },
  {
    key: "torqueNm",
    label: "Torque",
    unit: "Nm",
    format: (v) => Math.round(v).toString(),
  },
  {
    key: "zeroTo100",
    label: "0–100 km/h",
    unit: "s",
    format: (v) => v.toFixed(1),
  },
  {
    key: "topSpeedKmh",
    label: "Top speed",
    unit: "km/h",
    format: (v) => Math.round(v).toString(),
  },
  {
    key: "weightKg",
    label: "Weight",
    unit: "kg",
    format: (v) => Math.round(v).toLocaleString("en-US"),
  },
];

/**
 * Numbers interpolate with the timeline, so dragging between two cars
 * counts the figures from one to the other as the body morphs.
 */
export function SpecPanel({
  controller,
  stops,
}: {
  controller: TimelineController;
  stops: Stop[];
}) {
  const valueRefs = useRef<(HTMLSpanElement | null)[]>([]);
  const engineRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    return controller.subscribe((position) => {
      const i = Math.max(0, Math.min(stops.length - 2, Math.floor(position)));
      const j = Math.min(stops.length - 1, i + 1);
      const t = Math.min(1, Math.max(0, position - i));
      const a = stops[i].specs;
      const b = stops[j].specs;
      ROWS.forEach((row, k) => {
        const el = valueRefs.current[k];
        if (!el) return;
        const va = a[row.key];
        const vb = b[row.key];
        // Undocumented figures (e.g. the T7 prototype's weight) stay blank
        // rather than being invented by interpolation.
        if (va == null || vb == null) {
          const known = t < 0.5 ? va : vb;
          el.textContent = known == null ? "—" : row.format(known);
          return;
        }
        el.textContent = row.format(va + (vb - va) * t);
      });
      if (engineRef.current)
        engineRef.current.textContent = (t < 0.5 ? a : b).engine;
    });
  }, [controller, stops]);

  return (
    <dl className="grid w-full grid-cols-[auto_1fr] gap-x-6 gap-y-2.5 text-[12.5px] leading-tight">
      <dt className="text-neutral-400">Engine</dt>
      <dd className="text-right text-neutral-800">
        <span ref={engineRef} />
      </dd>
      {ROWS.map((row, k) => (
        <div key={row.key} className="contents">
          <dt className="text-neutral-400">{row.label}</dt>
          <dd className="text-right tabular-nums text-neutral-800">
            <span
              ref={(node) => {
                valueRefs.current[k] = node;
              }}
            />
            <span className="ml-1 text-neutral-400">{row.unit}</span>
          </dd>
        </div>
      ))}
    </dl>
  );
}
