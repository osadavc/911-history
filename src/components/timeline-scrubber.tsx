"use client";

import { useEffect, useRef, useState } from "react";
import type { TimelineController } from "@/lib/timeline";

const TICKS_PER_STOP = 4;
const MIN_TICK = 12;
const MAX_TICK = 64;
// Width of the "dock magnification" bump, in ticks.
const SIGMA = 7;

type ScrubberStop = { id: string; label: string; ariaLabel: string };

type Marker = { position: number; label: string };

type Props = {
  controller: TimelineController;
  stops: ScrubberStop[];
  /** Milestones between stops (fractional stop positions). */
  markers?: Marker[];
};

export function TimelineScrubber({ controller, stops, markers = [] }: Props) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const tickRefs = useRef<(HTMLSpanElement | null)[]>([]);
  const headRef = useRef<HTMLSpanElement>(null);
  const [spacing, setSpacing] = useState(10);
  const [active, setActive] = useState(controller.activeIndex);
  const [dragging, setDragging] = useState(false);

  const tickCount = (stops.length - 1) * TICKS_PER_STOP + 1;
  const width = (tickCount - 1) * spacing;
  const labelGap = spacing * TICKS_PER_STOP;
  const labelEvery = labelGap < 40 ? 2 : 1;

  useEffect(() => {
    const wrap = wrapRef.current;
    if (!wrap) return;
    const observer = new ResizeObserver(([entry]) => {
      const available = entry.contentRect.width - 48;
      setSpacing(Math.max(4.5, Math.min(11, available / (tickCount - 1))));
    });
    observer.observe(wrap);
    return () => observer.disconnect();
  }, [tickCount]);

  useEffect(() => {
    return controller.subscribe((position) => {
      const head = position * TICKS_PER_STOP;
      for (let i = 0; i < tickRefs.current.length; i++) {
        const tick = tickRefs.current[i];
        if (!tick) continue;
        const d = i - head;
        const k = Math.exp(-(d * d) / (2 * SIGMA * SIGMA));
        const h = MIN_TICK + (MAX_TICK - MIN_TICK) * k;
        tick.style.transform = `scaleY(${h / MAX_TICK})`;
        tick.style.opacity = String(0.17 + 0.33 * k);
      }
      if (headRef.current) {
        headRef.current.style.transform = `translateX(${head * spacing}px)`;
      }
      setActive(Math.round(position));
    });
  }, [controller, spacing]);

  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;
    let samples: { t: number; p: number }[] = [];
    let pointerId: number | null = null;
    let downX = 0;
    let downP = 0;
    let scrubbing = false;

    const positionAt = (clientX: number) => {
      const rect = track.getBoundingClientRect();
      return (clientX - rect.left) / spacing / TICKS_PER_STOP;
    };

    const onDown = (event: PointerEvent) => {
      if (event.button !== 0) return;
      pointerId = event.pointerId;
      track.setPointerCapture(pointerId);
      downX = event.clientX;
      downP = positionAt(event.clientX);
      scrubbing = false;
      samples = [{ t: event.timeStamp, p: downP }];
      // Glide the playhead to the pointer; a drag takes over from there.
      controller.animateTo(downP);
      setDragging(true);
    };
    const onMove = (event: PointerEvent) => {
      if (event.pointerId !== pointerId) return;
      // Ignore click jitter until the pointer really travels.
      if (!scrubbing && Math.abs(event.clientX - downX) < 3) return;
      scrubbing = true;
      const p = positionAt(event.clientX);
      samples.push({ t: event.timeStamp, p });
      samples = samples.filter((s) => event.timeStamp - s.t < 90);
      controller.scrubTo(p);
    };
    const onUp = (event: PointerEvent) => {
      if (event.pointerId !== pointerId) return;
      pointerId = null;
      setDragging(false);
      if (!scrubbing) {
        controller.animateTo(Math.round(downP));
        return;
      }
      const first = samples[0];
      const last = samples[samples.length - 1];
      const dt = last && first ? (last.t - first.t) / 1000 : 0;
      const velocity = dt > 0.008 ? (last.p - first.p) / dt : 0;
      controller.release(velocity);
    };

    track.addEventListener("pointerdown", onDown);
    track.addEventListener("pointermove", onMove);
    track.addEventListener("pointerup", onUp);
    track.addEventListener("pointercancel", onUp);
    return () => {
      track.removeEventListener("pointerdown", onDown);
      track.removeEventListener("pointermove", onMove);
      track.removeEventListener("pointerup", onUp);
      track.removeEventListener("pointercancel", onUp);
    };
  }, [controller, spacing]);

  const onKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "ArrowRight" || event.key === "ArrowUp") {
      event.preventDefault();
      controller.step(1);
    } else if (event.key === "ArrowLeft" || event.key === "ArrowDown") {
      event.preventDefault();
      controller.step(-1);
    } else if (event.key === "Home") {
      event.preventDefault();
      controller.animateTo(0);
    } else if (event.key === "End") {
      event.preventDefault();
      controller.animateTo(stops.length - 1);
    }
  };

  return (
    <div ref={wrapRef} className="flex w-full justify-center select-none">
      <div className="relative" style={{ width: width + 1 }}>
        <div
          ref={trackRef}
          role="slider"
          tabIndex={0}
          aria-label="Porsche 911 timeline"
          aria-valuemin={0}
          aria-valuemax={stops.length - 1}
          aria-valuenow={active}
          aria-valuetext={stops[active]?.ariaLabel}
          onKeyDown={onKeyDown}
          className={`relative h-[64px] touch-none outline-none focus-visible:ring-2 focus-visible:ring-neutral-900/20 rounded-sm ${
            dragging ? "cursor-grabbing" : "cursor-grab"
          }`}
        >
          {Array.from({ length: tickCount }, (_, i) => (
            <span
              // biome-ignore lint/suspicious/noArrayIndexKey: ticks are positional
              key={i}
              ref={(node) => {
                tickRefs.current[i] = node;
              }}
              className="absolute bottom-0 h-[64px] w-px origin-bottom bg-neutral-900 will-change-transform"
              style={{ left: i * spacing }}
            />
          ))}
          {markers.map((marker) => (
            <span
              key={marker.label}
              title={marker.label}
              className="absolute -top-3 size-[3px] -translate-x-1/2 rounded-full bg-neutral-400"
              style={{ left: marker.position * TICKS_PER_STOP * spacing }}
            />
          ))}
          <span
            ref={headRef}
            className="pointer-events-none absolute bottom-0 left-0 h-[70px] w-[2px] -translate-x-[0.5px] rounded-full bg-neutral-950 will-change-transform"
          />
        </div>
        <div className="relative mt-4 h-7">
          {stops.map((stop, index) => {
            if (index % labelEvery !== 0 && index !== active) return null;
            const isActive = index === active;
            return (
              <button
                key={stop.id}
                type="button"
                onClick={() => controller.animateTo(index)}
                aria-label={stop.ariaLabel}
                className={`absolute top-0 -translate-x-1/2 rounded-md px-1.5 py-1 font-sans text-[12.5px] leading-none tabular-nums tracking-[0.01em] transition-colors hover:bg-neutral-900/[0.05] ${
                  isActive
                    ? "font-semibold text-neutral-950"
                    : "text-neutral-500 hover:text-neutral-800"
                }`}
                style={{ left: index * labelGap }}
              >
                {stop.label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
