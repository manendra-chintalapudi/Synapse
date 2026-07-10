"""
Structured retrieval layer: federated SQL over the plant's four source systems via Trino.

Trino (container `synapse-trino`, http://localhost:8080) federates the four per-system
DuckDB files as separate catalogs using the OFFICIAL Trino DuckDB connector
(connector.name=duckdb, catalog properties in synapse/trino/catalog/):

    erp.main    -- coils, coil_materials, raw_materials
    scada.main  -- equipment
    qms.main    -- quality_tests, deviations, standards
    cmms.main   -- failures, rca, technicians, procedures

query_federated(sql) is what the router's structured_retrieval_node calls going forward --
one SQL string can join across all four systems (e.g. erp.main.coils JOIN
scada.main.equipment JOIN qms.main.quality_tests) instead of connecting to individual
DuckDB files directly.
"""
import os

import trino

TRINO_HOST = os.environ.get("TRINO_HOST", "localhost")
TRINO_PORT = int(os.environ.get("TRINO_PORT", "8080"))
TRINO_USER = os.environ.get("TRINO_USER", "synapse")

CATALOGS = {
    "erp": ["coils", "coil_materials", "raw_materials"],
    "scada": ["equipment"],
    "qms": ["quality_tests", "deviations", "standards"],
    "cmms": ["failures", "rca", "technicians", "procedures"],
}


def get_connection():
    return trino.dbapi.connect(host=TRINO_HOST, port=TRINO_PORT, user=TRINO_USER)


def query_federated(sql: str) -> list:
    """Run arbitrary federated SQL across the erp/scada/qms/cmms catalogs.

    Returns a list of dicts (column name -> value), one per row. Raises on SQL errors --
    callers (the retrieval node) decide how to surface failures."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        columns = [d[0] for d in cur.description] if cur.description else []
        return [dict(zip(columns, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def health_check() -> dict:
    """Confirm every catalog answers a trivial query; returns {catalog: table_count}."""
    out = {}
    for cat, tables in CATALOGS.items():
        rows = query_federated(f"SHOW TABLES FROM {cat}.main")
        found = {r["Table"] for r in rows}
        missing = [t for t in tables if t not in found]
        out[cat] = {"tables": len(found), "missing": missing}
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
