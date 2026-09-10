# -*- coding: utf-8 -*-
"""Build the Global CCGT/HRSG Fleet Inventory dataset from the PowerAtlas master.

A harmonised single-table view of the world's combined-cycle gas turbine (CCGT)
plants and their heat-recovery steam generators (HRSG): capacity, owner,
commissioning year, lifecycle status, number of HRSG units, CHP flag, gas/steam
turbine models, and (where available) annual CO2. Compiled from WRI GPPD +
Global Energy Monitor (GOGPT) + Climate TRACE. NOT new primary data — the
contribution is the cleaned, deduplicated, analysis-ready CCGT/HRSG subset that
is otherwise only available across paid fleet trackers.

Reproducible: reads ../../ventures/poweratlas/output/power_plants_master.json.
Outputs data/, datapackage.json, croissant.json, data_dictionary.csv.
"""
import os, sys, json, csv, io, collections

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, "..", "..", "ventures", "poweratlas", "output", "power_plants_master.json")
OUT = os.path.join(HERE, "data"); os.makedirs(OUT, exist_ok=True)

P = json.load(open(MASTER, encoding="utf-8"))
ccgt = [p for p in P if p.get("technology") == "CCGT" or p.get("hrsg")]

# Optional EIA-860 per-site enrichment for US plants (gas-turbine count, duct burners, HRSG bypass…)
ENR = {}
_ep = os.path.join(HERE, "eia_enrichment.json")
if os.path.exists(_ep):
    ENR = json.load(open(_ep))

# --- canonical country name per ISO3 (fix "United States of America" vs "United States") ---
name_votes = collections.defaultdict(collections.Counter)
for p in ccgt:
    if p.get("cc3") and p.get("country"):
        name_votes[p["cc3"]][p["country"]] += 1
canon = {cc3: c.most_common(1)[0][0] for cc3, c in name_votes.items()}

def tclass(t):
    """Indicative gas-turbine technology class from model strings (global)."""
    if not t: return ""
    u = t.upper()
    if any(k in u for k in ["9HA", "7HA", "M501J", "M701J", "9000HL", "GT36"]): return "H/J-class"
    if any(k in u for k in ["9FA", "9FB", "7FA", "7FB", "M501F", "M701F", "4000F", "5000F", "GT26", "GT24", "V94.3", "V84.3"]): return "F-class"
    if any(k in u for k in ["9E", "7E", "M501D", "2000E", "SGT-800", "SGT-700", "SGT-600", "V94.2", "GT13"]): return "E/legacy-class"
    return "other/unspecified"

def sanitize(v):
    """Spreadsheet-formula guard for TEXT values only: numeric values
    (including negatives) pass through unchanged; a leading '=', '+', '@'
    or a non-numeric leading '-' is escaped with an apostrophe."""
    if v is None: return ""
    s = str(v)
    if not s: return s
    if s[0] in ("=", "+", "@"):
        return "'" + s
    if s[0] == "-":
        try:
            float(s); return s
        except ValueError:
            return "'" + s
    return s

COLS = ["plant_id", "name", "country", "iso3", "latitude", "longitude",
        "capacity_mw", "commissioning_year", "gem_status",
        "hrsg_units", "chp", "gas_steam_turbine_models", "turbine_class", "technology",
        "owner", "co2_tonnes_per_year", "co2_source", "co2_basis",
        "generation_gwh", "region", "nearest_place", "data_source",
        "gas_turbine_count", "duct_burners", "hrsg_bypass_capability",
        "carbon_capture", "planned_retirement_year", "us_eia_plant_code",
        "measured_thermal_efficiency_pct", "measured_heat_rate_btu_per_kwh",
        "measured_co2_intensity_kg_per_mwh", "measured_capacity_factor",
        "measured_net_generation_gwh"]

