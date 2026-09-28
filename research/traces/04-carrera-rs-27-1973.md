# 04-carrera-rs-27-1973: 911 Carrera RS 2.7 Coupé, MY1973, Sport (M471)

Script: `research/traces/04-carrera-rs-27-1973.py` → `src/data/cars/04-carrera-rs-27-1973.json`,
`research/traces/04-carrera-rs-27-1973.calib.json`, checks in `research/traces/04-carrera-rs-27-1973/`.

**Traced car:** the Porsche Museum's white RS 2.7 with green "Carrera" script and green Fuchs
centres. Photos 01-side-left, 02-front and 03-rear are the museum studio shots marked
`"tracing"`, and 04, 05, 17 and 18 show the same car. It is a **Sport (M471)**: no overriders,
no sill strip, no rubber bumper strips, and a one-piece rear bumper with a raised centre
section (sources.json: "No bumper overriders (Sport)"; geometry.json 04 rear.bumper).

## What changed from stop 03, and where each part comes from

The research lists every visual change (history.md "What changed visually vs the 1969–73 911",
geometry.json 04 `changes_from_previous_stop`, `body`, `rear_spoiler`, `rear`). All other parts
are the F-series shell, which is the shell of stop 03.

| part | source | result |
|---|---|---|
| shell: roof, glasshouse, lids ahead of the spoiler, front wings, plan, sill | 1967 factory body drawing, with the 02/03 calibration (2.4567 mm/px, ground y 644.3, front axle "Plan 0" 2066, bumper face 1713) | same frame as 03 → clean morph |
| wheelbase 2271, length 4147, width 1652, tracks 1372/1394 | specs.json 04 | FA 0.8672, RA 3.1382, L 4.147 |
| **ducktail** (lid profile, lip, rear face) | photo 01 profile (column/row scans), photo 03 width | lip top 0.98 m at x 3.92–3.95, trailing edge x 3.993; lip ±0.46 m wide |
| engine-lid grille (black louvres ahead of the lip) | photo 01 (u 1555–1650), tbp-83845 plan | x 3.51–3.74, ±0.36 m |
| **rear flare** (+42 mm) | tbp-83845 plan outline (shape only), scaled to 1652 mm | peak half-width 0.826 at 0.1–0.2 m behind the rear axle; blends from the factory plan between x 2.45 and 2.75 |
| wheel arches (front and flared rear) | photo 01, radial scans from the hub centres (body = white or green pixels) | arch tops 0.706 (front) / 0.675 (rear) |
| front bumper and chin spoiler (body colour, no guards, no strip) | photo 01 | face 0.505 → 0.299 m, spoiler edge 0.28–0.30 m |
| Sport rear bumper | photo 01 profile + photo 03 widths | side portions to x 4.09 (±0.745 m, 0.34–0.50 m high); raised centre section (±0.43 m) to L at 0.487 m |
| door / glass / trim / drip rail / handle / vent bar | photo 01, checked on the factory sheet | see the note below |
| "Carrera" stripe + script | photo 01 green pixels | left flank; mirrored for the right flank |

**Door and glass note.** The factory sheet is a body-in-white drawing, so its door and window
lines are the *apertures*. The photo confirms this: the door front edge is at 1.383 m, and the
sheet's aperture line is at 1.381 m. The 02/03 door-gap (sheet x 2296) and DLO readings sit
5–9 cm ahead of these lines. The RS decals were therefore re-traced from photo 01. The
03 → 04 morph shifts the door line by ≈5 cm, which is visible but smooth.

## Calibration

* **Photo 01.** Hub centres come from rim-lip circle fits, (414.78, 787.30) and (1397.76, 788.02),
  with rms 0.4 px. 982.98 px = 2271 mm gives 2.3103 mm/px at the wheel planes; tyre contact is
  at y 919.
  * **x.** Features near the wheel planes use the near-plane scale about the front hub.
    Centre-plane tail features (lid, lip, bumper profile) are stretched about the rear hub by
    KT = 1.027, so the photo's rear-most bumper point (u 1823) lands on L. They are 0.4–0.8 m
    farther from the camera than the hubs.
  * **y.** The model keeps 03's body frame at the official 1320 mm height. The photo's shell
    features sit 3–6 cm lower above the tyre contact than the factory sheet puts them, so the
    museum car sits lower on its wheels. The 03 trace saw the same effect on its photo.
    Photo heights are mapped with DELTA(x) = 0.0614 − 0.0086·x m, a least-squares fit on 6 shell
    landmarks common to the sheet and the photo:

    | landmark | residual |
    |---|---|
    | belt | −1.0 cm |
    | glass top | +0.9 cm |
    | roof | −0.3 cm |
    | fastback | +0.1 cm |
    | front arch top | +0.9 cm |
    | headlamp | −0.6 cm |
