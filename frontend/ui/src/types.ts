export type JsonRecord = Record<string, any>;

export interface RcaSummary {
  total_failures: number;
  failures_with_rca: number;
  rca_completion_pct: number;
  most_common_failure_mode: { name: string; count: number };
  most_affected_equipment: { equipment_id: string; name: string; count: number };
  filters: { equipment_types: string[]; severities: string[]; date_min?: string; date_max?: string };
}
export interface FailureRow {
  failure_id: string; equipment_id: string; equipment_name: string; equipment_type: string;
  failure_date: string; failure_mode: string; severity: string; status: string; has_rca: boolean;
  recurrence_count: number;
}
export interface FailureList { count: number; failures: FailureRow[]; }
export interface FailureDetail extends JsonRecord {
  failure: JsonRecord; equipment: JsonRecord; rca: JsonRecord; technician: JsonRecord;
  evidence_chain: JsonRecord[]; downstream_tests: JsonRecord[]; recurrences: JsonRecord[];
  recurrence_count: number; recommended_actions: JsonRecord[]; confidence: JsonRecord;
  severity: string; status: string; provenance: JsonRecord;
}

export interface ComplianceSummary extends JsonRecord { standards: StandardRow[]; headline: JsonRecord; provenance: JsonRecord; }
export interface StandardRow extends JsonRecord {
  family_id: string; name: string; scope: string; clause_count: number; total_tests: number;
  pass_count: number; fail_count: number; failure_rate_pct: number; deviation_count: number;
  trend: JsonRecord; risk: JsonRecord;
}
export interface StandardDetail extends JsonRecord {
  standard: StandardRow; clauses: JsonRecord[]; deviations: JsonRecord[];
  deviation_groups: { month: JsonRecord[]; equipment: JsonRecord[] };
  pattern: JsonRecord; cross_dimensional_flags: JsonRecord[]; provenance: JsonRecord;
}
