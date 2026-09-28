"use client";

import { useEffect, useState } from "react";
import { RollingNumber } from "@/components/rolling-number";
import { TimelineScrubber } from "@/components/timeline-scrubber";
import { TimelineController } from "@/lib/timeline";

// Working list from research/STOPS.md — interaction test only.
const YEARS = [
  1959, 1963, 1964, 1969, 1973, 1974, 1975, 1978, 1984, 1989, 1994, 1998, 2002,
  2005, 2009, 2012, 2016, 2019, 2024,
];

export function LabTimeline() {
  const [controller] = useState(() => new TimelineController(YEARS.length, 0));
  useEffect(() => {
    (window as unknown as { __timeline: TimelineController }).__timeline =
      controller;
    return () => controller.dispose();
  }, [controller]);
  const subscribeYear = (update: (v: number) => void) =>
    controller.subscribe((p) => {
      const i = Math.min(YEARS.length - 2, Math.floor(p));
      const t = p - i;
      update(YEARS[i] + (YEARS[i + 1] - YEARS[i]) * t);
    });
  return (
    <div className="flex w-full flex-col items-center gap-10">
      <RollingNumber
        digits={4}
        subscribe={subscribeYear}
        className="text-6xl font-semibold tracking-tight"
      />
      <TimelineScrubber
        controller={controller}
        stops={YEARS.map((y, i) => ({
          id: `${i}`,
          label: String(y),
          ariaLabel: String(y),
        }))}
      />
    </div>
  );
}
