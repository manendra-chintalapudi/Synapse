import * as React from "react";
import * as Accordion from "@radix-ui/react-accordion";
import * as Tabs from "@radix-ui/react-tabs";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  CheckCircle,
  ChevronDown,
  Database,
  ExternalLink,
  FileCheck,
  FlaskConical,
  Gauge,
  GitBranch,
  Info,
  Layers,
  Link,
  Minus,
  Package,
  Shield,
  TestTube,
  TrendingDown,
  TrendingUp,
  User,
  Wrench,
} from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { toast } from "sonner";
import type {
  ComplianceSummary,
  JsonRecord,
  StandardDetail,
  StandardRow,
} from "./types";
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
  SourcePill,
  TooltipButton,
  cn,
  labelize,
  number,
  shortDate,
} from "./ui";

interface ComplianceAppProps {
  initialFamilyId?: string;
}

type GroupMode = "month" | "equipment";

function numeric(value: unknown): number {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function percent(value: unknown, digits = 2): string {
  return `${numeric(value).toFixed(digits)}%`;
}

function signedPoints(value: unknown): string {
  const points = numeric(value);
  return `${points > 0 ? "+" : ""}${points.toFixed(2)} pp`;
}

function record(value: unknown): JsonRecord {
  return value && typeof value === "object" && !Array.isArray(value)
    ? value as JsonRecord
    : {};
}

function records(value: unknown): JsonRecord[] {
  return Array.isArray(value) ? value.map(record) : [];
}

function text(value: unknown, fallback = "—"): string {
  const result = String(value ?? "").trim();
  return result || fallback;
}

function familyFromHash(): string {
  const parts = window.location.hash.replace(/^#\//, "").split("/");
  if (parts[0] !== "compliance" || !parts[1]) return "";
  try {
    return decodeURIComponent(parts.slice(1).join("/"));
  } catch {
    return parts.slice(1).join("/");
  }
}

function updateComplianceHash(familyId?: string): void {
  const next = familyId
    ? `#/compliance/${encodeURIComponent(familyId)}`
    : "#/compliance";
  if (window.location.hash !== next) window.history.pushState({}, "", next);
}

function badgeToneForSeverity(value: unknown): "red" | "amber" | "neutral" {
  const severity = String(value || "").toLowerCase();
  if (severity === "critical" || severity === "high") return "red";
  if (severity === "medium" || severity === "moderate") return "amber";
  return "neutral";
}

function RiskBadge({ risk }: { risk?: JsonRecord }) {
  const warning = Boolean(risk?.warning);
  return (
    <Badge tone={warning ? "amber" : "green"}>
      {warning ? <AlertTriangle size={13} aria-hidden="true" /> : <CheckCircle size={13} aria-hidden="true" />}
      {text(risk?.label, warning ? "Review required" : "Stable trend")}
    </Badge>
  );
}

function ConfidenceBadge({ confidence }: { confidence: unknown }) {
  const level = String(confidence || "low").toLowerCase();
  const tone = level === "high" ? "green" : level === "medium" ? "amber" : "red";
  return <Badge tone={tone}>{labelize(level)} confidence</Badge>;
}

function TrendIcon({ change }: { change: number }) {
  if (change > 0) return <TrendingUp size={17} aria-hidden="true" />;
  if (change < 0) return <TrendingDown size={17} aria-hidden="true" />;
  return <Minus size={17} aria-hidden="true" />;
}

function LinkagePrecheck({ summary }: { summary: ComplianceSummary }) {
  const total = numeric(summary.total_deviations);
  const linked = numeric(summary.failure_linked_deviations);
  const ready = total === 0 || linked > 0;
  return (
    <div
      className={cn("sp-compliance-precheck", ready ? "sp-compliance-precheck--ready" : "sp-compliance-precheck--missing")}
      role={ready ? "status" : "alert"}
    >
      {ready ? <GitBranch size={18} aria-hidden="true" /> : <AlertTriangle size={18} aria-hidden="true" />}
      <div>
        <strong>{ready ? "Compliance-to-failure linkage confirmed" : "Compliance linkage needs attention"}</strong>
        <span>
          {ready
            ? `${number(linked)} of ${number(total)} deviations resolve to a downstream Failure record; linked RCA evidence remains available in each deviation.`
            : `${number(total)} deviations are present, but none resolve through Deviation → Coil/Equipment → Failure → RCA. Run the compliance-enrichment linkage before relying on pattern results.`}
        </span>
      </div>
    </div>
  );
}

function SummaryStrip({ summary }: { summary: ComplianceSummary }) {
  const headline = record(summary.headline);
  const totalDeviations = numeric(summary.total_deviations);
  const failureLinked = numeric(summary.failure_linked_deviations);
  const linkageCoverage = totalDeviations ? 100 * failureLinked / totalDeviations : 0;
  const windowDays = numeric(summary.window_days) || 30;

  return (
    <>
      <LinkagePrecheck summary={summary} />
      <motion.section
        className="sp-compliance-headline"
        aria-labelledby="sp-compliance-headline-title"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.24 }}
      >
        <div className="sp-compliance-headline__icon"><Activity size={22} aria-hidden="true" /></div>
        <div className="sp-compliance-headline__copy">
          <span>Strongest observed compliance signal</span>
          <h2 id="sp-compliance-headline-title">{percent(headline.value_pct)}</h2>
          <p>{text(headline.label, `Failure-linked deviations followed by equipment failure within ${windowDays} days`)}</p>
        </div>
        <div className="sp-compliance-headline__sample">
          <strong>{number(headline.numerator)} of {number(headline.denominator)}</strong>
          <span>failure-linked deviations</span>
          <Badge tone="violet">Directional, not causal</Badge>
        </div>
      </motion.section>

      <div className="sp-compliance-metrics" aria-label="Compliance summary metrics">
        <MetricCard
          label="Standards tracked"
          value={number(summary.total_standard_nodes)}
          detail={`${number(summary.active_standard_families)} active families · ${number(summary.active_clause_count)} tested clauses`}
          icon={Shield}
          index={0}
        />
        <MetricCard
          label="Overall test failure rate"
          value={percent(summary.overall_deviation_rate_pct)}
          detail={`${number(summary.failed_tests)} failed of ${number(summary.total_tests)} tests`}
          icon={Gauge}
          index={1}
        />
        <MetricCard
          label="Total deviations"
          value={number(totalDeviations)}
          detail={`${number(summary.coil_sourced_deviations)} coil · ${number(summary.equipment_sourced_deviations)} equipment`}
          icon={AlertTriangle}
          index={2}
        />
        <MetricCard
          label="Failure linkage coverage"
          value={percent(linkageCoverage)}
          detail={`${number(failureLinked)} linked · ${percent(summary.downstream_failure_pct_all)} downstream within ${windowDays}d`}
          icon={Link}
          index={3}
        />
      </div>
      <p className="sp-compliance-scope"><Info size={15} aria-hidden="true" />{text(record(summary.provenance).scope, "Temporal linkage is descriptive, not causal.")}</p>
    </>
  );
}

