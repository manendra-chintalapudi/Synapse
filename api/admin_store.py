"""
Admin Console data-management backend: structured row additions + unstructured uploads.

STRUCTURED: add_structured(entity_type, record)
    Validates required fields + FK targets, INSERTs the row into the correct DuckDB
    system table, MERGEs the Neo4j node, and creates the ontology-defined relationships
    (PRODUCED_AT, MADE_FROM, TESTED_BY, TESTED_AGAINST, HAS_DEVIATION, EXPERIENCED,
    DIAGNOSED_BY, PERFORMED_BY, FOLLOWS_PROCEDURE) so additions never bypass the graph.
    No new labels or relationship types -- everything flows through the locked ontology.
    NOTE: FAILED_STANDARD is intentionally NOT created here; that edge is reserved for
    deviation-linked quality tests (integrity invariant). New tests get TESTED_AGAINST.

UNSTRUCTURED: extract_entities(text) + commit_document(...)
    Runs the entity-index extraction (known IDs + names from the ontology, standard
    aliases, dates) against uploaded text, and -- after human confirmation -- creates the
    Document node, links DOCUMENTED_IN where the ontology allows it (Failure/Deviation
    sources only), chunks the text, and adds the chunks to the LIVE Chroma vectorstore so
    the content is immediately queryable in chat.
"""
import base64
import io
import json
import re
import sys
import threading
from datetime import date
from pathlib import Path

