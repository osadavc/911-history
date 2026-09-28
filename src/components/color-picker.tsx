"use client";

import { useId } from "react";
import type { PaintColor } from "@/data/types";

type Props = {
  colors: PaintColor[];
  selected: number;
  onSelect: (index: number) => void;
};

export function ColorPicker({ colors, selected, onSelect }: Props) {
  const name = useId();
  const current = colors[selected];
  return (
    <fieldset className="flex flex-col items-center gap-3">
      <legend className="sr-only">Factory paint colour</legend>
      <div className="flex flex-wrap justify-center gap-1.5">
        {colors.map((color, index) => (
          <label
            key={`${color.name}-${color.code ?? index}`}
            title={color.name}
            className="group relative cursor-pointer"
          >
            <input
              type="radio"
              name={name}
              value={index}
              checked={index === selected}
              onChange={() => onSelect(index)}
              className="peer sr-only"
              aria-label={`${color.name}${color.code ? `, paint code ${color.code}` : ""}`}
            />
            <span
              className="block size-[18px] rounded-[3px] transition-transform duration-150 ease-out group-hover:scale-110 group-active:scale-95 peer-checked:ring-[1.5px] peer-checked:ring-neutral-900 peer-checked:ring-offset-2 peer-checked:ring-offset-[#f4f3f0] peer-focus-visible:outline-2 peer-focus-visible:outline-offset-4 peer-focus-visible:outline-neutral-900/40"
              style={{
                backgroundColor: color.hex,
                boxShadow: "inset 0 0 0 1px rgb(0 0 0 / 0.14)",
              }}
            />
          </label>
        ))}
      </div>
      <p
        className="h-4 text-[12px] leading-4 text-neutral-500"
        aria-live="polite"
      >
        <span className="text-neutral-800">{current?.name}</span>
        {current?.code ? (
          <span className="ml-1.5 tabular-nums">{current.code}</span>
        ) : null}
        {current?.type === "metallic" ? (
          <span className="ml-1.5">· metallic</span>
        ) : null}
      </p>
    </fieldset>
  );
}
