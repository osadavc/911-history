"""Build research/index.html: every photo, blueprint, colour and spec per timeline stop.

Run from the repo root:  python3 research/tools/make_index.py
Open research/index.html in a browser (paths are relative, works from file://).
"""
import html
import json
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")


def load(path, default):
    try:
        with open(os.path.join(ROOT, path)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def stops():
    rows = []
    with open(os.path.join(ROOT, "STOPS.md")) as f:
        for line in f:
            m = re.match(r"\|\s*(\d\d-[\w.-]+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", line)
            if m:
                rows.append({"id": m.group(1), "title": m.group(2), "years": m.group(3)})
    return rows


def esc(v):
    return html.escape(str(v)) if v is not None else ""


specs = load("specs.json", {})
colors = load("colors.json", {})
geometry = load("geometry.json", {})

parts = []
nav = []
total = 0
for stop in stops():
    sid = stop["id"]
    photo_dir = os.path.join(ROOT, "photos", sid)
    sources = load(f"photos/{sid}/sources.json", [])
    by_file = {s.get("file"): s for s in sources if isinstance(s, dict)}
    files = sorted(f for f in os.listdir(photo_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))) if os.path.isdir(photo_dir) else []
    total += len(files)
    bp_dir = os.path.join(ROOT, "blueprints", sid)
    bps = sorted(f for f in os.listdir(bp_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"))) if os.path.isdir(bp_dir) else []
    nav.append(f'<a href="#{sid}">{esc(sid)} <b>{len(files)}</b></a>')

    spec = specs.get(sid, {}) if isinstance(specs, dict) else {}
    spec_rows = ""
    if spec:
        eng = spec.get("engine", {}) or {}
        perf = spec.get("performance", {}) or {}
        dims = spec.get("dimensions_mm", {}) or {}
        cells = [
            ("Model", spec.get("name")),
            ("Code", spec.get("internal_code")),
            ("Years", spec.get("production_years")),
            ("Engine", f'{eng.get("displacement_cc", "")} cc {eng.get("layout", "")} {eng.get("aspiration", "")}'),
            ("Power", f'{eng.get("power_ps", "")} PS @ {eng.get("power_rpm", "")}'),
            ("Torque", f'{eng.get("torque_nm", "")} Nm'),
            ("0-100", perf.get("zero_to_100_kmh_s")),
            ("Top speed", f'{perf.get("top_speed_kmh")} km/h'),
            ("Weight", (lambda w: (f'{w.get("value")} kg ({w.get("standard")})' if w.get("value") is not None else "—") if isinstance(w, dict) else w)(spec.get("weight_kg"))),
            ("L/W/H/WB", f'{dims.get("length", "")}/{dims.get("width", "")}/{dims.get("height", "")}/{dims.get("wheelbase", "")}'),
        ]
        spec_rows = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in cells)
        if spec.get("summary"):
            spec_rows += f'<tr><th>Summary</th><td>{esc(spec.get("summary"))}</td></tr>'

    swatches = ""
    for c in (colors.get(sid, []) if isinstance(colors, dict) else []):
        if not isinstance(c, dict):
            continue
        swatches += (
            f'<span class="sw{" feat" if c.get("featured") else ""}" title="{esc(c.get("name"))} {esc(c.get("code"))} ({esc(c.get("type"))})">'
            f'<i style="background:{esc(c.get("hex"))}"></i>{esc(c.get("name"))}<small>{esc(c.get("code"))}</small></span>'
        )

    tiles = ""
    for f in files:
        meta = by_file.get(f, {})
        rel = f"photos/{sid}/{f}"
        badge = f'<em>{esc(meta.get("tracing"))} ref</em>' if meta.get("tracing") else ""
        credit = f'{esc(meta.get("author", ""))} · {esc(meta.get("license", ""))}'
        src = meta.get("source_page") or meta.get("image_url") or ""
        tiles += (
            f'<figure><a href="{esc(rel)}" target="_blank"><img loading="lazy" src="{esc(rel)}"></a>'
            f'<figcaption>{badge}<b>{esc(f)}</b> {esc(meta.get("description", ""))}<br>'
            f'<a href="{esc(src)}" target="_blank">source</a> · {credit}</figcaption></figure>'
        )
    bp_tiles = "".join(
        f'<figure><a href="blueprints/{esc(sid)}/{esc(f)}" target="_blank"><img loading="lazy" src="blueprints/{esc(sid)}/{esc(f)}"></a><figcaption>{esc(f)}</figcaption></figure>'
        for f in bps
    )
    parts.append(
        f'<section id="{esc(sid)}"><h2>{esc(sid)} <span>{esc(stop["title"])} · {esc(stop["years"])}</span></h2>'
        f'<p class="count">{len(files)} photos · {len(bps)} blueprints</p>'
        + (f"<table>{spec_rows}</table>" if spec_rows else "")
        + (f'<div class="swatches">{swatches}</div>' if swatches else "")
        + f'<div class="grid">{tiles}</div>'
        + (f'<h3>Blueprints</h3><div class="grid">{bp_tiles}</div>' if bp_tiles else "")
        + "</section>"
    )

lineups = sorted(f for f in os.listdir(os.path.join(ROOT, "photos", "lineups")) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))) if os.path.isdir(os.path.join(ROOT, "photos", "lineups")) else []
lineup_html = "".join(f'<figure><a href="photos/lineups/{esc(f)}" target="_blank"><img loading="lazy" src="photos/lineups/{esc(f)}"></a><figcaption>{esc(f)}</figcaption></figure>' for f in lineups)

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>911 Research</title><style>
:root{{--bg:#f6f5f2;--fg:#1a1a1a;--mute:#777;--line:#e2e0da}}
body{{margin:0;background:var(--bg);color:var(--fg);font:13px/1.45 -apple-system,system-ui,sans-serif}}
header{{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:12px 20px;z-index:2}}
header h1{{font-size:15px;margin:0 0 6px}} nav{{display:flex;flex-wrap:wrap;gap:4px 12px}} nav a{{color:var(--mute);text-decoration:none}} nav b{{color:var(--fg)}}
section{{padding:20px;border-bottom:1px solid var(--line)}} h2{{font-size:16px;margin:0}} h2 span{{color:var(--mute);font-weight:400}}
.count{{color:var(--mute);margin:4px 0 10px}} table{{border-collapse:collapse;margin:0 0 10px}} th{{text-align:left;color:var(--mute);font-weight:400;padding:1px 14px 1px 0;vertical-align:top}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}} figure{{margin:0}} img{{width:100%;aspect-ratio:3/2;object-fit:cover;border-radius:4px;background:#ddd}}
figcaption{{font-size:11px;color:var(--mute);margin-top:3px;word-break:break-word}} figcaption b{{color:var(--fg);font-weight:500}} em{{background:#1a1a1a;color:#fff;font-style:normal;padding:0 4px;border-radius:3px;margin-right:4px}}
.swatches{{display:flex;flex-wrap:wrap;gap:6px 14px;margin:0 0 12px}} .sw{{display:flex;align-items:center;gap:5px}} .sw i{{width:14px;height:14px;border-radius:3px;box-shadow:inset 0 0 0 1px #0002}} .sw small{{color:var(--mute)}} .feat{{font-weight:600}}
</style></head><body><header><h1>Life of a 911 — research ({total} photos)</h1><nav>{"".join(nav)}</nav></header>
{"<section><h2>Lineups</h2><div class='grid'>" + lineup_html + "</div></section>" if lineup_html else ""}
{"".join(parts)}</body></html>"""
with open(os.path.join(ROOT, "index.html"), "w") as f:
    f.write(page)
print("wrote research/index.html with", total, "photos")
