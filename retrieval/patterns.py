"""
Cross-dimensional compliance pattern detection over the knowledge graph.

Extends the Deviation -> Coil/Equipment -> Failure -> RCA chain checks with correlations
computed across MULTIPLE dimensions simultaneously -- the "catches what a single-system
check would miss" layer. Four dimensions are checked:

    shift        -- do failures concentrate on equipment maintained by one shift?
    procedure    -- does one Procedure appear disproportionately in failure RCAs?
    supplier     -- does one RawMaterial supplier appear disproportionately in coils that
                    BOTH failed quality tests AND ran on failure-affected equipment?
    maintenance  -- do failures cluster near recorded maintenance visits / interval classes?

HARD RULES (trust over drama):
  * Only existing relationship types are traversed -- no new labels or rel types.
  * Every finding states its sample size (n).
  * Findings with n < LOW_N are flagged confidence="low" and worded as tentative;
    n < MIN_N findings are dropped entirely (a 2-data-point "pattern" is noise).

detect_patterns(dimensions=None) -> list of finding dicts:
    {"dimension", "finding", "sample_size", "confidence", "evidence_rows"}
The pipeline attaches these to graph evidence when a question has pattern/causal intent.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graph_store import query_graph

MIN_N = 3      # below this a correlation is not even reported
LOW_N = 8      # below this a correlation is reported but flagged low-confidence
RATIO_FLOOR = 1.30   # over-representation threshold before we call something a pattern


def _confidence(n):
    return "low" if n < LOW_N else ("medium" if n < 25 else "high")


# ---------------------------------------------------------------------------
# 1) SHIFT: failures on equipment, attributed to the maintaining technicians' shift
# ---------------------------------------------------------------------------
def shift_correlation():
    rows = query_graph("""
        MATCH (e:Equipment)-[:MAINTAINED_BY]->(t:Technician)
        WITH DISTINCT t.shift AS shift, e
        OPTIONAL MATCH (e)-[:EXPERIENCED]->(f:Failure)
        RETURN shift, count(DISTINCT e) AS equipment_n, count(f) AS failures
        ORDER BY shift
    """)
    rows = [r for r in rows if r["shift"] and r["equipment_n"]]
    if len(rows) < 2:
        return None
    for r in rows:
        r["failures_per_equipment"] = round(r["failures"] / r["equipment_n"], 2)
    hi = max(rows, key=lambda r: r["failures_per_equipment"])
    lo = min(rows, key=lambda r: r["failures_per_equipment"])
    if lo["failures_per_equipment"] == 0 or hi["failures"] < MIN_N:
        return None
    ratio = hi["failures_per_equipment"] / lo["failures_per_equipment"]
    if ratio < RATIO_FLOOR:
        return None
    n = hi["failures"] + lo["failures"]
    return {
        "dimension": "shift",
        "finding": (f"Equipment maintained by Shift {hi['shift']} technicians shows "
                    f"{hi['failures_per_equipment']} failures/equipment vs "
                    f"{lo['failures_per_equipment']} for Shift {lo['shift']} "
                    f"({ratio:.1f}x, n={n} failures across "
                    f"{hi['equipment_n'] + lo['equipment_n']} equipment)"),
        "sample_size": n,
        "confidence": _confidence(n),
        "evidence_rows": rows,
    }


# ---------------------------------------------------------------------------
# 2) PROCEDURE: which procedures appear disproportionately in failure RCAs
# ---------------------------------------------------------------------------
def procedure_correlation():
    rows = query_graph("""
        MATCH (:Failure)-[:DIAGNOSED_BY]->(r:RCA)
        WHERE r.procedure_ref IS NOT NULL
        WITH r.procedure_ref AS procedure_ref, count(*) AS failures
        ORDER BY failures DESC LIMIT 5
        OPTIONAL MATCH (p:Procedure {procedure_id: procedure_ref})
        RETURN procedure_ref, p.title AS title, failures
    """)
    total = query_graph(
        "MATCH (:Failure)-[:DIAGNOSED_BY]->(r:RCA) WHERE r.procedure_ref IS NOT NULL "
        "RETURN count(*) AS n, count(DISTINCT r.procedure_ref) AS procs")
    if not rows or not total:
        return None
    n_all, n_procs = total[0]["n"], max(total[0]["procs"], 1)
    top = rows[0]
    expected = n_all / n_procs
    if top["failures"] < MIN_N or top["failures"] < expected * RATIO_FLOOR:
        return None
    return {
        "dimension": "procedure",
        "finding": (f"Procedure {top['procedure_ref']} ('{top['title']}') is referenced in "
                    f"{top['failures']} of {n_all} failure RCAs -- {top['failures']/n_all:.0%} "
                    f"of all violated-procedure findings vs ~{expected/n_all:.0%} expected if "
                    f"spread evenly across {n_procs} procedures (n={top['failures']})"),
        "sample_size": top["failures"],
        "confidence": _confidence(top["failures"]),
        "evidence_rows": rows,
    }


# ---------------------------------------------------------------------------
# 3) SUPPLIER: raw-material suppliers over-represented in double-trouble coils
#    (coil failed a quality test AND its production equipment experienced failures)
# ---------------------------------------------------------------------------
def supplier_correlation():
    affected = query_graph("""
        MATCH (c:Coil)-[:TESTED_BY]->(:QualityTest)-[:FAILED_STANDARD]->(:Standard)
        MATCH (c)-[:PRODUCED_AT]->(:Equipment)-[:EXPERIENCED]->(:Failure)
        MATCH (c)-[:MADE_FROM]->(rm:RawMaterial)
        RETURN rm.supplier_id AS supplier, count(DISTINCT c) AS affected_coils
        ORDER BY affected_coils DESC
    """)
    baseline = query_graph("""
        MATCH (c:Coil)-[:MADE_FROM]->(rm:RawMaterial)
        RETURN rm.supplier_id AS supplier, count(DISTINCT c) AS all_coils
    """)
    if not affected or not baseline:
        return None
    base = {r["supplier"]: r["all_coils"] for r in baseline}
    total_affected = sum(r["affected_coils"] for r in affected)
    total_base = sum(base.values())
    best = None
    for r in affected:
        b = base.get(r["supplier"])
        if not b or r["affected_coils"] < MIN_N:
            continue
        ratio = (r["affected_coils"] / total_affected) / (b / total_base)
        if ratio >= RATIO_FLOOR and (best is None or ratio > best[1]):
            best = (r, ratio)
    if best is None:
        return None
    r, ratio = best
    return {
        "dimension": "supplier",
        "finding": (f"Supplier {r['supplier']} appears in {r['affected_coils']} of "
                    f"{total_affected} coils that both failed quality tests and ran on "
                    f"failure-affected equipment -- {ratio:.1f}x its baseline share of the "
                    f"coil population (n={r['affected_coils']})"),
        "sample_size": r["affected_coils"],
        "confidence": _confidence(r["affected_coils"]),
        "evidence_rows": affected[:5],
    }


# ---------------------------------------------------------------------------
# 4) MAINTENANCE: failure timing vs recorded maintenance visits + interval class
# ---------------------------------------------------------------------------
def maintenance_correlation():
    rows = query_graph("""
        MATCH (e:Equipment)-[m:MAINTAINED_BY]->(:Technician),
              (e)-[:EXPERIENCED]->(f:Failure)
        WHERE m.shift_date IS NOT NULL AND f.timestamp IS NOT NULL
        WITH duration.inDays(date(m.shift_date),
                             date(datetime(replace(f.timestamp, ' ', 'T')))).days AS d
        RETURN
          sum(CASE WHEN abs(d) <= 7  THEN 1 ELSE 0 END) AS within_7d,
          sum(CASE WHEN abs(d) <= 14 THEN 1 ELSE 0 END) AS within_14d,
          count(*) AS pairs
    """)
    interval = query_graph("""
        MATCH (e:Equipment)-[:EXPERIENCED]->(f:Failure)
        RETURN e.maintenance_interval AS interval,
               count(DISTINCT e) AS equipment_n, count(f) AS failures
        ORDER BY failures DESC
    """)
    finding = None
    if rows and rows[0]["pairs"] >= MIN_N:
        r = rows[0]
        share7 = r["within_7d"] / r["pairs"]
        # ±7d of a random point in a ~6-month window ~= 8% expected; call out >2x that
        if share7 >= 0.16:
            finding = (f"{r['within_7d']} of {r['pairs']} failure/maintenance-visit pairs "
                       f"({share7:.0%}) fall within 7 days of a recorded maintenance visit "
                       f"-- vs ~8% expected by chance (n={r['pairs']})")
            n = r["pairs"]
    if finding is None and interval:
        top = interval[0]
        if top["failures"] >= MIN_N and top["equipment_n"]:
            per = top["failures"] / top["equipment_n"]
            others = [i for i in interval[1:] if i["equipment_n"]]
            if others:
                other_per = sum(i["failures"] for i in others) / sum(i["equipment_n"] for i in others)
                if other_per > 0 and per / other_per >= RATIO_FLOOR:
                    finding = (f"Equipment on '{top['interval']}' maintenance shows "
                               f"{per:.1f} failures/equipment vs {other_per:.1f} for other "
                               f"interval classes ({per/other_per:.1f}x, n={top['failures']})")
                    n = top["failures"]
    if finding is None:
        return None
    return {
        "dimension": "maintenance",
        "finding": finding,
        "sample_size": n,
        "confidence": _confidence(n),
        "evidence_rows": interval[:5],
    }


DIMENSIONS = {
    "shift": shift_correlation,
    "procedure": procedure_correlation,
    "supplier": supplier_correlation,
    "maintenance": maintenance_correlation,
}

# question intent -> which adjacent dimensions to auto-check alongside the asked one
PATTERN_INTENT_RX = re.compile(
    r"pattern|correlat|cluster|trend|recurring|repeat|common (cause|thread)|"
    r"disproportion|systemic|root cause across|why do .*(fail|deviat)|"
    r"which (shift|supplier|technician|procedure).*(most|worst|more)|"
    r"any (link|connection) between", re.IGNORECASE)


def detect_patterns(dimensions=None):
    """Run correlation checks; returns only findings that clear MIN_N and RATIO_FLOOR,
    each with sample_size and confidence. dimensions=None -> all four."""
    out = []
    for name in (dimensions or DIMENSIONS):
        fn = DIMENSIONS.get(name)
        if fn is None:
            continue
        try:
            f = fn()
            if f:
                out.append(f)
        except Exception as exc:                    # one bad query must not kill the rest
            out.append({"dimension": name, "finding": f"(check failed: {exc})",
                        "sample_size": 0, "confidence": "error", "evidence_rows": []})
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for f in detect_patterns():
        print(f"[{f['confidence']:<6} n={f['sample_size']:>3}] {f['dimension']}: {f['finding']}")
