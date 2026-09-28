# Tracing a 911 stop into a car definition

Every timeline stop is described by one JSON file, `src/data/cars/<stop-id>.json`,
matching the `CarDef` type in `src/lib/car/types.ts`. The app lofts a body from
these curves and morphs vertex-for-vertex between neighbouring stops, so the
**conventions below must be identical for every stop** — otherwise the morph
blends unrelated features.

Every number must be derived from the research material for that stop
(`research/blueprints/<stop>/`, `research/photos/<stop>/` — especially files
marked `"tracing"` in `sources.json` — and dimensions in `research/specs.json` /
`research/geometry.json`). Record how each part was derived in
`research/traces/<stop-id>.md` (image used, calibration points, scale, checks).

## Coordinates (metres)

- `x` — distance from the **front tip** (foremost point of the car) rearwards.
- `y` — height above the ground.
- `z` — distance from the centre line (always ≥ 0; the car is symmetric).
- `length`, `frontAxle`, `rearAxle` are x positions; `trackFront/Rear` are full track widths.

## Calibration

- Side view: anchor on both wheel centres (`SideCalib` in `trace_lib.py`) using the
  official wheelbase; front axle height = tyre radius. Check that the computed overall
  length and height match the official figures within ~2 %. Body-in-white drawings
  without wheels: use the axle marks / arch centres, overall length, and dimension
  annotations printed on the drawing.
- Front/rear views: centre line + ground line + a known width (overall width, or the
  track measured between tyre centres) — `FrontCalib`.
- Top view: front and rear tips + centre line — `TopCalib`.
- Photos have perspective: prefer blueprints for the envelope, use photos to check
  proportions and to place details. Use distant, near-orthographic photos only.

## Body curves (`body`)

Each curve is a list of `[x, value]` keys sorted by x, spanning `0 … length`
(monotone cubic interpolation, so place keys at every change of direction; 15–40
keys per curve is typical). A cross-section at any x passes through, in order:

| key pair | point | 911 meaning |
|---|---|---|
| `floorY` | P0 floor centre (z = 0) | underside at the centre line: floor pan, bumper/apron bottoms at the ends |
| `rockerZ`,`rockerY` | P1 lower outer edge | sill/rocker bottom edge; **inside the wheel arches this is the arch edge** (the arch cut-out from the side view) at the fender's outer z |
| `sideZ`,`sideY` | P2 widest point | plan-view half-width (top view outline) and the height where that width occurs (front/rear views) |
| `crestZ`,`crestY` | P3 shoulder / fender crest | front: the crest of the front fender (above the headlight, higher than the hood); cabin: the door shoulder just below the window; rear: the crest of the rear hip |
| `beltZ`,`beltY` | P4 belt | cabin: the side-window sill (base of the glass). Ahead of the windscreen: the hood's side edge where it meets the fender. Behind the rear window: the engine-lid side edge |
| `roofZ`,`roofY` | P5 roof rail | cabin: the drip rail / top edge of the side glass; ahead of / behind the cabin it collapses onto the hood / engine lid (z small, y ≈ topY) |
| `topY` | P6 top centre | centre-line height: hood, windscreen, roof, rear window, engine lid, tail |

Notes:
- At x = 0 and x = length all z values are 0 (the section closes to a line).
- The side-view silhouette top equals `max(crestY, topY, roofY)` — on the front of a
  911 the fender crest is higher than the hood, so the side silhouette there is the
  crest, and `topY` (hood centre) comes from the front view / 3⁄4 photos.
- Wheel arches only raise `rockerY` (and pull `rockerZ` out to the fender lip);
  `floorY` stays low under the arches.
- Ducktail/whale tail: the ducktail is part of the body (`topY`/`crestY` kick up at
  the tail); a whale tail or tea tray is a separate `wing`.

## Decals (`decals`)

Flat shapes projected onto the body. Use **these slot ids** (only the ones the car
has); the same id on neighbouring stops morphs, a missing id dissolves.
Points are in car space for the plane: side `[x, y]`, top `[x, z]`, front/rear `[z, y]`
(z ≥ 0, right half only — mirrored automatically). Start closed outlines at the
**lowest-front** point and go **clockwise as seen in that view**, so shapes line up.

