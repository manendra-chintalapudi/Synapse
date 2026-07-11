# -*- coding: utf-8 -*-
"""Build the static graph_data.json consumed by the Knowledge Graph UI (frontend/chat.html).

Read-only over the ontology; touches no backend/synthesizer/router logic. Regenerate after
any change to ontology/nodes/*.json or ontology/relationships/*.json:

    python synapse/frontend/build_graph_data.py

Emits stats (counts, by-type, top-degree), a schema map (dominant endpoint pair per
relationship type), and compact node/edge lists (id/label/type/degree/props).
"""
import json, os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))          # synapse/
N = os.path.join(ROOT, "ontology", "nodes")
R = os.path.join(ROOT, "ontology", "relationships")
OUT = os.path.join(HERE, "assets", "graph_data.json")

def j(name, base):
    with open(os.path.join(base, name + ".json"), encoding="utf-8") as f:
        return json.load(f)

NODE_FILES = ["standard","raw_material","equipment","technician","procedure","coil",
              "quality_test","failure","deviation","rca","document"]
REL_FILES = ["produced_at","made_from","tested_by","failed_standard","tested_against",
             "has_deviation","experienced","diagnosed_by","performed_by","maintained_by",
             "follows_procedure","references_standard","documented_in","version_of"]
PK = {"standard":"standard_id","raw_material":"material_id","equipment":"equipment_id",
      "technician":"technician_id","procedure":"procedure_id","coil":"coil_id",
      "quality_test":"test_id","failure":"failure_id","deviation":"deviation_id",
      "rca":"rca_id","document":"document_id"}
LABEL = {"standard":"Standard","raw_material":"RawMaterial","equipment":"Equipment",
         "technician":"Technician","procedure":"Procedure","coil":"Coil",
         "quality_test":"QualityTest","failure":"Failure","deviation":"Deviation",
         "rca":"RCA","document":"Document"}
TYPE_OF = {"produced_at":"PRODUCED_AT","made_from":"MADE_FROM","tested_by":"TESTED_BY",
           "failed_standard":"FAILED_STANDARD","tested_against":"TESTED_AGAINST",
           "has_deviation":"HAS_DEVIATION","experienced":"EXPERIENCED","diagnosed_by":"DIAGNOSED_BY",
           "performed_by":"PERFORMED_BY","maintained_by":"MAINTAINED_BY",
           "follows_procedure":"FOLLOWS_PROCEDURE","references_standard":"REFERENCES_STANDARD",
           "documented_in":"DOCUMENTED_IN","version_of":"VERSION_OF"}

def short(s, n=48):
    s = str(s or ""); return s if len(s) <= n else s[:n-1] + "…"

def disp(t, r):
    if t == "equipment":    return short(r.get("name"), 30)
    if t == "procedure":    return short(r.get("title"), 34)
    if t == "technician":   return short(r.get("name"), 24)
    if t == "standard":     return short(r.get("name"), 40)
    if t == "failure":      return f'{r["failure_id"]} · {short(r.get("failure_mode"),18)}'
    if t == "raw_material": return f'{r["material_id"]} · {short(r.get("type"),16)}'
    return str(r[PK[t]])

def props(t, r):
    if t == "coil":         return {"grade": r.get("grade"), "thickness_mm": r.get("thickness_mm"), "status": r.get("status")}
    if t == "equipment":    return {"machine_type": r.get("type"), "location": short(r.get("location"),34), "maintenance": r.get("maintenance_interval")}
    if t == "failure":      return {"mode": r.get("failure_mode"), "equipment": r.get("equipment_id"), "when": short(r.get("timestamp"),19)}
    if t == "rca":          return {"procedure": r.get("procedure_ref"), "cause": short(r.get("root_cause_text"),60)}
    if t == "quality_test": return {"fault": r.get("fault_type"), "coil": r.get("coil_id"), "standard": r.get("standard_ref")}
    if t == "deviation":    return {"severity": r.get("severity"), "desc": short(r.get("description"),50)}
    if t == "standard":     return {"name": short(r.get("name"),50), "superseded_by": r.get("superseded_by")}
    if t == "technician":   return {"role": r.get("role"), "shift": r.get("shift"), "cert": short(r.get("certification"),28)}
    if t == "procedure":    return {"title": short(r.get("title"),44), "equipment": r.get("equipment_ref")}
    if t == "raw_material": return {"material": r.get("type"), "supplier": r.get("supplier_id")}
    if t == "document":     return {"doc_type": r.get("doc_type"), "source": r.get("source_type"), "about": r.get("related_entity_id")}
    return {}

nodes, by_type = {}, {}
for t in NODE_FILES:
    recs = j(t, N); by_type[LABEL[t]] = len(recs)
    for r in recs:
        nid = str(r[PK[t]])
        nodes[nid] = {"id": nid, "label": disp(t, r), "type": LABEL[t], "degree": 0, "props": props(t, r)}

edges, rel_by_type, schema_pairs = [], {}, defaultdict(Counter)
for fn in REL_FILES:
    recs = j(fn, R); rel_by_type[TYPE_OF[fn]] = len(recs)
    for e in recs:
        s = str(e["from"]["key"]); t = str(e["to"]["key"])
        edges.append({"s": s, "t": t, "type": TYPE_OF[fn]})
        schema_pairs[TYPE_OF[fn]][(e["from"]["label"], e["to"]["label"])] += 1
        if s in nodes: nodes[s]["degree"] += 1
        if t in nodes: nodes[t]["degree"] += 1

top = sorted(nodes.values(), key=lambda n: n["degree"], reverse=True)[:8]
top_degree = [{"id": n["id"], "label": n["label"], "type": n["type"], "degree": n["degree"]} for n in top]
# emit EVERY distinct (from -> to) shape per relationship type (matches the Neo4j
# DISTINCT labels(a)-[type(r)]->labels(b) ground truth), not just the dominant pair
schema = [{"type": rt, "from": frm, "to": to, "count": cnt}
          for rt, c in schema_pairs.items() for (frm, to), cnt in c.items()]
schema.sort(key=lambda e: (e["from"], e["type"], e["to"]))

out = {"stats": {"node_total": len(nodes), "edge_total": len(edges), "type_count": len(NODE_FILES),
                 "by_type": by_type, "rel_by_type": rel_by_type, "top_degree": top_degree},
       "schema": schema, "nodes": list(nodes.values()), "edges": edges}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print(f"wrote {OUT}  ({len(nodes)} nodes, {len(edges)} edges, {os.path.getsize(OUT)/1024:.0f}KB)")