function StandardsTable({ rows, onOpen }: { rows: StandardRow[]; onOpen: (familyId: string) => void }) {
  if (!rows.length) {
    return <EmptyState title="No active standards" detail="No tested standard family was returned by Neo4j." />;
  }

  return (
    <>
      <div className="sp-compliance-table-wrap">
        <table className="sp-table sp-compliance-table">
          <thead>
            <tr>
              <th scope="col">Standard</th>
              <th scope="col">Scope</th>
              <th scope="col">Total tests</th>
              <th scope="col">Pass</th>
              <th scope="col">Fail</th>
              <th scope="col">Failure rate</th>
              <th scope="col">Risk / gap</th>
              <th scope="col"><span className="sp-sr-only">Open</span></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.family_id}
                className="sp-compliance-table__row"
                tabIndex={0}
                aria-label={`Open ${row.name}, ${percent(row.failure_rate_pct)} failure rate`}
                onClick={() => onOpen(row.family_id)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onOpen(row.family_id);
                  }
                }}
              >
                <td>
                  <strong>{row.name}</strong>
                  <span>{number(row.clause_count)} clauses · {number(row.deviation_count)} deviations</span>
                </td>
                <td className="sp-compliance-table__scope">{row.scope}</td>
                <td>{number(row.total_tests)}</td>
                <td><span className="sp-compliance-value sp-compliance-value--pass">{number(row.pass_count)}</span></td>
                <td><span className="sp-compliance-value sp-compliance-value--fail">{number(row.fail_count)}</span></td>
                <td><strong>{percent(row.failure_rate_pct)}</strong></td>
                <td><RiskBadge risk={record(row.risk)} /></td>
                <td><Button variant="ghost" size="icon" aria-label={`Open ${row.name}`} onClick={(event) => { event.stopPropagation(); onOpen(row.family_id); }}><ArrowRight size={17} aria-hidden="true" /></Button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="sp-mobile-list sp-compliance-mobile-list">
        {rows.map((row) => (
          <button
            type="button"
            className="sp-mobile-card sp-compliance-mobile-card"
            key={row.family_id}
            onClick={() => onOpen(row.family_id)}
          >
            <span className="sp-compliance-mobile-card__top">
              <span><strong>{row.name}</strong><small>{number(row.clause_count)} clauses · {number(row.deviation_count)} deviations</small></span>
              <RiskBadge risk={record(row.risk)} />
            </span>
            <span className="sp-compliance-mobile-card__scope">{row.scope}</span>
            <span className="sp-compliance-mobile-card__stats">
              <span><small>Tests</small><strong>{number(row.total_tests)}</strong></span>
              <span><small>Passed</small><strong>{number(row.pass_count)}</strong></span>
              <span><small>Failed</small><strong>{number(row.fail_count)}</strong></span>
              <span><small>Failure rate</small><strong>{percent(row.failure_rate_pct)}</strong></span>
            </span>
            <span className="sp-compliance-mobile-card__open">Open standard <ArrowRight size={15} aria-hidden="true" /></span>
          </button>
        ))}
      </div>
    </>
  );
}

