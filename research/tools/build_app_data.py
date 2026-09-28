"""Compile the research into the compact data the app ships: src/data/stops.json.

Reads research/specs.json (sourced specs), research/colors.json (sourced factory
paints) and the traced car definitions in src/data/cars/. Only stops with a traced
car are included, in timeline order.

Run from the repo root:  python3 research/tools/build_app_data.py
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Display labels (editorial). Names/codes restate research/specs.json in short form; the
# span here is only a fallback — the researched production_years wins when parseable.
LABELS = {
    "00-t7-1959": ("Type 7 prototype", "Type 754 T7", "1959–1960"),
    "01-901-1963": ("901", "IAA show car", "1963–1964"),
    "02-911-swb-1964": ("911 2.0", "O/A-series", "1964–1968"),
    "03-911-lwb-1969": ("911", "B–F series", "1969–1973"),
    "04-carrera-rs-27-1973": ("911 Carrera RS 2.7", "F-series", "1972–1973"),
    "05-g-series-1974": ("911 2.7", "G-series", "1973–1977"),
    "06-930-turbo-1975": ("911 Turbo 3.0", "930", "1975–1977"),
    "07-911-sc-1978": ("911 SC", "G-series", "1977–1983"),
    "08-carrera-32-1984": ("911 Carrera 3.2", "G-series", "1983–1989"),
    "09-964-1989": ("911 Carrera 2", "964", "1988–1994"),
    "10-993-1994": ("911 Carrera", "993", "1993–1998"),
    "11-996-1-1998": ("911 Carrera", "996.1", "1997–2001"),
    "12-996-2-2002": ("911 Carrera", "996.2", "2001–2004"),
    "13-997-1-2005": ("911 Carrera", "997.1", "2004–2008"),
    "14-997-2-2009": ("911 Carrera", "997.2", "2008–2012"),
    "15-991-1-2012": ("911 Carrera", "991.1", "2011–2015"),
    "16-991-2-2016": ("911 Carrera", "991.2", "2015–2019"),
    "17-992-1-2019": ("911 Carrera", "992.1", "2019–2024"),
    "18-992-2-2024": ("911 Carrera", "992.2", "2024–today"),
}


# Scrubber year per stop: the calendar year each car was shown / production began,
# i.e. Porsche's own dating (research/history.md → "Timeline stop recommendations").
YEARS = {
    "00-t7-1959": 1959, "01-901-1963": 1963, "02-911-swb-1964": 1964, "03-911-lwb-1969": 1968,
    "04-carrera-rs-27-1973": 1972, "05-g-series-1974": 1973, "06-930-turbo-1975": 1974,
    "07-911-sc-1978": 1977, "08-carrera-32-1984": 1983, "09-964-1989": 1988, "10-993-1994": 1993,
    "11-996-1-1998": 1997, "12-996-2-2002": 2001, "13-997-1-2005": 2004, "14-997-2-2009": 2008,
    "15-991-1-2012": 2011, "16-991-2-2016": 2015, "17-992-1-2019": 2018, "18-992-2-2024": 2024,
}


def load(path, default):
    try:
        with open(os.path.join(ROOT, path)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def num(v):
    """Pull a number out of a spec value that may be a dict {value: ...} or a string."""
    if isinstance(v, dict):
        v = v.get("value")
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        m = re.search(r"[\d.]+", v.replace(",", ""))
        return float(m.group()) if m else None
    return None


def engine_label(engine):
    cc = num(engine.get("displacement_cc"))
    litres = f"{cc / 1000:.1f} L" if cc else ""
    asp = (engine.get("aspiration") or "").lower()
    cooling = (engine.get("cooling") or "").lower()
    if "twin" in asp or "bi-turbo" in asp or "biturbo" in asp:
        kind = "twin-turbo"
    elif "turbo" in asp:
        kind = "turbo"
    elif "air" in cooling:
        kind = "air-cooled"
    elif "water" in cooling or "liquid" in cooling:
        kind = "water-cooled"
    else:
        kind = ""
    return " ".join(p for p in (litres, kind, "flat-six") if p)


def first_sentences(text, limit=210):
    """Keep whole sentences up to ~limit characters for the side panel."""
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    out = ""
    for p in parts:
        if out and len(out) + len(p) + 1 > limit:
            break
        out = f"{out} {p}".strip()
    return out


def main():
    specs = load("research/specs.json", {})
    colors = load("research/colors.json", {})
    stops = []
    for sid, (name, code, span) in LABELS.items():
        car_path = os.path.join(ROOT, "src", "data", "cars", f"{sid}.json")
        if not os.path.exists(car_path):
            continue
        spec = specs.get(sid, {})
        # Prefer the researched production span when it starts with a plain "YYYY–YYYY".
        m = re.match(r"\s*(\d{4})\s*[–-]\s*(\d{4}|present)", str(spec.get("production_years", "")))
        if m:
            span = f"{m.group(1)}–{'today' if m.group(2) == 'present' else m.group(2)}"
        engine = spec.get("engine", {}) or {}
        perf = spec.get("performance", {}) or {}
        palette = []
        for c in colors.get(sid, []) if isinstance(colors, dict) else []:
            if not isinstance(c, dict) or not c.get("hex") or not c.get("featured"):
                continue
            # The T7 was a one-off: show only its own paint, not the 356 "context" colours.
            if str(c.get("note") or c.get("notes") or "").startswith("Context colour"):
                continue
            kind = c.get("type", "solid")
            palette.append({
                "name": c.get("name"),
                "code": c.get("code") or None,
                "hex": c.get("hex").lower(),
                "type": "metallic" if kind == "metallic" else ("special" if kind in ("special", "pts") else "solid"),
                "iconic": bool(c.get("iconic")),
            })
        stops.append({
            "id": sid,
            "year": YEARS[sid],
            "name": name,
            "code": code,
            "span": span,
            "summary": first_sentences(spec.get("summary", "")),
            "specs": {
                "engine": engine_label(engine),
                "powerPs": num(engine.get("power_ps")),
                "torqueNm": num(engine.get("torque_nm")),
                "zeroTo100": num(perf.get("zero_to_100_kmh_s")),
                "topSpeedKmh": num(perf.get("top_speed_kmh")),
                "weightKg": num(spec.get("weight_kg")),
            },
            "colors": palette,
            "signature": 0,        })
    # Default colour per stop: an iconic colour of that era (research/colors.json), picked so
    # neighbours differ and a drag through time also walks through each era's signature paints.
    def dist(a, b):
        ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
        cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
        return sum((x - y) ** 2 for x, y in zip(ca, cb)) ** 0.5

    prev = None
    for stop in stops:
        pal = stop["colors"]
        if not pal:
            continue
        iconic = [i for i, c in enumerate(pal) if c["iconic"]] or list(range(len(pal)))
        choice = iconic[0]
        if prev:
            far = [i for i in iconic if dist(pal[i]["hex"], prev) > 90]
            if far:
                choice = far[0]
        stop["signature"] = choice
        prev = pal[choice]["hex"]
    for stop in stops:
        for c in stop["colors"]:
            c.pop("iconic", None)

    out = os.path.join(ROOT, "src", "data", "stops.json")
    with open(out, "w") as f:
        json.dump(stops, f, indent=1, ensure_ascii=False)

    # Static registry of the traced cars that made it into the timeline.
    lines = ['import type { CarDef } from "@/lib/car/types";']
    for i, stop in enumerate(stops):
        lines.append(f'import car{i} from "./{stop["id"]}.json";')
    lines += ["", "/** Traced car definitions by timeline stop id (generated by research/tools/build_app_data.py). */",
              "export const CARS: Record<string, CarDef> = {"]
    for i, stop in enumerate(stops):
        lines.append(f'  "{stop["id"]}": car{i} as unknown as CarDef,')
    lines += ["};", ""]
    with open(os.path.join(ROOT, "src", "data", "cars", "index.ts"), "w") as f:
        f.write("\n".join(lines))
    missing = [s["id"] for s in stops if not s["colors"]]
    print(f"wrote {os.path.relpath(out, ROOT)}: {len(stops)} stops; without colours: {missing}")


if __name__ == "__main__":
    main()
