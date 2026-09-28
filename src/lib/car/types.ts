import type { Finish } from "@/lib/pixel/materials";
import type { BodyCurves } from "./body";

export type Pt = readonly [number, number];

export type DecalPlane = "side" | "top" | "front" | "rear";
export type DecalKind = "fill" | "line" | "band";

/**
 * A flat shape projected onto the body. Coordinates are in car space:
 * x = metres from the front tip rearwards, y = height, z = half-width.
 *  side  → points are [x, y], applied where the body faces sideways
 *  top   → points are [x, z], applied where the body faces up
 *  front → points are [z, y], applied where the body faces forward
 *  rear  → points are [z, y], applied where the body faces backwards
 */
export type Decal = {
  /** Slot name; decals with the same id morph into each other. */
  id: string;
  plane: DecalPlane;
  kind: DecalKind;
  points: readonly Pt[];
  finish: Finish;
  /** Hex colour, or "paint" to follow the selected body colour. */
  color: string;
  /** Line / rim-band width in metres (0 = one art pixel). */
  width?: number;
  /** Minimum dot(normal, projection axis) for the decal to apply. */
  facing?: number;
  /** Clip range along the projection axis, in car space (side: |z|, top: y, front/rear: x). */
  depth?: readonly [number, number];
  /** Darker stripes (grilles/louvres): [period m, duty 0..1]. */
  stripes?: readonly [number, number];
  /**
   * Which of the decal's two point coordinates the stripes repeat along.
   * Default: "a" (x) on the top plane, "b" (y) on side/front/rear — i.e.
   * slats across the car. Use the other axis for lengthwise louvres.
   */
  stripeAxis?: "a" | "b";
  /** Only one side of the car (fuel flap, single badges). Left = driver side on LHD cars. */
  side?: "left" | "right";
};

export type WheelDesign =
  | "steel-hubcap"
  | "fuchs"
  | "cookie"
  | "ats"
  | "cup"
  | "twist"
  | "five-spoke"
  | "twin-spoke"
  | "ten-spoke";

export type WheelDef = {
  /** Overall tyre diameter, m. */
  diameter: number;
  /** Tyre section width, m. */
  width: number;
  /** Rim diameter, m. */
  rim: number;
  design: WheelDesign;
  /** Spoke / face colour. */
  face: string;
  /** Rim lip colour. */
  lip: string;
  /** Brake caliper colour (null = drum/hidden). */
  caliper: string | null;
};

export type LampDef = {
  /** Centre of the lens in car space [x, y, z]. */
  centre: readonly [number, number, number];
  /** Lens outline in the lens plane, metres, around its centre ([u right, v up]). */
  outline: readonly Pt[];
  /** Lens axis: yaw (deg, 0 = straight ahead) and pitch (deg, + = tilted back). */
  yaw: number;
  pitch: number;
  /** Surround ring width (m) and finish. */
  ring: number;
  ringColor: string;
  ringFinish: Finish;
  lensColor: string;
  /** Inner graphic: "sealed" round beam, "projector", "led4" four-point DRL, "bar" LED strip. */
  graphic: "sealed" | "projector" | "led4" | "bar";
};

export type MirrorDef = {
  /** Mount point on the door / A-pillar triangle, car space. */
  at: readonly [number, number, number];
  /** Housing size: length (x), height (y), depth (z out from the body). */
  size: readonly [number, number, number];
  shape: "round" | "flag" | "aero";
  color: string;
  finish: Finish;
  /** Early cars had a single mirror on the driver's (left) door. */
  sides?: "left" | "both";
};

export type WingDef = {
  kind: "none" | "whale" | "tea-tray";
  /** Leading / trailing edge x (car space). */
  x0: number;
  x1: number;
  /** Top surface height at the leading edge. */
  y: number;
  halfSpan: number;
  /** Rubber lip colour along the trailing edge. */
  lip: string;
  /** Slab thickness, m (default 0.05). */
  thickness?: number;
  /** How far the trailing edge sweeps up above the leading edge, m (default 0). */
  rise?: number;
  /** Height of the rubber lip standing on the trailing edge, m (default 0). */
  lipHeight?: number;
};

export type CarDef = {
  id: string;
  length: number;
  frontAxle: number;
  rearAxle: number;
  trackFront: number;
  trackRear: number;
  body: BodyCurves;
  decals: readonly Decal[];
  wheels: { front: WheelDef; rear: WheelDef };
  headlight: LampDef;
  mirror: MirrorDef;
  wing: WingDef;
  /** Exhaust tips: [x, y, z] car space, radius. */
  exhausts: readonly (readonly [number, number, number, number])[];
};