function StandardsList({ summary, onOpen }: { summary: ComplianceSummary; onOpen: (familyId: string) => void }) {
  const standards = React.useMemo(
    () => [...(summary.standards || [])].sort((left, right) => numeric(right.failure_rate_pct) - numeric(left.failure_rate_pct)),
    [summary.standards],
  );

  return (
    <motion.div
      className="sp-compliance-list"
      key="standards-list"
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -12 }}
      transition={{ duration: 0.2 }}
    >
      <PillarHeader
        eyebrow="Quality intelligence"
        title="Compliance"
        description="Track standards, investigate deviations, and follow evidence into downstream failures and RCA."
      >
        <SourcePill>Direct Neo4j · no LLM</SourcePill>
      </PillarHeader>
      <SummaryStrip summary={summary} />
      <Card className="sp-compliance-standards">
        <CardHeader>
          <div>
            <CardTitle>Standards ranked by failure rate</CardTitle>
            <CardDescription>{number(standards.length)} active families · highest-risk performer first</CardDescription>
          </div>
          <Badge tone="indigo"><TrendingDown size={13} aria-hidden="true" />Sorted descending</Badge>
        </CardHeader>
        <CardContent><StandardsTable rows={standards} onOpen={onOpen} /></CardContent>
      </Card>
    </motion.div>
  );
}

interface MonthlyPoint {
  month: string;
  label: string;
  failureRate: number;
  failed: number;
  total: number;
}

