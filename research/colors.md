# Porsche 911 factory colours, 1959–2026

Research for the "Life of a 911" colour selector, compiled 27 September 2026. The machine-readable data is in [`colors.json`](./colors.json): an object keyed by stop id (see [`STOPS.md`](./STOPS.md)), each holding an array of colours with `name`, `name_de`, `code`, `type` (`solid`/`metallic`/`special`/`pts`), `years`, `hex`, `hex_source` (`url` + `method`), `iconic`, `featured`, `sources`, an optional `note`, and `hex_candidates` (every swatch value that went into the hex).

There are **519 colour entries across all 19 stops**. Each stop has 6–10 `featured` colours, chosen to cover the iconic shades plus a spread of hues. 59 entries carry a low-confidence hex; their `hex_source.method` says so.

## How names, codes and years were verified

- **Porsche's own statements come first.** These include the Paint to Sample (PTS) colour library ([media.porsche.com/paint-to-sample](https://media.porsche.com/paint-to-sample), about 240 colours with official histories), the current [911 configurator](https://configurator.porsche.com/en-US/mode/model/9921B2), press kits, and Porsche Klassik/Christophorus articles. The two most useful articles are [the Klassik colour-history piece](https://newsroom.porsche.com/en/history/porsche-history-911-chameleon-944-928-colourful-tradition-13262.html), which gives the 1964/65 launch palette, and [Christophorus "Flying Colors"](https://newsroom.porsche.com/en/christophorus/porsche-targa-colors-11179.html), which lists the colours of each 911 generation at launch.
- **Model-year availability** comes from the Porsche Club of America's [Rennbow colour wiki](https://www.rennbow.org/color-wiki) (year and model searches, plus per-colour pages) and from paintref.com year pages. paintref is behind a CAPTCHA, so its pages were read from Common Crawl captures. German Wikipedia supplied colour lists for the 930 (from the 1980 '911 SC – 911 Turbo Farben' chart), 996, 997 and 991. [colors.stuttcars.com](https://colors.stuttcars.com/) adds factory-chart references (1965, 1968, 1971, and factory overviews for the 964 and 993).
- **A colour is listed only if at least two independent sources support it for that model and era,** or one Porsche source does. Rennbow years are years in which examples were *recorded*, not always the brochure years. Where only Rennbow supports an exact year range, the `note` says so.
- **Special colours are included when a source ties them to the stop,** and the famous ones are flagged: Linden Green, the 1960s specials, Mexico Blue on the last 993, and the 991/992 Paint to Sample classics.

## How the hex values were made (and how dark samples were fixed)

1. **Colours still in the current configurator** (Chalk, Provence, Aventurine Green, Gentian Blue, Guards Red, Black, White, GT Silver, and others): the hex is the median of the lit door panel in Porsche's own configurator render. The renders use the daylight setting, the low side camera and the white room. The method string lists the other sources and their ΔE from this value.
2. **All other colours:** the hex is the CIELAB mean of independent swatch sources. Each source type counts once, and only one Porsche render or library value is allowed. The source types are the PTS library `sg_hex_color`, the Porsche paint-sample renders shown on stuttcars, paintref chips, PaintScratch touch-up swatches, Rennbow chips, and panel samples from verified photos in `research/photos/<stop>/` whose source names the colour. Candidates more than 30 ΔE from the median are rejected. If no two sources agree within 30 ΔE, all of them are averaged and the entry is marked low confidence. PaintScratch placeholder swatches (one hex shared by three or more different colours, such as `#800000` or `#C0C0C0`) are ignored.
3. **The coordinator's dark samples, cross-checked:** these values came from shaded configurator studio swatches and were replaced. Chalk went from `#8f8f89` to `#b9bcbe`, Provence from `#565058` to `#6c677d`, and Aventurine Green Metallic from `#595953` to `#7f8484`. The same fix applies to Shade Green, Oak Green Neo, Slate Grey Neo, Lugano Blue, Cartagena Yellow, Vanadium Grey and Ice Grey. The old values stay in `hex_candidates` (as `pts` or `cfgswatch`), so the change is visible.
4. **Photo cross-checks** used the 25th–75th luminance-percentile median of a lit, non-highlight body-panel box. Period slides were first white-balanced against their licence plate. Photos used: 901 No. 57 (Signal Red), a 1966 911 (Polo Red), a 1973 911 T (Light Ivory), a 911 S 2.4 (Gemini Blue), a 1995 993 (Polar Silver), a 1976 930 (Emerald Green), several 996 cars from Bring a Trailer, the T7, the yellow and white 901 prototypes, and 'Quickblau'.
5. **Validation:** for the 17 current colours that have a daylight render, the consensus method was re-run without the render. It lands a mean of 12.2 ΔE (median 9.1, maximum 25.8) from Porsche's render. Expect older colours to be about that close. The same paint always gets the same hex in every stop, for example Guards Red from 1974 to 2026, Speed Yellow, and Irish Green.

## How the palette evolved

