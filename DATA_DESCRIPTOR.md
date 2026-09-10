# Global CCGT & HRSG Fleet Inventory: a harmonised single-table compilation with capacity, owner, HRSG-unit counts and turbine models

**Author:** Dmytro Aheiev (Inzonex) · **Version:** 1.0 · **License:** CC BY 4.0

> Data-descriptor preprint, prepared for EarthArXiv. This is a harmonised compilation of existing
> open datasets, not new primary measurement.

## Abstract

We present an open, analysis-ready inventory of **2,813 combined-cycle gas turbine (CCGT) power
plants worldwide** and their **heat-recovery steam generators (HRSG)** — approximately **2,067 GW
across 134 countries**. Each record carries installed capacity (100% coverage), operating company
(99%), commissioning year (89%), lifecycle status (92%), the number of HRSG units at the plant
(100%), a combined-heat-and-power flag (36%), the gas and steam turbine make/model where reported
(18%), and annual CO₂ where available (32%, predominantly Climate TRACE modelled estimates; the
remainder regulator-measured from US EPA GHGRP / EU ETS, flagged per row in `co2_basis`). The table
is compiled and deduplicated from the WRI Global Power Plant Database, Global Energy Monitor's
Global Oil & Gas Plant Tracker, and Climate TRACE. **The contribution is the cleaned, CCGT/HRSG-
specific single-table view** — fleet detail (HRSG-unit counts, turbine models) that is otherwise
dispersed across these sources or held only in paid commercial trackers. It supports power-systems
modelling, waste-heat / HRSG engineering research, and gas-fleet age and retirement analysis.

## Background & Summary

The WRI Global Power Plant Database provides a global plant backbone but does not flag which gas
plants are combined-cycle, nor expose HRSG structure. Global Energy Monitor tracks gas units with
status and, for many, turbine models; Climate TRACE adds modelled emissions. No single **open**
source presents a CCGT/HRSG-specific fleet table with HRSG-unit counts and turbine models — that
detail is otherwise assembled inside subscription products. This dataset fills that convenience gap
by harmonising the three open sources into one deduplicated table keyed on plant identity.

## Methods

**Sources.** WRI GPPD (capacity, owner, coordinates, fuel); Global Energy Monitor — Global Oil & Gas
Plant Tracker (combined-cycle status, HRSG-unit count, turbine models, lifecycle status, CHP);
Climate TRACE (asset-level modelled CO₂). US EPA GHGRP / EU ETS supply regulator-measured CO₂ for
the US/EU subset. **US EIA Form 860** (generator-level) adds per-site engineering detail for 458
matched US plants: number of combustion turbines, duct burners, HRSG-bypass capability, carbon
capture and planned retirement year. **US EPA eGRID** (built on continuous stack monitoring, CEMS)
adds **measured** operations for ~430 US plants: net thermal efficiency (= 3412.14 ÷ heat rate),
heat rate (Btu/kWh), CO₂-intensity (kg/MWh) and capacity factor. These are metered, not modelled —
kept strictly separate from the modelled Climate TRACE CO₂. Measured operations are US-only (no
equivalent open metered source exists globally); the fleet-structure layer is global.

**Selection.** Plants flagged as combined-cycle (`technology = CCGT`) or carrying an HRSG flag
(n = 2,813). **Deduplication & identity** retained one record per physical plant; country names were
canonicalised via ISO3 (e.g. "United States of America" → "United States"). **CO₂ provenance** is
explicit: `co2_basis` distinguishes measured (EPA/EU ETS) from modelled (Climate TRACE). **CSV
sanitisation:** cells beginning with `= + - @` are apostrophe-prefixed to neutralise formula
injection. The transform is a single reproducible script, `build_dataset.py`.

## Data Records

One row per plant; primary key `plant_id`. Key fields: `capacity_mw`, `commissioning_year`,
`gem_status`, `hrsg_units`, `chp`, `gas_steam_turbine_models`, `owner`, `co2_tonnes_per_year`,
`co2_source`, `co2_basis`, `generation_gwh`, `region`, `data_source` (WRI / GEM-GOGPT / Climate
TRACE). Full definitions in `data_dictionary.csv`.

## Technical Validation

Provenance of every row is preserved in `data_source`; CO₂ provenance in `co2_source`/`co2_basis`.
Summed capacity (≈ 2,067 GW) is consistent in order of magnitude with global operating + planned
combined-cycle capacity. Plant identity, coordinates and capacity inherit from WRI GPPD / GEM.

## Usage Notes

For fleet-age or retirement work use `commissioning_year` + `gem_status`. For HRSG / waste-heat work
use `hrsg_units` + `capacity_mw` + `gas_steam_turbine_models`. **Do not treat the CO₂ column as a
complete or measured inventory** — it is 32% populated and mostly modelled (read `co2_basis`).

## Limitations

- **Compilation, not new measurement** — all attributes derive from the three open sources.
- Turbine models cover 18% of plants; CHP flag 36%; CO₂ 32% (mostly modelled).
- Owner normalisation is best-effort, not an authoritative registry.

## Data Availability

Archived on Zenodo (CC BY 4.0). Reproducible via `build_dataset.py` from the open source datasets.

## Acknowledgements

Builds on the open datasets of WRI, Global Energy Monitor, Climate TRACE, the US EPA and the EU
(EU ETS).
