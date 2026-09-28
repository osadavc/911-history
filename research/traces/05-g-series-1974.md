# 05-g-series-1974 — 911 2.7 Coupé, G-series narrow body (MY1974–77)

Script: `research/traces/05-g-series-1974.py` (writes `src/data/cars/05-g-series-1974.json`,
`research/traces/05-g-series-1974.calib.json` and the `check-*.png` overlays).
The script also holds the G-series body model (`gseries_body`, `gseries_decals`) that
06 / 07 / 08 import, so the four G-series stops share one set of conventions.

## Spec car

Base 911 2.7 Coupé (150 PS), narrow body, no spoiler (specs.json 05; history.md "Timeline
stop recommendations": the 04 → 05 → 06 wide / narrow / wide zig-zag is historically right).

| figure | value | source |
|---|---|---|
| length / wheelbase | 4291 / 2271 mm | specs.json 05 |
| overhang front / rear | 932 / 1088 mm | geometry.json 05 (drawing dims 36.69 in; 168.94 − 89.41 − 36.69 in) |
| width | 1610 mm (at both axles) | specs.json 05 |
| height | 1320 mm | specs.json 05 |
| tracks | 1360 / 1342 mm | specs.json 05 (base 911, 5.5J) |
| tyres / wheels | 165 HR 15 on 5.5J × 15 steel with chromed hub caps | specs.json 05 |

## References

- **Side, front, rear:** `blueprints/05…/brochure_1975-US-911S_side-front-rear.png`, the
  official Porsche dimension drawing from the 1975 US brochure (911 S; inch dims).
- **Side photo:** `photos/05…/01-side-left.jpg` (Porsche studio profile, "tracing": side;
  a 1974 coupé without spoiler/script — used as the generic 1974 silhouette).
- **Rear photos:** 20-rear, 25-rear-34-right (lamp order, overriders, lid script).
- **Plan:** no 1974–77 plan exists in the research set (blueprints/05 sources.json:
  use the SC / Carrera 3.2 plans). Composite of three G-series plan views:
  `07…/vec-30946` (SC vendor 4-view), `08…/vec-1941` (Carrera 3.2 vendor 4-view),
  `07…/tbp-58380` (Autocar SC package drawing).
- **Front-lid centre line:** the dashed hidden lid line of the Polish 930 plan
  (`06…/dd_911-turbo_plan01…`, same G-series lid and wings).

## Calibration

Side view (3.0606 mm/px): wheel centres x 327.4 / 1069.4 px = centroids of the vertical
extension lines of the printed 36.69 in / 89.41 in dimensions (they pass through the
drawn wheel centres) → 742.0 px = 2271 mm. Ground = centre of the ground line, y 534.5.
Checks: roof y 102 → **1.3237 m** (official 1.320, +0.3 %); nose extension line x 23.5 →
front overhang **0.930 m** (official 0.932); drawn tyre r 104.6 px = 0.320 m = the labelled
185/70 VR 15.

**Rear overhang correction.** The sheet's rear extreme (the rubber guard, extension line
x 1443.5) lies 1.145 m behind the rear axle at the wheelbase scale, but the printed figures
give 1.088 m (the blueprint notes already flag "rear overhang measures 44.2 in vs 42.8 in").
The rear arch is drawn symmetric about the axle, and the official dd930 drawing plus three
side photos put the rear bellows 0.59–0.64 m behind the rear axle, so the excess lies
behind the arch: everything behind x 1192 px (the arch's rear leg) is compressed by
K = 0.926 so the guard lands on the official 4.291 m. `ref-side.png` is the sheet with the
same correction applied (used by check-side.png).

End views (their vertical scale differs from the lateral one, so each axis is calibrated
on its own and `ref-front.png` / `ref-rear.png` are isotropic copies):
front — centre x 303.5, lateral 1610 mm / 545 px = 2.954 mm/px, vertical ground 1165.5 /
roof 736.5 ↔ 1.320 m → 3.077 mm/px. Rear — centre x 1128, 1610 mm / 550 px = 2.927 mm/px
(check: the printed 36.82 in rear-window width spans 320 px → 2.922), vertical from the
printed 51.97 in height (y 735.5 → 1168) → 3.052 mm/px.

## How each curve was made

- **topY** (centre line): side-view top edge (auto, first dark pixel per column; the
  23.03 in / 25.39 in dimension annotations over the screens masked, the dotted
  engine-lid grille bridged) from the cowl to the tail; ahead of the cowl the lid centre =
  wing silhouette minus the drop read on the Polish 930 side view (0.124 m at 0.5 m ahead of
  the front axle → 0 at 0.06 m behind it); lid front edge 0.583 m (front view y 976).
- **crestY / crestZ**: wing silhouette over the lamps (side view), wing top 0.885 m at the
  A-pillar base (front view y 878, z 0.660), door shoulder 21 mm below the sill, rear-wing
  ridge 0.888 m / z 0.676 at the C-pillar base (rear view), then 40 mm below the deck edge;
  lamp z from the front view (0.61).
- **beltY / beltZ**: lid side edge 30 mm below the lid crown (z 0.424 at the lid corner,
  front view; 0.585 at the cowl, dd930 plan), window sill (side view), then the drawn deck
  edge (drip rail down the rear-window side → engine-lid gutter; z 0.483 → 0.427, rear view).
- **roofY / roofZ**: drip rail (side view), z 0.536 (rear view roof corner), rear-window
  half-width 0.468 (printed 36.82 in); behind the cabin P5 lies on the crowned deck between
  the centre line and the deck edge, y5 = top − (top − y4)·(z5/z4)^3.8 — the exponent fitted
  to the rear view (the grille's top edge is 3.4 cm lower at z 0.375 than on the centre line,
  the deck edge 8.7 cm lower at z 0.48). The flat-P5 convention of 02 made a W-shaped deck
  with a centre ridge that scalloped the rear-window / grille decals.
- **rockerY** (lower edge): hand-read on 10 px grids — nose rubber, bumper bottoms,
  aprons, the outer edge of the black wheel-well band for both arches, painted sill bottom.
- **floorY**: 6.3 in (160 mm) printed under the floor centre; bumper / apron bottoms.
- **sideZ**: plan composite (median of the three plan views, each normalised at the front
  axle; mirrors bridged; Savitzky–Golay 0.15 m) scaled to 805 mm at the front axle, the
  SC/Carrera rear-wing widening (+21 mm/side) removed so the rear axle is also 805 mm; the
  loft bulge beyond P2 compensated so the top-view outline equals the target (max width
  1.620 m, +0.6 %).
- **sideY**: bumper rubbing-strip level at the ends, 0.55 m mid-body, ≥ arch edge + 30 mm.
  Over the front apron (x 0.07–0.28) P1 is pulled to the centre line and P2 sits at the apron
  corner so the apron face is body-coloured (the underbody segment would paint it black).

## Decals and parts (G-series set)

Side glass / quarter glass / vent divider (chrome frames, MY1974 911), drip rail (chrome),
door shut line, pull handle (photo: X 2.43–2.59), black rubbing strip on the sill,
rubbing strips along both bumper sides, **bellows-front / bellows-rear** (x 140–190 /
1283–1330 px, full bumper height), amber indicator wrap, tail-lamp side. Front view: rubbing
strip, amber indicators in the bumper ends (x 40–113 px), rubber lip on the nose. Rear view:
lamp units red / clear / amber inboard → outboard (photos 20, 25), red reflector band with
black PORSCHE lettering (`badge-rear`, as TRACING.md), rubbing strip, plate, rubber
overriders (z 0.31–0.41). Top: windscreen, rear window, black slatted lid grille, cowl grille,
crest, fuel flap on the left wing (studio photo X 1.17–1.34), lid gaps, and the "911" lid
script (`badge-model` in the top plane, like 03, placed on the lid at the rear-view height
0.745–0.765 m; photos 20, 25).

Headlamp: ring Ø 0.236 m, lens Ø 0.195 m, centre z 0.628 (front view), x 0.306 / y 0.706
(side view lamp glass), pitch 10° (glass leans back 13/72 px), chrome ring (1974 factory
photos). Mirror: single chrome flag mirror on the driver's door (geometry.json 05; front
view head at z 0.77–0.90, y ≈ 0.91). Exhaust: one pipe on the car's left (rear view x 940,
side view end (1368, 435)). Wheels: steel with hub caps, **0.60 m** tyre (165 HR 15 has no
aspect ratio; no 1974–77 photo shows it, so the value measured for the same tyre on the
1964–68 car's photos, 0.265 × wheelbase, is used), width 0.165, rim 0.381.

## Checks

- `check-side.png`: silhouette, arches, sill, bumpers, glasshouse lines sit on the drawing
  (corrected sheet) within ~1–2 px (3–6 mm).
- `check-side-photo.png` (hub-calibrated): arches, wheels, sill strip, door shut lines and
  handle sit on the photo; centre-line features project 5 % large (hubs are ~0.7 m nearer
  the camera). `check-side-photo-centre.png`: same photo calibrated for the centre plane
  (scale ratio 0.947 from the bumper tips) — the roof / screen / deck line sit on the
  photo within ~10 px (≈ 25 mm; the photographed Carrera's rear deck reads ≈ 40 mm lower).
- `check-front.png` / `check-rear.png`: section silhouettes, lamps, bumper, lamp row, plate
  and overriders on the (isotropic) end views.
- `check-top.png`: outline on the SC plan (the narrow body is 21 mm/side inside the SC
  rear wings, as expected).
- Overall: length 4.291, wheelbase 2.271, height 1.324 (+0.3 %), width 1.61 at both axles.

## Known uncertainties

- Lid centre line taken from the 930 Polish plan (same lid; not an official drawing).
- No original 1974–77 plan view: plan shape from SC / Carrera 3.2 plans minus the rear-wing
  widening (official widths enforce the axles only).
- Engine-lid / rear-window transverse crown is inferred (side-view deck edge + parabola);
  the brochure rear view suggests a slightly flatter lid top (≈ 6 cm crown vs 8.7 cm).
- Rear overhang: printed dims vs drawn sheet differ by 5 %; printed (official) used.
- The drawing is a US 911 S: its tall rubber guards and under-bumper fog lamps are US /
  option items. Fog lamps are omitted; the overriders are kept (RoW photos show them too).
- Tyre diameter for 165 HR 15 borrowed from the 02 photo measurement (±1.5 %).
- Chrome headlamp ring / window frames per 1974 factory photos (MY1975 Carrera differs).
- Decal budget: 03 → 05 unions 43 slots, 05 ↔ 06 ↔ 07 ↔ 08 ↔ 09 36–39 slots / ≤ 906 points
  (renderer cap 64 slots).