**Prototypes (1959–1963).** The one-off Type 754 T7 was later 'painted green metallic' and still wears that colour in the Porsche Museum ([stuttcars](https://www.stuttcars.com/porsche-911-f-series-the-story/)). No option list existed, so stop 00 pairs the T7 green with clearly labelled 356 B colours from 1959–61 as context. The first 901 prototype of 1962 was 'a clean, simple white' ([Porsche Klassik](https://newsroom.porsche.com/en/history/porsche-history-911-chameleon-944-928-colourful-tradition-13262.html)). The prototypes that followed wore white, dark blue (later red), yellow, 'Quickblau' and Signal Red, according to [Excellence](https://www.excellence-mag.com/issues/304/articles/out-of-the-shadows). The car on the IAA stand in September 1963 was the fifth prototype, chassis 13 325, with a Karmann body 'gelb lackiert' ([book excerpt](https://silo.tips/download/die-porsche-911-premiere-das-highlight-auf-der-iaa-in-frankfurt-1963); [stuttcars](https://www.stuttcars.com/porsche-911-f-series-the-story/)). Its exact shade is not named anywhere.

**The 1960s: signal colours and soft pastels.** At launch the 911 came in seven standard colours: Slate Grey, Ruby Red, Sky Blue, Light Ivory, Champagne Yellow, Irish Green and Signal Red. Four specials were also offered: Dolphin Grey, Togo Brown, Bali Blue and Black. By 1966 there were 30 special colours, including the first four metallics ([Porsche Klassik](https://newsroom.porsche.com/en/history/porsche-history-911-chameleon-944-928-colourful-tradition-13262.html)). Ferry Porsche's first 911, chassis 300 003, was painted green, his favourite colour ([Porsche Newsroom](https://newsroom.porsche.com/en/products/porsche-one-millionth-911-milestone-details-13734.html)); the PTS library names it Irish Green. The 1966–68 Targa launched in Aga Blue, Black, Slate Grey, Polo Red, Irish Green, Bahama Yellow, Light Ivory, Golf Blue and Sand Beige ([Christophorus](https://newsroom.porsche.com/en/christophorus/porsche-targa-colors-11179.html)). Jochen Rindt's 1967 911 S was Bahama Yellow ([Christophorus](https://newsroom.porsche.com/en/2022/history/porsche-911-s-jochen-rindt-vienna-garage-heinz-swoboda-christophorus-400-27214.html)), and the film car of Le Mans was Slate Grey ([Porsche](https://newsroom.porsche.com/en/2019/history/porsche-klassik-908-lemans-mcqueen-film-motorsports-15964.html)).

**Around 1969–1973: the loud years.** Porsche describes Canary Yellow, Blood Orange, Pastel Blue and Albert Blue 'setting the beat', with Bahama Yellow, Sepia Brown and Light Ivory as the softer side. In 'the psychedelic late 60s and 70s' came the 'frog-like' Viper Green, Gemini Blue Metallic and Gulf Blue ([Klassik](https://newsroom.porsche.com/en/history/porsche-history-911-chameleon-944-928-colourful-tradition-13262.html)). The PTS library dates Signal Orange (codes 1414, 1410 and 116), Gulf Orange (from 1972), Aubergine, Fraise/Rose Red and the special Linden Green to this period. The Carrera RS 2.7 was offered in 29 paint tones, 27 of which were built, including Bright Yellow, Red and Blood Orange ([Porsche](https://newsroom.porsche.com/en/2022/history/porsche-50-years-911-carrera-rs-2-7-germanys-fastest-sports-car-28486.html)). The favourite was still Grand Prix White with blue, red, green or black 'Carrera' script and wheel centres to match ([Klassik](https://newsroom.porsche.com/en/history/porsche-history-911-chameleon-944-928-colourful-tradition-13262.html)).

**The G-series and 930 (1974–1989): calmer, then red, white and pastel.** The G-model launched in Grand Prix White, Yellow-Green, Mexico Blue, Peru Red, Cockney Brown, Sahara Beige, Orange, Guards Red and Light Yellow ([Christophorus](https://newsroom.porsche.com/en/christophorus/porsche-targa-colors-11179.html)). From 1975 the range turned 'somewhat calmer', with darker tones, understatement and an eye on resale value ([Klassik](https://newsroom.porsche.com/en/history/porsche-history-911-chameleon-944-928-colourful-tradition-13262.html)). The production Turbo was unveiled in Viper Green Diamond ([Porsche](https://newsroom.porsche.com/en/press-kits/50-years-porsche-turbo/The-beginning-of-the-series.html)). The PTS library says the 930 'became famous when it was introduced in Oakgreenmetallic'. The 1980 SC/Turbo chart lists ten solid and ten metallic colours ([German Wikipedia](https://de.wikipedia.org/wiki/Porsche_930)). Through the 1980s Guards Red became the signature: 'hardly any other colour is as typical for a sports car' (PTS). The mid-1980s 'Miami Vice' fashion brought pastels ([Klassik](https://newsroom.porsche.com/en/history/porsche-history-911-chameleon-944-928-colourful-tradition-13262.html)), and the 3.2 Carrera added Cassis Red, Granite Green ([238 built](https://newsroom.porsche.com/en/2021/history/porsche-klassik-911-carrera-3-2-granite-green-christian-geistdoerfer-18920.html)) and the Diamond Blue Metallic of the anniversary model ([Porsche](https://newsroom.porsche.com/en/2024/history/porsche-klassik-911-g-model-anniversary-model-1987-35245.html)).

**The 964 and 993 (1989–1998): metallics and bold brights.** The 964 launched with Dark Blue, Murano Green, Guards Red, Grand Prix White, Linen, Apricot Beige and Black ([Christophorus](https://newsroom.porsche.com/en/christophorus/porsche-targa-colors-11179.html)). The early 1990s added Maritime Blue, Rubystone (Ruby Star) on the 964 Carrera RS, and Mint Green, colours Porsche now says have 'cult status' ([Porsche 2025](https://newsroom.porsche.com/en/2025/products/porsche-custom-colours-requested-of-customers-39156.html); [eight generations](https://newsroom.porsche.com/en/2019/history/porsche-klassik-911-eight-generations-dna-18914.html)). The 1993 '30 Years 911' came in Viola, Amethyst or Polar Silver Metallic ([German Wikipedia](https://de.wikipedia.org/wiki/Porsche_964)). The 993 launched with Riviera Blue, 'one of the market launch colours' (PTS), Speed Yellow, Amaranth Violet and a set of pearl metallics. From 1997 Arctic Silver replaced Polar Silver, and Arena Red Metallic bridged the last air-cooled and first water-cooled 911s (PTS).

**The 996 and 997 (1998–2012): the silver-and-grey era.** Arctic Silver was the silver of the first water-cooled decade, 1997–2006 ([German Wikipedia](https://de.wikipedia.org/wiki/Porsche_996)). The range filled with Seal Grey, Atlas Grey, Meteor Grey, Basalt Black and GT Silver, which the PTS library says was first used on a 911 for the 2003 '40 Years of 911' model. Speed Yellow, Guards Red and Cobalt Blue kept some colour. The 997 GT3 RS brought back loud colours with RS Green, developed for it in 2007 (PTS), and an orange, and the 2009 Sport Classic's deep grey sold out within 48 hours ([Klassik](https://newsroom.porsche.com/en/history/porsche-history-911-chameleon-944-928-colourful-tradition-13262.html)).

**The 991 and 992 (2012–today): heritage revivals, chalk and Paint to Sample.** Racing Yellow replaced Speed Yellow with the 991 (PTS). Lava Orange and Ultraviolet launched the 991 GT3 RS ([Klassik](https://newsroom.porsche.com/en/history/porsche-history-911-chameleon-944-928-colourful-tradition-13262.html)), and Miami Blue was first offered in 2017 (PTS). Crayon/Chalk arrived for all 911s in 2017 ([Porsche](https://newsroom.porsche.com/en/products/porsche-new-model-year-connectivity-colours-innovations-13535.html)) and became one of the most popular colours of the early 2020s (PTS). The one-millionth 911 of 2017 was painted Irish Green. The 992 brought Gentian Blue, Aventurine Green, and the 2021 performance shades Python Green and Shark Blue. The 992.2 sorts its range into colour worlds. Legends holds Crayon, Shade Green Metallic and Slate Grey Neo; Dreams holds Gentian Blue, Carmine Red and Guards Red, plus the new Lugano Blue and Cartagena Yellow Metallic ([press kit](https://newsroom.porsche.com/en/press-kits/911/Exterior--design-and-body.html)). Heritage shades such as Ruby Star Neo and Shore Blue sit alongside. Beyond the standard list, Paint to Sample and Paint to Sample Plus can recreate almost any historic colour, which is how Signal Yellow, Riviera Blue, Mint Green and Irish Green return on new cars ([PTS library](https://media.porsche.com/paint-to-sample); [Porsche](https://newsroom.porsche.com/en/2024/products/porsche-panamera-paints-development-process-35031.html); [Porsche 2025](https://newsroom.porsche.com/en/2025/products/porsche-custom-colours-requested-of-customers-39156.html)).

## Colours per stop

★ = `featured`, ◆ = `iconic`. "Hex basis" summarises `hex_source.method`: "consensus of *n*" is the CIELAB mean of *n* independent sources, "(low)" means low confidence. Codes are Porsche paint codes; codes in brackets are later or alternative codes from the sources.

### 00-t7-1959 — Type 754 T7 prototype (1959)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Green Metallic (T7 prototype) | grünmetallic | — | special | 1959–1961 | `#344931` | ★◆ | photo only (low) |
| Signal Red | signalrot | 6011 | solid | 1960–1961 | `#e8160d` | ★ | consensus of 2 |
| Slate Grey | schiefergrau | 6001 | solid | 1960–1961 | `#5b5d5f` | ★ | consensus of 4 |
| Heron Grey | reihergrau | 6007 | solid | 1960–1961 | `#9ca0a3` |  | mean of 2 disagreeing sources (low) |
| Ivory | elfenbein | 6004 | solid | 1959–1961 | `#e7dcb8` | ★ | consensus of 2 |
| Ruby Red | rubinrot | 6002 | solid | 1960 | `#b5271c` | ★ | consensus of 2 |
| Aetna Blue | ätnablau | 6003 | solid | 1961 | `#475d6e` | ★ | single source (low) |
| Royal Blue | königsblau | 6012 | solid | 1960 | `#0c5e98` |  | single source (low) |
| Condor Yellow | kondorgelb | 6010 | solid | 1960 | `#f7ee92` |  | single source (low) |
| Silver Metallic (Aluminium) | silbermetallic | 6006 | metallic | 1959–1961 | `#cdced3` | ★ | consensus of 3 |
| Meissen Blue | meißenblau | 5703 | solid | 1959 | `#9fb9c5` |  | consensus of 2 |
| Fjord Green | fjordgrün | 6005 | solid | 1959 | `#093a3b` | ★ | consensus of 2 |
| Oslo Blue | osloblau | — | solid | 1960–1961 | `#206291` |  | mean of 2 disagreeing sources (low) |

### 01-901-1963 — Porsche 901, IAA 1963

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Yellow (IAA 1963 show car) | gelb | — | special | 1963 | `#eae1c1` | ★◆ | photo only (low) |
| Signal Red | signalrot | 6407 | solid | 1963–1964 | `#e8160d` | ★◆ | consensus of 2 |
| White (prototype 901/01 'Sturmvogel') | weiß | — | special | 1962–1963 | `#dad4da` | ★ | photo only (low) |
| Quick Blue (prototype 'Quickblau') | quickblau | — | special | 1963 | `#3d7394` | ★ | photo only (low) |
| Irish Green | irischgrün | 6406 | solid | 1964 | `#244b2a` | ★◆ | consensus of 4 |
| Slate Grey | schiefergrau | 6401 | solid | 1964 | `#5b5d5f` | ★ | consensus of 4 |
| Ruby Red | rubinrot | 6402 | solid | 1964 | `#b5271c` | ★ | consensus of 2 |
| Sky Blue (Enamel Blue) | emailblau | 6403 | solid | 1964 | `#4297c8` | ★ | single source (low) |
| Light Ivory | hellelfenbein | 6404 | solid | 1964 | `#e8e1ca` | ★ | consensus of 4 |
| Champagne Yellow | champagnegelb | 6405 | solid | 1964 | `#f0e07f` |  | consensus of 2 |
| Dolphin Grey (special) | delfingrau | 6410 | solid | 1964 | `#c5cdc9` |  | consensus of 3 |
| Togo Brown (special) | togobraun | 6411 | solid | 1964 | `#3c1f0c` |  | single source (low) |
| Bali Blue (special) | baliblau | 6412 | solid | 1964 | `#172b55` |  | mean of 2 disagreeing sources (low) |
| Black (special) | schwarz | 6413 | solid | 1964 | `#17181a` |  | Porsche daylight render |

### 02-911-swb-1964 — 911 short wheelbase (1964–1968)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Signal Red | signalrot | 6407 / 016 | solid | 1964–1968 | `#e8160d` | ★◆ | consensus of 2 |
| Ruby Red | rubinrot | 6402 / 015 | solid | 1964–1967 | `#b5271c` |  | consensus of 2 |
| Sky Blue (Enamel Blue) | emailblau | 6403 | solid | 1964–1965 | `#4297c8` |  | single source (low) |
| Light Ivory | hellelfenbein | 6404 / 6604 / 6804 | solid | 1964–1968 | `#e8e1ca` | ★ | consensus of 4 |
| Champagne Yellow | champagnegelb | 6405 / 6822 | solid | 1964–1968 | `#f0e07f` | ★ | consensus of 2 |
| Irish Green | irischgrün | 6406 / 6606 / 6806 | solid | 1964–1968 | `#244b2a` | ★◆ | consensus of 4 |
| Slate Grey | schiefergrau | 6401 / 6601 / 6801 | solid | 1964–1968 | `#5b5d5f` | ★◆ | consensus of 4 |
| Dolphin Grey (special) | delfingrau | 6410 | solid | 1964–1965 | `#c5cdc9` |  | consensus of 3 |
| Togo Brown (special) | togobraun | 6411 | solid | 1964–1965 | `#3c1f0c` |  | single source (low) |
| Bali Blue (special) | baliblau | 6412 | solid | 1964–1965 | `#172b55` | ★ | mean of 2 disagreeing sources (low) |
| Black | schwarz | 6413 / 6609 | solid | 1964–1968 | `#17181a` |  | Porsche daylight render |
| Polo Red | polorot | 6602 / 6802 | solid | 1966–1968 | `#842b33` | ★ | consensus of 2 |
| Bahama Yellow | bahamagelb | 6605 / 6805 | solid | 1966–1968 | `#d18e27` | ★◆ | consensus of 4 |
| Sand Beige | sandbeige | 6607 / 6807 | solid | 1966–1968 | `#c7a66d` |  | consensus of 3 |
| Golf Blue | golfblau | 6603 | solid | 1966–1967 | `#1a4e8d` | ★ | mean of 2 disagreeing sources (low) |
| Aga Blue | agablau | 6608 | solid | 1966–1967 | `#16374e` |  | single source (low) |
| Ossi Blue | ossiblau | 6803 | solid | 1968 | `#2059a9` |  | consensus of 3 |
| Burgundy Red | burgundrot | 6808 | solid | 1968 | `#561f23` |  | mean of 2 disagreeing sources (low) |
| Tangerine | blutorange | 6809 | solid | 1968 | `#db4323` | ★ | consensus of 3 |
| Signal Yellow | signalgelb | 6823 / 114 | solid | 1966–1968 | `#fca613` |  | consensus of 3 |
| Signal Green (special) | signalgrün | 6829 | solid | 1968 | `#3aab4f` |  | consensus of 4 |
| Sepia Brown | sepiabraun | 6836 | solid | 1966–1968 | `#764d27` |  | consensus of 3 |
| Olive | olive | 6835 | solid | 1966–1968 | `#7f8053` |  | consensus of 2 |
| Beige Grey | beigegrau | 622 / 6834 | solid | 1966–1968 | `#aba185` |  | consensus of 4 |
| Canary Yellow | zitronengelb | 6824 | solid | 1966–1968 | `#fef56a` |  | single source (low) |
| Pastel Blue | pastellblau | 6826 | solid | 1966–1968 | `#80b5d8` |  | consensus of 2 |
| Stone Grey (special) | steingrau | 75741 | solid | 1966–1968 | `#a5a075` |  | consensus of 2 |
| Linden Green (special colour) | lindgrün | 6710 / 6767 | special | 1967–1968 | `#b6bf2d` |  | mean of 2 disagreeing sources (low) |
| Silver Metallic | silbermetallic | 6851 | metallic | 1966–1968 | `#cdced3` |  | consensus of 3 |
| Blue Metallic | blaumetallic | 6853 | metallic | 1966–1968 | `#277cbd` |  | single source (low) |
| Dark Green Metallic | dunkelgrünmetallic | 6852 | metallic | 1966–1968 | `#3b603a` |  | mean of 2 disagreeing sources (low) |
| Dark Red Metallic | dunkelrotmetallic | 6854 | metallic | 1966–1968 | `#ac4a3c` |  | consensus of 2 |

### 03-911-lwb-1969 — 911 long wheelbase (1969–1973)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Black | schwarz | 041 | solid | 1969–1973 | `#17181a` |  | Porsche daylight render |
| Light Ivory | hellelfenbein | 6804 / 1111 / 131 | solid | 1969–1973 | `#e8e1ca` | ★ | consensus of 4 |
| Ivory | elfenbein | 132 | solid | 1970–1973 | `#ede8c1` |  | consensus of 3 |
| Grand Prix White | grandprixweiß | 908 | solid | 1971–1973 | `#fafbf9` |  | consensus of 3 |
| Slate Grey | schiefergrau | 6801 | solid | 1969 | `#5b5d5f` | ★◆ | consensus of 4 |
| Polo Red | polorot | 6802 | solid | 1969 | `#842b33` |  | consensus of 2 |
| Irish Green | irischgrün | 6806 / 1515 / 213 | solid | 1969–1973 | `#244b2a` | ★ | consensus of 4 |
| Bahama Yellow | bahamagelb | 6805 | solid | 1969 | `#d18e27` |  | consensus of 4 |
| Sand Beige | sandbeige | 6807 | solid | 1969 | `#c7a66d` |  | consensus of 3 |
| Tangerine (Blood Orange) | blutorange | 6809 / 2323 / 018 | solid | 1969–1973 | `#db4323` | ★◆ | consensus of 3 |
| Signal Yellow | signalgelb | 6823 / 114 | solid | 1969–1973 | `#fca613` | ★ | consensus of 3 |
| Burgundy Red | burgundrot | 6808 / 2424 / 017 | solid | 1969–1971 | `#561f23` |  | mean of 2 disagreeing sources (low) |
| Ossi Blue | ossiblau | 6803 | solid | 1969 | `#2059a9` |  | consensus of 3 |
| Champagne Yellow | champagnegelb | 6822 | solid | 1969 | `#f0e07f` |  | consensus of 2 |
| Olive | olive | 6835 / 414 | solid | 1969–1973 | `#7f8053` |  | consensus of 2 |
| Sepia Brown | sepiabraun | 6836 / 7474 / 415 | solid | 1969–1973 | `#764d27` |  | consensus of 3 |
| Beige Grey | beigegrau | 7575 / 622 | solid | 1969–1973 | `#aba185` |  | consensus of 4 |
| Leaf Green (Bush Green) | buschgrün | 218 | solid | 1969–1973 | `#467146` |  | consensus of 3 |
| Pastel Blue | pastellblau | 6826 / 321 | solid | 1969–1971 | `#80b5d8` |  | consensus of 2 |
| Crystal Blue | kristallblau | 6825 / 320 | solid | 1969–1971 | `#a6e9ef` |  | single source (low) |
| Canary Yellow | zitronengelb | 6824 / 115 | solid | 1969–1971 | `#fef56a` |  | single source (low) |
| Signal Green | signalgrün | 6829 / 217 | solid | 1969–1971 | `#3aab4f` |  | consensus of 4 |
| Grey White | weißgrau | 620 | solid | 1969–1971 | `#eaeaea` |  | single source (low) |
| Albert Blue | albertblau | 1818 / 325 | solid | 1970–1972 | `#132d57` | ★ | consensus of 2 |
| Bahia Red | bahiarot | 1313 / 022 / 013 | solid | 1970–1973 | `#c00415` |  | mean of 2 disagreeing sources (low) |
| Conda Green | condagrün | 2626 / 222 | solid | 1970–1972 | `#1a9d45` |  | consensus of 2 |
| Glacier Blue | gletscherblau | 6666 / 326 | solid | 1970–1973 | `#81c3e0` |  | mean of 2 disagreeing sources (low) |
| Light Yellow | hellgelb | 6262 / 117 | solid | 1970–1973 | `#eefa55` |  | consensus of 2 |
| Signal Orange | signalorange | 1414 / 116 / L20E | solid | 1970–1973 | `#e67715` | ★◆ | consensus of 4 |
| Light Red | hellrot | 7979 / 023 | solid | 1970–1971 | `#ed1a1a` |  | single source (low) |
| Turquoise | türkis | 6464 / 340 | solid | 1970–1971 | `#72c7ce` |  | single source (low) |
| Green Turquoise | türkisgrün | 220 | solid | 1970–1971 | `#56b88e` |  | single source (low) |
| Gulf Orange | golforange | 6161 / 019 | solid | 1972–1973 | `#f16527` | ◆ | consensus of 3 |
| Viper Green | vipergrün | 225 | solid | 1972–1973 | `#187b32` | ★◆ | consensus of 3 |
| Aubergine | aubergine | 025 | solid | 1972–1973 | `#562130` | ★ | consensus of 3 |
| Gulf Blue | golfblau | 328 | solid | 1972–1973 | `#8dbfd6` |  | consensus of 2 |
| Rose Red (Fraise) | fraise | 024 | solid | 1972–1973 | `#c91842` |  | consensus of 3 |
| Sea Blue (Dalmatian Blue) | dalmatinerblau | 329 | solid | 1972–1973 | `#323b77` |  | mean of 2 disagreeing sources (low) |
| Royal Blue | königsblau | 305 | solid | 1969–1972 | `#15408b` |  | consensus of 3 |
| Light Green (Jade Green) | hellgrün | 227 | solid | 1972–1973 | `#3bc096` |  | consensus of 2 |
| Yellow-Green (Lime Green) | gelbgrün | 137 | solid | 1972–1973 | `#68cc24` |  | consensus of 3 |
| Linden Green (special colour) | lindgrün | 6710 / 6767 / 226 | special | 1969–1973 | `#b6bf2d` | ◆ | mean of 2 disagreeing sources (low) |
| Silver Metallic | silbermetallic | 6851 / 8080 / 936 | metallic | 1969–1973 | `#c8cbd0` |  | consensus of 3 |
| Metallic Blue | blaumetallic | 6853 / 3224 / 334 | metallic | 1969–1973 | `#277cbd` |  | single source (low) |
| Metallic Dark Green | dunkelgrünmetallic | 6852 | metallic | 1969 | `#3b603a` |  | mean of 2 disagreeing sources (low) |
| Metallic Dark Red | dunkelrotmetallic | 6854 | metallic | 1969 | `#ac4a3c` |  | consensus of 2 |
| Metallic Green | grünmetallic | 8383 / 221 / 230 | metallic | 1970–1973 | `#5f9159` |  | mean of 2 disagreeing sources (low) |
| Metallic Red | rotmetallic | 8181 / 021 | metallic | 1970–1971 | `#c23d33` |  | mean of 2 disagreeing sources (low) |
| Gemini Blue Metallic | geminiblaumetallic | 8484 / 330 / 335 | metallic | 1971–1973 | `#4c86b9` | ★ | consensus of 3 |
| Gold Metallic | goldmetallic | 8888 / 133 | metallic | 1971–1973 | `#e3b152` |  | mean of 2 disagreeing sources (low) |

### 04-carrera-rs-27-1973 — 911 Carrera RS 2.7 (1972–1973)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Grand Prix White with Carrera script | grandprixweiß | 908 | solid | 1972–1973 | `#fafbf9` | ★◆ | consensus of 3 |
| Light Yellow | hellgelb | 117 | solid | 1972–1973 | `#eefa55` | ★ | consensus of 2 |
| Signal Yellow | signalgelb | 114 | solid | 1972–1973 | `#fca613` |  | consensus of 3 |
| Tangerine (Blood Orange) | blutorange | 018 | solid | 1972–1973 | `#db4323` | ★◆ | consensus of 3 |
| Gulf Orange | golforange | 019 | solid | 1972–1973 | `#f16527` | ★◆ | consensus of 3 |
| Signal Orange | signalorange | L20E / 116 | solid | 1972–1973 | `#e67715` | ◆ | consensus of 4 |
| Bahia Red | bahiarot | 013 / 022 | solid | 1972–1973 | `#c00415` |  | mean of 2 disagreeing sources (low) |
| Rose Red (Fraise) | fraise | 024 | solid | 1973 | `#c91842` | ★ | consensus of 3 |
| Aubergine | aubergine | 025 | solid | 1972–1973 | `#562130` | ★ | consensus of 3 |
| Viper Green | vipergrün | 225 | solid | 1972–1973 | `#187b32` | ★◆ | consensus of 3 |
| Light Green (Jade Green) | hellgrün | 227 | solid | 1972–1973 | `#3bc096` |  | consensus of 2 |
| Irish Green | irischgrün | 213 | solid | 1972–1973 | `#244b2a` |  | consensus of 4 |
| Gulf Blue | golfblau | 328 | solid | 1972–1973 | `#8dbfd6` | ★ | consensus of 2 |
| Sea Blue (Dalmatian Blue) | dalmatinerblau | 329 | solid | 1972–1973 | `#323b77` |  | mean of 2 disagreeing sources (low) |
| Glacier Blue | gletscherblau | 326 | solid | 1972–1973 | `#81c3e0` |  | mean of 2 disagreeing sources (low) |
| Light Ivory | hellelfenbein | 131 | solid | 1972–1973 | `#e8e1ca` |  | consensus of 4 |
| Black | schwarz | 041 | solid | 1972–1973 | `#17181a` |  | Porsche daylight render |
| Sepia Brown | sepiabraun | 415 | solid | 1972–1973 | `#764d27` |  | consensus of 3 |
| Olive | olive | 414 | solid | 1972–1973 | `#7f8053` |  | consensus of 2 |
| Beige Grey | beigegrau | 622 | solid | 1972–1973 | `#aba185` |  | consensus of 4 |
| Silver Metallic | silbermetallic | 936 | metallic | 1972–1973 | `#c8cbd0` | ★ | consensus of 3 |
| Gemini Blue Metallic | geminiblaumetallic | 335 | metallic | 1972–1973 | `#4c86b9` |  | consensus of 3 |
| Gold Metallic | goldmetallic | 133 | metallic | 1972–1973 | `#e3b152` |  | mean of 2 disagreeing sources (low) |
| Metallic Blue | blaumetallic | 334 | metallic | 1972–1973 | `#277cbd` |  | single source (low) |

### 05-g-series-1974 — G-series 911 (1974–1977)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Grand Prix White | grandprixweiß | 908 | solid | 1974–1977 | `#fafbf9` | ★ | consensus of 3 |
| Guards Red | indischrot | 027 | solid | 1974–1977 | `#b2211f` | ★ | Porsche daylight render |
| Black | schwarz | 041 | solid | 1974–1977 | `#17181a` | ★ | Porsche daylight render |
| Light Yellow | hellgelb | 117 | solid | 1974–1977 | `#eefa55` | ★ | consensus of 2 |
| Yellow-Green (Lime Green) | gelbgrün | 137 | solid | 1974–1976 | `#68cc24` | ★◆ | consensus of 3 |
| Mexico Blue | mexikoblau | 336 | solid | 1974–1977 | `#2380af` | ★◆ | consensus of 3 |
| Peru Red | perurot | 042 | solid | 1974–1977 | `#822623` | ★ | consensus of 3 |
| Cockney Brown (Bitter Chocolate) | cockneybraun | 408 | solid | 1974–1977 | `#5b422e` |  | consensus of 2 |
| Sahara Beige | saharabeige | 516 | solid | 1974–1977 | `#ffda84` |  | mean of 2 disagreeing sources (low) |
| Orange | orange | 156 | solid | 1974–1975 | `#ee6330` |  | consensus of 2 |
| Signal Orange | signalorange | 116 | solid | 1974–1975 | `#e67715` |  | consensus of 4 |
| Continental Orange | continental orange | 107 | solid | 1975–1977 | `#e74d07` | ★ | consensus of 3 |
| Talbot Yellow | talbotgelb | 106 | solid | 1976–1977 | `#f8c533` |  | consensus of 3 |
| Arrow Blue | pfeilblau | 305 | solid | 1976–1977 | `#15408b` |  | consensus of 3 |
| Irish Green | irischgrün | 213 | solid | 1974–1977 | `#244b2a` |  | consensus of 4 |
| Rose Red (Fraise) | fraise | 024 | solid | 1974–1975 | `#c91842` |  | consensus of 3 |
| Aubergine | aubergine | 025 | solid | 1974–1975 | `#562130` |  | consensus of 3 |
| Olive | olive | 414 | solid | 1974–1975 | `#7f8053` |  | consensus of 2 |
| Gulf Blue | golfblau | 328 | solid | 1974–1975 | `#8dbfd6` |  | consensus of 2 |
| Lilac | flieder | 341 / 601 | solid | 1975–1977 | `#dcc9df` |  | consensus of 3 |
| Apple Green | daphnegrün | 260 | solid | 1976–1977 | `#91e22c` |  | consensus of 2 |
| Speedway Green | speedwaygrün | 258 | solid | 1976–1977 | `#309c2e` |  | mean of 2 disagreeing sources (low) |
| Coppa Florio Blue | coppaflorioblau | 360 | solid | 1976–1977 | `#baeefb` |  | consensus of 2 |
| Silver Metallic | silbermetallic | 936 | metallic | 1974–1977 | `#c8cbd0` | ★ | consensus of 3 |
| Copper Brown Metallic | kupferbraunmetallic | 443 / 432 | metallic | 1974–1977 | `#63391b` | ★ | consensus of 2 |
| Emerald Green Metallic | smaragdgrünmetallic | 264 | metallic | 1974–1977 | `#548b50` |  | consensus of 3 |
| Ice Green Metallic | silbergrünmetallic | 266 | metallic | 1974–1977 | `#c4dcd8` |  | consensus of 3 |
| Gemini Blue Metallic | geminiblaumetallic | 335 | metallic | 1974 | `#4c86b9` |  | consensus of 3 |
| Metallic Blue | blaumetallic | 334 | metallic | 1974–1975 | `#277cbd` |  | single source (low) |
| Salmon Metallic | lachsmetallic | 036 | metallic | 1974–1976 | `#d2641a` |  | consensus of 2 |
| Minerva Blue Metallic | minervablaumetallic | 304 | metallic | 1976–1977 | `#2d76a8` |  | consensus of 3 |
| Oak Green Metallic | eichengrünmetallic | 265 | metallic | 1976–1977 | `#3b4c3d` |  | consensus of 4 |
| Platinum Metallic | platinmetallic | 944 | metallic | 1976–1977 | `#b2b1a7` |  | consensus of 3 |
| Sienna Metallic | siennametallic | 436 | metallic | 1976–1977 | `#b42919` |  | consensus of 2 |

### 06-930-turbo-1975 — 911 Turbo, type 930 (1975–1989)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Black | schwarz | 041 | solid | 1975–1989 | `#17181a` | ★ | Porsche daylight render |
| Grand Prix White | grandprixweiß | 908 | solid | 1975–1989 | `#fafbf9` | ★ | consensus of 3 |
| Guards Red | indischrot | 027 | solid | 1979–1989 | `#b2211f` | ★ | Porsche daylight render |
| Arrow Blue | pfeilblau | 305 | solid | 1975–1980 | `#15408b` |  | consensus of 3 |
| Talbot Yellow | talbotgelb | 106 | solid | 1975–1981 | `#f8c533` | ★ | consensus of 3 |
| Mocha Black | moccaschwarz | 451 | solid | 1979–1982 | `#221915` |  | consensus of 4 |
| Cashmere Beige | kaschmirbeige | 502 | solid | 1977–1980 | `#b2703a` |  | consensus of 2 |
| Cockney Brown | cockneybraun | 408 | solid | 1975–1980 | `#5b422e` |  | consensus of 2 |
| Lilac | flieder | 601 | solid | 1975–1980 | `#dcc9df` |  | consensus of 3 |
| Olive Green | olivgrün | 274 | solid | 1977–1980 | `#486638` |  | consensus of 3 |
| Silver Metallic | silbermetallic | 936 | metallic | 1975–1980 | `#c8cbd0` | ★ | consensus of 3 |
| Minerva Blue Metallic | minervablaumetallic | 304 | metallic | 1976–1980 | `#2d76a8` | ★ | consensus of 3 |
| Petrol Blue Metallic | petrolblaumetallic | 376 | metallic | 1977–1980 | `#22636b` | ★ | consensus of 3 |
| Light Green Metallic | lindgrünmetallic | 275 | metallic | 1977–1980 | `#aeb67b` |  | consensus of 3 |
| Copper Brown Metallic | braunkupfer metallic | 443 | metallic | 1976–1980 | `#63391b` | ★ | consensus of 2 |
| Black Metallic | schwarzmetallic | 708 | metallic | 1979–1981 | `#0e0f15` |  | consensus of 2 |
| Light Blue Metallic | hellblaumetallic | 30T | metallic | 1979–1982 | `#83a5b4` |  | consensus of 3 |
| Tobacco Metallic | tabakmetallic | 464 | metallic | 1978–1980 | `#7f683f` |  | consensus of 2 |
| Oak Green Metallic | eichengrünmetallic | 265 / 22L | metallic | 1977–1989 | `#3b4c3d` | ★◆ | consensus of 4 |
| Opal Metallic (Casablanca Beige) | opalmetallic | 463 | metallic | 1978–1980 | `#b39062` |  | consensus of 3 |
| Emerald Green Metallic | smaragdgrünmetallic | 264 | metallic | 1975–1977 | `#548b50` | ★ | consensus of 3 |
| Ice Green Metallic | silbergrünmetallic | 266 | metallic | 1975–1977 | `#c4dcd8` |  | consensus of 3 |
| Wine Red Metallic | weinrotmetallic | 895 | metallic | 1981–1982 | `#97262c` |  | mean of disagreeing sources (low) |
| Venetian Blue Metallic | venezianischblaumetallic | 35U / 36P | metallic | 1987–1988 | `#3b5975` |  | consensus of 3 |
| Dark Blue | dunkelblau | 347 | solid | 1987–1989 | `#172344` |  | consensus of 3 |

### 07-911-sc-1978 — 911 SC (1978–1983)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Black | schwarz | 041 / 700 | solid | 1978–1983 | `#17181a` | ★ | Porsche daylight render |
| Grand Prix White | grandprixweiß | 908 | solid | 1978–1983 | `#fafbf9` | ★ | consensus of 3 |
| Guards Red | indischrot | 027 | solid | 1978–1983 | `#b2211f` | ★ | Porsche daylight render |
| Arrow Blue | pfeilblau | 305 | solid | 1978–1982 | `#15408b` |  | consensus of 3 |
| Talbot Yellow | talbotgelb | 106 | solid | 1978–1981 | `#f8c533` | ★ | consensus of 3 |
| Mocha Black | moccaschwarz | 451 / LM9V | solid | 1979–1982 | `#221915` |  | consensus of 4 |
| Cashmere Beige | kaschmirbeige | 502 | solid | 1978–1980 | `#b2703a` |  | consensus of 2 |
| Cockney Brown | cockneybraun | 408 | solid | 1978–1980 | `#5b422e` |  | consensus of 2 |
| Lilac (Moonstone) | flieder | 601 / LM7A | solid | 1978–1980 | `#dcc9df` |  | consensus of 3 |
| Olive Green | olivgrün | 274 | solid | 1978–1980 | `#486638` |  | consensus of 3 |
| Continental Orange | continental orange | 107 | solid | 1978 | `#e74d07` |  | consensus of 3 |
| Fern Green | farngrün | 273 | solid | 1978–1980 | `#27885d` |  | mean of 2 disagreeing sources (low) |
| Chiffon White | chiffonweiß | 182 | solid | 1981–1983 | `#faf9e3` |  | consensus of 3 |
| Bamboo Beige | bambusbeige | 523 | solid | 1981–1983 | `#ecce8a` |  | consensus of 3 |
| Glacier Blue | gletscherblau | 32Z | solid | 1983 | `#cde3e3` |  | consensus of 2 |
| Silver Metallic | silbermetallic | 936 | metallic | 1978–1980 | `#c8cbd0` |  | consensus of 3 |
| Minerva Blue Metallic | minervablaumetallic | 304 / LM5Y | metallic | 1978–1982 | `#2d76a8` | ★ | consensus of 3 |
| Petrol Blue Metallic | petrolblaumetallic | 376 / LM5V | metallic | 1978–1980 | `#22636b` | ★ | consensus of 3 |
| Light Green Metallic | lindgrünmetallic | 275 | metallic | 1978–1980 | `#aeb67b` |  | consensus of 3 |
| Copper Brown Metallic | braunkupfer metallic | 443 | metallic | 1978–1980 | `#63391b` | ★ | consensus of 2 |
| Oak Green Metallic | eichengrünmetallic | 265 | metallic | 1978–1980 | `#3b4c3d` | ★ | consensus of 4 |
| Tobacco Metallic | tabakmetallic | 464 | metallic | 1979–1980 | `#7f683f` |  | consensus of 2 |
| Opal Metallic (Casablanca Beige) | opalmetallic | 463 | metallic | 1979–1980 | `#b39062` |  | consensus of 3 |
| Black Metallic | schwarzmetallic | LM9Y / 708 | metallic | 1979–1982 | `#0e0f15` |  | consensus of 2 |
| Light Blue Metallic | hellblaumetallic | 30T | metallic | 1979–1982 | `#83a5b4` |  | consensus of 3 |
| Jet Black Metallic | tiefschwarzmetallic | 2T | metallic | 1980 | `#27292c` |  | Porsche daylight render |
| Platinum Metallic | platinmetallic | 655 / LM8U | metallic | 1981–1983 | `#8b8873` | ★ | consensus of 3 |
| Moss Green Metallic | moosgrünmetallic | 20C | metallic | 1981–1983 | `#234926` |  | consensus of 3 |
| Pacific Blue Metallic | pazifikblaumetallic | 31G | metallic | 1981–1982 | `#315570` |  | consensus of 3 |
| Rosewood Metallic | palisandermetallic | 474 | metallic | 1981–1982 | `#583f32` |  | consensus of 3 |
| Wine Red Metallic | weinrotmetallic | 895 | metallic | 1981–1982 | `#97262c` |  | mean of disagreeing sources (low) |
| Pewter Metallic | zinnmetallic | 956 | metallic | 1981–1983 | `#b6bec2` |  | consensus of 3 |
| Meteor Grey Metallic | meteorgraumetallic | LY7Z | metallic | 1982 | `#56575f` |  | consensus of 3 |
| Light Bronze Metallic | hellbronzemetallic | LM1V | metallic | 1983 | `#d1ccac` |  | consensus of 2 |
| Kiln Red Metallic | zieglerotmetallic | 811 | metallic | 1983 | `#c22d39` |  | consensus of 2 |
| Quartz Grey Metallic | quarzgraumetallic | 662 | metallic | 1983 | `#6b5950` |  | consensus of 4 |
| Ruby Red Metallic | rubinrotmetallic | 810 | metallic | 1983 | `#a3241c` |  | consensus of 2 |
| Slate Blue Metallic | schieferblaumetallic | 661 | metallic | 1983 | `#8ba1af` |  | consensus of 2 |

### 08-carrera-32-1984 — 911 Carrera 3.2 (1984–1989)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Black | schwarz | 041 / 700 (A1) | solid | 1984–1989 | `#17181a` | ★ | Porsche daylight render |
| Grand Prix White | grandprixweiß | 908 (P5) | solid | 1984–1989 | `#fafbf9` | ★ | consensus of 3 |
| Guards Red | indischrot | 027 / LM3A (G1) | solid | 1984–1989 | `#b2211f` | ★◆ | Porsche daylight render |
| Chiffon White | chiffonweiß | 182 (P2) | solid | 1984–1985 | `#faf9e3` |  | consensus of 3 |
| Glacier Blue | gletscherblau | 32Z (K4) | solid | 1984 | `#cde3e3` |  | consensus of 2 |
| Dark Blue | dunkelblau | 347 (K5) | solid | 1984–1989 | `#172344` |  | consensus of 3 |
| Marble Grey | marmorgrau | 673 (A8) | solid | 1985–1986 | `#d1d2cb` |  | consensus of 2 |
| Pastel Beige | pastellbeige | 536 / LM1N (D4) | solid | 1985–1986 | `#f4eac2` |  | mean of 2 disagreeing sources (low) |
| Carmine Red | karminrot | 80F (G4) | solid | 1987–1988 | `#95100d` |  | consensus of 3 |
| Summer Yellow | sommergelb | 10W / LM1A (B1) | solid | 1987–1988 | `#ead547` | ★ | consensus of 3 |
| Caramel Beige | keramikbeige | 499 (D9) | solid | 1988 | `#d4a270` |  | consensus of 2 |
| Silver Metallic | silbermetallic | 936 (S7) | metallic | 1984–1989 | `#c8cbd0` | ★ | consensus of 3 |
| Platinum Metallic | platinmetallic | 655 / LM8U (U1) | metallic | 1984 | `#8b8873` |  | consensus of 3 |
| Pewter Metallic | zinnmetallic | 956 (Z8) | metallic | 1984 | `#b6bec2` |  | consensus of 3 |
| Light Bronze Metallic | hellbronzemetallic | LM1V / 966 | metallic | 1984 | `#d1ccac` |  | consensus of 2 |
| Kiln Red Metallic | zieglerotmetallic | 811 (X3) | metallic | 1984 | `#c22d39` |  | consensus of 2 |
| Ruby Red Metallic | rubinrotmetallic | 810 (X7) | metallic | 1984 | `#a3241c` |  | consensus of 2 |
| Slate Blue Metallic | schieferblaumetallic | 661 (X6) | metallic | 1984 | `#8ba1af` |  | consensus of 2 |
| Quartz Grey Metallic | quarzgraumetallic | 662 (X5) | metallic | 1984 | `#6b5950` |  | consensus of 4 |
| Moss Green Metallic | moosgrünmetallic | 20C / LM6V (X2) | metallic | 1984–1986 | `#234926` |  | consensus of 3 |
| Meteor Grey Metallic | meteorgraumetallic | 961 (Y5) | metallic | 1985–1986 | `#656869` |  | mean of 2 disagreeing sources (low) |
| Garnet Red Metallic | granatrotmetallic | 822 / LM3Y (S2) | metallic | 1985–1986 | `#922432` |  | consensus of 3 |
| Iris Blue Metallic | irisblaumetallic | 33P (S3) | metallic | 1985–1986 | `#96b9c2` |  | consensus of 2 |
| Nutmeg Brown Metallic | muskatbraunmetallic | 492 (S1) | metallic | 1985–1986 | `#624029` |  | consensus of 2 |
| Prussian Blue Metallic | preußischblaumetallic | 33X (S4) | metallic | 1985–1986 | `#25456b` |  | consensus of 2 |
| White Gold Metallic | weißgoldmetallic | 539 (S6) | metallic | 1985–1986 | `#d1cbb4` |  | consensus of 2 |
| Crystal Green Metallic | kristallgrünmetallic | 33N / LM6Y (S5) | metallic | 1985–1986 | `#acc2b0` |  | consensus of 2 |
| Cassis Red Metallic | cassisrotmetallic | 80D (F9) | metallic | 1987–1988 | `#a88d98` | ★ | consensus of 3 |
| Diamond Blue Metallic | diamantblaumetallic | 697 / LM5U (F5) | metallic | 1987–1989 | `#d9d9e9` | ★ | consensus of 2 |
| Espresso Brown Metallic | espressobraunmetallic | 40D (F6) | metallic | 1987–1988 | `#3c3029` |  | consensus of 3 |
| Granite Green Metallic | felsengrünmetallic | 699 (F3) | metallic | 1987–1988 | `#858f84` | ★ | consensus of 4 |
| Lagoon Green Metallic | lagunengrünmetallic | 35Y (F2) | metallic | 1987–1988 | `#a8c5b4` |  | consensus of 2 |
| Marine Blue Metallic | marineblaumetallic | 35V (F7) | metallic | 1987–1988 | `#657581` |  | consensus of 3 |
| Nougat Brown Metallic | nougatbraunmetallic | 40B / LM8V (F4) | metallic | 1987–1988 | `#cb9f74` | ★ | consensus of 2 |
| Venetian Blue Metallic | venezianischblaumetallic | 35U / 36P (F8) | metallic | 1987–1988 | `#3b5975` | ★ | consensus of 3 |
| Ocean Blue Metallic | ozeanblau | LY5Z (Q2) | metallic | 1987–1988 | `#3b536a` |  | consensus of 3 |
| Stone Grey Metallic | steingraumetallic | 693 / LY7U (U8) | metallic | 1989 | `#919494` |  | consensus of 4 |
| Slate Grey Metallic | schiefergraumetallic | 22D (Q9) | metallic | 1989 | `#626264` |  | consensus of 3 |
| Velvet Red Metallic | samtrotmetallic | 81L (U6) | metallic | 1989 | `#af243a` |  | consensus of 3 |
| Baltic Blue Metallic | baltischblaumetallic | 37B (C7) | metallic | 1989 | `#425877` |  | consensus of 3 |
| Forest Green Metallic | tannengrünmetallic | 22E (W7) | metallic | 1989 | `#19402d` |  | consensus of 4 |
| Linen Grey Metallic | leinengraumetallic | 550 (W5) | metallic | 1989 | `#c8c0af` |  | consensus of 3 |
| Coral Metallic | korallemetallic | 81K (Z9) | metallic | 1989 | `#d38c69` |  | consensus of 3 |
| Cognac Brown Metallic | cognacbraunmetallic | 40L (Z7) | metallic | 1989 | `#80573c` |  | consensus of 3 |

### 09-964-1989 — 964 (1989–1994)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Black | schwarz | 041 / 700 (A1) | solid | 1989–1994 | `#17181a` | ★ | Porsche daylight render |
| Grand Prix White | grandprixweiß | 908 (P5) | solid | 1989–1994 | `#fafbf9` | ★ | consensus of 3 |
| Guards Red | indischrot | 027 / 80K / LM3A (G1) | solid | 1989–1994 | `#b2211f` | ★◆ | Porsche daylight render |
| Dark Blue | dunkelblau | 347 (K5) | solid | 1989–1990 | `#172344` |  | consensus of 3 |
| Murano Green | muranogrün | 22C (N6) | solid | 1989–1990 | `#2e6c6f` |  | consensus of 3 |
| Linen Grey | leinengrau | 60M (E2) | solid | 1989–1990 | `#d4cdb9` |  | consensus of 3 |
| Apricot Beige | apricotbeige | 548 (E4) | solid | 1989–1990 | `#fadbaa` |  | consensus of 3 |
| Mint Green | mintgrün | 22R (N4) | solid | 1991–1993 | `#76e1b9` | ★ | consensus of 4 |
| Signal Green | signalgrün | 22S (M1) | solid | 1991–1993 | `#3aab4f` |  | consensus of 4 |
| Maritime Blue | maritimblau | 38B / LM5A (F2) | solid | 1991–1993 | `#304ca3` | ★◆ | consensus of 4 |
| Rubystone Red (Ruby Star) | sternrubin | 82N / LM3B (G4) | solid | 1991–1993 | `#8b2246` | ★◆ | consensus of 4 |
| Speed Yellow | speedgelb | 12G / 12H (X4) | solid | 1994 | `#e4b12a` |  | consensus of 5 |
| Riviera Blue | rivierablau | 39E (S8) | solid | 1994 | `#348ebd` |  | consensus of 3 |
| Amaranth Violet | amarantviolett | 39D (T3) | solid | 1994 | `#4c3866` |  | consensus of 3 |
| Silver Metallic | silbermetallic | 980 (S7) | metallic | 1989–1990 | `#cfd7e0` |  | consensus of 3 |
| Slate Grey Metallic | schiefergraumetallic | 22D / 23F (Q9) | metallic | 1989–1994 | `#626264` |  | consensus of 3 |
| Stone Grey Metallic | steingraumetallic | 693 / LY7U (U8) | metallic | 1989–1990 | `#919494` |  | consensus of 4 |
| Forest Green Metallic | tannengrünmetallic | 22E (W7) | metallic | 1989–1990 | `#19402d` |  | consensus of 4 |
| Velvet Red Metallic | samtrotmetallic | 81L / LN3U (U6) | metallic | 1989–1990 | `#af243a` |  | consensus of 3 |
| Cognac Brown Metallic | cognacbraunmetallic | 40L (Z7) | metallic | 1989–1990 | `#80573c` |  | consensus of 3 |
| Linen Grey Metallic | leinengraumetallic | 550 / LM1U (W5) | metallic | 1989–1990 | `#c8c0af` |  | consensus of 3 |
| Coral Metallic | korallemetallic | 81K (Z9) | metallic | 1989–1990 | `#d38c69` |  | consensus of 3 |
| Baltic Blue Metallic | baltischblaumetallic | 37B / LM5P (C7) | metallic | 1989–1990 | `#425877` |  | consensus of 3 |
| Diamond Blue Metallic | diamantblaumetallic | 697 / LM5U (F5) | metallic | 1989–1990 | `#d9d9e9` |  | consensus of 2 |
| Black Metallic (Black Pearl) | schwarzmetallic | 738 (Z8) | metallic | 1991–1994 | `#0e0f15` |  | consensus of 2 |
| Polar Silver Metallic | polarsilbermetallic | 92E (A8) | metallic | 1991–1994 | `#bfcbd1` | ★ | consensus of 4 |
| Midnight Blue Metallic | mitternachtsblaumetallic | 37W (F8) | metallic | 1991–1994 | `#131d2d` | ★ | consensus of 4 |
| Cobalt Blue Metallic | kobaltblaumetallic | 37U / LM5N (F6) | metallic | 1991–1993 | `#335497` |  | consensus of 5 |
| Horizon Blue Metallic | horizontblaumetallic | 37X (F4) | metallic | 1991–1993 | `#7b95bd` |  | consensus of 3 |
| Amethyst Metallic | amethystmetallic | 38A (F9) | metallic | 1991–1993 | `#492335` | ★ | consensus of 4 |
| Coral Red Metallic | korallenrotmetallic | 82H (G7) | metallic | 1991–1992 | `#d73832` |  | consensus of 3 |
| Amazon Green Metallic | amazonasgrünmetallic | 37Z / 39A (N7) | metallic | 1991–1994 | `#18333f` |  | consensus of 3 |
| Oak Green Metallic | eichengrünmetallic | 22L (N9) | metallic | 1991–1993 | `#3b4c3d` |  | consensus of 4 |
| Viola Metallic | violametallic | 3AE / 39G | metallic | 1993–1994 | `#37213f` |  | consensus of 3 |
| Violet Blue Metallic | violettblaumetallic | 37E / 3AF | metallic | 1993 | `#735ea5` |  | consensus of 2 |
| Raspberry Red Metallic | himbeerrotmetallic | 83E / 82E (A7) | metallic | 1993–1994 | `#af3853` |  | consensus of 2 |
| Iris Blue Metallic | irisblaumetallic | 39N / 39V | metallic | 1994 | `#242a56` |  | consensus of 3 |
| Aventurine Green Metallic | aventuragrünmetallic | 39R / 39S (K6) | metallic | 1994 | `#2f443e` |  | consensus of 3 |

### 10-993-1994 — 993 (1994–1998)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Black | schwarz | 041 / 741 / 747 (A1) | solid | 1994–1998 | `#17181a` |  | Porsche daylight render |
| Grand Prix White | grandprixweiß | 908 (P5) | solid | 1994–1996 | `#fafbf9` | ★ | consensus of 3 |
| Guards Red | indischrot | 80K / LM3A / 027 (G1) | solid | 1994–1998 | `#b2211f` | ★◆ | Porsche daylight render |
| Speed Yellow | speedgelb | 12G / 12H (X4) | solid | 1994–1998 | `#e4b12a` | ★◆ | consensus of 5 |
| Riviera Blue | rivierablau | 39E / 3AG (S8) | solid | 1994–1995 | `#348ebd` | ★◆ | consensus of 3 |
| Amaranth Violet | amarantviolett | 39D / 3AH (T3) | solid | 1994–1995 | `#4c3866` | ★ | consensus of 3 |
| Blue Turquoise | blautürkis | 3AR / 3AS (J1) | solid | 1996–1998 | `#165376` |  | consensus of 2 |
| Glacier White | gletscherweiß | 3AT / 3AU (Z1) | solid | 1997–1998 | `#f2f5f5` |  | consensus of 2 |
| Pastel Yellow | pastellgelb | 12L / 12M (Q1) | solid | 1997–1998 | `#fff984` |  | mean of 2 disagreeing sources (low) |
| Dark Blue | dunkelblau | 347 / 3C7 (55) | solid | 1997 | `#172344` |  | consensus of 3 |
| Black Metallic (Black Pearl) | schwarzmetallic | 744 / 746 (Z8) | metallic | 1994–1998 | `#0e0f15` |  | consensus of 2 |
| Polar Silver Metallic | polarsilbermetallic | 92E / 92M (A8) | metallic | 1994–1996 | `#bfcbd1` | ★ | consensus of 4 |
| Midnight Blue Metallic | mitternachtsblaumetallic | 37W / 39C (F8) | metallic | 1994–1996 | `#131d2d` | ★ | consensus of 4 |
| Iris Blue Metallic | irisblaumetallic | 39N / 39V (D3) | metallic | 1994–1996 | `#242a56` |  | consensus of 3 |
| Aventurine Green Metallic | aventuragrünmetallic | 39R / 39S (K6) | metallic | 1994–1996 | `#2f443e` | ★ | consensus of 3 |
| Slate Grey Metallic | schiefergraumetallic | 22D / 23F (Q9) | metallic | 1994–1998 | `#626264` |  | consensus of 3 |
| Viola Metallic | violametallic | 3AE / 39G | metallic | c. 1994–1998 | `#37213f` |  | consensus of 3 |
| Turquoise Metallic | türkisgrünmetallic | 25C / 25D (K1) | metallic | 1996 | `#2d7373` |  | mean of 2 disagreeing sources (low) |
| Ocean Jade Metallic |  | 25H / 25K (J3) | metallic | 1997–1998 | `#539389` |  | single source (low) |
| Arctic Silver Metallic | arktissilbermetallic | 92T / 92U (X1) | metallic | 1997–1998 | `#c2bfc3` | ★◆ | consensus of 4 |
| Arena Red Metallic | arenarotmetallic | 84R / 84S (H8) | metallic | 1997–1998 | `#6b1f28` | ★◆ | consensus of 5 |
| Ocean Blue Metallic | ozeanblaumetallic | 3AY / 3AZ (E1) | metallic | 1997–1998 | `#1c3244` |  | consensus of 3 |
| Zenith Blue Metallic | zenithblaumetallic | 3AW / 3AX (F1) | metallic | 1997–1998 | `#3b3f7b` |  | consensus of 3 |
| Vesuvio Metallic | vesuviometallic | 40W / 40X (K3) | metallic | 1997–1998 | `#4c3b4a` |  | consensus of 3 |
| Forest Green Metallic | tannengrünmetallic | 22E (W7 / 53) | metallic | 1997–1998 | `#19402d` |  | consensus of 4 |
| Mexico Blue (special order) | mexikoblau | 336 | special | 1995–1998 | `#2380af` | ◆ | consensus of 3 |

### 11-996-1-1998 — 996.1 (1998–2001)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Black | schwarz | 041 / 741 | solid | 1998–2001 | `#17181a` |  | Porsche daylight render |
| Guards Red | indischrot | 80K / 84A | solid | 1998–2001 | `#b2211f` | ★ | Porsche daylight render |
| Glacier White | firnweiß | 3AU | solid | 1998–1999 | `#f2f5f5` | ★ | consensus of 2 |
| Pastel Yellow | pastellgelb | 12M | solid | 1998–1999 | `#fff984` |  | mean of 2 disagreeing sources (low) |
| Biarritz White | biarritzweiß | 9A2 / 9A3 | solid | 2000–2001 | `#e9e6db` |  | consensus of 3 |
| Speed Yellow | speedgelb | 12G / 12H | solid | 1998–2001 | `#e4b12a` | ★◆ | consensus of 5 |
| Black Metallic | schwarzmetallic | 744 / 746 | metallic | 1998–2001 | `#0e0f15` |  | consensus of 2 |
| Arctic Silver Metallic | arktissilbermetallic | 92T / 92U | metallic | 1998–2001 | `#c2bfc3` | ★◆ | consensus of 4 |
| Polar Silver Metallic | polarsilbermetallic | 92E / 92M | metallic | 1998–2001 | `#bfcbd1` |  | consensus of 4 |
| Ocean Blue Metallic | ozeanblaumetallic | 3AZ / 3AY | metallic | 1998–2000 | `#1c3244` | ★ | consensus of 3 |
| Zenith Blue Metallic | zenithblaumetallic | 3AX / 3AW | metallic | 1998–2000 | `#3b3f7b` | ★ | consensus of 3 |
| Arena Red Metallic | arenarotmetallic | 84S / 84R | metallic | 1998–2000 | `#6b1f28` | ★ | consensus of 5 |
| Vesuvio Metallic | vesuviometallic | 40X / 40W | metallic | 1998–2000 | `#4c3b4a` |  | consensus of 3 |
| Forest Green Metallic | tannengrünmetallic | 22E / 2B4 | metallic | 1998–2001 | `#19402d` |  | consensus of 4 |
| Midnight Blue Metallic | nachtblaumetallic | 37W / 39C | metallic | 1998–2001 | `#131d2d` |  | consensus of 4 |
| Paladio Metallic | paladiometallic | 554 / 555 | metallic | 1998–2000 | `#b0aa8e` |  | single source (low) |
| Iris Blue Metallic | irisblau perlcolor | 39N / 39V | metallic | 1998–2000 | `#242a56` |  | consensus of 3 |
| Cobalt Blue Metallic | kobaltblaumetallic | 37U / 3C8 | metallic | 2000–2001 | `#335497` |  | consensus of 5 |
| Dark Blue | dunkelblau | 347 / 3C7 | solid | 2000–2001 | `#172344` |  | consensus of 3 |
| Wimbledon Green Metallic | wimbledongrünmetallic | 23I / 3B6 | metallic | 2000–2001 | `#49807e` |  | consensus of 3 |
| Viola Metallic | violametallic | 3AE / 39G | metallic | 2000–2001 | `#37213f` |  | consensus of 3 |
| Rainforest (Jungle) Green Metallic | dschungelgrünmetallic | 2A1 / 2A2 | metallic | 2000–2001 | `#164838` |  | consensus of 3 |
| Orient Red Metallic | orientrotmetallic | 8A3 / 8A4 | metallic | 2000–2001 | `#ba2d2c` |  | consensus of 3 |
| Zanzibar (Orange) Red Metallic | orangerot perlcolor | 1A8 / 1A9 | metallic | 2000–2001 | `#c43c23` |  | consensus of 3 |
| Lapis Blue Metallic | lapisblaumetallic | 3A8 / 3A9 | metallic | 2001 | `#152359` |  | consensus of 3 |
| Seal Grey Metallic | sealgraumetallic | 6B4 / 6B5 | metallic | 2001 | `#717472` |  | consensus of 4 |
| Meridian Metallic | meridianmetallic | 6A6 / 6A7 | metallic | 2001 | `#abaaa7` |  | consensus of 3 |
| Violet Chromaflair | violettchromaflair | 3C5 / 3C4 | special | 2000 (Millennium Edition only) | `#120313` |  | single source (low) |

### 12-996-2-2002 — 996.2 (2002–2004)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Black | schwarz | 041 / 741 | solid | 2002–2004 | `#17181a` |  | Porsche daylight render |
| Guards Red | indischrot | 80K / 84A | solid | 2002–2004 | `#b2211f` | ★◆ | Porsche daylight render |
| Carrara White | carraraweiß | B9A | solid | 2002–2004 | `#f0f0ed` | ★ | consensus of 3 |
| Speed Yellow | speedgelb | 12G / 12H | solid | 2002–2004 | `#e4b12a` | ★◆ | consensus of 5 |
| Basalt Black Metallic | basaltschwarzmetallic | C9Z | metallic | 2002–2004 | `#131520` | ★ | consensus of 2 |
| Arctic Silver Metallic | arktissilbermetallic | 92T / 92U | metallic | 2002–2004 | `#c2bfc3` | ★ | consensus of 4 |
| Polar Silver Metallic | polarsilbermetallic | 92M | metallic | 2002–2004 | `#bfcbd1` |  | consensus of 4 |
| Seal Grey Metallic | sealgraumetallic | 6B4 / 6B5 | metallic | 2002–2004 | `#717472` | ★ | consensus of 4 |
| Slate Grey Metallic | schiefergraumetallic | 22D / 23F | metallic | 2002–2004 | `#626264` |  | consensus of 3 |
| Atlas Grey Metallic | atlasgraumetallic | M7X | metallic | 2004 | `#484940` |  | consensus of 3 |
| Lapis Blue Metallic | lapisblaumetallic | 3A8 / M5W | metallic | 2002–2004 | `#152359` | ★ | consensus of 3 |
| Midnight (Night) Blue Metallic | nachtblaumetallic | 39C | metallic | 2002–2004 | `#131d2d` |  | consensus of 4 |
| Cobalt Blue Metallic | kobaltblaumetallic | 3C8 | metallic | 2002–2004 | `#335497` | ★ | consensus of 5 |
| Meridian Metallic | meridianmetallic | 6A6 / 6A7 | metallic | 2002–2004 | `#abaaa7` |  | consensus of 3 |
| Forest Green Metallic | tannengrünmetallic | 2B4 | metallic | 2002–2004 | `#19402d` |  | consensus of 4 |
| Lago Green (Dark Teal) Metallic | lagogrünmetallic | M6W | metallic | 2003–2004 | `#2a4444` |  | consensus of 3 |
| Orient Red Metallic | orientrotmetallic | 8A3 / 8A4 | metallic | 2002 | `#ba2d2c` |  | consensus of 3 |
| Zanzibar (Orange) Red Metallic | orangerot perlcolor | 1A8 / 1A9 | metallic | 2002 | `#c43c23` |  | consensus of 3 |
| Rainforest (Jungle) Green Metallic | dschungelgrünmetallic | 2A1 / 2A2 | metallic | 2002 | `#164838` |  | consensus of 3 |
| Carmon Red Metallic | carmonrotmetallic | M3W | metallic | 2004 | `#890a22` |  | consensus of 3 |
| GT Silver Metallic | GT-silbermetallic | M7Z | special | 2003–2004 (40 Years of 911 edition) | `#c6cad2` | ★◆ | Porsche daylight render |

### 13-997-1-2005 — 997.1 (2005–2008)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Black | schwarz | 041 / 741 | solid | 2005–2008 | `#17181a` |  | Porsche daylight render |
| Guards Red | indischrot | 84A / 80K | solid | 2005–2008 | `#b2211f` | ★ | Porsche daylight render |
| Carrara White | carraraweiß | B9A | solid | 2005–2008 | `#f0f0ed` | ★ | consensus of 3 |
| Speed Yellow | speedgelb | 12H / 12G | solid | 2005–2008 | `#e4b12a` | ★ | consensus of 5 |
| Basalt Black Metallic | basaltschwarzmetallic | C9Z | metallic | 2005–2008 | `#131520` | ★ | consensus of 2 |
| Arctic Silver Metallic | arktissilbermetallic | 92U | metallic | 2005–2008 | `#c2bfc3` | ★ | consensus of 4 |
| Atlas Grey Metallic | atlasgraumetallic | M7X | metallic | 2005–2008 | `#484940` | ★ | consensus of 3 |
| Seal Grey Metallic | sealgraumetallic | 6B4 | metallic | 2005–2008 | `#717472` | ★ | consensus of 4 |
| Slate Grey Metallic | schiefergraumetallic | 23F / 22D | metallic | 2005–2008 | `#626264` |  | consensus of 3 |
| Lapis Blue Metallic | lapisblaumetallic | M5W | metallic | 2005–2008 | `#152359` | ★ | consensus of 3 |
| Midnight Blue Metallic | nachtblaumetallic | 39C | metallic | 2005–2008 | `#131d2d` |  | consensus of 4 |
| Cobalt Blue Metallic | kobaltblaumetallic | 3C8 | metallic | 2005–2008 | `#335497` | ★◆ | consensus of 5 |
| Carmon Red Metallic | carmonrotmetallic | M3W | metallic | 2005–2008 | `#890a22` | ★ | consensus of 3 |
| Lago Green (Dark Teal) Metallic | lagogrünmetallic | M6W | metallic | 2005–2008 | `#2a4444` |  | consensus of 3 |
| Forest Green Metallic | tannengrünmetallic | 2B4 | metallic | 2005–2008 | `#19402d` |  | consensus of 4 |
| Meteor Grey Metallic | meteorgraumetallic | M7W | metallic | 2006–2008 | `#605e5b` |  | consensus of 4 |
| Macadamia Metallic | macadamiametallic | M8W | metallic | 2008 | `#4f382c` |  | consensus of 3 |
| GT Silver Metallic | GT-silbermetallic | M7Z | metallic | 2005–2008 | `#c6cad2` |  | Porsche daylight render |
| Dark Olive Metallic | dunkelolivmetallic | M6X | metallic | 2005–2008 | `#32301d` |  | consensus of 3 |
| Green (RS Green) | grün | 2D8 | special | 2007–2008 (911 GT3 RS) | `#42ab63` | ◆ | consensus of 3 |
| Orange | orange | 8C6 | special | 2007–2008 (911 GT3 RS) | `#da6433` |  | consensus of 2 |

### 14-997-2-2009 — 997.2 (2009–2012)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Black | schwarz | 041 | solid | 2009–2012 | `#17181a` |  | Porsche daylight render |
| Guards Red | indischrot | 84A / 80K | solid | 2009–2012 | `#b2211f` | ★ | Porsche daylight render |
| Carrara White | carraraweiß | B9A | solid | 2009–2012 | `#f0f0ed` | ★ | consensus of 3 |
| Speed Yellow | speedgelb | 12H / 12G | solid | 2009–2012 | `#e4b12a` | ★ | consensus of 5 |
| Basalt Black Metallic | basaltschwarzmetallic | C9Z | metallic | 2009–2012 | `#131520` | ★ | consensus of 2 |
| Arctic Silver Metallic | arktissilbermetallic | 92U | metallic | 2009–2012 | `#c2bfc3` |  | consensus of 4 |
| Platinum Silver Metallic | platinsilbermetallic | M7T | metallic | 2009–2012 | `#d3d1c7` |  | consensus of 3 |
| Meteor Grey Metallic | meteorgraumetallic | M7W | metallic | 2009–2012 | `#605e5b` |  | consensus of 4 |
| Atlas Grey Metallic | atlasgraumetallic | M7X | metallic | 2009–2010 | `#484940` |  | consensus of 3 |
| Aqua Blue Metallic | aquablaumetallic | M5R | metallic | 2009–2012 | `#2141af` | ★ | consensus of 3 |
| Macadamia Metallic | macadamiametallic | M8W | metallic | 2009–2012 | `#4f382c` | ★ | consensus of 3 |
| Dark Blue Metallic | dunkelblaumetallic | M5X | metallic | 2010–2012 | `#243b4e` |  | consensus of 3 |
| Midnight Blue Metallic | nachtblaumetallic | 39C | metallic | 2009–2010 | `#131d2d` |  | consensus of 4 |
| Agate Grey Metallic | achatgraumetallic | M7S | metallic | 2011–2012 | `#575756` |  | consensus of 3 |
| GT Silver Metallic | GT-silbermetallic | M7Z | metallic | 2009–2012 | `#c6cad2` | ★ | Porsche daylight render |
| Porsche Racing Green Metallic | porscheracinggreenmetallic | 22G | metallic | 2009–2012 | `#2a442e` | ★ | consensus of 4 |
| Crème White | cremeweiß | 51A | solid | 2009–2012 | `#f0e6d3` | ★ | consensus of 4 |
| Ruby Red Metallic | rubinrotmetallic | 8A7 | metallic | 2009–2012 | `#a21d26` |  | consensus of 4 |
| Amethyst Metallic | amethystmetallic | M4Z | metallic | 2010–2012 | `#492335` |  | consensus of 4 |
| Ipanema Blue Metallic | ipanemablaumetallic | 3S2 (F2) | metallic | 2012 | `#62a9b3` |  | consensus of 3 |
| Nordic Gold Metallic | nordischgoldmetallic | M2Z | metallic | 2009–2011 | `#be782c` | ★◆ | consensus of 4 |
| Malachite Green Metallic | malachitgrünmetallic | 2B5 | metallic | 2009–2010 | `#49584f` |  | consensus of 2 |
| Sport Classic Grey | sportclassicgrau | 63A | special | 2009–2010 (911 Sport Classic only) | `#b5bcbd` | ◆ | consensus of 2 |

### 15-991-1-2012 — 991.1 (2012–2015)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| Black | schwarz | 041 (option A1) | solid | 2012–2015 | `#17181a` | ★ | Porsche daylight render |
| White | weiß | C9A (option 0Q) | solid | 2012–2015 | `#d7dade` | ★ | Porsche daylight render |
| Carrara White | carraraweiß | B9A | solid | 2011–2012 | `#f0f0ed` |  | consensus of 3 |
| Guards Red | indischrot | 84A | solid | 2012–2015 | `#b2211f` | ★ | Porsche daylight render |
| Racing Yellow | racinggelb | 1S1 | solid | 2012–2015 | `#f1dc2c` | ★◆ | consensus of 3 |
| Basalt Black Metallic | basaltschwarzmetallic | C9Z | metallic | 2012–2015 | `#131520` |  | consensus of 2 |
| Agate Grey Metallic | achatgraumetallic | M7S | metallic | 2012–2015 | `#575756` | ★ | consensus of 3 |
| Platinum Silver Metallic | platinsilbermetallic | M7T | metallic | 2012–2015 | `#d3d1c7` |  | consensus of 3 |
| Rhodium Silver Metallic | rhodiumsilbermetallic | M7U | metallic | 2014–2015 | `#d3d6de` |  | consensus of 3 |
| Dark Blue Metallic | dunkelblaumetallic | M5X | metallic | 2012–2015 | `#243b4e` |  | consensus of 3 |
| Aqua Blue Metallic | aquablaumetallic | M5R | metallic | 2012–2015 | `#2141af` | ★◆ | consensus of 3 |
| Anthracite Brown Metallic | anthrazitbraunmetallic | M8S | metallic | 2012–2015 | `#3b3732` | ★ | consensus of 3 |
| Mahogany Metallic | mahagonimetallic | M8Y | metallic | 2012–2015 | `#442921` |  | consensus of 4 |
| Ruby Red Metallic | rubinrotmetallic | 8A7 / M3X | metallic | 2012 | `#a21d26` |  | consensus of 4 |
| Amaranth Red Metallic | amarantrotmetallic | 8L1 | metallic | 2013–2015 | `#ac170e` |  | consensus of 3 |
| Sapphire Blue Metallic | saphirblaumetallic | M5J | metallic | 2014–2015 | `#245292` |  | consensus of 3 |
| GT Silver Metallic | GT-silbermetallic | M7Z | metallic | 2012–2015 | `#c6cad2` | ★ | Porsche daylight render |
| Cognac Metallic | cognacmetallic | M8Z | metallic | 2012–2015 | `#ab865e` |  | consensus of 2 |
| Lime Gold Metallic | limegoldmetallic | 5P1 | metallic | 2012–2015 | `#dcd99f` |  | consensus of 3 |
| Lava Orange | lavaorange | M2A | special | 2015 (911 GT3 RS launch) | `#dc3919` | ★◆ | consensus of 4 |
| Ultraviolet | ultraviolett | M4A | special | 2015 (911 GT3 RS) | `#453558` |  | consensus of 3 |
| Geyser Grey Metallic | geysirgraumetallic | 9G5 | special | 2013–2014 (50 Years 911 edition) | `#d1cdbd` | ◆ | consensus of 3 |
| Graphite Grey | graphitgrau | 7B2 | special | 2013–2014 (50 Years 911 edition) | `#403f3f` |  | consensus of 2 |

### 16-991-2-2016 — 991.2 (2016–2019)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| White | weiß | C9A (option 0Q) | solid | 2016–2019 | `#d7dade` | ★ | Porsche daylight render |
| Black | schwarz | 041 (option A1) | solid | 2016–2019 | `#17181a` | ★ | Porsche daylight render |
| Guards Red | indischrot | 84A (option G1) | solid | 2016–2019 | `#b2211f` | ★ | Porsche daylight render |
| Racing Yellow | racinggelb | 1S1 (option P3) | solid | 2016–2019 | `#f1dc2c` | ★ | consensus of 3 |
| Lava Orange | lavaorange | M2A (option H2) | solid | 2016–2019 | `#dc3919` | ★◆ | consensus of 4 |
| Miami Blue | miamiblau | M5C (option J5) | solid | 2017–2019 | `#2e91ab` | ★◆ | consensus of 4 |
| Carmine Red | karminrot | M3C (option 0L) | solid | 2016–2019 | `#8d1c27` |  | Porsche daylight render |
| Chalk (Crayon) | kreide | M9A (option 3H) | solid | 2017–2019 (MY2018 on) | `#b9bcbe` | ★◆ | Porsche daylight render |
| Jet Black Metallic | tiefschwarzmetallic | C9X (option 2T) | metallic | 2016–2019 | `#27292c` |  | Porsche daylight render |
| Carrara White Metallic | carraraweißmetallic | S9R (option 2Y) | metallic | 2016–2019 | `#dfe4e5` |  | consensus of 3 |
| GT Silver Metallic | GT-silbermetallic | M7Z (option U2) | metallic | 2016–2019 | `#c6cad2` | ★ | Porsche daylight render |
| Rhodium Silver Metallic | rhodiumsilbermetallic | M7U (option S2) | metallic | 2016–2019 | `#d3d6de` |  | consensus of 3 |
| Agate Grey Metallic | achatgraumetallic | M7S (option N0) | metallic | 2016–2019 | `#575756` |  | consensus of 3 |
| Night Blue Metallic | nachtblaumetallic | M5F (option N5) | metallic | 2016–2019 | `#16293e` |  | consensus of 3 |
| Sapphire Blue Metallic | saphirblaumetallic | M5J (option N1) | metallic | 2016–2019 | `#245292` | ★ | consensus of 3 |
| Graphite Blue Metallic | graphitblaumetallic | M5G (option A7) | metallic | 2017–2019 | `#49545b` | ★ | consensus of 4 |
| Mahogany Metallic | mahagonimetallic | M8Y | metallic | 2016–2017 | `#442921` |  | consensus of 4 |
| Saffron Yellow Metallic | safrangelbmetallic | — | special | 2017–2019 (911 Turbo / Turbo S only) | `#dfd942` |  | single source (low) |
| Lizard Green | lizardgrün | M6B | special | 2018–2019 (911 GT3 RS) | `#5dd02b` | ◆ | consensus of 3 |
| Irish Green (one-off) | irischgrün | Y79 (current PTS code) | special | 2017 (one-millionth 911) | `#244b2a` | ◆ | consensus of 4 |

### 17-992-1-2019 — 992.1 (2019–2024)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| White | weiß | C9A (option 0Q) | solid | 2019–2024 | `#d7dade` | ★ | Porsche daylight render |
| Black | schwarz | 041 (option A1) | solid | 2019–2024 | `#17181a` | ★ | Porsche daylight render |
| Guards Red | indischrot | 84A (option G1) | solid | 2019–2024 | `#b2211f` | ★ | Porsche daylight render |
| Racing Yellow | racinggelb | 1S1 (option P3) | solid | 2019–2023 | `#f1dc2c` | ★◆ | consensus of 3 |
| Jet Black Metallic | tiefschwarzmetallic | C9X (option 2T) | metallic | 2019–2024 | `#27292c` |  | Porsche daylight render |
| Carrara White Metallic | carraraweißmetallic | S9R (option 2Y) | metallic | 2019–2023 | `#dfe4e5` |  | consensus of 3 |
| GT Silver Metallic | GT-silbermetallic | M7Z (option U2) | metallic | 2019–2024 | `#c6cad2` |  | Porsche daylight render |
| Agate Grey Metallic | achatgraumetallic | M7S (option N0) | metallic | 2019–2024 | `#575756` |  | consensus of 3 |
| Night Blue Metallic | nachtblaumetallic | M5F (option N5) | metallic | 2019–2022 | `#16293e` |  | consensus of 3 |
| Gentian Blue Metallic | enzianblaumetallic | M5D (option 1A) | metallic | 2019–2024 | `#273b7a` | ★ | Porsche daylight render |
| Aventurine Green Metallic | aventuringrünmetallic | M6T (option U4) | metallic | 2019–2024 | `#7f8484` | ★◆ | Porsche daylight render |
| Dolomite Silver Metallic | dolomitsilbermetallic | M7P (option F0) | metallic | 2019–2023 | `#c8cfd3` |  | consensus of 4 |
| Carmine Red | karminrot | M3C (option 0L) | solid | 2019–2024 | `#8d1c27` |  | Porsche daylight render |
| Lava Orange | lavaorange | M2A (option H2) | solid | 2019–2023 | `#dc3919` |  | consensus of 4 |
| Miami Blue | miamiblau | M5C (option J5) | solid | 2019–2021 | `#2e91ab` | ★ | consensus of 4 |
| Chalk (Crayon) | kreide | M9A (option 3H) | solid | 2019–2024 | `#b9bcbe` | ★◆ | Porsche daylight render |
| Python Green | pythongrün | M6C (option 3I) | solid | 2021–2024 | `#1a9646` | ★◆ | consensus of 3 |
| Shark Blue | sharkblue | D5C | solid | 2021–2024 | `#1975c5` | ★◆ | consensus of 2 |
| Arctic Grey | arktikgrau | M7K (option U0) | solid | 2022–2024 | `#5f6265` |  | consensus of 3 |
| Ice Grey Metallic | eisgraumetallic | M7N (option G7) | metallic | 2022–2024 | `#e4e6ea` |  | Porsche daylight render |
| Ruby Star Neo | sternrubin neo | M4B | solid | 2022–2024 | `#722347` |  | consensus of 2 |
| Shade Green Metallic | shadegreenmetallic | M6F | metallic | 2023–2024 | `#adc6c6` |  | Porsche daylight render |
| Shore Blue Metallic | shoreblaumetallic | R5G | special | 2023 (911 S/T Heritage Design Package only) | `#5f839d` |  | mean of 2 disagreeing sources (low) |

### 18-992-2-2024 — 992.2 (2024–today)

| Colour | German | Code | Type | Years | Hex | ★◆ | Hex basis |
|---|---|---|---|---|---|---|---|
| White | weiß | C9A (option 0Q) | solid | 2024–2026 | `#d7dade` | ★ | Porsche daylight render |
| Black | schwarz | 041 (option A1) | solid | 2024–2026 | `#17181a` | ★ | Porsche daylight render |
| Jet Black Metallic | tiefschwarzmetallic | C9X (option 2T) | metallic | 2024–2026 | `#27292c` |  | Porsche daylight render |
| Vanadium Grey Metallic | vanadiumgraumetallic | M7B (option 1H) | metallic | 2024–2026 | `#748190` |  | Porsche daylight render |
| GT Silver Metallic | GT-silbermetallic | M7Z (option U2) | metallic | 2024–2026 | `#c6cad2` | ★ | Porsche daylight render |
| Ice Grey Metallic | eisgraumetallic | M7N (option G7) | metallic | 2024–2026 | `#e4e6ea` |  | Porsche daylight render |
| Guards Red | indischrot | 84A (option G1) | solid | 2024–2026 | `#b2211f` | ★ | Porsche daylight render |
| Gentian Blue Metallic | enzianblaumetallic | M5D (option 1A) | metallic | 2024–2026 | `#273b7a` | ★ | Porsche daylight render |
| Carmine Red | karminrot | M3C (option 0L) | solid | 2024–2026 | `#8d1c27` |  | Porsche daylight render |
| Lugano Blue | luganoblau | Q5G (option O1) | solid | 2024–2026 | `#0e4d92` | ★◆ | Porsche daylight render |
| Cartagena Yellow Metallic | cartagenagelbmetallic | M1Q (option D9) | metallic | 2024–2026 | `#d2d498` | ★◆ | Porsche daylight render |
| Provence | provence | M4C (option 6M) | solid | 2026 (current configurator) | `#6c677d` |  | Porsche daylight render |
| Chalk (Crayon) | kreide | M9A (option 3H) | solid | 2024–2026 | `#b9bcbe` | ★◆ | Porsche daylight render |
| Shade Green Metallic | shadegreenmetallic | M6F (option G9) | metallic | 2024–2026 | `#adc6c6` | ★◆ | Porsche daylight render |
| Slate Grey Neo | schiefergrau neo | option 2M | solid | 2024–2026 | `#4a505a` | ★◆ | Porsche daylight render |
| Oak Green Metallic Neo | oakgrünmetallic neo | M6Y (option N4) | metallic | 2026 (current configurator) | `#345239` |  | Porsche daylight render |
| Aventurine Green Metallic | aventuringrünmetallic | M6T (option U4) | metallic | 2026 (current configurator) | `#7f8484` |  | Porsche daylight render |
| Miami Blue (Paint to Sample) | miamiblau | M5C | pts | 2024–2026 | `#2e91ab` |  | consensus of 4 |
| Python Green (Paint to Sample) | pythongrün | M6C | pts | 2024–2026 | `#1a9646` |  | consensus of 3 |
| Shark Blue (Paint to Sample) | sharkblue | D5C | pts | 2024–2026 | `#1975c5` |  | consensus of 2 |
| Riviera Blue (Paint to Sample) | rivierablau | 39E | pts | 2024–2026 | `#348ebd` |  | consensus of 3 |
| Signal Yellow (Paint to Sample) | signalgelb | 114 | pts | 2024–2026 | `#fca613` |  | consensus of 3 |

## Sources

`colors.json` cites 682 distinct URLs, all fetched in this session. By site: rennbow.org (282), paintscratch.com (195), colors.stuttcars.com (72), paintref.com (51), newsroom.porsche.com (31), prs.porsche.com (17), configurator.porsche.com (10), bringatrailer.com (8), commons.wikimedia.org (7), de.wikipedia.org (5), stuttcars.com (1), media.porsche.com (1), silo.tips (1), excellence-mag.com (1). Each entry cites the specific Rennbow, PaintScratch, stuttcars and paintref pages it relies on. The main documents are:

- <https://bringatrailer.com/listing/1991-porsche-911-carrera-2-coupe-56/>
- <https://bringatrailer.com/listing/1995-porsche-911-carrera-coupe-152/>
- <https://bringatrailer.com/listing/1999-porsche-911-carrera-coupe-175/>
- <https://bringatrailer.com/listing/1999-porsche-911-carrera-coupe-216/>
- <https://bringatrailer.com/listing/2001-porsche-911-carrera-coupe-51/>
- <https://bringatrailer.com/listing/2002-porsche-911-carrera-72/>
- <https://bringatrailer.com/listing/2002-porsche-911-carrera-coupe-55/>
- <https://bringatrailer.com/listing/2003-porsche-911-carrera-coupe-48/>
- <https://commons.wikimedia.org/wiki/File:1966_Porsche_911_p%C3%B3l%C3%B3piros_Batthy%C3%A1ny-kast%C3%A9ly_Bicske.jpg>
- <https://commons.wikimedia.org/wiki/File:1976_Porsche_930_Turbo,_Emerald_Green_met,_front_left.jpg>
- <https://commons.wikimedia.org/wiki/File:Alois_Ruf_Jr_with_901_prototype_at_Pebble_Beach_Concours_2023.jpg>
- <https://commons.wikimedia.org/wiki/File:Porsche-911-T-2.4-Classic-1973-beige-LightIvory131-RAL1015-profil-droite-byRundvald.jpg>
- <https://commons.wikimedia.org/wiki/File:Porsche_901_prototype_at_Pebble_Beach_Concours_2023.jpg>
- <https://commons.wikimedia.org/wiki/File:Porsche_911S_Classic_2.4L_Blue_Gemini.jpg>
- <https://commons.wikimedia.org/wiki/File:Projet_T7.JPG>
- <https://configurator.porsche.com/assets/exteriors/studio_1H.jpg>
- <https://configurator.porsche.com/assets/exteriors/studio_2M.jpg>
- <https://configurator.porsche.com/assets/exteriors/studio_6M.jpg>
- <https://configurator.porsche.com/assets/exteriors/studio_D9.jpg>
- <https://configurator.porsche.com/assets/exteriors/studio_G7.jpg>
- <https://configurator.porsche.com/assets/exteriors/studio_G9.jpg>
- <https://configurator.porsche.com/assets/exteriors/studio_N4.jpg>
- <https://configurator.porsche.com/assets/exteriors/studio_O1.jpg>
- <https://configurator.porsche.com/de-DE/mode/model/9921B2>
- <https://configurator.porsche.com/en-US/mode/model/9921B2>
- <https://de.wikipedia.org/wiki/Porsche_930>
- <https://de.wikipedia.org/wiki/Porsche_964>
- <https://de.wikipedia.org/wiki/Porsche_991>
- <https://de.wikipedia.org/wiki/Porsche_996>
- <https://de.wikipedia.org/wiki/Porsche_997>
- <https://media.porsche.com/paint-to-sample>
- <https://newsroom.porsche.com/en/2019/history/porsche-klassik-908-lemans-mcqueen-film-motorsports-15964.html>
- <https://newsroom.porsche.com/en/2019/history/porsche-klassik-911-eight-generations-dna-18914.html>
- <https://newsroom.porsche.com/en/2019/products/porsche-911-rev-counter-analogue-eight-generations-992-timeless-machine-valencia-16966.html>
- <https://newsroom.porsche.com/en/2019/products/porsche-last-911-generation-991-19601.html>
- <https://newsroom.porsche.com/en/2020/history/porsche-classic-factory-restoration-911-s-targa-1967-23123.html>
- <https://newsroom.porsche.com/en/2020/history/porsche-klassik-rally-dieter-roescheisen-heigo-911-sc-19632.html>
- <https://newsroom.porsche.com/en/2021/history/porsche-klassik-911-carrera-3-2-granite-green-christian-geistdoerfer-18920.html>
- <https://newsroom.porsche.com/en/2022/history/porsche-50-years-911-carrera-rs-2-7-germanys-fastest-sports-car-28486.html>
- <https://newsroom.porsche.com/en/2022/history/porsche-911-s-jochen-rindt-vienna-garage-heinz-swoboda-christophorus-400-27214.html>
- <https://newsroom.porsche.com/en/2022/history/porsche-klassik-911-sc-weissach-edition-merlin-assfalg-28981.html>
- <https://newsroom.porsche.com/en/2022/products/porsche-911-sport-classic-world-premiere-28164.html>
- <https://newsroom.porsche.com/en/2024/history/porsche-klassik-911-g-model-anniversary-model-1987-35245.html>
- <https://newsroom.porsche.com/en/2024/history/porsche-museum-special-exhibition-beyond-performance-50-years-porsche-turbo-36970.html>
- <https://newsroom.porsche.com/en/2025/products/porsche-custom-colours-requested-of-customers-39156.html>
- <https://newsroom.porsche.com/en/christophorus/porsche-targa-colors-11179.html>
- <https://newsroom.porsche.com/en/history/porsche-911-evolutionary-history-754-901-ferry-porsche-14641.html>
- <https://newsroom.porsche.com/en/history/porsche-911-seven-generations-part-3-type-964-16466.html>
- <https://newsroom.porsche.com/en/history/porsche-911-seven-generations-part-7-type-991-16499.html>
- <https://newsroom.porsche.com/en/history/porsche-frank-marrenbach-carrera-rs-2-7-garage-black-forest-65-years-christophorus-collection-birthday-14666.html>
- <https://newsroom.porsche.com/en/history/porsche-history-911-chameleon-944-928-colourful-tradition-13262.html>
- <https://newsroom.porsche.com/en/history/porsche-museum-restoration-number-57-911-901-barn-find-collection-14639.html>
- <https://newsroom.porsche.com/en/press-kits/60-Years-Porsche-911/1.-Generation---Motoren.html>
- <https://newsroom.porsche.com/en/press-kits/911-s-t/Design-and-equipment.html>
- <https://newsroom.porsche.com/en/press-kits/911/Exterior--design-and-body.html>
- <https://newsroom.porsche.com/en/press-kits/Porsche-Heritage-Experience/Porsche-911-(Typ-992)-Carrera-T.html>
- <https://newsroom.porsche.com/en/press-kits/Porsche-Museum/Porsche-911-(901-Nr.-57).html>
- <https://newsroom.porsche.com/en/press-kits/pfv-porsche-911-turbo-s/Body,-aerodynamics-and-design.html>
- <https://newsroom.porsche.com/en/products/porsche-911-carrera-t-puristic-performance-driving-pleasure-touring-14410.html>
- <https://newsroom.porsche.com/en/products/porsche-colors-911-gt3-rs-lizard-green-communication-color-design-barbara-sika-daniela-milosevic-sina-brunner-christophorus-386-15491.html>
- <https://newsroom.porsche.com/en/products/porsche-new-model-year-connectivity-colours-innovations-13535.html>
- <https://newsroom.porsche.com/en/products/porsche-one-millionth-911-milestone-details-13734.html>
- <https://silo.tips/download/die-porsche-911-premiere-das-highlight-auf-der-iaa-in-frankfurt-1963>
- <https://www.excellence-mag.com/issues/304/articles/out-of-the-shadows>
- <https://www.stuttcars.com/porsche-911-f-series-the-story/>
- Porsche configurator renders: `prs.porsche.com/iod/image/US/...` (17 render URLs, one per current colour; listed in each `hex_source.url`)
- paintref.com year and colour pages (via Common Crawl), e.g. <http://paintref.com/cgi-bin/colorcodedisplay.cgi?dupont=29003&rows=50&syear=1962&smanuf=Porsche&smodel=&sname=Slate%20Gray>, <http://paintref.com/cgi-bin/colorcodedisplay.cgi?make=Porsche&con=k&year=1968&rows=50>, <http://paintref.com/cgi-bin/colorcodedisplay.cgi?make=Porsche&con=k&year=1976&rows=50>, <http://paintref.com/cgi-bin/colorcodedisplay.cgi?make=Porsche&con=k&year=2018&rows=50>, <http://paintref.com/cgi-bin/colorcodedisplay.cgi?make=Porsche&year=1959&con=ky&rows=50>, <http://paintref.com/cgi-bin/colorcodedisplay.cgi?make=Porsche&year=1960&con=ky&rows=50>, <http://paintref.com/cgi-bin/colorcodedisplay.cgi?make=Porsche&year=1967&con=ky&rows=50>, <http://paintref.com/cgi-bin/colorcodedisplay.cgi?make=Porsche&year=1979&con=ky&rows=50>, <http://paintref.com/cgi-bin/colorcodedisplay.cgi?make=Porsche&year=1982&con=ky&rows=50>, <http://paintref.com/cgi-bin/colorcodedisplay.cgi?make=Porsche&year=1990&con=ky&rows=50>, <http://paintref.com/cgi-bin/colorcodedisplay.cgi?make=Porsche&year=1992&con=ky&rows=50>, <http://paintref.com/cgi-bin/colorcodedisplay.cgi?make=Porsche&year=1995&con=ky&rows=50>
- Rennbow colour wiki (<https://www.rennbow.org/color-wiki>): year/model searches and per-colour pages
- PaintScratch Porsche colour pages (<https://www.paintscratch.com/colors/porsche/>)
- stuttcars colour database (<https://colors.stuttcars.com/>)

## Uncertainties and gaps

- **Stop 00 (T7)** had no colour options. Its only documented colour is 'green metallic', with no name or code, and the hex comes from a museum photo. The other twelve entries are 356 B/356 A factory colours of 1959–61, marked as context in their `note`. Remove them if the UI should show only the prototype's own paint.
- **Stop 01 (901):** the IAA car's yellow is unnamed. Its hex comes from a white-balanced Porsche period photo of *a* yellow 901 prototype, possibly sister car 13 324 'Zitronenfalter'. The white 901/01 and 'Quickblau' hexes also come from single photos. Prototype 13 323 'Blaumeise' (dark blue, later red) is omitted because no image or swatch was found.
- **Single-source or disagreeing hexes** are flagged 'low confidence' in `hex_source.method`. Examples: Sky Blue, Togo Brown, Aga Blue, Canary Yellow, Crystal Blue, Royal Blue 6012, Condor Yellow, Metallic Blue, Light Red, Turquoise, Violet Chromaflair, Saffron Yellow and Shore Blue. Editor chips (Rennbow) tend to read bright, paintref chips dark, and PaintScratch varies.
- **Conflicting names in the sources:**
  - 25H/25K is 'Dragonfly Turquoise' in stuttcars and 'Ocean Jade' in PaintScratch.
  - 80D is Cassis Red in Rennbow and PaintScratch but 'Oasis Red' in paintref.
  - 10W is Summer Yellow, but stuttcars calls it 'Lemon Yellow'.
  - 499 appears as Caramel, Ceramic and Carmel Beige.
  - 018/6809 is Tangerine or Blood Orange (the German name is Blutorange).
  - 305 was Royal Blue in 1969–72 and Arrow Blue from 1976.
  - 463 is Opal in the 1980 chart and Casablanca Beige elsewhere.
  - Porsche's 'Viper Green Diamond' on the 1974 Turbo show car maps to Emerald Green Metallic (264/249) only by Rennbow's code list.
- **Model-year ranges for pre-1990 colours** mostly come from Rennbow, which records examples seen, and from paintref year pages. Brochures would be definitive, but none from the air-cooled era were fetched this session. Examples: Zermatt Silver on the 964 is left out because the sources conflict, and the RS 2.7's 'Bright Yellow' is matched to Light Yellow 117 by inference.
- **Iconic flags** are set only where a fetched source singles out the colour. The coordinator's list was checked this way. Gentian Blue is featured but not marked iconic, because no fetched source calls it a launch or signature colour.
- **Search limits:** the web-search quota ran out early in the session. Later research used Porsche sitemaps, Common Crawl captures (paintref), site JSON APIs (Rennbow, stuttcars, PaintScratch) and the configurator's render service instead of search engines. Some brochure-level confirmations could not be reached this way.
