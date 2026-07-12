import * as React from "react";
import * as Dialog from "@radix-ui/react-dialog";
import * as Tabs from "@radix-ui/react-tabs";
import {
  Activity,
  AlertOctagon,
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  Check,
  CheckCircle2,
  ClipboardCheck,
  Factory,
  FileCheck2,
  FileSearch,
  FileText,
  Gauge,
  History,
  Link2,
  ListFilter,
  RefreshCw,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  TestTube2,
  TriangleAlert,
  UserRound,
  Workflow,
  Wrench,
  X,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { AnimatePresence, motion } from "motion/react";

import type { FailureDetail, FailureList, FailureRow, JsonRecord, RcaSummary } from "./types";
import {
  apiFetch,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  EmptyState,
  ErrorState,
  LoadingState,
  MetricCard,
  PillarHeader,
  SelectControl,
  SourcePill,
  TooltipButton,
  labelize,
  number,
  shortDate,
} from "./ui";

type BadgeTone = "neutral" | "indigo" | "green" | "amber" | "red" | "violet" | "cyan";

interface RcaFilters {
  equipmentType: string;
  dateFrom: string;
  dateTo: string;
  severity: string;
  hasRca: string;
  sort: string;
}

const EMPTY_FILTERS: RcaFilters = {
  equipmentType: "",
  dateFrom: "",
  dateTo: "",
  severity: "",
  hasRca: "",
  sort: "recent",
};

function stringValue(value: unknown, fallback = "—"): string {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

function severityTone(value: unknown): BadgeTone {
  const level = String(value || "").toLowerCase();
  if (level === "critical" || level === "high") return "red";
  if (level === "medium") return "amber";
  if (level === "low") return "cyan";
  return "neutral";
}

function statusTone(value: unknown): BadgeTone {
  const status = String(value || "").toLowerCase();
  if (status === "resolved") return "green";
  if (status === "recurring") return "violet";
  if (status === "open") return "amber";
  return "neutral";
}

function confidenceTone(value: unknown): BadgeTone {
  const level = String(value || "").toLowerCase();
  if (level === "high") return "green";
  if (level === "medium") return "amber";
  return "red";
}

function failureFromHash(): string {
  const parts = window.location.hash.replace(/^#\//, "").split("/");
  if (parts[0] !== "rca" || !parts[1]) return "";
  try { return decodeURIComponent(parts.slice(1).join("/")); }
  catch { return parts.slice(1).join("/"); }
}

function updateRcaHash(failureId?: string) {
  const next = failureId ? `#/rca/${encodeURIComponent(failureId)}` : "#/rca";
  if (window.location.hash === next) return;
  try {
    window.history.pushState(window.history.state, "", next);
  } catch {
    window.location.hash = next.slice(1);
  }
}

function chainIcon(kind: unknown) {
  const icons: Record<string, LucideIcon> = {
    failure: AlertOctagon,
    rca: FileSearch,
    technician: UserRound,
    procedure: Workflow,
    deviation: TriangleAlert,
    standard: ShieldCheck,
    document: FileText,
  };
  return icons[String(kind || "").toLowerCase()] || Link2;
}

function recordList(record: unknown): JsonRecord[] {
  if (Array.isArray(record)) {
    return record.map((item) =>
      item && typeof item === "object" ? (item as JsonRecord) : { value: item },
    );
  }
  if (record && typeof record === "object") return [record as JsonRecord];
  return record === null || record === undefined ? [] : [{ value: record }];
}

function formatRecordValue(value: unknown): string {
  let text: string;
  if (typeof value === "object" && value !== null) {
    try {
      text = JSON.stringify(value);
    } catch {
      text = String(value);
    }
  } else {
    text = stringValue(value);
  }
  return text.length > 320 ? `${text.slice(0, 317)}…` : text;
}

function RecordDialog({ step, onClose }: { step: JsonRecord | null; onClose: () => void }) {
  const records = recordList(step?.record);
  const title = `${stringValue(step?.kind, "Evidence")} record${records.length > 1 ? "s" : ""}`;
  const portalContainer = document.getElementById("rca-react-root");

  return (
    <Dialog.Root open={Boolean(step)} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal container={portalContainer}>
        <Dialog.Overlay className="sp-dialog-overlay" />
        <Dialog.Content className="sp-dialog" aria-describedby="sp-rca-record-description">
          <div className="sp-dialog__head sp-dialog__header">
            <div>
              <Dialog.Title className="sp-dialog__title">{title}</Dialog.Title>
              <Dialog.Description className="sp-dialog__description" id="sp-rca-record-description">
                {step?.id
                  ? `${stringValue(step.kind)} ${stringValue(step.id)} · direct linked record`
                  : `No linked ${String(step?.kind || "evidence").toLowerCase()} record was found.`}
              </Dialog.Description>
            </div>
            <Dialog.Close asChild>
              <TooltipButton label="Close record preview" variant="ghost" size="icon">
                <X size={18} aria-hidden="true" />
              </TooltipButton>
            </Dialog.Close>
          </div>

          {records.length ? (
            <div className="sp-dialog__records">
              {records.slice(0, 6).map((record, recordIndex) => {
                const fields = Object.entries(record).filter(([, value]) => value !== null && value !== "");
                return (
                  <section className="sp-dialog__record" key={`${String(step?.kind)}-${recordIndex}`}>
                    {records.length > 1 && <h3>Record {recordIndex + 1}</h3>}
                    <dl className="sp-record-grid">
                      {fields.slice(0, 12).map(([key, value]) => (
                        <div className="sp-record sp-record-grid__item" key={key}>
                          <dt>{labelize(key)}</dt>
                          <dd>{formatRecordValue(value)}</dd>
                        </div>
                      ))}
                    </dl>
                  </section>
                );
              })}
              {records.length > 6 && (
                <p className="sp-dialog__more">Showing 6 of {number(records.length)} linked records.</p>
              )}
            </div>
          ) : (
            <EmptyState
              title="Evidence gap"
              detail={`No ${String(step?.kind || "evidence").toLowerCase()} is linked to this failure in Neo4j.`}
            />
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

function FailureBadges({ row }: { row: Pick<FailureRow, "severity" | "status" | "has_rca"> }) {
  return (
    <div className="sp-rca-badges">
      <Badge tone={severityTone(row.severity)}>{labelize(row.severity)}</Badge>
      <Badge tone={statusTone(row.status)}>{labelize(row.status)}</Badge>
      <Badge tone={row.has_rca ? "green" : "neutral"}>{row.has_rca ? "RCA linked" : "RCA missing"}</Badge>
    </div>
  );
}

function FailureDesktopTable({ rows, openFailure }: { rows: FailureRow[]; openFailure: (id: string) => void }) {
  return (
    <div className="sp-table-scroll sp-rca__table-wrap">
      <table className="sp-table sp-rca__table">
        <caption className="sp-sr-only">Failure records. Select a row to inspect its evidence and RCA.</caption>
        <thead>
          <tr>
            <th scope="col">Equipment</th>
            <th scope="col">Failure date</th>
            <th scope="col">Failure mode</th>
            <th scope="col">Severity</th>
            <th scope="col">Status</th>
            <th scope="col">RCA</th>
            <th scope="col"><span className="sp-sr-only">Open record</span></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const open = () => openFailure(row.failure_id);
            return (
              <tr
                className="sp-rca__row"
                key={row.failure_id}
                tabIndex={0}
                aria-label={`Open failure ${row.failure_id}`}
                onClick={open}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    open();
                  }
                }}
              >
                <td className="sp-table__primary">
                  <strong>{stringValue(row.equipment_name, "Unknown equipment")}</strong>
                  <small>{stringValue(row.equipment_id)} · {labelize(row.equipment_type)}</small>
                </td>
                <td>{shortDate(row.failure_date)}</td>
                <td className="sp-table__primary">
                  <strong>{labelize(row.failure_mode)}</strong>
                  <small>
                    {row.recurrence_count > 1
                      ? `${number(row.recurrence_count)} matching causes`
                      : "No matching recurrence"}
                  </small>
                </td>
                <td><Badge tone={severityTone(row.severity)}>{labelize(row.severity)}</Badge></td>
                <td><Badge tone={statusTone(row.status)}>{labelize(row.status)}</Badge></td>
                <td>
                  <span className={row.has_rca ? "sp-rca__yes" : "sp-rca__no"}>
                    {row.has_rca ? <Check size={16} aria-hidden="true" /> : "—"}
                    <span className="sp-sr-only">{row.has_rca ? "RCA linked" : "No RCA"}</span>
                  </span>
                </td>
                <td><Button variant="ghost" size="icon" aria-label={`Open failure ${row.failure_id}`} onClick={(event) => { event.stopPropagation(); open(); }}><ArrowRight className="sp-rca__row-arrow" size={17} aria-hidden="true" /></Button></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function FailureMobileCards({ rows, openFailure }: { rows: FailureRow[]; openFailure: (id: string) => void }) {
  return (
    <div className="sp-mobile-list sp-rca__mobile-list">
      {rows.map((row) => (
        <button className="sp-mobile-card sp-rca-mobile-card" key={row.failure_id} onClick={() => openFailure(row.failure_id)}>
          <span className="sp-rca-mobile-card__topline">
            <span>{row.failure_id}</span>
            <span>{shortDate(row.failure_date)}</span>
          </span>
          <strong>{stringValue(row.equipment_name, "Unknown equipment")}</strong>
          <small>{stringValue(row.equipment_id)} · {labelize(row.equipment_type)}</small>
          <span className="sp-rca-mobile-card__mode">{labelize(row.failure_mode)}</span>
          <span className="sp-rca-mobile-card__footer">
            <FailureBadges row={row} />
            <ArrowRight size={17} aria-hidden="true" />
          </span>
        </button>
      ))}
    </div>
  );
}

function EvidenceChain({ steps, onPreview }: { steps: JsonRecord[]; onPreview: (step: JsonRecord) => void }) {
  if (!steps.length) {
    return <EmptyState title="No evidence chain found" detail="This failure has no graph-linked evidence records." />;
  }

  return (
    <div className="sp-rca-chain" aria-label="Linked evidence chain">
      {steps.map((step, index) => {
        const Icon = chainIcon(step.kind);
        const missing = !step.id;
        return (
          <React.Fragment key={`${String(step.kind)}-${index}`}>
            <button
              className={`sp-rca-chain__step${missing ? " sp-rca-chain__step--missing" : ""}`}
              onClick={() => onPreview(step)}
              aria-label={missing
                ? `Inspect missing ${stringValue(step.kind, "evidence")} link`
                : `Preview ${stringValue(step.kind)} ${stringValue(step.id)}`}
            >
              <span className="sp-rca-chain__icon"><Icon size={17} aria-hidden="true" /></span>
              <span className="sp-rca-chain__kind">{stringValue(step.kind, "Evidence")}</span>
              <strong>{stringValue(step.id, "Evidence gap")}</strong>
              <small>{stringValue(step.label, "Not linked")}</small>
              <Badge tone={step.citation === "RAG" ? "violet" : "cyan"}>{stringValue(step.citation, "Graph")}</Badge>
            </button>
            {index < steps.length - 1 && <ArrowRight className="sp-rca-chain__connector" size={16} aria-hidden="true" />}
          </React.Fragment>
        );
      })}
    </div>
  );
}

function NarrativePanel({ detail }: { detail: FailureDetail }) {
  const rca = detail.rca || {};
  const technician = detail.technician || {};
  const hasDocuments = Array.isArray(detail.documents) && detail.documents.length > 0;
  return (
    <Card className="sp-rca-panel">
      <CardHeader>
        <div>
          <CardTitle>RCA narrative</CardTitle>
          <CardDescription>Recorded finding, response, and procedure gap</CardDescription>
        </div>
        <Badge tone={rca.rca_id ? "indigo" : "neutral"}>{stringValue(rca.rca_id, "No RCA")}</Badge>
      </CardHeader>
      <CardContent className="sp-rca-narrative">
        <article>
          <span className="sp-rca-narrative__icon"><Sparkles size={17} aria-hidden="true" /></span>
          <div>
            <h3>Root-cause finding</h3>
            <p>{stringValue(rca.root_cause_text, "No root-cause finding is recorded.")}</p>
            <Badge tone="cyan">Graph</Badge>
          </div>
        </article>
        <article>
          <span className="sp-rca-narrative__icon"><Wrench size={17} aria-hidden="true" /></span>
          <div>
            <h3>Corrective action</h3>
            <p>{stringValue(rca.corrective_action, "No corrective action is recorded.")}</p>
            <div className="sp-rca-citations">
              <Badge tone="cyan">Graph</Badge>
              {hasDocuments && <Badge tone="violet">RAG</Badge>}
            </div>
          </div>
        </article>
        <article>
          <span className="sp-rca-narrative__icon"><Workflow size={17} aria-hidden="true" /></span>
          <div>
            <h3>Procedure finding</h3>
            <p>{stringValue(rca.violated_step, "No violated step is recorded.")}</p>
            <Badge tone="cyan">Graph</Badge>
          </div>
        </article>
        <div className="sp-rca-byline">
          <span><UserRound size={15} aria-hidden="true" /> Technician: <strong>{stringValue(technician.name, "Unlinked")}</strong>{technician.technician_id ? ` (${technician.technician_id})` : ""}</span>
          <span><CalendarDays size={15} aria-hidden="true" /> RCA date: <strong>{shortDate(rca.rca_date)}</strong></span>
        </div>
      </CardContent>
    </Card>
  );
}

function DownstreamPanel({ tests }: { tests: JsonRecord[] }) {
  return (
    <Card className="sp-rca-panel">
      <CardHeader>
        <div>
          <CardTitle>Downstream impact</CardTitle>
          <CardDescription>{number(tests.length)} linked quality result{tests.length === 1 ? "" : "s"}</CardDescription>
        </div>
        <TestTube2 size={19} aria-hidden="true" />
      </CardHeader>
      <CardContent>
        {tests.length ? (
          <>
            <div className="sp-rca-impact-wrap">
              <table className="sp-rca-impact">
                <caption className="sp-sr-only">Quality tests downstream of this failure</caption>
                <thead><tr><th scope="col">Test ID</th><th scope="col">Result</th><th scope="col">Standard</th><th scope="col">Test date</th></tr></thead>
                <tbody>
                  {tests.slice(0, 50).map((test, index) => (
                    <tr key={stringValue(test.test_id, String(index))}>
                      <td><strong>{stringValue(test.test_id)}</strong></td>
                      <td><Badge tone={String(test.result || "").toLowerCase().startsWith("fail") ? "red" : "green"}>{stringValue(test.result)}</Badge></td>
                      <td>{stringValue(test.standard_id)}</td>
                      <td>{shortDate(test.test_date)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {tests.length > 50 && <p className="sp-rca-panel__note">Showing 50 of {number(tests.length)} linked results.</p>}
          </>
        ) : (
          <EmptyState title="No downstream quality impact linked" detail="No QualityTest is reachable through this failure’s deviations and coils." />
        )}
      </CardContent>
    </Card>
  );
}

function ActionsPanel({
  actions,
  checked,
  setChecked,
}: {
  actions: JsonRecord[];
  checked: Record<number, boolean>;
  setChecked: React.Dispatch<React.SetStateAction<Record<number, boolean>>>;
}) {
  return (
    <Card className="sp-rca-panel sp-rca-actions">
      <CardHeader>
        <div>
          <CardTitle>Recommended action checklist</CardTitle>
          <CardDescription>Deterministic actions derived from recorded RCA fields</CardDescription>
        </div>
        <ClipboardCheck size={19} aria-hidden="true" />
      </CardHeader>
      <CardContent>
        {actions.length ? (
          <div className="sp-rca-checklist">
            {actions.map((action, index) => (
              <label className="sp-rca-checklist__item" key={`${String(action.role)}-${index}`}>
                <input
                  type="checkbox"
                  checked={Boolean(checked[index])}
                  onChange={(event) => setChecked((current) => ({ ...current, [index]: event.target.checked }))}
                  aria-label={`Mark action ${index + 1} complete`}
                />
                <span className="sp-rca-checklist__check"><Check size={14} aria-hidden="true" /></span>
                <span>
                  <Badge tone="indigo">{stringValue(action.role, "Owner")}</Badge>
                  <p>{stringValue(action.text)}</p>
                </span>
              </label>
            ))}
          </div>
        ) : (
          <EmptyState title="No role-scoped action available" detail="No action can be derived from the recorded RCA fields." />
        )}
      </CardContent>
    </Card>
  );
}

function RecurrencePanel({ detail, openFailure }: { detail: FailureDetail; openFailure: (id: string) => void }) {
  const recurrences = detail.recurrences || [];
  return (
    <Card className="sp-rca-panel sp-rca-sidebar-card">
      <CardHeader>
        <div>
          <CardTitle>Recurrence</CardTitle>
          <CardDescription>Exact normalized cause or action</CardDescription>
        </div>
        <History size={18} aria-hidden="true" />
      </CardHeader>
      <CardContent>
        {detail.recurrence_count ? (
          <>
            <div className="sp-rca-recurrence__callout">
              <strong>{number(detail.recurrence_count)}</strong>
              <span>other failure{detail.recurrence_count === 1 ? "" : "s"} share this cause or corrective action</span>
            </div>
            <div className="sp-rca-recurrence__links">
              {recurrences.slice(0, 12).map((item) => (
                <button key={stringValue(item.failure_id)} onClick={() => openFailure(String(item.failure_id))}>
                  <span><strong>{stringValue(item.failure_id)}</strong><small>{labelize(item.failure_mode)}</small></span>
                  <ArrowRight size={15} aria-hidden="true" />
                </button>
              ))}
              {detail.recurrence_count > 12 && <small>+{number(detail.recurrence_count - 12)} more linked failures</small>}
            </div>
          </>
        ) : (
          <EmptyState title="No matching recurrence" detail="No other RCA has the same normalized root-cause text or corrective action." />
        )}
      </CardContent>
    </Card>
  );
}

function ConfidencePanel({ detail }: { detail: FailureDetail }) {
  const confidence = detail.confidence || {};
  return (
    <Card className="sp-rca-panel sp-rca-sidebar-card">
      <CardHeader>
        <div>
          <CardTitle>Confidence</CardTitle>
          <CardDescription>Evidence-calibrated, no model self-scoring</CardDescription>
        </div>
        <Gauge size={18} aria-hidden="true" />
      </CardHeader>
      <CardContent className="sp-rca-confidence">
        <Badge tone={confidenceTone(confidence.level)}>{labelize(confidence.level || "low")}</Badge>
        <p>{stringValue(confidence.reason, "No confidence evidence is recorded.")}</p>
        <dl>
          <div><dt>Sample size</dt><dd>{number(confidence.sample_size || 1)}</dd></div>
          <div><dt>Source types</dt><dd>{number(confidence.corroborating_sources || 0)}</dd></div>
        </dl>
      </CardContent>
    </Card>
  );
}

function ProvenancePanel({ detail }: { detail: FailureDetail }) {
  const provenance = detail.provenance || {};
  return (
    <Card className="sp-rca-panel sp-rca-sidebar-card">
      <CardHeader>
        <div>
          <CardTitle>Provenance</CardTitle>
          <CardDescription>How this view was assembled</CardDescription>
        </div>
        <FileCheck2 size={18} aria-hidden="true" />
      </CardHeader>
      <CardContent className="sp-rca-provenance">
        <SourcePill>Direct Neo4j · no LLM</SourcePill>
        <dl>
          <div><dt>Query mode</dt><dd>{labelize(provenance.query_mode || "direct_read_only_cypher")}</dd></div>
          <div><dt>LLM used</dt><dd>{provenance.llm_used ? "Yes" : "No"}</dd></div>
        </dl>
        <p>{stringValue(provenance.procedure_path, "Procedure link unavailable")}</p>
      </CardContent>
    </Card>
  );
}

function FailureDetailView({
  detail,
  failureId,
  loading,
  error,
  retry,
  goBack,
  openFailure,
}: {
  detail: FailureDetail | null;
  failureId: string;
  loading: boolean;
  error: string;
  retry: () => void;
  goBack: () => void;
  openFailure: (id: string) => void;
}) {
  const [preview, setPreview] = React.useState<JsonRecord | null>(null);
  const [checked, setChecked] = React.useState<Record<number, boolean>>({});
  const titleRef = React.useRef<HTMLHeadingElement>(null);

  React.useEffect(() => {
    const closeWhenRcaIsInactive = () => {
      const route = window.location.hash.replace(/^#\//, "").split("/")[0];
      if (route !== "rca") setPreview(null);
    };
    window.addEventListener("hashchange", closeWhenRcaIsInactive);
    window.addEventListener("popstate", closeWhenRcaIsInactive);
    return () => {
      window.removeEventListener("hashchange", closeWhenRcaIsInactive);
      window.removeEventListener("popstate", closeWhenRcaIsInactive);
    };
  }, []);

  React.useEffect(() => {
    setPreview(null);
    setChecked({});
  }, [failureId]);

  React.useEffect(() => {
    if (detail) titleRef.current?.focus();
  }, [detail]);

  if (loading && !detail) {
    return (
      <div className="sp-rca-detail">
        <Button variant="ghost" onClick={goBack}><ArrowLeft size={16} aria-hidden="true" /> All failures</Button>
        <LoadingState label={`Loading ${failureId} evidence…`} />
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="sp-rca-detail">
        <Button variant="ghost" onClick={goBack}><ArrowLeft size={16} aria-hidden="true" /> All failures</Button>
        <ErrorState error={error || `Failure ${failureId} was not found.`} retry={retry} />
      </div>
    );
  }

  const failure = detail.failure || {};
  const equipment = detail.equipment || {};
  const detailBadgeRow: Pick<FailureRow, "severity" | "status" | "has_rca"> = {
    severity: detail.severity,
    status: detail.status,
    has_rca: Boolean(detail.rca?.rca_id),
  };

  return (
    <div className="sp-rca-detail">
      <header className="sp-detail-header sp-rca-detail__header">
        <Button variant="ghost" onClick={goBack}><ArrowLeft size={16} aria-hidden="true" /> All failures</Button>
        <div className="sp-detail-header__title sp-rca-detail__identity">
          <span className="sp-eyebrow">Failure evidence · {stringValue(failure.failure_id, failureId)}</span>
          <h1 ref={titleRef} tabIndex={-1}>{stringValue(equipment.name || equipment.equipment_id, "Unknown equipment")}</h1>
          <p>{stringValue(equipment.equipment_id)} · {shortDate(failure.timestamp)} · {labelize(failure.failure_mode)}</p>
        </div>
        <div className="sp-detail-header__badges"><FailureBadges row={detailBadgeRow} /></div>
      </header>

      <Card className="sp-rca-panel sp-rca-evidence-card">
        <CardHeader>
          <div>
            <CardTitle>Evidence chain</CardTitle>
            <CardDescription>Focused graph trail · select any step to preview its record</CardDescription>
          </div>
          <Link2 size={19} aria-hidden="true" />
        </CardHeader>
        <CardContent>
          <EvidenceChain steps={detail.evidence_chain || []} onPreview={setPreview} />
        </CardContent>
      </Card>

      <div className="sp-detail-grid sp-rca-detail__grid">
        <Tabs.Root className="sp-tabs sp-stack sp-rca-detail__main" defaultValue="analysis">
          <Tabs.List className="sp-tabs__list" aria-label="Failure detail sections">
            <Tabs.Trigger className="sp-tabs__trigger" value="analysis"><FileSearch size={15} aria-hidden="true" /> Analysis</Tabs.Trigger>
            <Tabs.Trigger className="sp-tabs__trigger" value="impact"><TestTube2 size={15} aria-hidden="true" /> Downstream impact <span>{number(detail.downstream_tests?.length || 0)}</span></Tabs.Trigger>
            <Tabs.Trigger className="sp-tabs__trigger" value="actions"><ClipboardCheck size={15} aria-hidden="true" /> Actions <span>{number(detail.recommended_actions?.length || 0)}</span></Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content className="sp-tabs__content" value="analysis"><NarrativePanel detail={detail} /></Tabs.Content>
          <Tabs.Content className="sp-tabs__content" value="impact"><DownstreamPanel tests={detail.downstream_tests || []} /></Tabs.Content>
          <Tabs.Content className="sp-tabs__content" value="actions">
            <ActionsPanel actions={detail.recommended_actions || []} checked={checked} setChecked={setChecked} />
          </Tabs.Content>
        </Tabs.Root>

        <aside className="sp-stack sp-rca-detail__sidebar">
          <RecurrencePanel detail={detail} openFailure={openFailure} />
          <ConfidencePanel detail={detail} />
          <ProvenancePanel detail={detail} />
        </aside>
      </div>

      <RecordDialog step={preview} onClose={() => setPreview(null)} />
    </div>
  );
}

export default function RcaApp({ initialFailureId }: { initialFailureId?: string }) {
  const [summary, setSummary] = React.useState<RcaSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = React.useState(true);
  const [summaryError, setSummaryError] = React.useState("");
  const [summaryRequest, setSummaryRequest] = React.useState(0);

  const [filters, setFilters] = React.useState<RcaFilters>(EMPTY_FILTERS);
  const [failureList, setFailureList] = React.useState<FailureList | null>(null);
  const [listLoading, setListLoading] = React.useState(true);
  const [listError, setListError] = React.useState("");
  const [listRequest, setListRequest] = React.useState(0);

  const [selectedFailureId, setSelectedFailureId] = React.useState<string | null>(initialFailureId || null);
  const [detail, setDetail] = React.useState<FailureDetail | null>(null);
  const [detailLoading, setDetailLoading] = React.useState(Boolean(initialFailureId));
  const [detailError, setDetailError] = React.useState("");
  const [detailRequest, setDetailRequest] = React.useState(0);

  const openFailure = React.useCallback((failureId: string) => {
    const cleanId = String(failureId || "").trim();
    if (!cleanId) return;
    setSelectedFailureId(cleanId);
    setDetail(null);
    setDetailError("");
    updateRcaHash(cleanId);
  }, []);

  const goBack = React.useCallback(() => {
    setSelectedFailureId(null);
    setDetail(null);
    setDetailError("");
    updateRcaHash();
  }, []);

  React.useEffect(() => {
    let active = true;
    setSummaryLoading(true);
    setSummaryError("");
    apiFetch<RcaSummary>("/api/rca/summary")
      .then((payload) => active && setSummary(payload))
      .catch((error: unknown) => active && setSummaryError(error instanceof Error ? error.message : String(error)))
      .finally(() => active && setSummaryLoading(false));
    return () => { active = false; };
  }, [summaryRequest]);

  React.useEffect(() => {
    let active = true;
    const params = new URLSearchParams();
    if (filters.equipmentType) params.set("equipment_type", filters.equipmentType);
    if (filters.dateFrom) params.set("date_from", filters.dateFrom);
    if (filters.dateTo) params.set("date_to", filters.dateTo);
    if (filters.severity) params.set("severity", filters.severity);
    if (filters.hasRca) params.set("has_rca", filters.hasRca);
    params.set("sort", filters.sort || "recent");
    setListLoading(true);
    setListError("");
    apiFetch<FailureList>(`/api/rca/failures?${params.toString()}`)
      .then((payload) => active && setFailureList(payload))
      .catch((error: unknown) => active && setListError(error instanceof Error ? error.message : String(error)))
      .finally(() => active && setListLoading(false));
    return () => { active = false; };
  }, [filters, listRequest]);

  React.useEffect(() => {
    if (!selectedFailureId) return;
    let active = true;
    setDetailLoading(true);
    setDetailError("");
    apiFetch<FailureDetail>(`/api/rca/failures/${encodeURIComponent(selectedFailureId)}`)
      .then((payload) => active && setDetail(payload))
      .catch((error: unknown) => active && setDetailError(error instanceof Error ? error.message : String(error)))
      .finally(() => active && setDetailLoading(false));
    return () => { active = false; };
  }, [selectedFailureId, detailRequest]);

  React.useEffect(() => {
    if (initialFailureId) openFailure(initialFailureId);
  }, [initialFailureId, openFailure]);

  React.useEffect(() => {
    const handleOpenFailure = (event: Event) => {
      const detailValue = (event as CustomEvent<unknown>).detail;
      let failureId = "";
      if (typeof detailValue === "string") failureId = detailValue;
      else if (detailValue && typeof detailValue === "object") {
        const value = detailValue as { failureId?: unknown; failure_id?: unknown };
        failureId = String(value.failureId || value.failure_id || "");
      }
      if (failureId) openFailure(failureId);
    };
    window.addEventListener("synapse-open-failure", handleOpenFailure);
    return () => window.removeEventListener("synapse-open-failure", handleOpenFailure);
  }, [openFailure]);

  React.useEffect(() => {
    const syncFromHistory = () => {
      const failureId = failureFromHash();
      setSelectedFailureId(failureId || null);
      if (!failureId) { setDetail(null); setDetailError(""); }
    };
    window.addEventListener("popstate", syncFromHistory);
    window.addEventListener("hashchange", syncFromHistory);
    return () => {
      window.removeEventListener("popstate", syncFromHistory);
      window.removeEventListener("hashchange", syncFromHistory);
    };
  }, []);

  const rows = failureList?.failures || [];
  const updateFilter = <K extends keyof RcaFilters>(key: K, value: RcaFilters[K]) => {
    setFilters((current) => ({ ...current, [key]: value }));
  };

  return (
    <section className="sp-rca" aria-label="RCA and failures">
      <AnimatePresence mode="wait" initial={false}>
        {selectedFailureId ? (
          <motion.div
            className="sp-rca__view"
            key={`detail-${selectedFailureId}`}
            initial={{ opacity: 0, x: 18 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 12 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
          >
            <FailureDetailView
              detail={detail}
              failureId={selectedFailureId}
              loading={detailLoading}
              error={detailError}
              retry={() => setDetailRequest((request) => request + 1)}
              goBack={goBack}
              openFailure={openFailure}
            />
          </motion.div>
        ) : (
          <motion.div
            className="sp-rca__view"
            key="failure-list"
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -12 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
          >
            <PillarHeader
              eyebrow="RCA & Failures"
              title="Failure intelligence, fully traceable"
              description="Move from an equipment event to its evidence, root cause, downstream impact, and response without losing the thread."
            >
              <SourcePill>Direct Neo4j · no LLM</SourcePill>
            </PillarHeader>

            {summaryLoading && !summary ? (
              <LoadingState label="Loading failure overview…" />
            ) : summaryError && !summary ? (
              <ErrorState error={summaryError} retry={() => setSummaryRequest((request) => request + 1)} />
            ) : summary ? (
              <section className="sp-metrics sp-rca__metrics" aria-label="RCA summary">
                <MetricCard icon={Activity} index={0} label="Total failures" value={number(summary.total_failures)} detail="Tracked equipment events" />
                <MetricCard icon={CheckCircle2} index={1} label="RCA completion" value={`${Number(summary.rca_completion_pct || 0).toFixed(1)}%`} detail={`${number(summary.failures_with_rca)} completed records`} featured />
                <MetricCard icon={Zap} index={2} label="Most common mode" value={number(summary.most_common_failure_mode?.count)} detail={labelize(summary.most_common_failure_mode?.name)} />
                <MetricCard icon={Factory} index={3} label="Most affected equipment" value={number(summary.most_affected_equipment?.count)} detail={summary.most_affected_equipment?.name || summary.most_affected_equipment?.equipment_id || "—"} />
              </section>
            ) : null}

            <Card className="sp-rca__browser">
              <CardHeader>
                <div>
                  <CardTitle>Failure register</CardTitle>
                  <CardDescription>Filter the operating history, then select a failure to follow its evidence.</CardDescription>
                </div>
                <div className="sp-rca__browser-actions">
                  <Badge tone="indigo">{listLoading ? "Updating…" : `${number(failureList?.count || 0)} failures`}</Badge>
                  <TooltipButton
                    label="Clear all filters"
                    variant="ghost"
                    size="icon"
                    onClick={() => setFilters(EMPTY_FILTERS)}
                    disabled={Object.entries(filters).every(([key, value]) => value === (key === "sort" ? "recent" : ""))}
                  >
                    <RotateCcw size={16} aria-hidden="true" />
                  </TooltipButton>
                  <TooltipButton label="Refresh failure records" variant="ghost" size="icon" onClick={() => setListRequest((request) => request + 1)}>
                    <RefreshCw size={16} aria-hidden="true" />
                  </TooltipButton>
                </div>
              </CardHeader>
              <CardContent>
                <div className="sp-rca__filter-heading"><ListFilter size={16} aria-hidden="true" /><span>Six ways to focus the register</span></div>
                <div className="sp-fields sp-rca__filters">
                  <SelectControl
                    label="Equipment type"
                    value={filters.equipmentType}
                    onValueChange={(value) => updateFilter("equipmentType", value)}
                    placeholder="All equipment"
                    options={(summary?.filters.equipment_types || []).map((value) => ({ value, label: labelize(value) }))}
                  />
                  <label className="sp-field">
                    <span>From date</span>
                    <span className="sp-date-input">
                      <CalendarDays size={15} aria-hidden="true" />
                      <input
                        type="date"
                        value={filters.dateFrom}
                        min={summary?.filters.date_min || undefined}
                        max={summary?.filters.date_max || undefined}
                        onChange={(event) => updateFilter("dateFrom", event.target.value)}
                      />
                    </span>
                  </label>
                  <label className="sp-field">
                    <span>To date</span>
                    <span className="sp-date-input">
                      <CalendarDays size={15} aria-hidden="true" />
                      <input
                        type="date"
                        value={filters.dateTo}
                        min={summary?.filters.date_min || undefined}
                        max={summary?.filters.date_max || undefined}
                        onChange={(event) => updateFilter("dateTo", event.target.value)}
                      />
                    </span>
                  </label>
                  <SelectControl
                    label="Severity"
                    value={filters.severity}
                    onValueChange={(value) => updateFilter("severity", value)}
                    placeholder="All severities"
                    options={(summary?.filters.severities || []).map((value) => ({ value, label: labelize(value) }))}
                  />
                  <SelectControl
                    label="RCA coverage"
                    value={filters.hasRca}
                    onValueChange={(value) => updateFilter("hasRca", value)}
                    placeholder="All RCA states"
                    options={[{ value: "true", label: "RCA completed" }, { value: "false", label: "RCA missing" }]}
                  />
                  <SelectControl
                    label="Sort by"
                    value={filters.sort}
                    onValueChange={(value) => updateFilter("sort", value || "recent")}
                    options={[
                      { value: "recent", label: "Most recent" },
                      { value: "severe", label: "Highest severity" },
                      { value: "recurring", label: "Most recurring" },
                    ]}
                  />
                </div>

                <div className="sp-rca__results" aria-live="polite" aria-busy={listLoading}>
                  {listLoading ? (
                    <LoadingState label="Loading failure records…" />
                  ) : listError ? (
                    <ErrorState error={listError} retry={() => setListRequest((request) => request + 1)} />
                  ) : rows.length ? (
                    <>
                      <FailureDesktopTable rows={rows} openFailure={openFailure} />
                      <FailureMobileCards rows={rows} openFailure={openFailure} />
                    </>
                  ) : (
                    <EmptyState title="No matching failures" detail="Try widening the date range or clearing one of the filters." />
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