* **tbp-83845 (RS 4-view line drawing).** Hub fits (895.63, 325.98) and (1612.33, 325.89);
  716.7 px = 2271 mm. By its own hubs it measures L 4.151, front overhang 0.870, rear 1.010 and
  roof 1.288 (−2.4 %), and its plan reads ~2.6 % wide. It draws a Touring, and its rear-most
  point is the bumper / overrider at 0.44 m height.
  * sources.json's "−3.2 %" WB/L error came from a coarser hub estimate. By its hubs the
    drawing agrees with the official length.
  * vec-4925 (+2.1 % in sources.json), with hubs from tyre-edge fits (398.4 px = 2271 mm),
    gives a front overhang of 0.860, a rear overhang of 0.906 and L 4.037. That does not match
    its own printed 4102. Its rear overhang is even shorter than photo 01 shows at the
    near-plane scale (0.98 m), so only its front overhang was used, as a cross-check.
* **End photos 02 and 03.**
  * Lateral scale is set per depth. It comes from the 520 mm plates (front 360 px, rear 367 px)
    and the tracks (tyre centres 872 / 890 px), which put the camera ≈9.7 / 9.4 m from the plates.
    Then z = |u − centre| · s · (D + Δx)/D.
  * Heights come from photo 01 where possible.
  * For the check overlays, the ground rows (1250 / 1228) were fitted on the bumper-plane parts.

## Checks

| check | model | reference |
|---|---|---|
| wheelbase | 2.271 | 2271 (specs.json) |
| length | 4.147 | 4147 (specs.json; the brochure gives 4102 and de.wikipedia 4163) |
| front / rear overhang | 0.867 / 1.009 | tbp-83845 0.870 / 1.010; vec-4925 0.860 / 0.906 (rear rejected) |
| width | 1.652 | 1652 |
| height | 1.322 | 1320 |
| tyres | 0.640 / 0.639 m | 185/70 R15 and 215/60 R15, computed (TRACING.md); photo 01 loaded radius (hub to contact) 0.304 m, consistent with ~1.6 cm deflection |

* **`check-side-photo-persp.png`** is the main side check. It uses a pinhole camera, via the 996
  trace's photo-fit helper, with the hubs pinned and a hub height of 0.349 m in the model
  frame. It gets IoU 0.936 at D 9 m with the camera 1.0 m high, and a median top-edge error of 0 mm.
  * Door, glass, handle, script and arches lie on the photo.
  * In the photo the nose is 1.6 cm shorter and the tail 3.7 cm longer than the model (see
    doubts).
* **`check-side-photo.png`** is the flat, hub-calibrated overlay. All near-plane features match.
  The centre-plane nose appears 0.11 m ahead of the photo's nose; this is perspective, not
  a shape error.
* **`check-side.png`** (tbp-83845, hubs pinned).
  * These match the drawing: the ducktail tip, lid louvres, lamp boxes, bumper and front
    bumper top, relative to the hubs.
  * The drawing's front spoiler reaches ~4.5 cm lower than the photo, and the photo is used.
  * Its car also sits lower on its wheels, like the photo.
* **`check-top.png`** (tbp-83845 plan): the outline, the rear flare and the grille box sit on the
  drawing. The windscreen, rear window, fuel flap and lid gap are the 03 shell values.
* **`check-front.png` / `check-rear.png`** (studio photos, bumper-plane scale): the lamps, horn
  grilles, reflectors, plate, "PORSCHE" comb and "Carrera RS" boxes sit on the photo. The body
  silhouette is drawn too large/high there because a single orthographic scale cannot fit a
  photo taken from ~9.5 m.
* **`render.png`** shows six views. Morphs 03 → 04 → 05 were checked at t = 0.3, 0.5 and 0.7
  (front and rear three-quarter views): no stray decals, and the ducktail grows cleanly out of
  the flat lid.

## Parts and decals

