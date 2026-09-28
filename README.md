# Life of a 911

Drag a timeline from the Porsche 911's first design study to today and watch one
pixel-art 3D car morph through every generation, with the paint colours each era
offered and a small panel of what each car delivered.

```bash
bun install
bun run dev   # http://localhost:3000
```

## What's in it

- **19 stops** from the 1959 Type 7 design study to the current 992.2
  (`research/STOPS.md`), each a traced 3D car that morphs into the next.
- **~590 verified reference photos** (18–51 per stop), plus 32 lineup shots.
- **99 blueprints and drawings**, each checked against the official wheelbase/length ratio.
- **Sourced specs** for every stop, with 158 source conflicts logged, a ~28,600-word
  history, ~1,300 documented design details and 519 period factory paint colours.
- Milestones (Targa, Fuchs wheels, Turbo, water cooling, the millionth 911…) appear
  as the timeline rolls past them.

## How it works

- **Research first.** Everything the page shows comes from `research/`:
  - `photos/<stop>/`: verified reference photos per stop, with `sources.json` (author, licence, what was checked).
  - `blueprints/<stop>/`: factory drawings and four-view blueprints.
  - `specs.json` and `history.md`: sourced specs and history. Conflicts between sources are logged with the value chosen.
  - `geometry.json`: documented design details per stop (lamps, bumpers, trims, wheels).
  - `colors.json`: factory paint colours per era.

  Open `research/index.html` (built by `python3 research/tools/make_index.py`) to browse all of it.
- **Tracing.** Each stop has a reproducible trace script in `research/traces/<stop>.py`.
  It calibrates the drawings and photos against the official dimensions, extracts
  silhouettes, and records hand-read features. It then writes `src/data/cars/<stop>.json`.
  `research/tools/check_car.py` draws the result back over the references so each trace
  can be verified, and `research/tools/render_views.sh` renders it from six angles.
  `research/tools/TRACING.md` is the spec. `/lab` (dev only) renders any traced car or
  morph for these tools.
- **App data.** `python3 research/tools/build_app_data.py` compiles specs and colours
  into `src/data/stops.json` and the car registry `src/data/cars/index.ts`.
- **Morphing.** Every car is lofted through the same cross-section topology
  (`src/lib/car/body.ts`), so any two generations blend vertex-for-vertex. Windows,
  lamps, grilles and panel gaps are flat outlines projected onto the body
  (`body-material.ts`), and they morph too. Wheels, headlamps and mirrors are
  parametric parts. Paint blends in OKLab.
- **Pixel look.** `src/lib/pixel/stage.ts` renders at a low internal resolution with
  banded shading, a studio-horizon reflection and 1px outlines, and the browser
  upscales the canvas with `image-rendering: pixelated`.

## Code map

| Path | What |
|---|---|
| `src/components/life-of-911.tsx` | Page: year odometer, stage, spec panel, colour picker, timeline |
| `src/components/timeline-scrubber.tsx` | Dock-style magnifying tick scrubber (drag, flick, click, keys) |
| `src/lib/timeline.ts` | Continuous timeline position with spring snapping |
| `src/components/car-stage.tsx` | Three.js stage: orbit, view presets, shadow, morph per frame |
| `src/lib/car/*` | Car definition types, lofting, decals, wheels, lamps, morphing model |
| `src/lib/pixel/*` | Pixel renderer, materials, contact shadow |
| `src/data/*` | Compiled stops, traced cars, milestones |

## Licensing note

`research/photos/` and `research/blueprints/` (~360 MB) are mostly copyrighted press,
auction and drawing images kept as private modelling reference (each file's licence is
in its `sources.json`). Don't publish them. Keep the repo private, or git-ignore those
folders before pushing publicly. The app itself ships none of them.