function MonthlyTrend({ trend }: { trend: JsonRecord }) {
  const gradientId = React.useId().replace(/:/g, "");
  const monthly = records(trend.monthly).map((point): MonthlyPoint => ({
    month: text(point.month, "Unknown"),
    label: text(point.month, "Unknown").slice(5),
    failureRate: numeric(point.failure_rate_pct),
    failed: numeric(point.failed),
    total: numeric(point.total),
  }));

  if (!monthly.length) {
    return <EmptyState title="No dated trend available" detail="The standard has tests, but no usable test-date series." />;
  }

  return (
    <div className="sp-chart-block">
      <div
        className="sp-chart"
        role="img"
        aria-label={`Monthly failure-rate trend from ${monthly[0].month} to ${monthly[monthly.length - 1].month}`}
      >
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={monthly} margin={{ top: 16, right: 10, left: -12, bottom: 2 }} accessibilityLayer>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366f1" stopOpacity={0.34} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="4 5" vertical={false} />
            <XAxis dataKey="label" tickLine={false} axisLine={false} />
            <YAxis unit="%" tickLine={false} axisLine={false} domain={[0, "auto"]} />
            <Tooltip
              formatter={(value) => [`${numeric(value).toFixed(2)}%`, "Failure rate"]}
              labelFormatter={(_, payload) => text(payload?.[0]?.payload?.month, "Month")}
            />
            <Area
              type="monotone"
              dataKey="failureRate"
              stroke="#4f46e5"
              strokeWidth={2.5}
              fill={`url(#${gradientId})`}
              activeDot={{ r: 5 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <details className="sp-chart-data">
        <summary>View monthly values</summary>
        <ul>
          {monthly.map((point) => (
            <li key={point.month}>
              <span>{point.month}</span>
              <strong>{point.failureRate.toFixed(2)}%</strong>
              <small>{number(point.failed)} failed of {number(point.total)}</small>
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}

function PerformancePanel({ standard }: { standard: StandardRow }) {
  const trend = record(standard.trend);
  const change = numeric(trend.change_pp);
  const trendTone = change > 2 ? "red" : change > 0 ? "amber" : "green";
  return (
    <Card className="sp-compliance-panel sp-performance-panel">
      <CardHeader>
        <div>
          <CardTitle>Pass / fail performance</CardTitle>
          <CardDescription>Monthly series with rolling 90-day comparison</CardDescription>
        </div>
        <Badge tone={trendTone}><TrendIcon change={change} />{signedPoints(change)}</Badge>
      </CardHeader>
      <CardContent>
        <div className="sp-standard-stats">
          <div><TestTube size={17} aria-hidden="true" /><span>Total tests</span><strong>{number(standard.total_tests)}</strong></div>
          <div className="sp-standard-stats__pass"><CheckCircle size={17} aria-hidden="true" /><span>Pass</span><strong>{number(standard.pass_count)}</strong></div>
          <div className="sp-standard-stats__fail"><AlertTriangle size={17} aria-hidden="true" /><span>Fail</span><strong>{number(standard.fail_count)}</strong></div>
          <div><Gauge size={17} aria-hidden="true" /><span>Failure rate</span><strong>{percent(standard.failure_rate_pct)}</strong></div>
        </div>
        <MonthlyTrend trend={trend} />
        <div className="sp-trend-comparison">
          <div><span>Recent 90 days</span><strong>{percent(trend.recent_rate_pct)}</strong><small>n={number(trend.recent_n)}</small></div>
          <ArrowRight size={18} aria-hidden="true" />
          <div><span>Prior 90 days</span><strong>{percent(trend.prior_rate_pct)}</strong><small>n={number(trend.prior_n)}</small></div>
          <Badge tone={trendTone}><TrendIcon change={change} />{signedPoints(change)}</Badge>
        </div>
      </CardContent>
    </Card>
  );
}

function DetailFact({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="sp-deviation-fact"><dt>{label}</dt><dd>{children}</dd></div>;
}

function FailureButton({ failureId, rcaId }: { failureId: string; rcaId?: string }) {
  const open = () => {
    if (!window.SynapsePillars?.openFailure) {
      toast.error("RCA navigation is not ready. Refresh the page and try again.");
      return;
    }
    window.SynapsePillars?.openFailure(failureId);
  };
  return (
    <Button className="sp-deviation-failure-link" size="sm" variant="outline" onClick={open}>
      Open {failureId} / {rcaId || "RCA"}<ExternalLink size={14} aria-hidden="true" />
    </Button>
  );
}

function DeviationRow({ row, windowDays }: { row: JsonRecord; windowDays: number }) {
  const deviation = record(row.deviation);
  const coil = record(row.coil);
  const equipment = record(row.equipment);
  const failure = record(row.failure);
  const rca = record(row.rca);
  const technician = record(row.technician);
  const materials = records(row.materials);
  const deviationId = text(deviation.deviation_id, "Deviation");
  const failureId = text(failure.failure_id, "");
  const downstream = Boolean(row.downstream_within_window);
  const delta = row.delta_days === null || row.delta_days === undefined ? null : numeric(row.delta_days);

  return (
    <Accordion.Item className="sp-deviation" value={deviationId}>
      <Accordion.Header className="sp-deviation__heading">
        <Accordion.Trigger className="sp-deviation__trigger">
          <span className="sp-deviation__identity"><strong>{deviationId}</strong><small>{shortDate(row.date_flagged)}</small></span>
          <Badge tone={badgeToneForSeverity(deviation.severity)}>{labelize(deviation.severity || "unrated")}</Badge>
          <span className="sp-deviation__equipment">{text(equipment.name || equipment.equipment_id, "Unlinked equipment")}</span>
          {failureId && <span className="sp-deviation__delta">{failureId}{delta !== null ? ` · ${delta}d` : ""}</span>}
          <ChevronDown className="sp-deviation__chevron" size={17} aria-hidden="true" />
        </Accordion.Trigger>
      </Accordion.Header>
      <Accordion.Content className="sp-deviation__content">
        <motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.16 }}>
          <dl className="sp-deviation__facts">
            <DetailFact label="Finding">{text(deviation.description, "No description is recorded.")}</DetailFact>
            <DetailFact label="Coil / heat">
              <span className="sp-entity-ref"><Package size={14} aria-hidden="true" />{text(coil.coil_id)} · {text(coil.heat_number)} · {text(coil.grade)}</span>
            </DetailFact>
            <DetailFact label="Equipment">
              <span className="sp-entity-ref"><Wrench size={14} aria-hidden="true" />{text(equipment.name)} ({text(equipment.equipment_id)})</span>
            </DetailFact>
            <DetailFact label="Linked failure">
              {failureId
                ? <span>{failureId} · {labelize(failure.failure_mode)}{downstream ? ` · followed within ${windowDays} days` : ""}</span>
                : <span className="sp-evidence-gap">No linked failure</span>}
            </DetailFact>
            <DetailFact label="RCA finding">
              {rca.rca_id
                ? <span>{text(rca.rca_id)} · {text(rca.root_cause_text, "No root-cause text recorded")}</span>
                : <span className="sp-evidence-gap">No linked RCA</span>}
            </DetailFact>
            <DetailFact label="RCA technician">
              {technician.technician_id
                ? <span>{text(technician.name)} ({text(technician.technician_id)}){technician.shift ? ` · assigned shift ${text(technician.shift)}` : ""}</span>
                : <span className="sp-evidence-gap">Unlinked</span>}
            </DetailFact>
            {materials.length > 0 && (
              <DetailFact label="Material sources">
                <span className="sp-deviation__materials">
                  {materials.map((material, index) => (
                    <Badge tone="neutral" key={`${text(material.material_id)}-${index}`}>
                      {text(material.material_id)} · {text(material.supplier_id, "supplier unknown")}
                    </Badge>
                  ))}
                </span>
              </DetailFact>
            )}
            <DetailFact label="Evidence jump">
              {failureId
                ? <FailureButton failureId={failureId} rcaId={text(rca.rca_id, "")} />
                : <span className="sp-evidence-gap">Available when a Failure relationship is present.</span>}
            </DetailFact>
          </dl>
        </motion.div>
      </Accordion.Content>
    </Accordion.Item>
  );
}

function DeviationGroups({ detail, mode }: { detail: StandardDetail; mode: GroupMode }) {
  const [openGroups, setOpenGroups] = React.useState<string[]>([]);
  const deviations = detail.deviations || [];
  const byId = React.useMemo(
    () => new Map(deviations.map((row) => [text(record(row.deviation).deviation_id, ""), row])),
    [deviations],
  );
  const groups = detail.deviation_groups?.[mode] || [];
  const windowDays = numeric(record(detail.pattern).window_days) || 30;

  React.useEffect(() => setOpenGroups([]), [mode]);

  if (!groups.length) {
    return <EmptyState title="No grouped deviations" detail={`No ${mode}-level grouping is available for this standard.`} />;
  }

  return (
    <Accordion.Root
      className="sp-deviation-groups"
      type="multiple"
      value={openGroups}
      onValueChange={setOpenGroups}
    >
      {groups.map((group, index) => {
        const groupValue = `${mode}-${text(group.key, String(index))}-${index}`;
        const isOpen = openGroups.includes(groupValue);
        const deviationIds = Array.isArray(group.deviation_ids) ? group.deviation_ids : [];
        const groupRows = isOpen
          ? deviationIds.map((item) => byId.get(text(item, ""))).filter(Boolean) as JsonRecord[]
          : [];
        return (
          <Accordion.Item className="sp-deviation-group" value={groupValue} key={groupValue}>
            <Accordion.Header className="sp-deviation-group__heading">
              <Accordion.Trigger className="sp-deviation-group__trigger">
                <span className="sp-deviation-group__title"><strong>{text(group.label, "Unknown group")}</strong><small>{number(group.count)} deviations</small></span>
                <span className="sp-deviation-group__signals">
                  <Badge tone="neutral">{number(group.linked_failures)} linked</Badge>
                  <Badge tone={numeric(group.downstream_within_window) ? "amber" : "neutral"}>{number(group.downstream_within_window)} downstream</Badge>
                </span>
                <ChevronDown className="sp-deviation-group__chevron" size={18} aria-hidden="true" />
              </Accordion.Trigger>
            </Accordion.Header>
            <Accordion.Content className="sp-deviation-group__content">
              {isOpen && (
                <Accordion.Root className="sp-deviation-list" type="multiple">
                  {groupRows.map((row, rowIndex) => (
                    <DeviationRow
                      key={`${text(record(row.deviation).deviation_id, "deviation")}-${rowIndex}`}
                      row={row}
                      windowDays={windowDays}
                    />
                  ))}
                </Accordion.Root>
              )}
            </Accordion.Content>
          </Accordion.Item>
        );
      })}
    </Accordion.Root>
  );
}

function DeviationsPanel({ detail }: { detail: StandardDetail }) {
  const [mode, setMode] = React.useState<GroupMode>("month");
  const pattern = record(detail.pattern);
  return (
    <Card className="sp-compliance-panel sp-deviations-panel">
      <CardHeader>
        <div>
          <CardTitle>Deviation evidence</CardTitle>
          <CardDescription>{number(pattern.deviation_cohort_n)} standard-cohort deviations · grouped before expansion</CardDescription>
        </div>
        <TooltipButton label="Groups load their individual deviation rows only when expanded." variant="ghost" size="icon">
          <Info size={17} aria-hidden="true" />
        </TooltipButton>
      </CardHeader>
      <CardContent>
        <Tabs.Root className="sp-tabs sp-deviation-tabs" value={mode} onValueChange={(value) => setMode(value as GroupMode)}>
          <Tabs.List className="sp-tabs__list" aria-label="Group deviations">
            <Tabs.Trigger className="sp-tabs__trigger" value="month"><Layers size={15} aria-hidden="true" />By month</Tabs.Trigger>
            <Tabs.Trigger className="sp-tabs__trigger" value="equipment"><Wrench size={15} aria-hidden="true" />By equipment</Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content className="sp-tabs__content" value="month"><DeviationGroups detail={detail} mode="month" /></Tabs.Content>
          <Tabs.Content className="sp-tabs__content" value="equipment"><DeviationGroups detail={detail} mode="equipment" /></Tabs.Content>
        </Tabs.Root>
      </CardContent>
    </Card>
  );
}

function ClausePanel({ clauses }: { clauses: JsonRecord[] }) {
  return (
    <Card className="sp-compliance-panel sp-clauses-panel">
      <CardHeader>
        <div><CardTitle>Clause performance</CardTitle><CardDescription>Risk warnings compare recent and prior 90-day windows</CardDescription></div>
        <Badge tone="neutral"><FileCheck size={13} aria-hidden="true" />{number(clauses.length)} clauses</Badge>
      </CardHeader>
      <CardContent>
        {clauses.length ? (
          <div className="sp-compliance-table-wrap">
            <table className="sp-table sp-clause-table">
              <thead><tr><th scope="col">Clause</th><th scope="col">Tests</th><th scope="col">Pass</th><th scope="col">Fail</th><th scope="col">Rate</th><th scope="col">Trend</th></tr></thead>
              <tbody>
                {clauses.map((clause, index) => {
                  const trend = record(clause.trend);
                  const change = numeric(trend.change_pp);
                  return (
                    <tr key={`${text(clause.standard_id, "clause")}-${index}`}>
                      <td><strong>{text(clause.standard_id)}</strong>{clause.clause_text && <span>{text(clause.clause_text)}</span>}</td>
                      <td>{number(clause.total_tests)}</td>
                      <td><span className="sp-compliance-value sp-compliance-value--pass">{number(clause.pass_count)}</span></td>
                      <td><span className="sp-compliance-value sp-compliance-value--fail">{number(clause.fail_count)}</span></td>
                      <td><strong>{percent(clause.failure_rate_pct)}</strong></td>
                      <td><Badge tone={clause.rising ? "red" : change > 0 ? "amber" : "green"}><TrendIcon change={change} />{signedPoints(change)}</Badge></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : <EmptyState title="No clause results" detail="No tested clauses were returned for this family." />}
      </CardContent>
    </Card>
  );
}

function PatternPanel({ pattern }: { pattern: JsonRecord }) {
  const downstream = numeric(pattern.downstream_failure_n);
  const linked = numeric(pattern.failure_linked_n);
  const cohort = numeric(pattern.deviation_cohort_n);
  const windowDays = numeric(pattern.window_days) || 30;
  const wilson = Array.isArray(pattern.wilson_95pct) ? pattern.wilson_95pct : [0, 0];
  const rootCause = text(pattern.most_common_root_cause, "");
  return (
    <Card className="sp-compliance-panel sp-pattern-panel">
      <CardHeader>
        <div><CardTitle>{windowDays}-day pattern detection</CardTitle><CardDescription>Direct temporal Cypher · n={number(linked)}</CardDescription></div>
        <ConfidenceBadge confidence={pattern.confidence} />
      </CardHeader>
      <CardContent>
        <div className="sp-pattern-score">
          <span><strong>{number(downstream)}</strong><small>of</small><strong>{number(linked)}</strong></span>
          <b>{percent(pattern.downstream_rate_among_linked_pct)}</b>
        </div>
        <p className="sp-pattern-statement">
          <strong>{number(downstream)} of {number(linked)}</strong> failure-linked deviations were followed by an equipment failure within {windowDays} days
          {rootCause ? <>, most commonly citing <strong>{rootCause}</strong>.</> : "."}
        </p>
        <div className="sp-pattern-rates">
          <div><span>Among linked</span><strong>{percent(pattern.downstream_rate_among_linked_pct)}</strong><small>n={number(linked)}</small></div>
          <div><span>Full cohort</span><strong>{percent(pattern.downstream_rate_full_cohort_pct)}</strong><small>n={number(cohort)}</small></div>
        </div>
        <div className="sp-pattern-interval">
          <span>95% Wilson interval</span><strong>{percent(wilson[0])}–{percent(wilson[1])}</strong>
        </div>
        {rootCause ? (
          <div className="sp-pattern-cause">
            <GitBranch size={17} aria-hidden="true" />
            <div><span>Most common linked root cause · {number(pattern.most_common_root_cause_n)}/{number(downstream)}</span><strong>{rootCause}</strong></div>
          </div>
        ) : <div className="sp-evidence-gap">No downstream RCA root cause is available for this cohort.</div>}
        <p className="sp-pattern-scope"><Info size={14} aria-hidden="true" />{text(pattern.scope, "Directional association only; causality is not inferred.")}</p>
      </CardContent>
    </Card>
  );
}

function FlagIcon({ dimension }: { dimension: unknown }) {
  const value = String(dimension || "").toLowerCase();
  if (value.includes("shift") || value.includes("technician")) return <User size={17} aria-hidden="true" />;
  if (value.includes("heat") || value.includes("material") || value.includes("supplier")) return <Package size={17} aria-hidden="true" />;
  return <FlaskConical size={17} aria-hidden="true" />;
}

function CrossFlagsPanel({ flags }: { flags: JsonRecord[] }) {
  return (
    <Card className="sp-compliance-panel sp-cross-flags-panel">
      <CardHeader><div><CardTitle>Cross-dimensional flags</CardTitle><CardDescription>Descriptive screening only</CardDescription></div></CardHeader>
      <CardContent>
        {flags.length ? (
          <div className="sp-cross-flags">
            {flags.map((flag, index) => (
              <div className="sp-cross-flag" key={`${text(flag.dimension, "flag")}-${index}`}>
                <span className="sp-cross-flag__icon"><FlagIcon dimension={flag.dimension} /></span>
                <div>
                  <span>{text(flag.dimension)} · n={number(flag.sample_size)}</span>
                  <strong>{text(flag.value)} · {percent(flag.share_pct, 1)}</strong>
                  <p>{text(flag.note, "Descriptive association only.")}</p>
                </div>
                <Badge tone={String(flag.confidence).toLowerCase() === "low" ? "amber" : "neutral"}>{labelize(flag.confidence || "low")}</Badge>
              </div>
            ))}
          </div>
        ) : <EmptyState title="No cross-dimensional flags" detail="No shift, technician, heat, or supplier concentration is linked to this standard." />}
      </CardContent>
    </Card>
  );
}

function RiskPanel({ risk, provenance }: { risk: JsonRecord; provenance: JsonRecord }) {
  const rising = numeric(risk.rising_clause_count);
  const missingActions = numeric(risk.missing_corrective_action_count);
  return (
    <Card className="sp-compliance-panel sp-risk-panel">
      <CardHeader><div><CardTitle>Risk / gap indicator</CardTitle><CardDescription>Trend and corrective-action observability</CardDescription></div><RiskBadge risk={risk} /></CardHeader>
      <CardContent>
        <div className="sp-risk-facts">
          <div className={cn("sp-risk-fact", rising > 0 && "sp-risk-fact--warning")}>
            <TrendingUp size={17} aria-hidden="true" />
            <span><strong>{number(rising)} rising clauses</strong><small>{rising ? "Above the recent-vs-prior threshold" : "No clause crosses the rising-rate threshold"}</small></span>
          </div>
          <div className={cn("sp-risk-fact", missingActions > 0 && "sp-risk-fact--warning")}>
            <FileCheck size={17} aria-hidden="true" />
            <span><strong>{number(missingActions)} missing action texts</strong><small>Among deviations with a linked failure</small></span>
          </div>
        </div>
        <p className="sp-risk-gap"><Info size={14} aria-hidden="true" />{text(provenance.followthrough_gap, "Corrective-action completion status is not modeled and is not inferred.")}</p>
      </CardContent>
    </Card>
  );
}

function ProvenancePanel({ provenance }: { provenance: JsonRecord }) {
  return (
    <Card className="sp-compliance-panel sp-provenance-panel">
      <CardHeader><div><CardTitle>Evidence provenance</CardTitle><CardDescription>No synthesis call</CardDescription></div><Database size={18} aria-hidden="true" /></CardHeader>
      <CardContent>
        <dl className="sp-provenance-list">
          <div><dt>Standard path</dt><dd>{text(provenance.standard_link, "Standard linkage unavailable")}</dd></div>
          <div><dt>Failure path</dt><dd>{text(provenance.failure_link, "Failure linkage unavailable")}</dd></div>
          <div><dt>Query mode</dt><dd>{labelize(provenance.query_mode || "direct_read_only_cypher")}</dd></div>
        </dl>
      </CardContent>
    </Card>
  );
}

function StandardDetailView({ detail, onBack }: { detail: StandardDetail; onBack: () => void }) {
  const standard = detail.standard;
  const pattern = record(detail.pattern);
  const risk = record(standard.risk);
  const provenance = record(detail.provenance);
  const reduceMotion = useReducedMotion();

  React.useEffect(() => {
    document.getElementById("sp-standard-detail-title")?.focus();
  }, [standard.family_id]);

  return (
    <motion.div
      className="sp-compliance-detail"
      key={`standard-${standard.family_id}`}
      initial={reduceMotion ? false : { opacity: 0, x: 18 }}
      animate={{ opacity: 1, x: 0 }}
      exit={reduceMotion ? undefined : { opacity: 0, x: 18 }}
      transition={{ duration: 0.22 }}
    >
      <header className="sp-compliance-detail__header">
        <Button variant="ghost" className="sp-detail-back" onClick={onBack}><ArrowLeft size={17} aria-hidden="true" />All standards</Button>
        <div className="sp-compliance-detail__title">
          <span className="sp-eyebrow">Standard detail</span>
          <h1 id="sp-standard-detail-title" tabIndex={-1}>{standard.name}</h1>
          <p>{standard.scope} · {number(standard.clause_count)} tested clauses</p>
        </div>
        <div className="sp-compliance-detail__badges"><RiskBadge risk={risk} /><ConfidenceBadge confidence={pattern.confidence} /></div>
      </header>

      <div className="sp-compliance-detail__grid">
        <main className="sp-compliance-detail__main">
          <PerformancePanel standard={standard} />
          <DeviationsPanel detail={detail} />
          <ClausePanel clauses={detail.clauses || []} />
        </main>
        <aside className="sp-compliance-detail__sidebar" aria-label="Pattern, flags, risk, and provenance">
          <PatternPanel pattern={pattern} />
          <CrossFlagsPanel flags={detail.cross_dimensional_flags || []} />
          <RiskPanel risk={risk} provenance={provenance} />
          <ProvenancePanel provenance={provenance} />
        </aside>
      </div>
    </motion.div>
  );
}

export default function ComplianceApp({ initialFamilyId }: ComplianceAppProps) {
  const [summary, setSummary] = React.useState<ComplianceSummary | null>(null);
  const [summaryError, setSummaryError] = React.useState("");
  const [summaryLoading, setSummaryLoading] = React.useState(true);
  const [summaryAttempt, setSummaryAttempt] = React.useState(0);
  const [selectedFamily, setSelectedFamily] = React.useState(() => initialFamilyId || familyFromHash());
  const [detail, setDetail] = React.useState<StandardDetail | null>(null);
  const [detailError, setDetailError] = React.useState("");
  const [detailLoading, setDetailLoading] = React.useState(Boolean(initialFamilyId || familyFromHash()));
  const [detailAttempt, setDetailAttempt] = React.useState(0);
  const detailCache = React.useRef(new Map<string, StandardDetail>());
  const reduceMotion = useReducedMotion();

  React.useEffect(() => {
    let active = true;
    setSummaryLoading(true);
    setSummaryError("");
    apiFetch<ComplianceSummary>("/api/compliance/summary")
      .then((payload) => { if (active) setSummary(payload); })
      .catch((error: unknown) => { if (active) setSummaryError(error instanceof Error ? error.message : String(error)); })
      .finally(() => { if (active) setSummaryLoading(false); });
    return () => { active = false; };
  }, [summaryAttempt]);

  React.useEffect(() => {
    if (!selectedFamily) {
      setDetail(null);
      setDetailError("");
      setDetailLoading(false);
      return;
    }
    const cached = detailCache.current.get(selectedFamily);
    if (cached && detailAttempt === 0) {
      setDetail(cached);
      setDetailError("");
      setDetailLoading(false);
      return;
    }
    let active = true;
    setDetail(null);
    setDetailError("");
    setDetailLoading(true);
    apiFetch<StandardDetail>(`/api/compliance/standards/${encodeURIComponent(selectedFamily)}`)
      .then((payload) => {
        if (!active) return;
        detailCache.current.set(selectedFamily, payload);
        setDetail(payload);
      })
      .catch((error: unknown) => {
        if (!active) return;
        const message = error instanceof Error ? error.message : String(error);
        setDetailError(message);
        toast.error(`Could not load ${selectedFamily}`, { description: message });
      })
      .finally(() => { if (active) setDetailLoading(false); });
    return () => { active = false; };
  }, [selectedFamily, detailAttempt]);

  React.useEffect(() => {
    const syncFromHistory = () => setSelectedFamily(familyFromHash());
    window.addEventListener("popstate", syncFromHistory);
    window.addEventListener("hashchange", syncFromHistory);
    return () => {
      window.removeEventListener("popstate", syncFromHistory);
      window.removeEventListener("hashchange", syncFromHistory);
    };
  }, []);

  React.useEffect(() => {
    if (initialFamilyId) setSelectedFamily(initialFamilyId);
  }, [initialFamilyId]);

  const openStandard = React.useCallback((familyId: string) => {
    setDetailAttempt(0);
    setSelectedFamily(familyId);
    updateComplianceHash(familyId);
  }, []);

  const closeStandard = React.useCallback(() => {
    setSelectedFamily("");
    setDetail(null);
    setDetailError("");
    updateComplianceHash();
    window.setTimeout(() => document.querySelector<HTMLElement>(".sp-page-header h1")?.focus(), 0);
  }, []);

  return (
    <div className="sp-compliance">
      <AnimatePresence mode="wait" initial={false}>
        {selectedFamily ? (
          <motion.div
            className="sp-compliance-detail-state"
            key={`detail-state-${selectedFamily}`}
            initial={reduceMotion ? false : { opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {detailLoading && <LoadingState label={`Loading ${selectedFamily} compliance evidence…`} />}
            {!detailLoading && detailError && (
              <div className="sp-compliance-detail-error">
                <Button variant="ghost" onClick={closeStandard}><ArrowLeft size={17} aria-hidden="true" />All standards</Button>
                <ErrorState error={detailError} retry={() => setDetailAttempt((value) => value + 1)} />
              </div>
            )}
            {!detailLoading && detail && <StandardDetailView detail={detail} onBack={closeStandard} />}
          </motion.div>
        ) : (
          <motion.div className="sp-compliance-list-state" key="list-state" initial={false} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            {summaryLoading && <LoadingState label="Loading compliance intelligence…" />}
            {!summaryLoading && summaryError && <ErrorState error={summaryError} retry={() => setSummaryAttempt((value) => value + 1)} />}
            {!summaryLoading && summary && <StandardsList summary={summary} onOpen={openStandard} />}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
