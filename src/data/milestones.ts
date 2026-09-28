/**
 * Milestones that didn't change the coupé's shape enough to be a stop, shown as
 * markers on the timeline. Source: research/history.md → "Timeline stop
 * recommendations" §4 (each entry links to its Porsche/press source there).
 */
export type Milestone = {
  /** Decimal year (e.g. 1998.25 ≈ 31 March 1998). */
  year: number;
  label: string;
  source: string;
};

export const MILESTONES: Milestone[] = [
  {
    year: 1965,
    label: "Targa shown at the IAA",
    source:
      "https://newsroom.porsche.com/en/press-kits/60-Years-Porsche-911/1.-Generation-Porsche-911-(Ur-Elfer),-1963-1973.html",
  },
  {
    year: 1966,
    label: "911 S — the first 911 on Fuchs forged wheels",
    source:
      "https://newsroom.porsche.com/en/products/porsche-one-millionth-911-milestone-seven-generations-13735.html",
  },
  {
    year: 1967,
    label: "Sportomatic semi-automatic",
    source:
      "https://newsroom.porsche.com/en/products/porsche-one-millionth-911-milestone-seven-generations-13735.html",
  },
  {
    year: 1972,
    label: "The ducktail",
    source:
      "https://newsroom.porsche.com/en/2022/history/porsche-50-years-911-carrera-rs-2-7-germanys-fastest-sports-car-28486.html",
  },
  {
    year: 1974,
    label: "The 911 Turbo",
    source:
      "https://newsroom.porsche.com/en/2024/history/porsche-drive-system-911-36059.html",
  },
  {
    year: 1981,
    label: "Peter Schutz reverses the 911's phase-out",
    source:
      "https://newsroom.porsche.com/en/company/porsche-peter-schutz-ceo-obituary-14435.html",
  },
  {
    year: 1982,
    label: "Cabriolet",
    source:
      "https://newsroom.porsche.com/en/products/porsche-one-millionth-911-milestone-seven-generations-13735.html",
  },
  {
    year: 1987,
    label: "The 250,000th 911",
    source:
      "https://newsroom.porsche.com/en/2024/history/porsche-klassik-911-g-model-anniversary-model-1987-35245.html",
  },
  {
    year: 1988.6,
    label: "Carrera 4 — the first all-wheel-drive 911",
    source:
      "https://newsroom.porsche.com/en/press-kits/60-Years-Porsche-911/3.-Generation-Porsche-911,-(964),-1988---1994.html",
  },
  {
    year: 1990,
    label: "Tiptronic",
    source:
      "https://newsroom.porsche.com/en/press-kits/60-Years-Porsche-911/3.-Generation-Porsche-911,-(964),-1988---1994.html",
  },
  {
    year: 1995,
    label: "993 Turbo — the first twin-turbo 911",
    source:
      "https://newsroom.porsche.com/en/2024/history/porsche-drive-system-911-36059.html",
  },
  {
    year: 1997.7,
    label: "Water cooling",
    source:
      "https://newsroom.porsche.com/en/2024/history/porsche-drive-system-911-36059.html",
  },
  {
    year: 1998.25,
    label: "The last air-cooled 911 leaves the line",
    source: "https://www.stuttcars.com/1998-porsche-993-turbo-last-waltz/",
  },
  {
    year: 2006,
    label: "Variable-geometry turbo",
    source:
      "https://newsroom.porsche.com/en/2024/history/porsche-drive-system-911-36059.html",
  },
  {
    year: 2008.5,
    label: "Direct injection and PDK",
    source:
      "https://newsroom.porsche.com/en/products/porsche-one-millionth-911-milestone-seven-generations-13735.html",
  },
  {
    year: 2011.7,
    label: "Seven-speed manual",
    source:
      "https://newsroom.porsche.com/dam/jcr:05c3198c-772f-4e4d-88ad-b6fce31b66ed/S11_0327_en.pdf",
  },
  {
    year: 2015.9,
    label: "Every Carrera turbocharged",
    source:
      "https://newsroom.porsche.com/en/products/porsche-911-carrera-new-2015-11366.html",
  },
  {
    year: 2017.36,
    label: "The one-millionth 911",
    source:
      "https://newsroom.porsche.com/en/products/porsche-one-millionth-911-milestone-13733.html",
  },
  {
    year: 2018.9,
    label: "Eight-speed PDK, built with room for an electric motor",
    source:
      "https://newsroom.porsche.com/en/press-kits/60-Years-Porsche-911/8.-Generation-Porsche-911,-(992),-seit-2018.html",
  },
  {
    year: 2024.4,
    label: "T-Hybrid",
    source:
      "https://newsroom.porsche.com/en/2024/products/porsche-new-911-world-premiere-hybrid-36322.html",
  },
];

/** Place a (decimal) year on the stop index axis by interpolating stop years. */
export function yearToPosition(years: number[], year: number): number | null {
  if (years.length === 0) return null;
  if (year < years[0] || year > years[years.length - 1] + 0.999) return null;
  for (let i = 0; i < years.length - 1; i++) {
    if (year >= years[i] && year < years[i + 1]) {
      return i + (year - years[i]) / (years[i + 1] - years[i]);
    }
  }
  return years.length - 1;
}