SYNAPSE_ROOT = Path(__file__).resolve().parent.parent
for _p in (SYNAPSE_ROOT / "retrieval", SYNAPSE_ROOT / "embeddings"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from graph_store import query_graph, get_driver          # retrieval/graph_store.py
from structured_store import execute_write               # retrieval/structured_store.py

# ---------------------------------------------------------------------------
# entity registry: form fields, DuckDB target, Neo4j label/pk, relationship wiring
# rel spec: (fk_field, rel_type, direction, target_label, target_pk)
#           direction "in"  => (Target)-[REL]->(This)
#           direction "out" => (This)-[REL]->(Target)
# ---------------------------------------------------------------------------
ENTITIES = {
    "Coil": {
        "duckdb": ("erp", "coils"),
        "pk": "coil_id",
        "fields": [
            {"name": "coil_id", "label": "Coil ID", "required": True, "placeholder": "C10401"},
            {"name": "grade", "label": "Grade", "required": True, "placeholder": "IS2062-E250"},
            {"name": "thickness_mm", "label": "Thickness (mm)", "type": "number"},
            {"name": "width_mm", "label": "Width (mm)", "type": "number"},
            {"name": "weight_kg", "label": "Weight (kg)", "type": "number"},
            {"name": "heat_number", "label": "Heat number", "placeholder": "H2026-0201"},
            {"name": "production_date", "label": "Production date", "type": "date"},
            {"name": "status", "label": "Status", "options": ["in_stock", "dispatched", "on_hold", "scrapped"]},
            {"name": "equipment_id", "label": "Produced at (Equipment ID)", "required": True, "fk": "Equipment"},
            {"name": "material_ids", "label": "Made from (Material IDs, comma-sep)", "fk_list": "RawMaterial"},
        ],
        "rels": [("equipment_id", "PRODUCED_AT", "out", "Equipment", "equipment_id"),
                 ("material_ids", "MADE_FROM", "out_list", "RawMaterial", "material_id")],
    },
    "Equipment": {
        "duckdb": ("scada", "equipment"),
        "pk": "equipment_id",
        "fields": [
            {"name": "equipment_id", "label": "Equipment ID", "required": True, "placeholder": "EQ-XXX-01"},
            {"name": "name", "label": "Name", "required": True},
            {"name": "type", "label": "Machine type", "placeholder": "coiler_unit"},
            {"name": "installed_date", "label": "Installed date", "type": "date"},
            {"name": "location", "label": "Location", "placeholder": "Rajendra Steel Plant, Mumbai Unit - ..."},
            {"name": "maintenance_interval", "label": "Maintenance interval",
             "options": ["monthly", "quarterly", "6-monthly", "annual"]},
        ],
        "rels": [],
    },
    "QualityTest": {
        "duckdb": ("qms", "quality_tests"),
        "pk": "test_id",
        "fields": [
            {"name": "test_id", "label": "Test ID", "required": True, "placeholder": "QT11942"},
            {"name": "coil_id", "label": "Coil ID", "required": True, "fk": "Coil"},
            {"name": "fault_type", "label": "Fault type", "placeholder": "coating_irregularity"},
            {"name": "test_date", "label": "Test date", "type": "date"},
            {"name": "standard_ref", "label": "Standard tested against", "required": True, "fk": "Standard"},
        ],
        "rels": [("coil_id", "TESTED_BY", "in", "Coil", "coil_id"),
                 ("standard_ref", "TESTED_AGAINST", "out", "Standard", "standard_id")],
    },
    "Deviation": {
        "duckdb": ("qms", "deviations"),
        "pk": "deviation_id",
        "fields": [
            {"name": "deviation_id", "label": "Deviation ID", "required": True, "placeholder": "DEV1665"},
            {"name": "coil_id_fk", "label": "Coil (if coil-side)", "fk": "Coil"},
            {"name": "equipment_id_fk", "label": "Equipment (if equipment-side)", "fk": "Equipment"},
            {"name": "failure_id_fk", "label": "Linked failure (optional)", "fk": "Failure"},
            {"name": "description", "label": "Description", "required": True, "type": "textarea"},
            {"name": "severity", "label": "Severity", "options": ["low", "medium", "high"]},
        ],
        "rels": [("coil_id_fk", "HAS_DEVIATION", "in", "Coil", "coil_id"),
                 ("equipment_id_fk", "HAS_DEVIATION", "in", "Equipment", "equipment_id")],
    },
    "Failure": {
        "duckdb": ("cmms", "failures"),
        "pk": "failure_id",
        "fields": [
            {"name": "failure_id", "label": "Failure ID", "required": True, "placeholder": "F1201"},
            {"name": "equipment_id", "label": "Equipment ID", "required": True, "fk": "Equipment"},
            {"name": "failure_mode", "label": "Failure mode", "placeholder": "power_failure"},
            {"name": "timestamp", "label": "Timestamp", "type": "datetime", "placeholder": "2026-07-11 14:30:00"},
        ],
        "rels": [("equipment_id", "EXPERIENCED", "in", "Equipment", "equipment_id")],
    },
    "RCA": {
        "duckdb": ("cmms", "rca"),
        "pk": "rca_id",
        "fields": [
            {"name": "rca_id", "label": "RCA ID", "required": True, "placeholder": "RCA1201"},
            {"name": "failure_id", "label": "Failure ID", "required": True, "fk": "Failure"},
            {"name": "rca_date", "label": "RCA date", "type": "date"},
            {"name": "root_cause_text", "label": "Root cause", "required": True, "type": "textarea"},
            {"name": "corrective_action", "label": "Corrective action", "type": "textarea"},
            {"name": "procedure_ref", "label": "Violated procedure (optional)", "fk": "Procedure"},
            {"name": "violated_step", "label": "Violated step (quote it)"},
            {"name": "analyst", "label": "Analyst (Technician ID)", "required": True, "fk": "Technician"},
        ],
        "rels": [("failure_id", "DIAGNOSED_BY", "in", "Failure", "failure_id"),
                 ("analyst", "PERFORMED_BY", "out", "Technician", "technician_id")],
    },
    "Technician": {
        "duckdb": ("cmms", "technicians"),
        "pk": "technician_id",
        "fields": [
            {"name": "technician_id", "label": "Technician ID", "required": True, "placeholder": "T1026"},
            {"name": "name", "label": "Name", "required": True},
            {"name": "role", "label": "Role",
             "options": ["maintenance_technician", "equipment_engineer", "quality_inspector"]},
            {"name": "shift", "label": "Shift", "options": ["A", "B", "C"]},
            {"name": "certification", "label": "Certification"},
        ],
        "rels": [],
    },
    "Procedure": {
        "duckdb": ("cmms", "procedures"),
        "pk": "procedure_id",
        "fields": [
            {"name": "procedure_id", "label": "Procedure ID", "required": True, "placeholder": "PROC-032"},
            {"name": "title", "label": "Title", "required": True},
            {"name": "steps_text", "label": "Steps", "type": "textarea"},
            {"name": "equipment_ref", "label": "Governs equipment", "required": True, "fk": "Equipment"},
        ],
        "rels": [("equipment_ref", "FOLLOWS_PROCEDURE", "in", "Equipment", "equipment_id")],
    },
    "RawMaterial": {
        "duckdb": ("erp", "raw_materials"),
        "pk": "material_id",
        "fields": [
            {"name": "material_id", "label": "Material ID", "required": True, "placeholder": "RM1041"},
            {"name": "type", "label": "Material type", "required": True, "placeholder": "iron_ore"},
            {"name": "supplier_id", "label": "Supplier ID", "placeholder": "SUP-011"},
        ],
        "rels": [],
    },
    "Standard": {
        "duckdb": ("qms", "standards"),
        "pk": "standard_id",
        "fields": [
            {"name": "standard_id", "label": "Standard ID", "required": True, "placeholder": "STD-IS2062-05"},
            {"name": "name", "label": "Name", "required": True},
            {"name": "clause_text", "label": "Clause text", "type": "textarea"},
        ],
        "rels": [],
    },
}

_PK_OF = {"Equipment": "equipment_id", "Coil": "coil_id", "RawMaterial": "material_id",
          "Standard": "standard_id", "Failure": "failure_id", "Technician": "technician_id",
          "Procedure": "procedure_id", "Deviation": "deviation_id", "RCA": "rca_id",
          "QualityTest": "test_id", "Document": "document_id"}


def schema_for_ui():
    """Field specs per entity type for the Admin UI form builder."""
    return {name: {"pk": spec["pk"], "fields": spec["fields"]} for name, spec in ENTITIES.items()}


def _node_exists(label, pk, value):
    rows = query_graph(f"MATCH (n:{label} {{{pk}: $v}}) RETURN count(n) AS c", {"v": value})
    return bool(rows and rows[0]["c"])


def add_structured(entity_type: str, record: dict) -> dict:
    """Validate -> DuckDB INSERT -> Neo4j MERGE node + ontology relationships."""
    spec = ENTITIES.get(entity_type)
    if spec is None:
        raise ValueError(f"unknown entity type: {entity_type}")
    pk = spec["pk"]

    # ---- validate ----
    clean = {}
    for f in spec["fields"]:
        v = record.get(f["name"])
        if isinstance(v, str):
            v = v.strip()
        if f["name"] == "material_ids" and isinstance(v, str):
            v = [m.strip() for m in v.split(",") if m.strip()]
        if f.get("required") and not v:
            raise ValueError(f"missing required field: {f['name']}")
        if v not in (None, "", []):
            clean[f["name"]] = v
    if _node_exists(entity_type, pk, clean[pk]):
        raise ValueError(f"{entity_type} {clean[pk]} already exists")
    for fk_field, _rel, _dir, target, target_pk in spec["rels"]:
        vals = clean.get(fk_field)
        if not vals:
            continue
        for v in (vals if isinstance(vals, list) else [vals]):
            if not _node_exists(target, target_pk, v):
                raise ValueError(f"{fk_field}: {target} '{v}' not found in the graph")
    if entity_type == "Deviation" and not (clean.get("coil_id_fk") or clean.get("equipment_id_fk")):
        raise ValueError("a deviation needs a coil_id_fk or an equipment_id_fk")

    # ---- DuckDB insert (bridge-table handling for coil materials) ----
    cat, table = spec["duckdb"]
    cols = [f["name"] for f in spec["fields"] if f["name"] in clean and f["name"] != "material_ids"]
    execute_write(
        f"INSERT INTO {cat}.main.{table} ({', '.join(cols)}) "
        f"VALUES ({', '.join('?' for _ in cols)})",
        [clean[c] for c in cols])
    if entity_type == "Coil":
        for mid in clean.get("material_ids", []):
            execute_write("INSERT INTO erp.main.coil_materials VALUES (?, ?)", [clean[pk], mid])

    # ---- Neo4j node + relationships ----
    props = {k: v for k, v in clean.items() if k != "material_ids"}
    if "material_ids" in clean:
        props["material_ids"] = clean["material_ids"]        # list of primitives is fine
    rels_created = []
    with get_driver().session() as s:
        s.run(f"MERGE (n:{entity_type} {{{pk}: $pk}}) SET n += $props",
              pk=clean[pk], props=props)
        for fk_field, rel, direction, target, target_pk in spec["rels"]:
            vals = clean.get(fk_field)
            if not vals:
                continue
            for v in (vals if isinstance(vals, list) else [vals]):
                if direction in ("out", "out_list"):
                    cy = (f"MATCH (a:{entity_type} {{{pk}: $a}}), (b:{target} {{{target_pk}: $b}}) "
                          f"MERGE (a)-[:{rel}]->(b)")
                else:
                    cy = (f"MATCH (a:{entity_type} {{{pk}: $a}}), (b:{target} {{{target_pk}: $b}}) "
                          f"MERGE (b)-[:{rel}]->(a)")
                s.run(cy, a=clean[pk], b=v)
                rels_created.append(f"{rel}->{v}" if direction.startswith("out") else f"{v}-{rel}->")
    return {"entity_type": entity_type, "id": clean[pk],
            "duckdb_table": f"{cat}.main.{table}", "relationships": rels_created}


def delete_structured(entity_type: str, entity_id: str) -> dict:
    """Admin undo/cleanup: remove a row + its node (DETACH). Used by tests and mistakes."""
    spec = ENTITIES.get(entity_type)
    if spec is None:
        raise ValueError(f"unknown entity type: {entity_type}")
    cat, table = spec["duckdb"]
    execute_write(f"DELETE FROM {cat}.main.{table} WHERE {spec['pk']} = ?", [entity_id])
    if entity_type == "Coil":
        execute_write("DELETE FROM erp.main.coil_materials WHERE coil_id = ?", [entity_id])
    with get_driver().session() as s:
        s.run(f"MATCH (n:{entity_type} {{{spec['pk']}: $id}}) DETACH DELETE n", id=entity_id)
    return {"deleted": entity_id}


# ---------------------------------------------------------------------------
# unstructured: text extraction -> entity detection -> confirmed commit
# ---------------------------------------------------------------------------
_index_lock = threading.Lock()
_entity_index = None

_STANDARD_ALIASES = [
    (re.compile(r"\bIS[\s:]*2062\b", re.I), "IS 2062"),
    (re.compile(r"\bIS[\s:]*1786\b", re.I), "IS 1786"),
    (re.compile(r"\bASTM\s*A\s*370\b", re.I), "ASTM A370"),
    (re.compile(r"\bFactories\s+Act\b", re.I), "Factories Act"),
]
_DATE_RX = re.compile(r"\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2})\b")
DOC_TYPES = ["work_order", "rca_report", "deviation_report", "inspection_report",
             "sop", "equipment_manual", "standard_reference"]
# ontology-allowed DOCUMENTED_IN sources per doc_type (Failure/Deviation only)
_DOC_LINK_LABEL = {"work_order": "Failure", "rca_report": "Failure",
                   "deviation_report": "Deviation", "inspection_report": "Deviation"}


def _build_entity_index():
    """Known IDs + display names from ontology/nodes/*.json (same corpus the router indexes)."""
    idx = []
    nodes_dir = SYNAPSE_ROOT / "ontology" / "nodes"
    name_field = {"equipment": "name", "technician": "name", "procedure": "title", "standard": "name"}
    for path in nodes_dir.glob("*.json"):
        stem = path.stem
        label = {"raw_material": "RawMaterial", "quality_test": "QualityTest",
                 "rca": "RCA"}.get(stem, stem.title().replace("_", ""))
        pk = _PK_OF.get(label)
        if pk is None:
            continue
        try:
            recs = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for r in recs:
            ent = {"id": str(r.get(pk)), "label": label}
            nf = name_field.get(stem)
            if nf and r.get(nf):
                ent["name"] = str(r[nf])
            idx.append(ent)
    return idx


def _get_index():
    global _entity_index
    with _index_lock:
        if _entity_index is None:
            _entity_index = _build_entity_index()
        return _entity_index


def decode_upload(filename: str, content_base64: str) -> str:
    """Base64 upload -> plain text. txt/md decoded directly; PDFs via pypdf."""
    raw = base64.b64decode(content_base64)
    ext = Path(filename).suffix.lower()
    if ext in (".txt", ".md", ".text", ".log", ".csv"):
        return raw.decode("utf-8", errors="replace")
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("PDF support requires the 'pypdf' package on the server") from exc
        reader = PdfReader(io.BytesIO(raw))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        if not text.strip():
            raise ValueError("no extractable text in this PDF (scanned image? OCR not available)")
        return text
    raise ValueError(f"unsupported file type '{ext}' — upload .txt, .md, or .pdf")


def extract_entities(text: str) -> dict:
    """Scan uploaded text for known entity IDs/names, standard references, and dates.
    Same index-first approach as the router's tier-1 matching."""
    found, seen = [], set()
    low = text.lower()
    for ent in _get_index():
        hit = None
        eid = ent["id"]
        if re.search(rf"\b{re.escape(eid)}\b", text, re.IGNORECASE):
            hit = eid
        elif ent.get("name") and len(ent["name"]) >= 6 and ent["name"].lower() in low:
            hit = ent["name"]
        if hit and (ent["label"], eid) not in seen:
            seen.add((ent["label"], eid))
            found.append({"id": eid, "label": ent["label"],
                          "name": ent.get("name", ""), "matched_on": hit})
    for rx, alias in _STANDARD_ALIASES:
        if rx.search(text) and not any(f["label"] == "Standard" and alias in f.get("name", "")
                                       for f in found):
            found.append({"id": alias, "label": "StandardFamily", "name": alias,
                          "matched_on": alias})
    dates = sorted(set(_DATE_RX.findall(text)))[:6]
    # suggested primary link: first Failure, else first Deviation, else first anything
    primary = next((f for f in found if f["label"] == "Failure"),
                   next((f for f in found if f["label"] == "Deviation"),
                        found[0] if found else None))
    return {"entities": found, "dates": dates,
            "suggested_related": primary["id"] if primary else "",
            "chars": len(text)}


def _chunk(text, target_words=220, overlap=30):
    words = text.split()
    if not words:
        return []
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i:i + target_words]))
        i += target_words - overlap
    return chunks