| id | plane | kind | finish | what |
|---|---|---|---|---|
| `side-glass` | side | fill | glass | door window + quarter window (one outline per window: `side-glass`, `quarter-glass`) |
| `quarter-glass` | side | fill | glass | rear quarter window if separate |
| `window-trim` | side | band | chrome / satin | frame around the side glass (chrome on classics, black on later cars) |
| `drip-rail` | side | line | chrome / satin | roof gutter line (classics) |
| `windscreen` | top | fill | glass | windscreen outline in plan view |
| `rear-window` | top | fill | glass | rear window outline in plan view |
| `door-gap`, `hood-gap`, `lid-gap`, `fuel-flap` | side/top | line | satin | panel gaps (hood/lid in top view) |
| `door-handle` | side | fill | chrome / satin | handle |
| `rocker-trim` | side | band/fill | chrome / satin | sill trim strip |
| `bumper-front`, `bumper-rear` | side | fill | chrome / satin / paint | bumper blade or impact bumper in side view |
| `bumper-front-face`, `bumper-rear-face` | front / rear | fill | same | bumper in front/rear view |
| `bumper-strip-front`, `bumper-strip-rear` | front / rear | fill | rubber | rubber rub strips |
| `bellows-front`, `bellows-rear` | side | fill | rubber | G-series accordion bellows |
| `indicator-front` | front | fill | lens | front turn signal (amber/clear) |
| `fog-front` | front | fill | lens | fog / driving lights |
| `intake-front` | front | fill (+stripes) | satin | front air intakes / grilles |
| `horn-grille` | front | fill (+stripes) | chrome/satin | classic horn grilles |
| `plate-front`, `plate-rear` | front / rear | fill | satin | licence plate recess |
| `taillight` | rear | fill | lens (#b3201a…) | tail lamp lens |
| `reflector-band` | rear | fill | lens | red band between tail lamps (964/993…), light bar (992) |
| `engine-grille` | top / rear | fill (+stripes) | satin | engine lid louvres |
| `badge-rear` | rear | fill | chrome / satin | "PORSCHE" script / lettering strip |
| `side-marker`, `side-repeater` | side | fill | lens | side reflectors / repeaters |
| `indicator-side`, `taillight-side` | side | fill | lens | lamp units wrapping round the corners |
| `intake-front-centre` | front | fill (+stripes) | satin | centre intake (modern aprons) |
| `reflector-rear` | rear | fill | lens | separate rear reflectors |
| `vent-rear` | rear | fill (+stripes) | satin | rear intercooler / air outlets (991.2 on) |
| `crest` | top | fill | chrome | Porsche crest on the front lid |

`color` is a hex or `"paint"` (body colour). `side: "left" | "right"` restricts a
decal to one side of the car (e.g. the fuel flap on the left front wing, a single
model badge); left = −z = the driver's side on left-hand-drive cars. `depth` limits where a decal applies
(side: |z| range; top: y range; front/rear: x range) so front decals don't print
on the rear, etc. `stripes: [period, duty]` darkens slats across the car by default
(along x on the top plane, along y elsewhere); add `stripeAxis: "a"` or `"b"` to repeat
them along the decal's first or second point coordinate instead, e.g. lengthwise
engine-lid louvres on the top plane use `stripeAxis: "b"` (they repeat across |z|).

## Parts

- `wheels.front/rear`: rim diameter from the tyre size (15 in → 0.381 m). Overall tyre
  diameter: for explicit aspect sizes compute it (205/55 R16 → 0.4064 + 2·0.205·0.55 =
  0.632 m); for sizes **without** an aspect ratio (e.g. 165 HR 15) do not assume one —
  measure it in side photos as a ratio to the wheelbase (scale-independent; the 1964–68
  car measures 0.265 × wheelbase ≈ 0.59–0.60 m, not the 0.65 m an 82 % profile gives),
  `design` from `RIM_DESIGNS` (closest match), colours from photos.
- `headlight`: lens centre `[x, y, z]`, outline `[u, v]` around the centre as seen from
  the front (u = image-right when looking at the car's right lamp, i.e. the lamp on
  the image-left of a front photo), `yaw`/`pitch` of the lens axis, ring width/colour.
- `mirror`, `wing`, `exhausts`: positions/sizes from photos. `mirror.sides: "left"` = a
  single driver's-door mirror (early cars); omit for a pair.
- Use `research/geometry.json` for each stop's documented details (bumper construction
  and finish, lamp units, grilles, badges, trims, mirrors, filler flap) — model what it
  documents, with colours/positions checked on photos.

## Verification (required)

Produce overlays in `research/traces/<stop-id>/`: side (top/bottom silhouettes,
arches, belt/roof lines, decals, wheel circles), top (plan outline, screens),
front and rear (section silhouettes, lamps) drawn over the reference images.
Iterate until they sit on the drawing/photo lines.