def row(p):
    src = p.get("co2_src")
    basis = "" if not src else ("measured" if src in ("US EPA GHGRP", "EU ETS") else "modelled (Climate TRACE)")
    en = ENR.get(p.get("id"), {})
    return {
        "plant_id": p.get("id"), "name": p.get("name"),
        "country": canon.get(p.get("cc3"), p.get("country")), "iso3": p.get("cc3"),
        "latitude": p.get("lat"), "longitude": p.get("lon"),
        "capacity_mw": p.get("capacity_mw"), "commissioning_year": p.get("year"),
        "gem_status": p.get("gem_status"), "hrsg_units": p.get("hrsg_units"),
        "chp": p.get("chp"), "gas_steam_turbine_models": p.get("turbine"),
        "turbine_class": tclass(p.get("turbine")), "technology": "CCGT", "owner": p.get("owner"),
        "co2_tonnes_per_year": p.get("co2"), "co2_source": src, "co2_basis": basis,
        "generation_gwh": p.get("generation_gwh"), "region": p.get("region"),
        "nearest_place": p.get("nearest_place"), "data_source": p.get("source"),
        "gas_turbine_count": en.get("gas_turbine_count"),
        "duct_burners": en.get("duct_burners"),
        "hrsg_bypass_capability": en.get("hrsg_bypass_capability"),
        "carbon_capture": en.get("carbon_capture"),
        "planned_retirement_year": en.get("planned_retirement_year"),
        "us_eia_plant_code": en.get("us_eia_plant_code"),
        "measured_thermal_efficiency_pct": en.get("measured_thermal_efficiency_pct"),
        "measured_heat_rate_btu_per_kwh": en.get("measured_heat_rate_btu_per_kwh"),
        "measured_co2_intensity_kg_per_mwh": en.get("measured_co2_intensity_kg_per_mwh"),
        "measured_capacity_factor": en.get("measured_capacity_factor"),
        "measured_net_generation_gwh": en.get("measured_net_generation_gwh"),
    }

rows = [row(p) for p in ccgt]
rows.sort(key=lambda r: -(r["capacity_mw"] or 0))