def next_document_id() -> str:
    rows = query_graph(
        "MATCH (d:Document) WHERE d.document_id STARTS WITH 'DOC' "
        "RETURN max(toInteger(substring(d.document_id, 3))) AS mx")
    mx = rows[0]["mx"] if rows and rows[0]["mx"] is not None else 1000
    return f"DOC{mx + 1}"


def commit_document(filename: str, title: str, doc_type: str, related_entity_id: str,
                    text: str, confirmed_entities: list) -> dict:
    """Human-confirmed commit: Document node -> ontology link -> chunks -> LIVE Chroma."""
    if doc_type not in DOC_TYPES:
        raise ValueError(f"doc_type must be one of {DOC_TYPES}")
    doc_id = next_document_id()
    rel_path = f"data/unstructured/documents/uploads/{doc_id}.md"

    # persist the source (best effort -- ephemeral on Railway, canonical copy is in Chroma)
    try:
        out = SYNAPSE_ROOT / "data" / "unstructured" / "documents" / "uploads"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{doc_id}.md").write_text(text, encoding="utf-8")
    except Exception:
        pass

    linked = None
    with get_driver().session() as s:
        s.run("""
            MERGE (d:Document {document_id: $id})
            SET d.title = $title, d.doc_type = $dt, d.vector_ref = $vr,
                d.related_entity_id = $re, d.source_type = 'uploaded',
                d.uploaded_from = $fn, d.upload_date = $today,
                d.mentioned_entities = $ents
        """, id=doc_id, title=title, dt=doc_type, vr=rel_path,
             re=related_entity_id or "", fn=filename, today=date.today().isoformat(),
             ents=[e for e in (confirmed_entities or [])][:40])
        # DOCUMENTED_IN only where the locked ontology allows (Failure/Deviation -> Document)
        src_label = _DOC_LINK_LABEL.get(doc_type)
        if src_label and related_entity_id:
            pk = _PK_OF[src_label]
            r = s.run(f"MATCH (a:{src_label} {{{pk}: $a}}), (d:Document {{document_id: $d}}) "
                      f"MERGE (a)-[:DOCUMENTED_IN]->(d) RETURN count(*) AS c",
                      a=related_entity_id, d=doc_id).single()
            if r and r["c"]:
                linked = f"({src_label} {related_entity_id})-[:DOCUMENTED_IN]->({doc_id})"

    # chunk + embed into the SAME vectorstore instance chat searches -> instantly queryable
    from search import _store
    chunks = _chunk(text)
    ids = [f"{doc_id}_chunk{i+1}" for i in range(len(chunks))]
    metadatas = [{"chunk_id": cid, "source_document_id": doc_id, "doc_type": doc_type,
                  "source_type": "uploaded"} for cid in ids]
    _store().add_texts(chunks, metadatas=metadatas, ids=ids)

    return {"document_id": doc_id, "chunks": len(chunks), "linked": linked,
            "vector_ref": rel_path}


def delete_document(doc_id: str) -> dict:
    """Cleanup/undo: remove the Document node, its Chroma chunks, and the saved file."""
    with get_driver().session() as s:
        s.run("MATCH (d:Document {document_id: $id}) DETACH DELETE d", id=doc_id)
    from search import _store
    try:
        got = _store()._collection.get(where={"source_document_id": doc_id})
        if got and got.get("ids"):
            _store()._collection.delete(ids=got["ids"])
            removed = len(got["ids"])
        else:
            removed = 0
    except Exception:
        removed = -1
    try:
        (SYNAPSE_ROOT / "data" / "unstructured" / "documents" / "uploads" / f"{doc_id}.md").unlink()
    except Exception:
        pass
    return {"deleted": doc_id, "chunks_removed": removed}
