"""
Tier 1 support: in-memory entity index for the Synapse router.

Builds a lookup of every referenceable entity from the existing node JSON files so
questions can be matched against real IDs and names without any LLM or DB call.

build_entity_index() -> {entity_type: [{"id", "name", "aliases": [...]}, ...]}
entity types: coil, equipment, standard, technician, doc_type
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # -> synapse/
NODES = ROOT / "ontology" / "nodes"

# extra human-language aliases per equipment type (how people actually refer to machines;
# includes legacy phrasing like "hot rolling mill" that appears in procedure/document text)
EQUIPMENT_TYPE_ALIASES = {
    "blast_furnace": ["blast furnace"],
    "hot_blast_stove": ["hot blast stove"],
    "sinter_plant_feeder": ["sinter plant feeder", "sinter feeder", "weigh belt feeder"],
    "electric_arc_furnace": ["electric arc furnace", "arc furnace", "eaf"],
    "ladle_furnace": ["ladle furnace"],
    "continuous_casting_machine": ["continuous casting machine", "casting machine", "caster", "ccm"],
    "reheating_furnace": ["reheating furnace", "reheat furnace"],
    "roughing_mill_stand": ["roughing mill", "hot rolling mill", "rolling mill"],
    "finishing_mill_stand": ["finishing mill", "hot rolling mill", "rolling mill"],
    "coiler_unit": ["coiler unit", "coiler", "downcoiler"],
    "runout_table": ["runout table", "run-out table", "runout cooling"],
    "overhead_crane": ["overhead crane", "eot crane", "crane"],
    "conveyor_system": ["conveyor system", "conveyor", "belt conveyor"],
}

DOC_TYPE_ALIASES = {
    "sop": ["sop", "standard operating procedure"],
    "rca_report": ["rca report", "rca", "root cause analysis"],
    "deviation_report": ["deviation report"],
    "equipment_manual": ["equipment manual", "manual"],
    "inspection_report": ["inspection report"],
    "standard_reference": ["standard reference"],
}


def _load(name):
    with open(NODES / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


def _standard_aliases(std_id, name):
    """Derive spoken forms from a standard's name, e.g. 'BIS IS:2062 -- ...' ->
    ['is 2062', 'is:2062', 'is2062'];  ASTM A370 -> ['astm a370', 'a370']."""
    aliases = {std_id.lower()}
    low = name.lower()
    # only the standard's OWN designation (first IS-number in the name) -- names may
    # mention other standards (e.g. the withdrawn IS:226 marker says "superseded by IS 2062")
    m = re.search(r"is[:\s]*(\d{3,4})", low)
    if m:
        num = m.group(1)
        aliases.update({f"is {num}", f"is:{num}", f"is{num}"})
    if re.search(r"astm\s*a\s*370", low):
        aliases.update({"astm a370", "a370", "astm a 370"})
    if "factories act" in low:
        aliases.update({"factories act", "factory act", "factories act, 1948", "factories act 1948"})
    return sorted(aliases)


def build_entity_index():
    """Build the full entity index from ontology/nodes/*.json (no DB, no LLM)."""
    index = {}

    index["coil"] = [
        {"id": c["coil_id"], "name": c["coil_id"], "aliases": [c["coil_id"].lower()]}
        for c in _load("coil")
    ]

    index["equipment"] = []
    for e in _load("equipment"):
        aliases = {e["equipment_id"].lower(), e["name"].lower()}
        aliases.update(EQUIPMENT_TYPE_ALIASES.get(e["type"], [e["type"].replace("_", " ")]))
        index["equipment"].append(
            {"id": e["equipment_id"], "name": e["name"], "aliases": sorted(aliases)}
        )

    index["standard"] = [
        {"id": s["standard_id"], "name": s["name"],
         "aliases": _standard_aliases(s["standard_id"], s["name"])}
        for s in _load("standard")
    ]

    index["technician"] = [
        {"id": t["technician_id"], "name": t["name"],
         "aliases": [t["technician_id"].lower(), t["name"].lower()]}
        for t in _load("technician")
    ]

    doc_types = sorted({d["doc_type"] for d in _load("document")})
    index["doc_type"] = [
        {"id": dt, "name": dt,
         "aliases": sorted(set(DOC_TYPE_ALIASES.get(dt, [])) | {dt.replace("_", " ")})}
        for dt in doc_types
    ]

    return index


if __name__ == "__main__":
    idx = build_entity_index()
    for etype, items in idx.items():
        print(f"{etype:<11} {len(items):>4} entities   e.g. {items[0]['id']} aliases={items[0]['aliases'][:3]}")