* **Wheels.**
  * Tyres: 185/70 VR 15 → 0.640 m and 215/60 VR 15 → 0.639 m, computed; widths 0.185 / 0.215.
  * Fuchs design; the museum car has green spoke centres and a polished lip (photos 01/02/05).
  * Tracks 1.372 / 1.394.
* **Headlamp**: 02/03 values (same part).
* **Mirror**: rectangular chrome mirror on the left door (MY1973; geometry.json 04), as `flag`.
  Photo 02 gives 0.15 × 0.075 m with the inner edge at z 0.769; photo 01 gives x 1.515 and
  y 0.96.
* **Exhaust**: a single tailpipe on the car's left, z 0.57 (photo 03) and y 0.34 (photo 01).
* **Decal slot ids are as in 03**: side-glass, quarter-glass, window-trim, vent-divider,
  drip-rail, door-gap, door-handle, bumper-front / bumper-rear, indicator-side,
  taillight-side, horn-grille, parking-front, indicator-front, taillight, reverse-light,
  indicator-rear, reflector-rear, plate-rear, badge-rear, windscreen, rear-window,
  engine-grille, cowl-grille, crest, fuel-flap (`side: left`), hood-gap and lid-gap.
  * bumper-front / bumper-rear here are the green stripe bands on the bumpers. They use
    `facing 0` so they wrap onto the faces; the rear one stops at |z| 0.535, as in photo 03.
  * horn-grille is black on MY1973 cars.
  * badge-rear is the green "PORSCHE" comb on the lid's lower edge.
  * **New ids**: `carrera-script` (left), `carrera-script-r` (right) and `script-rear` (the
    "Carrera RS" script, on the right of the lip only, as geometry.json 04 says).
* **The script** is the green areas of photo 01, which include the stripe pieces, the letter
  outlines and the letter counters. The white letters are reversed out of the stripe. The
  script is one even-odd polygon: 11 rings, blobs ≥ 180 px², simplified at 1 cm, 75 points.
  * **The right flank carries the mirror image**, reflected about the middle of the stripe:
    it reads rear-to-front, with the "C" ahead of the rear arch. This matches photos 07 and 22
    (two other RS 2.7 seen from the right). The museum car's right side is not photographed.
* **Absent parts.**
  * rocker-trim: the museum Sport has a white sill in photo 01. 03's chrome strip dissolves.
  * front guards / overriders (Sport).
  * **plate-front**: the museum shows a display plate, and the 1972 factory photos 14 and 15
    show no plate. That slot budget went to the right-hand script.
  * The central oil-cooler opening of the front spoiler (de.wikipedia) is hidden behind the
    plate in every museum photo, so it is not modelled.
* **Budget.** 03 ∪ 04 uses 40 ids and 750 points; 04 ∪ 05 uses 40 ids and 974 points. The
  shader draws 40 decals and 1024 points per morph pair, so **no further decal ids fit next to
  05**.

## Known uncertainties / open doubts

* **Length and overhang split.** specs.json chose 4147. geometry.json quotes 4102 (factory RS
  brochure), and de.wikipedia gives 4163. The model uses the drawings' front overhang and
  L 4147. The perspective check suggests the museum car's tail is ~3–4 cm longer than that. It
  depends on the fitted camera distance (8–12 m gives roughly ±2 cm), so it is within the spread
  of the sources.
* **Ducktail undercut.** In photo 01 the lip's underside curves forward-down to (3.91, 0.79)
  before the rear face runs back. A one-ring-per-x loft cannot hold a floating lip, so the
  side silhouette is filled under the lip. P3 → P4 closes it as a slope from the hip crest up to
  the lip's side edge. This is a car-system limitation, not a research gap.
* **Ride height.** The body is at 03's official-height frame. The museum car (and the RS
  drawing) sits 3–6 cm lower relative to its wheels, with a slight nose-down attitude (the
  DELTA slope). Heights read from the photo are shifted into the model frame, not copied.
* **Centre-plane heights** (lid, lip) from the flat mapping carry about ±1.5 cm of perspective
  uncertainty, depending on the unknown camera height.
* **Colour.** Green was sampled from the stripe and decal pixels of photos 01/03 (#1a9630). The
  period factory photos 14–16 show red script and red wheels; colours.json does not name the
  script colour.
* **Touring vs Sport.** specs.json's performance and weight figures are for the Touring. The
  traced car is a Sport (bumpers, trim), and the shape figures (L, W, H, WB, tracks) are
  common to both.
