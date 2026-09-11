# Global CCGT & HRSG Fleet Inventory (v1.0)

A harmonised, analysis-ready single table of **2,813 combined-cycle gas turbine (CCGT) power
plants worldwide** and their **heat-recovery steam generators (HRSG)** — **2,067 GW across 134
countries**.

Each record carries:

- **Capacity** (MW) — 100%
- **Operating company / owner** — 99%
- **Commissioning year** — 89%
- **Lifecycle status** (operating / construction / announced / mothballed) — 92%
- **Number of HRSG units** at the plant — 100%
- **CHP (cogeneration) flag** — 36%
- **Gas + steam turbine make/model** (e.g. *GE 9FB*, *Siemens SGT5-4000F*) — 18%
- **Annual CO₂** where available — 32% (read `co2_basis`)
- **US per-site engineering detail** (EIA-860): gas-turbine count, duct burners, HRSG-bypass
  capability, carbon capture, planned retirement — **458 US plants**
- **MEASURED operations** (US EPA eGRID / CEMS): net thermal efficiency, heat rate, CO₂-intensity
  (kg/MWh) and capacity factor — **~430 US plants** (metered, not modelled)

## Why this exists

WRI GPPD is plant-level and carries no CCGT flag or HRSG detail; GEM's trackers and Climate TRACE
each hold pieces. This dataset **compiles and deduplicates** them into one CCGT/HRSG-specific table
— the kind of fleet view that is otherwise only assembled inside **paid** trackers (Gas Turbine
World, McCoy Power Reports). It is a **cleaned compilation of open sources, not new primary
measurement.** Useful for power-systems / energy-engineering research, waste-heat & HRSG studies,
and gas-fleet age / retirement analysis.

## At a glance

| | |
|---|---|
| Records | **2,813** CCGT plants |
| Capacity | **≈ 2,067 GW** |
| Countries | **134** |
| HRSG units | 1–6 per plant (100% populated) |
| Turbine models | 18% of plants |
| CO₂ provenance | 232 measured (EPA/EU ETS) · 668 modelled (Climate TRACE) |
| License | CC BY 4.0 |

## Files

| File | What |
|---|---|
| `data/ccgt_hrsg_fleet.csv` / `.json` | The dataset (UTF-8, formula-injection sanitised) |
| `datapackage.json` | Frictionless schema |
| `croissant.json` | schema.org / Google Dataset Search metadata |
| `data_dictionary.csv` | Field codebook |
| `DATA_DESCRIPTOR.md` | Short data-descriptor (EarthArXiv-ready) |
| `CITATION.cff` · `LICENSE` | Citation metadata / CC BY 4.0 |
| `build_dataset.py` | Current builder. It does not reproduce the v1.0.0 files byte for byte; the files in `data/` are the exact v1.0.0 files from the Zenodo record |

## Honest limitations

- **Compilation, not measurement.** All fields derive from WRI GPPD, Global Energy Monitor (GOGPT)
  and Climate TRACE. The contribution is the cleaned, deduplicated CCGT/HRSG single-table view.
- **Turbine models cover 18%** of plants; absence ≠ no turbine, just not in source data.
- **CO₂ is partial (32%) and mostly modelled** (Climate TRACE); only the EPA/EU ETS subset is
  regulator-measured. Read `co2_basis` before using CO₂.
- Owner is best-effort, not an authoritative corporate registry.

## Sources & attribution

WRI Global Power Plant Database (CC BY 4.0) · Global Energy Monitor — Global Oil & Gas Plant Tracker
(CC BY 4.0) · Climate TRACE (CC BY 4.0) · US EIA Form 860 (public domain, US per-site engineering
detail) · US EPA eGRID (public domain, CEMS-based measured efficiency & CO₂-intensity). Please
attribute these upstream sources alongside this compilation.

## Citation

The Zenodo record is the citable version of record; this repository is the source.

> Aheiev, D. (2026). *Global CCGT & HRSG Fleet Inventory with measured US efficiency &
> CO2-intensity* (v1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.20728927

- Concept DOI (always the latest version): https://doi.org/10.5281/zenodo.20728927
- Documentation: https://inzonex.co.uk/poweratlas/ccgt-hrsg-fleet/

Released under CC BY 4.0.