# CSV
with open(os.path.join(OUT, "ccgt_hrsg_fleet.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
    for r in rows:
        w.writerow({k: sanitize(r[k]) for k in COLS})
# JSON
json.dump(rows, open(os.path.join(OUT, "ccgt_hrsg_fleet.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

# --- stats for descriptor ---
n = len(rows)
gw = round(sum((r["capacity_mw"] or 0) for r in rows) / 1000)
ncountry = len(set(r["iso3"] for r in rows if r["iso3"]))
cov = {c: round(100 * sum(1 for r in rows if r[c] not in (None, "", 0)) / n) for c in
       ["capacity_mw", "owner", "commissioning_year", "gem_status", "hrsg_units",
        "chp", "gas_steam_turbine_models", "co2_tonnes_per_year"]}
co2basis = collections.Counter(r["co2_basis"] for r in rows if r["co2_basis"])

DESC = (f"A harmonised single-table inventory of {n:,} combined-cycle gas turbine (CCGT) "
        f"power plants worldwide and their heat-recovery steam generators (HRSG) - "
        f"{gw:,} GW across {ncountry} countries. Each record carries capacity (100%), operating "
        f"company (99%), commissioning year (89%), lifecycle status (92%), number of HRSG units "
        f"(100%), a CHP flag (36%) and, where reported, the gas and steam turbine models (18%) and "
        f"annual CO2 (32%, mostly Climate TRACE modelled - read co2_basis). Compiled and "
        f"deduplicated from the WRI Global Power Plant Database, Global Energy Monitor (GOGPT) and "
        f"Climate TRACE. This is a cleaned, analysis-ready compilation of existing open sources - "
        f"not new primary measurement; equivalent fleet detail is otherwise only available across "
        f"paid trackers. CC BY 4.0.")
TITLE = "Global CCGT & HRSG Fleet Inventory: combined-cycle plants with capacity, owner, HRSG units and turbine models"

TYPES = {"latitude": "number", "longitude": "number", "capacity_mw": "number",
         "commissioning_year": "integer", "hrsg_units": "integer", "chp": "boolean",
         "co2_tonnes_per_year": "number", "generation_gwh": "number",
         "gas_turbine_count": "integer", "duct_burners": "boolean",
         "hrsg_bypass_capability": "boolean", "carbon_capture": "boolean",
         "planned_retirement_year": "integer",
         "measured_thermal_efficiency_pct": "number", "measured_heat_rate_btu_per_kwh": "integer",
         "measured_co2_intensity_kg_per_mwh": "integer", "measured_capacity_factor": "number",
         "measured_net_generation_gwh": "number"}
DDESC = {
 "plant_id": "Stable identifier (WRI GPPD id or GEM id)", "name": "Plant name",
 "country": "Country (canonicalised via ISO3)", "iso3": "ISO 3166-1 alpha-3",
 "latitude": "WGS84", "longitude": "WGS84", "capacity_mw": "Installed capacity, MW",
 "commissioning_year": "Year of commissioning where known (89%)",
 "gem_status": "Lifecycle status (operating/construction/announced/...) from GEM (92%)",
 "hrsg_units": "Number of heat-recovery steam generators at the plant (100%)",
 "chp": "Combined heat & power (cogeneration) flag (36% populated)",
 "gas_steam_turbine_models": "Gas + steam turbine make/model strings where known (18%)",
 "turbine_class": "Indicative GT technology class (H/J, F, E/legacy) from turbine model where known",
 "technology": "Constant: CCGT", "owner": "Operating company / owner (99%)",
 "co2_tonnes_per_year": "Annual CO2 where available (32%) - see co2_basis",
 "co2_source": "Climate TRACE / US EPA GHGRP / EU ETS",
 "co2_basis": "measured (EPA/EU ETS) or modelled (Climate TRACE)",
 "generation_gwh": "Annual generation, GWh, where reported (25%)",
 "region": "Sub-national region", "nearest_place": "Nearest populated place",
 "data_source": "Backbone provenance: WRI / GEM-GOGPT / Climate TRACE",
 "gas_turbine_count": "Number of combustion-turbine units (US plants, EIA-860 generator records)",
 "duct_burners": "HRSG supplementary firing present (US, EIA-860)",
 "hrsg_bypass_capability": "Plant can bypass its HRSG (simple-cycle operation) (US, EIA-860)",
 "carbon_capture": "Carbon-capture technology reported (US, EIA-860)",
 "planned_retirement_year": "Planned generator retirement year where filed (US, EIA-860)",
 "us_eia_plant_code": "EIA plant code (join key for US plants)",
 "measured_thermal_efficiency_pct": "MEASURED net thermal efficiency % = 3412.14/heat-rate (US, eGRID/EPA CEMS)",
 "measured_heat_rate_btu_per_kwh": "MEASURED annual heat rate, Btu/kWh (US, eGRID)",
 "measured_co2_intensity_kg_per_mwh": "MEASURED CO2 output rate, kg/MWh (US, eGRID/EPA CEMS)",
 "measured_capacity_factor": "MEASURED annual capacity factor (US, eGRID)",
 "measured_net_generation_gwh": "MEASURED annual net generation, GWh (US, eGRID)"}

fields = [{"name": c, "type": TYPES.get(c, "string"), "description": DDESC.get(c, "")} for c in COLS]
datapackage = {
 "name": "global-ccgt-hrsg-fleet",
 "title": TITLE, "version": "1.0.0", "description": DESC,
 "licenses": [{"name": "CC-BY-4.0", "path": "https://creativecommons.org/licenses/by/4.0/",
               "title": "Creative Commons Attribution 4.0 International"}],
 "contributors": [{"title": "Dmytro Aheiev", "organization": "Inzonex", "role": "author"}],
 "sources": [
   {"title": "WRI Global Power Plant Database", "path": "https://datasets.wri.org/datasets/global-power-plant-database"},
   {"title": "Global Energy Monitor - Global Oil & Gas Plant Tracker", "path": "https://globalenergymonitor.org/projects/global-oil-gas-plant-tracker/"},
   {"title": "Climate TRACE", "path": "https://climatetrace.org/"},
   {"title": "US EIA Form 860 (generator-level, combined-cycle detail for US plants)", "path": "https://www.eia.gov/electricity/data/eia860/"},
   {"title": "US EPA eGRID (CEMS-based MEASURED net generation, heat input, CO2 → efficiency & CO2-intensity for US plants)", "path": "https://www.epa.gov/egrid"},
 ],
 "resources": [{"name": "ccgt-hrsg-fleet", "path": "data/ccgt_hrsg_fleet.csv",
                "format": "csv", "mediatype": "text/csv", "encoding": "utf-8",
                "schema": {"fields": fields, "primaryKey": "plant_id"}}],
}
json.dump(datapackage, open(os.path.join(HERE, "datapackage.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

croissant = {
 "@context": {"@vocab": "https://schema.org/"}, "@type": "Dataset",
 "name": TITLE, "description": DESC,
 "license": "https://creativecommons.org/licenses/by/4.0/",
 "creator": {"@type": "Organization", "name": "Inzonex", "url": "https://inzonex.co.uk/"},
 "isAccessibleForFree": True,
 "keywords": ["CCGT", "combined cycle", "HRSG", "heat recovery steam generator", "gas turbine",
              "power plants", "energy", "waste heat", "cogeneration", "CHP"],
 "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv",
                   "contentUrl": "data/ccgt_hrsg_fleet.csv"}],
 "isBasedOn": [s["path"] for s in datapackage["sources"]],
}
json.dump(croissant, open(os.path.join(HERE, "croissant.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

with open(os.path.join(HERE, "data_dictionary.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["field", "type", "description"])
    for c in COLS:
        w.writerow([c, TYPES.get(c, "string"), DDESC.get(c, "")])

print(f"BUILT {n} CCGT/HRSG units | {gw} GW | {ncountry} countries")
print("coverage:", cov)
print("co2_basis:", dict(co2basis))
