import { CARS } from "./cars";
import stopsJson from "./stops.json";
import type { PaintColor, Stop } from "./types";

type StopJson = Omit<Stop, "car" | "colors"> & { colors: PaintColor[] };

/** Timeline stops compiled from research/ (see research/tools/build_app_data.py). */
export const STOPS: Stop[] = (stopsJson as StopJson[]).map((stop) => ({
  ...stop,
  car: CARS[stop.id],
}));
