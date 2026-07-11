"""
Structured retrieval layer: federated SQL over the plant's four source systems, executed
DIRECTLY with DuckDB (no separate Trino service).

DuckDB ATTACHes the four per-system DuckDB files as separate catalogs, so a single SQL string
can join across all four systems using the SAME three-part `catalog.main.table` naming the
Trino version used (e.g. `erp.main.coils JOIN scada.main.equipment`). SQL semantics are
identical to the previous Trino implementation — only the connection/execution layer changed,
which removes the Trino dependency for deployment (Railway / Vercel / Neo4j AuraDB).

    erp    -> erp.duckdb    (coils, coil_materials, raw_materials)
    scada  -> scada.duckdb  (equipment)
    qms    -> qms.duckdb    (quality_tests, deviations, standards)
    cmms   -> cmms.duckdb   (failures, rca, technicians, procedures)

The DuckDB files are read from DUCKDB_DIR (env var), defaulting to synapse/data/duckdb — point
it at a mounted-volume path in production if the files live there instead of in the image.

query_federated(sql) is what the router's structured_retrieval calls; one persistent in-memory
connection ATTACHes all four files once and per-query cursors keep concurrent reads (the
retrieval fan-out) safe.
"""
import os
import threading
import time
from pathlib import Path

import duckdb

_SYNAPSE_ROOT = Path(__file__).resolve().parent.parent          # -> synapse/
DUCKDB_DIR = os.environ.get("DUCKDB_DIR", str(_SYNAPSE_ROOT / "data" / "duckdb"))

CATALOGS = {
    "erp": ["coils", "coil_materials", "raw_materials"],
    "scada": ["equipment"],
    "qms": ["quality_tests", "deviations", "standards"],
    "cmms": ["failures", "rca", "technicians", "procedures"],
}

_conn = None
_lock = threading.Lock()


def _catalog_path(cat: str) -> str:
    return os.path.join(DUCKDB_DIR, f"{cat}.duckdb")


def get_connection():
    """Lazily create ONE in-memory DuckDB connection with all four files ATTACHed read-only.
    Reused for the process lifetime; per-query cursors keep concurrent reads safe. Lazy (not at
    import) so a missing/locked file surfaces on first query rather than breaking app startup."""
    global _conn
    if _conn is not None:
        return _conn
    with _lock:
        if _conn is not None:                       # double-checked under the lock
            return _conn
        con = duckdb.connect(":memory:")
        for cat in CATALOGS:
            path = _catalog_path(cat)
            for attempt in range(6):                # tolerate a transient OS file lock
                try:
                    con.execute(f"ATTACH '{path}' AS {cat} (READ_ONLY)")
                    break
                except duckdb.IOException:
                    if attempt == 5:
                        raise
                    time.sleep(0.8)
        _conn = con
        return _conn


def query_federated(sql: str) -> list:
    """Run arbitrary federated SQL across the erp/scada/qms/cmms catalogs.

    Returns a list of dicts (column name -> value), one per row. Raises on SQL errors --
    callers (the retrieval layer) decide how to surface failures. A fresh cursor per call
    (created under a short lock) makes concurrent reads from the retrieval fan-out safe."""
    con = get_connection()
    with _lock:
        cur = con.cursor()
    cur.execute(sql)
    columns = [d[0] for d in cur.description] if cur.description else []
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def health_check() -> dict:
    """Confirm every catalog is attached and exposes its expected tables; returns
    {catalog: {tables, missing}}."""
    con = get_connection()
    out = {}
    for cat, tables in CATALOGS.items():
        rows = con.cursor().execute(
            "SELECT table_name FROM information_schema.tables WHERE table_catalog = ?", [cat]
        ).fetchall()
        found = {r[0] for r in rows}
        out[cat] = {"tables": len(found), "missing": [t for t in tables if t not in found]}
    return out


if __name__ == "__main__":
    print("health:", health_check())
    demo = query_federated(
        "SELECT c.coil_id, c.grade, e.name AS equipment_name, COUNT(qt.test_id) AS tests "
        "FROM erp.main.coils c "
        "JOIN scada.main.equipment e ON c.equipment_id = e.equipment_id "
        "LEFT JOIN qms.main.quality_tests qt ON qt.coil_id = c.coil_id "
        "GROUP BY c.coil_id, c.grade, e.name ORDER BY tests DESC LIMIT 3"
    )
    for row in demo:
        print(row)
