"""
Build per-system DuckDB databases from the ontology node JSON files.

These DuckDB files are a PARALLEL, read-optimized representation for the
direct federated-SQL layer. The ontology/nodes/*.json files remain the source of
truth for Neo4j and are only READ here, never modified.

Nested JSON fields (composition, feature_values, sensor_values) are stored as
DuckDB's native JSON column type. The coil<->material relationship (originally the
material_ids array on each coil) is normalized into a separate bridge table
coil_materials(coil_id, material_id), one row per pair, so the federation layer can
push the join down cleanly. Scalars use VARCHAR / DOUBLE / DATE / TIMESTAMP.

Layout:
  data/duckdb/erp.duckdb   : coils, coil_materials, raw_materials
  data/duckdb/scada.duckdb : equipment, ai4i_events (official synthetic reference)
  data/duckdb/qms.duckdb   : quality_tests, deviations, standards
  data/duckdb/cmms.duckdb  : failures, rca, technicians, procedures
"""
import json
import os

import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
NODES = os.path.join(ROOT, "ontology", "nodes")
AI4I_CSV = os.path.join(ROOT, "data", "scada", "reference_data", "ai4i2020.csv")


def load(name):
    with open(os.path.join(NODES, name + ".json"), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Column specifications: (json_field_name, duckdb_type)
# JSON type -> value is json.dumps()'d before binding and cast in the INSERT.
# DATE/TIMESTAMP -> ISO string in source, cast in the INSERT.
# ---------------------------------------------------------------------------
SCHEMAS = {
    "coils": ("coil", [
        ("coil_id", "VARCHAR"), ("grade", "VARCHAR"), ("thickness_mm", "DOUBLE"),
        ("width_mm", "DOUBLE"), ("weight_kg", "DOUBLE"), ("heat_number", "VARCHAR"),
        ("production_date", "DATE"), ("status", "VARCHAR"), ("equipment_id", "VARCHAR"),
        # material_ids intentionally omitted here -> normalized into the
        # coil_materials bridge table (see build_coil_materials).
    ]),
    "raw_materials": ("raw_material", [
        ("material_id", "VARCHAR"), ("type", "VARCHAR"), ("composition", "JSON"),
        ("supplier_id", "VARCHAR"),
    ]),
    "equipment": ("equipment", [
        ("equipment_id", "VARCHAR"), ("name", "VARCHAR"), ("type", "VARCHAR"),
        ("installed_date", "DATE"), ("location", "VARCHAR"), ("real_data_link", "VARCHAR"),
        ("key_specifications", "JSON"), ("typical_failure_modes", "JSON"),
        ("maintenance_interval", "VARCHAR"),
    ]),
    "quality_tests": ("quality_test", [
        ("test_id", "VARCHAR"), ("coil_id", "VARCHAR"), ("feature_values", "JSON"),
        ("fault_type", "VARCHAR"), ("test_date", "DATE"), ("standard_ref", "VARCHAR"),
    ]),
    "deviations": ("deviation", [
        ("deviation_id", "VARCHAR"), ("coil_id_fk", "VARCHAR"), ("equipment_id_fk", "VARCHAR"),
        ("failure_id_fk", "VARCHAR"), ("description", "VARCHAR"), ("severity", "VARCHAR"),
    ]),
    "standards": ("standard", [
        ("standard_id", "VARCHAR"), ("name", "VARCHAR"), ("clause_text", "VARCHAR"),
        ("superseded_by", "VARCHAR"),
    ]),
    "failures": ("failure", [
        ("failure_id", "VARCHAR"), ("equipment_id", "VARCHAR"), ("failure_mode", "VARCHAR"),
        ("timestamp", "TIMESTAMP"), ("sensor_values", "JSON"),
        ("impacted_coil_ids", "JSON"), ("impacted_failed_tests", "INTEGER"),
    ]),
    "rca": ("rca", [
        ("rca_id", "VARCHAR"), ("failure_id", "VARCHAR"), ("rca_date", "DATE"),
        ("root_cause_text", "VARCHAR"), ("corrective_action", "VARCHAR"),
        ("procedure_ref", "VARCHAR"), ("violated_step", "VARCHAR"), ("analyst", "VARCHAR"),
    ]),
    "technicians": ("technician", [
        ("technician_id", "VARCHAR"), ("name", "VARCHAR"), ("role", "VARCHAR"),
        ("shift", "VARCHAR"), ("certification", "VARCHAR"),
    ]),
    "procedures": ("procedure", [
        ("procedure_id", "VARCHAR"), ("title", "VARCHAR"), ("steps_text", "VARCHAR"),
        ("equipment_ref", "VARCHAR"),
    ]),
}

# which tables live in which database file
DB_TABLES = {
    "erp.duckdb": ["coils", "coil_materials", "raw_materials"],
    "scada.duckdb": ["equipment", "ai4i_events"],
    "qms.duckdb": ["quality_tests", "deviations", "standards"],
    "cmms.duckdb": ["failures", "rca", "technicians", "procedures"],
}


def placeholder(sqltype):
    if sqltype in ("DATE", "TIMESTAMP", "JSON"):
        return f"CAST(? AS {sqltype})"
    return "?"


def build_table(con, table):
    source_name, columns = SCHEMAS[table]
    records = load(source_name)

    col_defs = ", ".join(f'"{n}" {t}' for n, t in columns)
    con.execute(f'DROP TABLE IF EXISTS "{table}"')
    con.execute(f'CREATE TABLE "{table}" ({col_defs})')

    placeholders = ", ".join(placeholder(t) for _, t in columns)
    insert_sql = f'INSERT INTO "{table}" VALUES ({placeholders})'

    rows = []
    for rec in records:
        row = []
        for name, sqltype in columns:
            val = rec.get(name)
            if sqltype == "JSON" and val is not None:
                val = json.dumps(val)
            row.append(val)
        rows.append(row)
    con.executemany(insert_sql, rows)
    return len(records)


def build_coil_materials(con):
    """Bridge table: unnest coil.material_ids into one row per (coil_id, material_id)."""
    coils = load("coil")
    con.execute('DROP TABLE IF EXISTS "coil_materials"')
    con.execute('CREATE TABLE "coil_materials" ("coil_id" VARCHAR, "material_id" VARCHAR)')
    rows = []
    for c in coils:
        for mid in (c.get("material_ids") or []):
            rows.append([c["coil_id"], mid])
    con.executemany('INSERT INTO "coil_materials" VALUES (?, ?)', rows)
    return len(rows)


def build_ai4i_events(con):
    """Load the official UCI AI4I synthetic reference with stable column names."""
    con.execute('DROP TABLE IF EXISTS "ai4i_events"')
    con.execute("""
        CREATE TABLE ai4i_events AS
        SELECT
          CAST("UDI" AS INTEGER) AS uid,
          CAST("Product ID" AS VARCHAR) AS product_id,
          CAST("Type" AS VARCHAR) AS product_type,
          CAST("Air temperature [K]" AS DOUBLE) AS air_temperature_k,
          CAST("Process temperature [K]" AS DOUBLE) AS process_temperature_k,
          CAST("Rotational speed [rpm]" AS INTEGER) AS rotational_speed_rpm,
          CAST("Torque [Nm]" AS DOUBLE) AS torque_nm,
          CAST("Tool wear [min]" AS INTEGER) AS tool_wear_min,
          CAST("Machine failure" AS INTEGER) AS machine_failure,
          CAST("TWF" AS INTEGER) AS tool_wear_failure,
          CAST("HDF" AS INTEGER) AS heat_dissipation_failure,
          CAST("PWF" AS INTEGER) AS power_failure,
          CAST("OSF" AS INTEGER) AS overstrain_failure,
          CAST("RNF" AS INTEGER) AS random_failure
        FROM read_csv_auto(?)
    """, [AI4I_CSV])
    return con.execute("SELECT COUNT(*) FROM ai4i_events").fetchone()[0]


# tables that are derived/normalized rather than loaded 1:1 from a node file
CUSTOM_BUILDERS = {"coil_materials": build_coil_materials, "ai4i_events": build_ai4i_events}


def build_all():
    os.makedirs(HERE, exist_ok=True)
    built = {}
    for db_file, tables in DB_TABLES.items():
        path = os.path.join(HERE, db_file)
        if os.path.exists(path):
            os.remove(path)  # rebuild cleanly
        con = duckdb.connect(path)
        try:
            con.execute("INSTALL json; LOAD json;")
        except Exception:
            pass  # json is built-in in recent DuckDB
        counts = {}
        for t in tables:
            if t in CUSTOM_BUILDERS:
                counts[t] = CUSTOM_BUILDERS[t](con)
            else:
                counts[t] = build_table(con, t)
        con.close()
        built[db_file] = counts
    return built


# ---------------------------------------------------------------------------
# Sanity checks + cross-table test queries
# ---------------------------------------------------------------------------
def show_rows(con, table, n=2):
    cols = [d[0] for d in con.execute(f'SELECT * FROM "{table}" LIMIT 0').description]
    rows = con.execute(f'SELECT * FROM "{table}" LIMIT {n}').fetchall()
    for r in rows:
        rec = dict(zip(cols, r))
        # truncate long JSON/text for display
        disp = {}
        for k, v in rec.items():
            s = str(v)
            disp[k] = s if len(s) <= 70 else s[:67] + "..."
        print(f"      {disp}")


CROSS_QUERIES = {
    "erp.duckdb": (
        "coils JOIN coil_materials JOIN raw_materials",
        """
        SELECT c.coil_id, c.grade, rm.material_id, rm.type
        FROM coils c
        JOIN coil_materials cm ON cm.coil_id = c.coil_id
        JOIN raw_materials rm ON rm.material_id = cm.material_id
        ORDER BY c.coil_id
        LIMIT 5
        """),
    "scada.duckdb": (
        "equipment grouped by type (single-table db -> aggregate test)",
        """
        SELECT type, COUNT(*) AS n, MIN(installed_date) AS oldest, MAX(installed_date) AS newest
        FROM equipment
        GROUP BY type
        ORDER BY n DESC
        """),
    "qms.duckdb": (
        "quality_tests JOIN deviations ON coil_id = coil_id_fk, JOIN standards",
        """
        SELECT qt.test_id, qt.coil_id, qt.fault_type, d.deviation_id, d.severity, s.standard_id
        FROM quality_tests qt
        JOIN deviations d ON qt.coil_id = d.coil_id_fk
        JOIN standards s ON qt.standard_ref = s.standard_id
        ORDER BY qt.test_id
        LIMIT 5
        """),
    "cmms.duckdb": (
        "failures JOIN rca ON failure_id, JOIN technicians ON analyst",
        """
        SELECT f.failure_id, f.failure_mode, r.rca_id, t.name AS analyst_name, t.role
        FROM failures f
        JOIN rca r ON f.failure_id = r.failure_id
        JOIN technicians t ON r.analyst = t.technician_id
        ORDER BY f.failure_id
        LIMIT 5
        """),
}


def sanity_check(built):
    for db_file, tables in DB_TABLES.items():
        path = os.path.join(HERE, db_file)
        con = duckdb.connect(path, read_only=True)
        print("=" * 74)
        print(f"{db_file}")
        print("=" * 74)
        for t in tables:
            cnt = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            print(f"  Table {t:<16} rows={cnt}")
            print("    first 2 rows:")
            show_rows(con, t, 2)
        label, sql = CROSS_QUERIES[db_file]
        print(f"\n  CROSS-TABLE TEST: {label}")
        cols = [d[0] for d in con.execute(sql).description]
        rows = con.execute(sql).fetchall()
        print(f"    columns: {cols}")
        for r in rows:
            print(f"    {r}")
        print(f"    -> {len(rows)} row(s) returned  [{'OK' if rows else 'NO ROWS'}]")
        con.close()
        print()


if __name__ == "__main__":
    built = build_all()
    print("Built DuckDB files:")
    for db, counts in built.items():
        print(f"  {db}: {counts}")
    print()
    sanity_check(built)
