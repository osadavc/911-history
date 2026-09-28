"use client";

import { useEffect, useRef } from "react";

type Props = {
  /** Number of integer digits to render. */
  digits: number;
  /** Pushes a (possibly fractional) value; fractions roll digits like an odometer. */
  subscribe: (update: (value: number) => void) => () => void;
  className?: string;
};

const STRIP = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0];
// Cell height in em; the extra room lets the edge fade avoid the resting glyph.
const CELL = 1.2;

/** Odometer position of the 10^place digit for a continuous value. */
function digitPosition(value: number, place: number) {
  const unit = 10 ** place;
  const base = Math.floor(value / unit);
  const lower = value - base * unit;
  const carry = Math.min(1, Math.max(0, lower - (unit - 1)));
  return (((base % 10) + 10) % 10) + carry;
}

export function RollingNumber({ digits, subscribe, className }: Props) {
  const stripRefs = useRef<(HTMLSpanElement | null)[]>([]);

  useEffect(() => {
    return subscribe((value) => {
      for (let i = 0; i < digits; i++) {
        const strip = stripRefs.current[i];
        if (!strip) continue;
        const place = digits - 1 - i;
        const pos = digitPosition(value, place);
        strip.style.transform = `translateY(${-pos * CELL}em)`;
        // Motion blur-ish softening while a digit is between two values.
        const between = Math.abs(pos - Math.round(pos));
        strip.style.filter = between > 0.02 ? `blur(${between * 1.2}px)` : "";
      }
    });
  }, [digits, subscribe]);

  return (
    <span
      className={`inline-flex overflow-hidden tabular-nums ${className ?? ""}`}
      style={{
        height: `${CELL}em`,
        lineHeight: CELL,
        maskImage:
          "linear-gradient(to bottom, transparent 0%, black 18%, black 82%, transparent 100%)",
      }}
    >
      {Array.from({ length: digits }, (_, i) => (
        <span
          // biome-ignore lint/suspicious/noArrayIndexKey: digit columns are positional
          key={i}
          className="relative inline-block"
          style={{ height: `${CELL}em` }}
        >
          <span
            ref={(node) => {
              stripRefs.current[i] = node;
            }}
            className="flex flex-col will-change-transform"
          >
            {STRIP.map((d, j) => (
              // biome-ignore lint/suspicious/noArrayIndexKey: the strip repeats 0
              <span key={j} className="block" style={{ height: `${CELL}em` }}>
                {d}
              </span>
            ))}
          </span>
        </span>
      ))}
    </span>
  );
}
