"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { MILESTONES, yearToPosition } from "@/data/milestones";
import type { Stop } from "@/data/types";
import { TimelineController } from "@/lib/timeline";
import { VIEWS, type ViewName } from "./car-stage";
import { ColorPicker } from "./color-picker";
import { RollingNumber } from "./rolling-number";
import { SpecPanel } from "./spec-panel";
import { TimelineScrubber } from "./timeline-scrubber";

const CarStage = dynamic(() => import("./car-stage").then((m) => m.CarStage), {
  ssr: false,
});

const BACKGROUND = "#f4f3f0";

const PIXEL_SIZES = [
  { size: 1.5, label: "Fine" },
  { size: 2, label: "Pixel" },
  { size: 3, label: "Chunky" },
];

const VIEW_LABELS: Record<ViewName, string> = {
  "three-quarter": "¾",
  side: "Side",
  front: "Front",
  rear: "Rear",
  top: "Top",
};

export function LifeOf911({ stops }: { stops: Stop[] }) {
  const [controller] = useState(() => new TimelineController(stops.length, 0));
  const [active, setActive] = useState(0);
  const [selected, setSelected] = useState(() => stops.map((s) => s.signature));
  const [view, setView] = useState<ViewName | null>("three-quarter");
  const [pixelSize, setPixelSize] = useState(2);
  const [milestone, setMilestone] = useState<
    (typeof MILESTONES)[number] | null
  >(null);

  useEffect(() => {
    // Surface a milestone while the rolling year passes it.
    return controller.subscribe((p) => {
      const i = Math.max(0, Math.min(stops.length - 2, Math.floor(p)));
      const j = Math.min(stops.length - 1, i + 1);
      const t = Math.min(1, Math.max(0, p - i));
      const year = stops[i].year + (stops[j].year - stops[i].year) * t;
      const near =
        MILESTONES.find((m) => Math.abs(m.year - year) < 0.5) ?? null;
      setMilestone((prev) => (prev === near ? prev : near));
    });
  }, [controller, stops]);

  useEffect(() => {
    const unsubscribe = controller.subscribe((p) => setActive(Math.round(p)));
    if (process.env.NODE_ENV !== "production") {
      (window as unknown as { __timeline?: TimelineController }).__timeline =
        controller;
    }
    return () => {
      unsubscribe();
      controller.dispose();
    };
  }, [controller]);

  const stop = stops[active];
  const paints = stops.map((s, i) => s.colors[selected[i]]?.hex ?? "#bbbbbb");

  const subscribeYear = (update: (value: number) => void) =>
    controller.subscribe((p) => {
      const i = Math.max(0, Math.min(stops.length - 2, Math.floor(p)));
      const j = Math.min(stops.length - 1, i + 1);
      const t = Math.min(1, Math.max(0, p - i));
      update(stops[i].year + (stops[j].year - stops[i].year) * t);
    });

  return (
    <main
      className="relative flex min-h-dvh flex-col overflow-hidden text-neutral-900 lg:h-dvh lg:min-h-[640px]"
      style={{ background: BACKGROUND }}
    >
      <header className="flex items-start justify-between px-6 pt-5 text-[12.5px] sm:px-8">
        <p className="font-medium tracking-tight">Life of a 911</p>
        <p className="hidden max-w-[16rem] text-right text-neutral-500 sm:block">
          Drag the timeline. Drag the car to turn it.
        </p>
      </header>

      <section className="flex flex-col items-center pt-6 sm:pt-4">
        <RollingNumber
          digits={4}
          subscribe={subscribeYear}
          className="text-[52px] font-semibold tracking-[-0.04em] sm:text-[64px]"
        />
        <p className="mt-1 text-[14px] font-medium tracking-tight">
          {stop.name}
        </p>
        <p className="mt-0.5 text-[12.5px] text-neutral-500">
          {stop.code} · {stop.span}
        </p>
        <p
          className="mt-2 h-4 text-[12px] leading-4 text-neutral-400 transition-opacity duration-200"
          style={{ opacity: milestone ? 1 : 0 }}
          aria-live="polite"
        >
          {milestone
            ? `${Math.floor(milestone.year)} · ${milestone.label}`
            : ""}
        </p>
      </section>

      <section className="relative flex flex-col lg:min-h-0 lg:flex-1">
        <div className="relative h-[36vh] min-h-[240px] sm:h-[44vh] lg:h-auto lg:min-h-0 lg:flex-1">
          <CarStage
            controller={controller}
            stops={stops}
            paints={paints}
            view={view}
            background={BACKGROUND}
            pixelSize={pixelSize}
            onUserOrbit={() => setView(null)}
          />
        </div>
        <aside className="order-last mx-auto hidden w-full max-w-[20rem] flex-col gap-4 px-6 py-4 lg:absolute lg:top-1/2 lg:right-8 lg:mx-0 lg:flex lg:w-[15rem] lg:-translate-y-1/2 lg:px-0 lg:py-0">
          <p className="text-[12.5px] leading-relaxed text-neutral-500">
            {stop.summary}
          </p>
          <SpecPanel controller={controller} stops={stops} />
        </aside>
      </section>

      <section className="flex flex-col items-center gap-4 pb-6">
        <div className="flex flex-wrap items-center justify-center gap-2">
          <div className="flex items-center gap-1 rounded-full bg-neutral-900/[0.04] p-0.5 text-[12px]">
            {(Object.keys(VIEWS) as ViewName[]).map((v) => (
              <button
                key={v}
                type="button"
                onClick={() => setView(v)}
                aria-pressed={view === v}
                className={`rounded-full px-2.5 py-1 transition-colors ${
                  view === v
                    ? "bg-white text-neutral-900 shadow-sm"
                    : "text-neutral-500 hover:text-neutral-800"
                }`}
              >
                {VIEW_LABELS[v]}
              </button>
            ))}
          </div>
          <fieldset className="flex items-center gap-1 rounded-full bg-neutral-900/[0.04] p-0.5 text-[12px]">
            <legend className="sr-only">Pixel size</legend>
            {PIXEL_SIZES.map(({ size, label }) => (
              <button
                key={size}
                type="button"
                onClick={() => setPixelSize(size)}
                aria-pressed={pixelSize === size}
                title={`Art pixel = ${size} screen pixels`}
                className={`rounded-full px-2.5 py-1 tabular-nums transition-colors ${
                  pixelSize === size
                    ? "bg-white text-neutral-900 shadow-sm"
                    : "text-neutral-500 hover:text-neutral-800"
                }`}
              >
                {label}
              </button>
            ))}
          </fieldset>
        </div>
        {stop.colors.length > 0 ? (
          <ColorPicker
            colors={stop.colors}
            selected={selected[active]}
            onSelect={(index) =>
              setSelected((prev) =>
                prev.map((value, i) => (i === active ? index : value)),
              )
            }
          />
        ) : null}
        <div className="mt-2 w-full px-2 sm:px-4">
          <TimelineScrubber
            controller={controller}
            markers={MILESTONES.flatMap((m) => {
              const position = yearToPosition(
                stops.map((s) => s.year),
                m.year,
              );
              return position === null
                ? []
                : [{ position, label: `${Math.floor(m.year)} · ${m.label}` }];
            })}
            stops={stops.map((s) => ({
              id: s.id,
              label: String(s.year),
              ariaLabel: `${s.year} — ${s.name}`,
            }))}
          />
        </div>
      </section>

      <aside className="mx-auto flex w-full max-w-[22rem] flex-col gap-4 px-6 pb-10 lg:hidden">
        <p className="text-[12.5px] leading-relaxed text-neutral-500">
          {stop.summary}
        </p>
        <SpecPanel controller={controller} stops={stops} />
      </aside>
    </main>
  );
}
