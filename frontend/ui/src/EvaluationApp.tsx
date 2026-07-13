import * as React from "react";
import * as Dialog from "@radix-ui/react-dialog";
import * as Tabs from "@radix-ui/react-tabs";
import {
  ArrowRight,
  BadgeCheck,
  BarChart3,
  BookOpenCheck,
  Check,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  Copy,
  Database,
  Download,
  ExternalLink,
  Factory,
  FileCheck2,
  FileJson,
  FileSearch,
  Gauge,
  GitBranch,
  Layers3,
  Link2,
  Network,
  Play,
  Scale,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  Target,
  TriangleAlert,
  UserCheck,
  X,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { toast } from "sonner";

import {
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  ErrorState,
  LoadingState,
  PillarHeader,
  SourcePill,
  cn,
  number,
} from "./ui";

type EvidenceStatus = "verified" | "scoped_verified" | "partial" | "pending" | "method_gap" | string;
type ProofTab = "extraction" | "graph" | "compliance" | "latency" | "provenance";
type ReviewScore = 0 | 1 | 2 | 3 | 4 | 5;

interface CriterionCard {
  id: string;
  criterion: number;
  label: string;
  status: EvidenceStatus;
  status_label: string;
  value: string;
  metric: string;
  detail: string;
  caveat: string;
  next_gate: string;
}

interface ExtractionBreakdown {
  id: string;
  label: string;
  documents: number;
  references: number;
  precision_pct: number;
  recall_pct: number;
  false_positives: number;
  false_negatives: number;
}

interface ExtractionEvidence {
  sample_size: number;
  precision_pct: number;
  recall_pct: number;
  f1_pct: number;
  true_positives: number;
  false_positives: number;
  false_negatives: number;
  self_document_id_count: number;
  non_self_reference_count: number;
  unknown_rejection: { true_positives: number; false_positives: number; false_negatives: number; precision: number; recall: number; f1: number };
  breakdown: ExtractionBreakdown[];
  entity_type_support: Record<string, number>;
  gold_sha256: string;
  annotation_method: string;
  extractor_module: string;
  production_usage: string;
  corpus_label: string;
  runtime_contract?: { passed: boolean; ontology_type_count: number; summary?: { valid_type_cases_passed?: number; valid_type_case_count?: number } };
  limitations: string[];
}

interface ShowcaseAnswer {
  id: string;
  question: string;
  role: string;
  source_layers: string[];
  ground_truth: string;
  model: string;
  sections: {
    direct: string;
    insight: string;
    action: string;
    sources: string[];
    so_what: string;
  };
  score: {
    pass_count: number;
    check_count: number;
    pass_rate_pct: number;
    fact_coverage_pct: number;
    insight: boolean;
    confidence: boolean;
    role_action: boolean;
    citations: boolean;
    healthy_execution: boolean;
  };
  expert_status: string;
  corpus_status: string;
  routes: { chat: string | null; rca: string | null; compliance: string | null };
}

interface AnswerBenchmark {
  case_count: number;
  automated_mean_pass_rate_pct: number;
  expert_validation_complete: boolean;
  generated_at: string;
  execution_scope: string;
  showcase_answers: ShowcaseAnswer[];
  all_cases: Array<{ id: string; question: string; pass_rate_pct: number; expert_status: string }>;
}

interface GraphEvidence {
  node_total: number;
  edge_total: number;
  node_type_count: number;
  relationship_type_count: number;
  directed_schema_link_count: number;
  node_counts: Record<string, number>;
  relationship_counts: Record<string, number>;
  checks: Record<string, number>;
  passed: boolean;
  live_parity?: {
    passed: boolean;
    generated_at: string;
    checks: Record<string, boolean>;
    scope_note: string;
  };
}

interface LatencyCase {
  id: string;
  question: string;
  total_s: number;
  routing_s: number;
  retrieval_s: number;
  synthesis_s: number;
  cached_repeat_s: number;
  layers: string[];
  model: string;
}

interface FastPathEvidence {
  case_count: number;
  passed: boolean;
  max_total_s: number;
  cases: Array<{ question: string; model_used: string; latency: { total_s: number; synthesis_s: number }; citation_count: number; passed: boolean }>;
  scope_note: string;
}

interface LatencyEvidence {
  measurement_surface: string;
  generated_at: string;
  sample_size: number;
  cold_uncached: { n: number; min_s: number; median_s: number; max_s: number; mean_s: number };
  cached_repeat: { n: number; min_s: number; median_s: number; max_s: number; mean_s: number };
  cases: LatencyCase[];
  scope_note: string;
  fast_path?: FastPathEvidence;
}

interface CompliancePattern {
  deviation_cohort_n: number;
  failure_linked_n: number;
  preceded_failure_within_30d_n: number;
  preceded_failure_rate_among_linked: number;
  preceded_failure_rate_95pct_wilson: number[];
  confidence: string;
}

interface ComplianceEvidence {
  window_days: number;
  patterns: Record<string, CompliancePattern>;
  accuracy: { n: number; true_positive: number; false_positive: number; true_negative: number; false_negative: number; accuracy: number; precision: number; recall: number; specificity: number };
  accuracy_scope: string;
  is1786: {
    deviation_cohort_n: number;
    failure_linked_n: number;
    downstream_n: number;
    rate_among_linked_pct: number;
    rate_full_cohort_pct: number;
    wilson_95pct: number[];
    confidence: string;
    top_root_cause: string;
    top_root_cause_n: number;
  };
}

interface ProvenanceDataset {
  name: string;
  status: string;
  rows: number;
  used_as: string;
  note?: string;
  machine_failures?: number;
  doi?: string;
  license?: string;
}

interface ProvenanceEvidence {
  real_csv_file_count: number;
  unique_real_payload_count: number;
  document_source_labels: Record<string, number>;
  datasets: ProvenanceDataset[];
}

interface ArtifactEvidence {
  label: string;
  file: string;
  url: string;
  status: EvidenceStatus;
  scope: string;
}

interface EvaluationData {
  schema_version: number;
  generated_from: string;
  generated_at: string;
  repository_base: string;
  headline: {
    criterion_count: number;
    verified_or_scoped_count: number;
    partial_count: number;
    expert_validation_complete: boolean;
    statement: string;
  };
  cards: CriterionCard[];
  entity_extraction: ExtractionEvidence;
  answer_benchmark: AnswerBenchmark;
  graph: GraphEvidence;
  latency: LatencyEvidence;
  compliance: ComplianceEvidence;
  provenance: ProvenanceEvidence;
  artifacts: ArtifactEvidence[];
}

type ReviewDimension = "factual" | "traceability" | "usefulness" | "role_action" | "confidence";

interface ExpertReview {
  case_id: string;
  question: string;
  reviewer: string;
  reviewer_role: string;
  scores: Record<ReviewDimension, ReviewScore>;
  critical_error: "" | "yes" | "no";
  notes: string;
  updated_at: string;
}

const REVIEW_KEY = "synapse_evaluation_expert_reviews_v1";
const REVIEW_DIMENSIONS: Array<{ id: ReviewDimension; label: string; hint: string }> = [
  { id: "factual", label: "Factual correctness", hint: "Matches the locked evidence without material error." },
  { id: "traceability", label: "Evidence traceability", hint: "A reviewer can follow each important fact to its source." },
  { id: "usefulness", label: "Operational usefulness", hint: "The answer helps a real plant decision." },
  { id: "role_action", label: "Role and action fit", hint: "The recommendation is appropriate for the named role." },
  { id: "confidence", label: "Confidence calibration", hint: "Certainty matches the strength and sample size of evidence." },
];

const CRITERION_ICONS: Record<number, LucideIcon> = {
  1: ScanSearch,
  2: Sparkles,
  3: Network,
  4: Clock3,
  5: ShieldCheck,
  6: Layers3,
};

const PROOF_FOR_CARD: Record<string, ProofTab | "answers"> = {
  entity_extraction: "extraction",
  answers: "answers",
  graph: "graph",
  latency: "latency",
  compliance: "compliance",
  discovery: "provenance",
};

function statusTone(status: EvidenceStatus): "neutral" | "indigo" | "green" | "amber" | "red" | "violet" | "cyan" {
  if (status === "verified") return "green";
  if (status === "scoped_verified") return "cyan";
  if (status === "partial") return "amber";
  if (status === "method_gap") return "red";
  if (status === "pending") return "neutral";
  return "violet";
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value || "—";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function percentage(value: number, digits = 1): string {
  return `${Number(value || 0).toFixed(digits)}%`;
}

function inlineEvidence(text: string): React.ReactNode {
  return String(text || "—").split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter(Boolean).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
    if (part.startsWith("`") && part.endsWith("`")) return <code key={index}>{part.slice(1, -1)}</code>;
    return <React.Fragment key={index}>{part}</React.Fragment>;
  });
}

function loadReviews(): Record<string, ExpertReview> {
  try {
    const value: unknown = JSON.parse(window.localStorage.getItem(REVIEW_KEY) || "{}");
    if (!value || typeof value !== "object" || Array.isArray(value)) return {};
    const sanitized: Record<string, ExpertReview> = {};
    for (const [caseId, raw] of Object.entries(value)) {
      if (!raw || typeof raw !== "object" || Array.isArray(raw)) continue;
      const candidate = raw as Partial<ExpertReview>;
      const rawScores = candidate.scores && typeof candidate.scores === "object"
        ? candidate.scores as Partial<Record<ReviewDimension, unknown>> : {};
      const scores = Object.fromEntries(REVIEW_DIMENSIONS.map(({ id }) => {
        const score = Number(rawScores[id]);
        return [id, Number.isInteger(score) && score >= 1 && score <= 5 ? score as ReviewScore : 0];
      })) as Record<ReviewDimension, ReviewScore>;
      sanitized[caseId] = {
        case_id: typeof candidate.case_id === "string" ? candidate.case_id : caseId,
        question: typeof candidate.question === "string" ? candidate.question : "",
        reviewer: typeof candidate.reviewer === "string" ? candidate.reviewer : "",
        reviewer_role: typeof candidate.reviewer_role === "string" ? candidate.reviewer_role : "",
        scores,
        critical_error: candidate.critical_error === "yes" || candidate.critical_error === "no" ? candidate.critical_error : "",
        notes: typeof candidate.notes === "string" ? candidate.notes : "",
        updated_at: typeof candidate.updated_at === "string" ? candidate.updated_at : "",
      };
    }
    return sanitized;
  } catch {
    return {};
  }
}

function emptyReview(answer: ShowcaseAnswer, previous?: ExpertReview): ExpertReview {
  return {
    case_id: answer.id,
    question: answer.question,
    reviewer: previous?.reviewer || "",
    reviewer_role: previous?.reviewer_role || "",
    scores: { factual: 0, traceability: 0, usefulness: 0, role_action: 0, confidence: 0 },
    critical_error: "",
    notes: "",
    updated_at: "",
  };
}

function isReviewComplete(review?: ExpertReview): boolean {
  if (!review || typeof review.reviewer !== "string" || typeof review.reviewer_role !== "string" || !review.reviewer.trim() || !review.reviewer_role.trim()) return false;
  if (review.critical_error !== "yes" && review.critical_error !== "no") return false;
  return Boolean(review.scores) && REVIEW_DIMENSIONS.every((dimension) => Number(review.scores[dimension.id]) > 0);
}

function scrollToId(id: string) {
  const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  window.requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" }));
}

function openHash(route: string | null) {
  if (route) window.location.hash = route;
}

function tryInChat(answer: ShowcaseAnswer) {
  const input = document.getElementById("q") as HTMLTextAreaElement | null;
  if (input) {
    input.value = answer.question;
    input.dispatchEvent(new Event("input", { bubbles: true }));
  }
  window.location.hash = answer.routes.chat || "#/chat";
  window.setTimeout(() => input?.focus(), 80);
}

async function copyAnswer(answer: ShowcaseAnswer) {
  const body = [
    answer.question,
    `Direct fact: ${answer.sections.direct}`,
    `Cross-reference: ${answer.sections.insight}`,
    `Operational implication: ${answer.sections.so_what}`,
    `Role-scoped action: ${answer.sections.action}`,
    "Sources:",
    ...answer.sections.sources.map((source) => `- ${source}`),
  ].join("\n\n");
  try {
    await navigator.clipboard.writeText(body);
    toast.success("Evidence answer copied");
  } catch {
    toast.error("Copy is unavailable in this browser");
  }
}

function CriterionGrid({ cards, onInspect }: { cards: CriterionCard[]; onInspect: (card: CriterionCard) => void }) {
  const reduceMotion = useReducedMotion();
  return <section className="sp-eval-criteria" aria-labelledby="eval-criteria-title">
    <div className="sp-eval-section-heading">
      <div><span>Judging scorecard</span><h2 id="eval-criteria-title">Six claims. Six evidence trails.</h2></div>
      <p>Headline results are intentionally paired with their next external validation gate.</p>
    </div>
    <div className="sp-eval-criteria__grid">
      {cards.map((card, index) => {
        const Icon = CRITERION_ICONS[card.criterion] || FileCheck2;
        return <motion.article key={card.id} className={cn("sp-eval-criterion", `sp-eval-criterion--${card.status}`)}
          initial={reduceMotion ? false : { opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * .045, duration: .24 }}>
          <div className="sp-eval-criterion__top">
            <span className="sp-eval-criterion__number">0{card.criterion}</span>
            <span className="sp-eval-criterion__icon"><Icon size={18} aria-hidden="true" /></span>
            <Badge tone={statusTone(card.status)}>{card.status_label}</Badge>
          </div>
          <h3>{card.label}</h3>
          <div className="sp-eval-criterion__value">{card.value}</div>
          <div className="sp-eval-criterion__metric">{card.metric}</div>
          <p>{card.detail}</p>
          <div className="sp-eval-criterion__scope"><TriangleAlert size={13} aria-hidden="true" /><span>{card.caveat}</span></div>
          <div className="sp-eval-criterion__gate"><Target size={13} aria-hidden="true" /><span><b>Next gate:</b> {card.next_gate}</span></div>
          <Button variant="ghost" size="sm" onClick={() => onInspect(card)}>Inspect proof <ArrowRight size={13} /></Button>
        </motion.article>;
      })}
    </div>
  </section>;
}

function AnswerEvidence({ answer, review, onReview }: { answer: ShowcaseAnswer; review?: ExpertReview; onReview: () => void }) {
  const reduceMotion = useReducedMotion();
  const committedExpertComplete = ["complete", "verified", "approved"].includes(String(answer.expert_status || "").toLowerCase());
  const layers = [
    { number: "01", label: "Direct fact", icon: Database, body: answer.sections.direct, tone: "graph" },
    { number: "02", label: "Cross-reference", icon: GitBranch, body: answer.sections.insight, tone: "cross" },
    { number: "03", label: "Operational implication", icon: Gauge, body: answer.sections.so_what, tone: "impact" },
    { number: "04", label: `Action for ${answer.role.replace("|", " / ")}`, icon: ClipboardCheck, body: answer.sections.action, tone: "action" },
  ];
  return <motion.article key={answer.id} className="sp-eval-answer" initial={reduceMotion ? false : { opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={reduceMotion ? undefined : { opacity: 0, x: -10 }} transition={{ duration: reduceMotion ? 0 : .2 }}>
    <header className="sp-eval-answer__header">
      <div>
        <div className="sp-eval-answer__badges">
          <Badge tone="indigo">{answer.score.pass_count}/{answer.score.check_count} automated checks</Badge>
          {answer.source_layers.map((layer) => <Badge key={layer} tone={layer === "Graph" ? "violet" : layer === "DFS" ? "cyan" : "green"}>{layer}</Badge>)}
          {answer.corpus_status.includes("synthetic") && <Badge tone="neutral">Locked synthetic/demo evidence</Badge>}
          <Badge tone={committedExpertComplete ? "green" : "amber"}>{committedExpertComplete ? "Committed expert review complete" : "Committed expert review pending"}</Badge>
          {isReviewComplete(review) && <Badge tone="cyan">Local review complete · export pending</Badge>}
        </div>
        <h3>{answer.question}</h3>
        <p>{answer.ground_truth}</p>
      </div>
      <div className="sp-eval-answer__score"><strong>{percentage(answer.score.pass_rate_pct, 0)}</strong><span>contract checks</span></div>
    </header>
    <div className="sp-eval-answer__layers">
      {layers.map(({ number: layerNumber, label, icon: Icon, body, tone }) => <section className={cn("sp-eval-layer", `sp-eval-layer--${tone}`)} key={label}>
        <div className="sp-eval-layer__heading"><span>{layerNumber}</span><Icon size={16} aria-hidden="true" /><h4>{label}</h4></div>
        <p>{inlineEvidence(body)}</p>
      </section>)}
    </div>
    <div className="sp-eval-answer__sources">
      <div className="sp-eval-answer__sources-title"><Link2 size={15} /><strong>Evidence cited</strong><span>{answer.model}</span></div>
      {answer.sections.sources.map((source) => <code key={source}>{source}</code>)}
    </div>
    <footer className="sp-eval-answer__actions">
      <Button onClick={() => tryInChat(answer)}><Play size={14} /> Try in Chat</Button>
      {answer.routes.rca && <Button variant="secondary" onClick={() => openHash(answer.routes.rca)}><Network size={14} /> Open RCA chain</Button>}
      {answer.routes.compliance && <Button variant="secondary" onClick={() => openHash(answer.routes.compliance)}><ShieldCheck size={14} /> Open compliance proof</Button>}
      <Button variant="outline" onClick={() => copyAnswer(answer)}><Copy size={14} /> Copy evidence</Button>
      <Button variant="outline" onClick={onReview}><UserCheck size={14} /> {review ? "Edit expert score" : "Score as expert"}</Button>
    </footer>
  </motion.article>;
}

function AnswerShowcase({ benchmark, reviews, onReview, onExport }: {
  benchmark: AnswerBenchmark;
  reviews: Record<string, ExpertReview>;
  onReview: (answer: ShowcaseAnswer) => void;
  onExport: () => void;
}) {
  const [selected, setSelected] = React.useState(benchmark.showcase_answers[0]?.id || "");
  const answer = benchmark.showcase_answers.find((item) => item.id === selected) || benchmark.showcase_answers[0];
  const completeCount = benchmark.showcase_answers.filter((item) => isReviewComplete(reviews[item.id])).length;
  if (!answer) return null;
  return <section className="sp-eval-showcase" id="eval-showcases" aria-labelledby="eval-showcase-title">
    <div className="sp-eval-section-heading">
      <div><span>Answer evidence</span><h2 id="eval-showcase-title">Four-layer synthesis, shown—not asserted.</h2></div>
      <div className="sp-eval-review-progress">
        <span><UserCheck size={14} /> {completeCount}/{benchmark.showcase_answers.length} local showcase reviews complete</span>
        <Button size="sm" variant="outline" onClick={onExport}><Download size={13} /> Export local reviews</Button>
      </div>
    </div>
    <div className="sp-eval-showcase__layout">
      <nav className="sp-eval-answer-picker" aria-label="Showcase answers">
        {benchmark.showcase_answers.map((item, index) => <button key={item.id} className={cn("sp-eval-answer-picker__item", selected === item.id && "is-active")}
          type="button" onClick={() => setSelected(item.id)} aria-current={selected === item.id ? "true" : undefined}>
          <span className="sp-eval-answer-picker__index">{String(index + 1).padStart(2, "0")}</span>
          <span className="sp-eval-answer-picker__copy"><strong>{item.question}</strong><small>{item.source_layers.join(" + ")} · {item.role.replace("|", " / ")}</small></span>
          {isReviewComplete(reviews[item.id]) ? <CheckCircle2 size={15} className="sp-eval-answer-picker__done" /> : <ArrowRight size={15} />}
        </button>)}
        <div className="sp-eval-answer-picker__scope">{benchmark.expert_validation_complete ? <CheckCircle2 size={14} /> : <TriangleAlert size={14} />}<p>{benchmark.expert_validation_complete ? "The committed expert gate is complete; browser-local scores remain separate until exported and incorporated." : "Automated checks validate answer structure and locked facts. An independent expert decision remains a separate gate."}</p></div>
      </nav>
      <AnimatePresence mode="wait"><AnswerEvidence answer={answer} review={reviews[answer.id]} onReview={() => onReview(answer)} /></AnimatePresence>
    </div>
  </section>;
}

function ExtractionProof({ evidence }: { evidence: ExtractionEvidence }) {
  const entityData = Object.entries(evidence.entity_type_support).map(([name, count]) => ({ name, count }));
  const passed = evidence.false_positives === 0 && evidence.false_negatives === 0 && evidence.runtime_contract?.passed === true;
  return <div className="sp-eval-proof-grid">
    <Card className="sp-eval-proof-card sp-eval-proof-card--wide">
      <CardHeader><div><CardTitle>Locked {evidence.sample_size}-document extraction test</CardTitle><CardDescription>Explicit canonical-ID resolution across manuals, SOPs and deviation reports.</CardDescription></div><Badge tone={passed ? "cyan" : "red"}>{passed ? "Scoped verified" : "Contract failed"}</Badge></CardHeader>
      <CardContent>
        <div className="sp-eval-proof-stats">
          <div><small>Precision</small><strong>{percentage(evidence.precision_pct, 0)}</strong></div>
          <div><small>Recall</small><strong>{percentage(evidence.recall_pct, 0)}</strong></div>
          <div><small>True positives</small><strong>{evidence.true_positives}</strong></div>
          <div><small>Stale IDs rejected</small><strong>{evidence.unknown_rejection.true_positives}</strong></div>
        </div>
        <div className="sp-eval-breakdown">
          {evidence.breakdown.map((row) => <div key={row.id}>
            <span><strong>{row.label}</strong><small>{row.documents} documents</small></span>
            <span><b>{row.references}</b><small>references</small></span>
            <span><b>{percentage(row.precision_pct, 0)} / {percentage(row.recall_pct, 0)}</b><small>P / R</small></span>
          </div>)}
        </div>
      </CardContent>
    </Card>
    <Card className="sp-eval-proof-card">
      <CardHeader><div><CardTitle>Entity coverage</CardTitle><CardDescription>Accepted canonical references by ontology type.</CardDescription></div><ScanSearch size={18} /></CardHeader>
      <CardContent><div className="sp-eval-chart sp-eval-chart--compact" role="img" aria-label={`Entity reference counts: ${entityData.map((item) => `${item.name} ${item.count}`).join(", ")}`}>
        <ResponsiveContainer width="100%" height="100%"><BarChart data={entityData} margin={{ top: 4, right: 4, bottom: 6, left: -18 }}>
          <CartesianGrid vertical={false} stroke="#eaecf4" /><XAxis dataKey="name" tickLine={false} axisLine={false} interval={0} angle={-20} textAnchor="end" height={55} /><YAxis tickLine={false} axisLine={false} allowDecimals={false} /><Tooltip /><Bar dataKey="count" name="References" fill="#5d66d8" radius={[6, 6, 0, 0]} />
        </BarChart></ResponsiveContainer>
      </div></CardContent>
    </Card>
    <Card className="sp-eval-proof-card">
      <CardHeader><div><CardTitle>Scope boundary</CardTitle><CardDescription>What this 100% result does and does not establish.</CardDescription></div><Scale size={18} /></CardHeader>
      <CardContent><ul className="sp-eval-limitations">{evidence.limitations.map((item) => <li key={item}><TriangleAlert size={13} /><span>{item}</span></li>)}</ul>
        <dl className="sp-eval-method-facts"><div><dt>Non-self references</dt><dd>{evidence.non_self_reference_count}</dd></div><div><dt>Document self-IDs</dt><dd>{evidence.self_document_id_count}</dd></div><div><dt>Manifest method</dt><dd>{evidence.annotation_method}</dd></div><div><dt>Production path</dt><dd><code>{evidence.production_usage}</code></dd></div><div><dt>Gold hash</dt><dd><code>{evidence.gold_sha256}</code></dd></div></dl>
      </CardContent>
    </Card>
  </div>;
}

function GraphProof({ graph }: { graph: GraphEvidence }) {
  const nodes = Object.entries(graph.node_counts).sort((a, b) => b[1] - a[1]).map(([name, count]) => ({ name, count }));
  const relationships = Object.entries(graph.relationship_counts).sort((a, b) => b[1] - a[1]);
  const checkLabels: Record<string, string> = { duplicate_nodes: "Duplicate nodes", duplicate_edges: "Duplicate edges", broken_endpoints: "Broken references", invalid_schema_edges: "Schema-invalid edges" };
  return <div className="sp-eval-proof-grid">
    <Card className="sp-eval-graph-hero sp-eval-proof-card--wide">
      <CardContent><div className="sp-eval-graph-hero__icon"><Network size={30} /></div><div><span>Locked ontology integrity</span><strong>{number(graph.node_total)} nodes <i>/</i> {number(graph.edge_total)} relationships</strong><p>{graph.node_type_count} node types · {graph.relationship_type_count} relationship names · {graph.directed_schema_link_count} allowed directed schema links</p></div><div className="sp-eval-graph-hero__badges"><Badge tone={graph.passed ? "green" : "red"}>{graph.passed ? "Local audit passes" : "Local audit failed"}</Badge>{graph.live_parity && <Badge tone={graph.live_parity.passed ? "cyan" : "red"}>{graph.live_parity.passed ? "Live Neo4j parity passes" : "Live parity failed"}</Badge>}</div></CardContent>
    </Card>
    <Card className="sp-eval-proof-card">
      <CardHeader><div><CardTitle>Integrity checks</CardTitle><CardDescription>Every count is computed from the locked graph artifacts.</CardDescription></div><BadgeCheck size={18} /></CardHeader>
      <CardContent><div className="sp-eval-integrity-grid">{Object.entries(graph.checks).map(([key, value]) => <div key={key} className={value === 0 ? "" : "is-failed"}>{value === 0 ? <CheckCircle2 size={17} /> : <TriangleAlert size={17} />}<span><strong>{value}</strong><small>{checkLabels[key] || key}</small></span></div>)}</div>
        <div className="sp-eval-scope-callout"><Scale size={15} /><p><b>Important wording:</b> {graph.relationship_type_count} relationship names are implemented across {graph.directed_schema_link_count} permitted directed label-to-label links. Those are different metrics.</p></div>
        {graph.live_parity && <div className="sp-eval-scope-callout"><Database size={15} /><p><b>Deployed parity:</b> {graph.live_parity.scope_note}</p></div>}
      </CardContent>
    </Card>
    <Card className="sp-eval-proof-card">
      <CardHeader><div><CardTitle>Node distribution</CardTitle><CardDescription>All {nodes.length} entity types in the evaluated graph.</CardDescription></div><BarChart3 size={18} /></CardHeader>
      <CardContent><div className="sp-eval-chart" role="img" aria-label={`Knowledge graph node counts: ${nodes.map((item) => `${item.name} ${item.count}`).join(", ")}`}><ResponsiveContainer width="100%" height="100%"><BarChart data={nodes} layout="vertical" margin={{ top: 2, right: 10, bottom: 2, left: 10 }}>
        <CartesianGrid horizontal={false} stroke="#eaecf4" /><XAxis type="number" tickLine={false} axisLine={false} /><YAxis type="category" dataKey="name" width={78} tickLine={false} axisLine={false} /><Tooltip /><Bar dataKey="count" name="Nodes" fill="#6972de" radius={[0, 7, 7, 0]} />
      </BarChart></ResponsiveContainer></div></CardContent>
    </Card>
    <Card className="sp-eval-proof-card sp-eval-proof-card--wide">
      <CardHeader><div><CardTitle>Relationship inventory</CardTitle><CardDescription>Exact edge counts behind the evidence chains.</CardDescription></div><Button size="sm" variant="secondary" onClick={() => openHash("#/graph")}><Network size={13} /> Explore graph</Button></CardHeader>
      <CardContent><div className="sp-eval-relations">{relationships.map(([name, count]) => <div key={name}><span>{name}</span><strong>{number(count)}</strong></div>)}</div></CardContent>
    </Card>
  </div>;
}

function ComplianceProof({ compliance }: { compliance: ComplianceEvidence }) {
  const patterns = Object.entries(compliance.patterns).map(([standard, pattern]) => ({
    standard,
    rate: Number((pattern.preceded_failure_rate_among_linked * 100).toFixed(2)),
    linked: pattern.failure_linked_n,
    downstream: pattern.preceded_failure_within_30d_n,
  }));
  return <div className="sp-eval-proof-grid">
    <Card className="sp-eval-compliance-hero sp-eval-proof-card--wide">
      <CardContent><div className="sp-eval-compliance-hero__score"><strong>{percentage(compliance.is1786.rate_among_linked_pct, 2)}</strong><span>of failure-linked IS:1786 deviations preceded failure within {compliance.window_days} days</span></div><div className="sp-eval-compliance-hero__sample"><b>{compliance.is1786.downstream_n} / {compliance.is1786.failure_linked_n}</b><span>Wilson 95% {compliance.is1786.wilson_95pct.join("–")}%</span><Badge tone="cyan">{compliance.is1786.confidence} sample confidence</Badge></div></CardContent>
    </Card>
    <Card className="sp-eval-proof-card">
      <CardHeader><div><CardTitle>Standard-family signal</CardTitle><CardDescription>Directional deviation → failure association, not causation.</CardDescription></div><ShieldCheck size={18} /></CardHeader>
      <CardContent><div className="sp-eval-chart" role="img" aria-label="Directional compliance linkage rates by standard family, with exact counts listed below"><ResponsiveContainer width="100%" height="100%"><BarChart data={patterns} margin={{ top: 8, right: 8, bottom: 6, left: -8 }}>
        <CartesianGrid vertical={false} stroke="#eaecf4" /><XAxis dataKey="standard" tickLine={false} axisLine={false} /><YAxis unit="%" tickLine={false} axisLine={false} /><Tooltip /><Bar dataKey="rate" name="Deviation before failure" fill="#7a5bc7" radius={[7, 7, 0, 0]} />
      </BarChart></ResponsiveContainer></div><div className="sp-eval-pattern-legend">{patterns.map((row) => <span key={row.standard}><b>{row.downstream}/{row.linked}</b> {row.standard}</span>)}</div></CardContent>
    </Card>
    <Card className="sp-eval-proof-card">
      <CardHeader><div><CardTitle>Temporal rule agreement</CardTitle><CardDescription>Balanced locked 30-event date-labelled set.</CardDescription></div><Target size={18} /></CardHeader>
      <CardContent><div className="sp-eval-accuracy"><strong>{compliance.accuracy.true_positive + compliance.accuracy.true_negative} / {compliance.accuracy.n}</strong><span>locked 30-day date-rule labels matched</span></div>
        <div className="sp-eval-confusion"><div className="is-positive"><b>{compliance.accuracy.true_positive}</b><span>True positive</span></div><div><b>{compliance.accuracy.false_positive}</b><span>False positive</span></div><div><b>{compliance.accuracy.false_negative}</b><span>False negative</span></div><div className="is-positive"><b>{compliance.accuracy.true_negative}</b><span>True negative</span></div></div>
        <p className="sp-eval-proof-note"><TriangleAlert size={13} /> {compliance.accuracy_scope}</p>
      </CardContent>
    </Card>
    <Card className="sp-eval-proof-card sp-eval-proof-card--wide">
      <CardHeader><div><CardTitle>Corroborated downstream pattern</CardTitle><CardDescription>Most common RCA among the {compliance.is1786.downstream_n} IS:1786 events inside the window.</CardDescription></div><Badge tone="violet">{compliance.is1786.top_root_cause_n} of {compliance.is1786.downstream_n} events</Badge></CardHeader>
      <CardContent><blockquote>{compliance.is1786.top_root_cause}</blockquote><div className="sp-eval-proof-actions"><Button variant="secondary" onClick={() => openHash("#/compliance/is-1786")}><ShieldCheck size={14} /> Inspect IS:1786 evidence</Button><Button variant="outline" onClick={() => openHash("#/rca/F1186")}><GitBranch size={14} /> Inspect an RCA chain</Button></div></CardContent>
    </Card>
  </div>;
}

function LatencyProof({ latency }: { latency: LatencyEvidence }) {
  const chart = latency.cases.map((item) => ({ name: item.id.replace(/_/g, " "), Routing: item.routing_s, Retrieval: item.retrieval_s, Synthesis: item.synthesis_s }));
  return <div className="sp-eval-proof-grid">
    <Card className="sp-eval-proof-card sp-eval-proof-card--wide">
      <CardHeader><div><CardTitle>Authenticated production baseline</CardTitle><CardDescription>{latency.measurement_surface} · server-reported timing · n={latency.sample_size}</CardDescription></div><Badge tone="amber">Operational baseline</Badge></CardHeader>
      <CardContent><div className="sp-eval-proof-stats sp-eval-proof-stats--latency"><div><small>Minimum</small><strong>{latency.cold_uncached.min_s.toFixed(2)}s</strong></div><div><small>Median</small><strong>{latency.cold_uncached.median_s.toFixed(2)}s</strong></div><div><small>Maximum</small><strong>{latency.cold_uncached.max_s.toFixed(2)}s</strong></div><div><small>Exact repeat</small><strong>{latency.cached_repeat.median_s.toFixed(2)}s</strong></div></div>
        <p className="sp-eval-proof-note sp-eval-proof-note--amber"><TriangleAlert size={13} /> {latency.scope_note}</p>
      </CardContent>
    </Card>
    <Card className="sp-eval-proof-card sp-eval-proof-card--wide">
      <CardHeader><div><CardTitle>Where the time went</CardTitle><CardDescription>Routing, retrieval and synthesis for the three uncached production questions.</CardDescription></div><Clock3 size={18} /></CardHeader>
      <CardContent><div className="sp-eval-chart sp-eval-chart--latency" role="img" aria-label="Production answer latency split into routing, retrieval and synthesis; exact totals are listed below"><ResponsiveContainer width="100%" height="100%"><BarChart data={chart} margin={{ top: 8, right: 8, bottom: 5, left: -8 }}>
        <CartesianGrid vertical={false} stroke="#eaecf4" /><XAxis dataKey="name" tickLine={false} axisLine={false} /><YAxis unit="s" tickLine={false} axisLine={false} /><Tooltip /><Legend /><Bar dataKey="Routing" stackId="time" fill="#9aa2ed" /><Bar dataKey="Retrieval" stackId="time" fill="#5963d5" /><Bar dataKey="Synthesis" stackId="time" fill="#8855c7" radius={[6, 6, 0, 0]} />
      </BarChart></ResponsiveContainer></div>
        <div className="sp-eval-latency-cases">{latency.cases.map((item) => <div key={item.id}><span><strong>{item.question}</strong><small>{item.layers.join(" + ")} · {item.model}</small></span><b>{item.total_s.toFixed(2)}s</b></div>)}</div>
      </CardContent>
    </Card>
    {latency.fast_path && <Card className="sp-eval-fastpath sp-eval-proof-card--wide">
      <CardContent><span className="sp-eval-fastpath__icon"><Zap size={23} /></span><div><small>Deterministic fast path</small><strong>{latency.fast_path.cases.filter((item) => item.passed).length}/{latency.fast_path.case_count} cited routine questions · ≤ {latency.fast_path.max_total_s.toFixed(2)}s · 0s synthesis</strong><p>{latency.fast_path.scope_note}</p></div><Badge tone={latency.fast_path.passed ? "green" : "red"}>{latency.fast_path.passed ? "Passed" : "Failed"}</Badge></CardContent>
    </Card>}
  </div>;
}

function ProvenanceProof({ provenance }: { provenance: ProvenanceEvidence }) {
  return <div className="sp-eval-proof-grid">
    <Card className="sp-eval-proof-card sp-eval-proof-card--wide">
      <CardHeader><div><CardTitle>Cross-functional evidence fabric</CardTitle><CardDescription>Four operational catalogs connect to graph and document evidence in one answer path.</CardDescription></div><Badge tone="amber">Integration demonstrated</Badge></CardHeader>
      <CardContent><div className="sp-eval-fabric" aria-label="Cross-functional source architecture">
        <div className="sp-eval-fabric__sources">{["ERP", "SCADA", "QMS", "CMMS"].map((source) => <span key={source}><Factory size={14} />{source}</span>)}</div>
        <ArrowRight size={20} className="sp-eval-fabric__arrow" />
        <div className="sp-eval-fabric__join"><Database size={18} /><strong>Federated SQL</strong><small>4 catalogs</small></div>
        <ArrowRight size={20} className="sp-eval-fabric__arrow" />
        <div className="sp-eval-fabric__evidence"><span><Network size={16} />Graph</span><span><BookOpenCheck size={16} />RAG</span></div>
      </div><p className="sp-eval-proof-note sp-eval-proof-note--amber"><TriangleAlert size={13} /> Capability and source integration are demonstrated. A before/after user study has not measured discovery improvement.</p></CardContent>
    </Card>
    <div className="sp-eval-datasets sp-eval-proof-card--wide">
      {provenance.datasets.map((dataset) => {
        const locallyDesignated = dataset.status === "locally_designated_real_source";
        return <Card className={cn("sp-eval-dataset", `sp-eval-dataset--${dataset.status}`)} key={dataset.name}>
          <CardContent><div className="sp-eval-dataset__top"><span><TriangleAlert size={18} /></span><Badge tone={locallyDesignated ? "amber" : "violet"}>{locallyDesignated ? "Locally designated source file" : "Official synthetic reference"}</Badge></div><h3>{dataset.name}</h3><strong>{number(dataset.rows)} rows</strong><p>{dataset.used_as}</p>{dataset.machine_failures !== undefined && <small>{number(dataset.machine_failures)} machine-failure labels · {dataset.license}</small>}{dataset.note && <div className="sp-eval-dataset__note">{dataset.note}</div>}{dataset.doi && <a href={`https://doi.org/${dataset.doi}`} target="_blank" rel="noreferrer">DOI {dataset.doi} <ExternalLink size={12} /></a>}</CardContent>
        </Card>;
      })}
    </div>
    <Card className="sp-eval-proof-card">
      <CardHeader><div><CardTitle>Source inventory</CardTitle><CardDescription>Duplicate content remains visible rather than inflating the claim.</CardDescription></div><FileSearch size={18} /></CardHeader>
      <CardContent><div className="sp-eval-proof-stats sp-eval-proof-stats--two"><div><small>Locally designated files</small><strong>{provenance.real_csv_file_count}</strong></div><div><small>Unique local payloads</small><strong>{provenance.unique_real_payload_count}</strong></div></div><p className="sp-eval-proof-note sp-eval-proof-note--amber"><TriangleAlert size={13} /> Local hashes and row counts are verified; upstream origin is not independently pinned for the two named source files.</p></CardContent>
    </Card>
    <Card className="sp-eval-proof-card">
      <CardHeader><div><CardTitle>Document provenance</CardTitle><CardDescription>The retrieval corpus is not represented as real plant documentation.</CardDescription></div><BookOpenCheck size={18} /></CardHeader>
      <CardContent><div className="sp-eval-document-sources">{Object.entries(provenance.document_source_labels).map(([label, count]) => <div key={label}><strong>{number(count)}</strong><span>{label}</span></div>)}</div><p className="sp-eval-proof-note"><TriangleAlert size={13} /> AI4I and the demo document corpus stay visibly labelled synthetic; they are not presented as real plant measurements.</p></CardContent>
    </Card>
  </div>;
}

function ProofTabs({ data, value, onValueChange }: { data: EvaluationData; value: ProofTab; onValueChange: (value: ProofTab) => void }) {
  const tabs: Array<{ id: ProofTab; label: string; icon: LucideIcon }> = [
    { id: "extraction", label: "Extraction", icon: ScanSearch },
    { id: "graph", label: "Graph integrity", icon: Network },
    { id: "compliance", label: "Compliance", icon: ShieldCheck },
    { id: "latency", label: "Latency", icon: Clock3 },
    { id: "provenance", label: "Provenance", icon: Layers3 },
  ];
  return <section className="sp-eval-proofs" id="eval-proofs" aria-labelledby="eval-proofs-title">
    <div className="sp-eval-section-heading"><div><span>Proof explorer</span><h2 id="eval-proofs-title">Inspect the benchmark behind each number.</h2></div><p>All views read the generated, browser-safe evaluation artifact—no LLM call is made.</p></div>
    <Tabs.Root className="sp-eval-tabs" value={value} onValueChange={(next) => onValueChange(next as ProofTab)}>
      <Tabs.List className="sp-eval-tabs__list" aria-label="Evaluation evidence tabs">{tabs.map(({ id, label, icon: Icon }) => <Tabs.Trigger className="sp-eval-tabs__trigger" value={id} key={id}><Icon size={15} />{label}</Tabs.Trigger>)}</Tabs.List>
      <Tabs.Content className="sp-eval-tabs__content" value="extraction"><ExtractionProof evidence={data.entity_extraction} /></Tabs.Content>
      <Tabs.Content className="sp-eval-tabs__content" value="graph"><GraphProof graph={data.graph} /></Tabs.Content>
      <Tabs.Content className="sp-eval-tabs__content" value="compliance"><ComplianceProof compliance={data.compliance} /></Tabs.Content>
      <Tabs.Content className="sp-eval-tabs__content" value="latency"><LatencyProof latency={data.latency} /></Tabs.Content>
      <Tabs.Content className="sp-eval-tabs__content" value="provenance"><ProvenanceProof provenance={data.provenance} /></Tabs.Content>
    </Tabs.Root>
  </section>;
}

function ArtifactSection({ data }: { data: EvaluationData }) {
  return <section className="sp-eval-methodology" id="eval-artifacts" aria-labelledby="eval-artifacts-title">
    <div className="sp-eval-section-heading"><div><span>Method and artifacts</span><h2 id="eval-artifacts-title">Reproduce every displayed claim.</h2></div><p>Generated {formatDate(data.generated_at)} from committed result files.</p></div>
    <div className="sp-eval-methodology__grid">
      <Card>
        <CardHeader><div><CardTitle>Evidence status vocabulary</CardTitle><CardDescription>A green badge is not allowed to hide a missing external gate.</CardDescription></div><Scale size={18} /></CardHeader>
        <CardContent><div className="sp-eval-status-legend"><div><Badge tone="green">Verified</Badge><p>Reproducible artifact passes the complete stated audit.</p></div><div><Badge tone="cyan">Scoped verified</Badge><p>Passes a deliberately narrow benchmark; scope is printed beside it.</p></div><div><Badge tone="amber">Partial</Badge><p>Internal evidence exists, but an external comparison or expert gate is open.</p></div><div><Badge tone="red">Method gap</Badge><p>Artifact is useful, but the evidence method lacks a required control.</p></div></div></CardContent>
      </Card>
      <Card>
        <CardHeader><div><CardTitle>Reproducibility contract</CardTitle><CardDescription>How this page avoids turning marketing copy into evidence.</CardDescription></div><FileCheck2 size={18} /></CardHeader>
        <CardContent><ul className="sp-eval-repro-list"><li><Check size={14} /><span>Metrics come from generated JSON, not hard-coded UI values.</span></li><li><Check size={14} /><span>Sample sizes and caveats stay attached to headlines.</span></li><li><Check size={14} /><span>Automated scores never substitute for expert validation.</span></li><li><Check size={14} /><span>Synthetic and unlabelled sources remain visibly disclosed.</span></li></ul><SourcePill>Static evidence artifact · no LLM</SourcePill></CardContent>
      </Card>
    </div>
    <div className="sp-eval-artifacts">
      {data.artifacts.map((artifact) => <a href={artifact.url} target="_blank" rel="noreferrer" className="sp-eval-artifact" key={artifact.file}>
        <span className="sp-eval-artifact__icon"><FileJson size={18} /></span><span className="sp-eval-artifact__copy"><strong>{artifact.label}</strong><code>{artifact.file}</code><small>{artifact.scope}</small></span><Badge tone={statusTone(artifact.status)}>{artifact.status.replace(/_/g, " ")}</Badge><ExternalLink size={14} />
      </a>)}
    </div>
  </section>;
}

function ExpertReviewDialog({ answer, existing, open, onOpenChange, onSave, onDelete }: {
  answer: ShowcaseAnswer | null;
  existing?: ExpertReview;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (review: ExpertReview) => void;
  onDelete: (caseId: string) => void;
}) {
  const [draft, setDraft] = React.useState<ExpertReview | null>(null);
  React.useEffect(() => {
    if (!answer) return;
    const previousReviewer = existing;
    setDraft(existing ? { ...existing, scores: { ...existing.scores } } : emptyReview(answer, previousReviewer));
  }, [answer, existing]);
  if (!answer || !draft) return null;
  const mean = REVIEW_DIMENSIONS.reduce((total, dimension) => total + draft.scores[dimension.id], 0) / REVIEW_DIMENSIONS.length;
  const portalContainer = document.getElementById("admin-react-root");
  return <Dialog.Root open={open} onOpenChange={onOpenChange}>
    <Dialog.Portal container={portalContainer}><Dialog.Overlay className="sp-dialog-overlay" /><Dialog.Content className="sp-dialog sp-eval-review-dialog" aria-describedby="eval-review-description">
      <div className="sp-dialog__header"><div><Dialog.Title className="sp-dialog__title">Independent expert score</Dialog.Title><Dialog.Description className="sp-dialog__description" id="eval-review-description">Saved only in this browser until you export it. It does not change Synapse's committed benchmark.</Dialog.Description></div><Dialog.Close asChild><Button size="icon" variant="ghost" aria-label="Close expert review"><X size={17} /></Button></Dialog.Close></div>
      <div className="sp-eval-review-question"><span>Case under review</span><strong>{answer.question}</strong><div>{answer.source_layers.map((layer) => <Badge tone="indigo" key={layer}>{layer}</Badge>)}</div></div>
      <div className="sp-eval-reviewer-fields"><label><span>Reviewer name / identifier</span><input value={draft.reviewer} onChange={(event) => setDraft({ ...draft, reviewer: event.target.value })} placeholder="Required for a complete review" /></label><label><span>Role / relevant experience</span><input value={draft.reviewer_role} onChange={(event) => setDraft({ ...draft, reviewer_role: event.target.value })} placeholder="e.g. steel plant QA lead" /></label></div>
      <div className="sp-eval-rubric">{REVIEW_DIMENSIONS.map((dimension) => <div className="sp-eval-rubric__row" key={dimension.id}><span><strong>{dimension.label}</strong><small>{dimension.hint}</small></span><div className="sp-eval-score-buttons" role="group" aria-label={`${dimension.label} score`}>{([1, 2, 3, 4, 5] as ReviewScore[]).map((score) => <button type="button" key={score} className={draft.scores[dimension.id] === score ? "is-selected" : ""} aria-pressed={draft.scores[dimension.id] === score} onClick={() => setDraft({ ...draft, scores: { ...draft.scores, [dimension.id]: score } })}>{score}</button>)}</div></div>)}</div>
      <div className="sp-eval-critical"><span><strong>Critical error?</strong><small>Would acting on this answer create a safety, quality or compliance risk?</small></span><div role="group" aria-label="Critical error status"><button type="button" aria-pressed={draft.critical_error === "no"} className={draft.critical_error === "no" ? "is-selected is-safe" : ""} onClick={() => setDraft({ ...draft, critical_error: "no" })}>No</button><button type="button" aria-pressed={draft.critical_error === "yes"} className={draft.critical_error === "yes" ? "is-selected is-danger" : ""} onClick={() => setDraft({ ...draft, critical_error: "yes" })}>Yes</button></div></div>
      <label className="sp-eval-review-notes"><span>Reviewer notes / required correction</span><textarea rows={3} value={draft.notes} onChange={(event) => setDraft({ ...draft, notes: event.target.value })} placeholder="Record missing evidence, corrections or approval rationale." /></label>
      <footer className="sp-eval-review-footer"><span className={isReviewComplete(draft) ? "is-complete" : ""}>{mean > 0 ? `Mean ${mean.toFixed(1)} / 5` : "Not scored"} · {isReviewComplete(draft) ? "complete" : "draft"}</span><div>{existing && <Button variant="ghost" onClick={() => onDelete(answer.id)}>Clear review</Button>}<Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button><Button onClick={() => onSave({ ...draft, updated_at: new Date().toISOString() })}><Check size={14} /> Save locally</Button></div></footer>
    </Dialog.Content></Dialog.Portal>
  </Dialog.Root>;
}

export default function EvaluationApp() {
  const [data, setData] = React.useState<EvaluationData | null>(null);
  const [error, setError] = React.useState("");
  const [loading, setLoading] = React.useState(true);
  const [activeProof, setActiveProof] = React.useState<ProofTab>("extraction");
  const [reviews, setReviews] = React.useState<Record<string, ExpertReview>>(loadReviews);
  const [reviewTarget, setReviewTarget] = React.useState<ShowcaseAnswer | null>(null);

  const load = React.useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/assets/evaluation_data.json", { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json() as EvaluationData;
      if (payload.schema_version !== 2) throw new Error(`Unsupported evaluation schema ${payload.schema_version ?? "unknown"}`);
      setData(payload);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unknown evaluation-data error");
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => { void load(); }, [load]);

  React.useEffect(() => {
    const closeWhenLeavingEvaluation = () => {
      const route = window.location.hash.replace(/^#\//, "").split("/")[0];
      if (route !== "admin") setReviewTarget(null);
    };
    window.addEventListener("hashchange", closeWhenLeavingEvaluation);
    window.addEventListener("popstate", closeWhenLeavingEvaluation);
    return () => {
      window.removeEventListener("hashchange", closeWhenLeavingEvaluation);
      window.removeEventListener("popstate", closeWhenLeavingEvaluation);
    };
  }, []);

  function persistReviews(next: Record<string, ExpertReview>) {
    setReviews(next);
    try { window.localStorage.setItem(REVIEW_KEY, JSON.stringify(next)); } catch { /* browser storage can be disabled */ }
  }

  function inspect(card: CriterionCard) {
    const destination = PROOF_FOR_CARD[card.id];
    if (destination === "answers") {
      scrollToId("eval-showcases");
      return;
    }
    setActiveProof(destination || "extraction");
    scrollToId("eval-proofs");
  }

  function saveReview(review: ExpertReview) {
    persistReviews({ ...reviews, [review.case_id]: review });
    setReviewTarget(null);
    toast.success(isReviewComplete(review) ? "Complete expert score saved locally" : "Expert-review draft saved locally");
  }

  function deleteReview(caseId: string) {
    const next = { ...reviews };
    delete next[caseId];
    persistReviews(next);
    setReviewTarget(null);
    toast.success("Local expert review cleared");
  }

  function exportReviews() {
    if (!data) return;
    const visibleCases = data.answer_benchmark.showcase_answers;
    const payload = {
      export_schema: 1,
      exported_at: new Date().toISOString(),
      benchmark_generated_at: data.generated_at,
      scope: "Local independent reviewer scores for Evaluation Lab showcase cases. This export is not part of the committed benchmark until independently reviewed and incorporated.",
      complete_showcase_reviews: visibleCases.filter((item) => isReviewComplete(reviews[item.id])).length,
      showcase_case_count: visibleCases.length,
      reviews: visibleCases.map((item) => reviews[item.id] || emptyReview(item)),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `synapse-expert-review-${new Date().toISOString().slice(0, 10)}.json`;
    anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast.success("Local expert reviews exported");
  }

  if (loading) return <div className="sp-app sp-eval"><div className="sp-app__inner"><LoadingState label="Loading evaluation evidence…" /></div></div>;
  if (error || !data) return <div className="sp-app sp-eval"><div className="sp-app__inner"><ErrorState error={error || "Evaluation data is unavailable"} retry={() => void load()} /></div></div>;

  return <section className="sp-app sp-eval" aria-label="Evaluation Lab">
    <div className="sp-app__inner">
      <PillarHeader eyebrow="Hackathon evaluation" title="Evaluation Lab" description="A judge-ready evidence surface for Synapse's extraction, answers, graph integrity, compliance detection, latency and cross-functional discovery.">
        <SourcePill>Committed artifacts · no LLM</SourcePill>
        <Button size="sm" variant="outline" onClick={() => scrollToId("eval-artifacts")}><FileJson size={13} /> Evidence files</Button>
      </PillarHeader>

      <section className="sp-eval-hero" aria-label="Evaluation status summary">
        <div className="sp-eval-hero__glow" />
        <div className="sp-eval-hero__copy"><span><Sparkles size={14} /> Evidence, not demo claims</span><h2>{data.headline.statement}</h2><p>Synapse separates repeatable internal proof from the external reviews and user studies that still need to happen.</p><div><Badge tone="green">{data.headline.verified_or_scoped_count} verified or scoped</Badge><Badge tone="amber">{data.headline.partial_count} partial</Badge><Badge tone={data.headline.expert_validation_complete ? "green" : "neutral"}>{data.headline.expert_validation_complete ? "Committed expert review complete" : "Committed expert review pending"}</Badge></div></div>
        <div className="sp-eval-hero__score"><span>Evaluation criteria</span><strong>{data.headline.criterion_count}</strong><small>schema v{data.schema_version} · {formatDate(data.generated_at)}</small></div>
      </section>

      <CriterionGrid cards={data.cards} onInspect={inspect} />
      <AnswerShowcase benchmark={data.answer_benchmark} reviews={reviews} onReview={setReviewTarget} onExport={exportReviews} />
      <ProofTabs data={data} value={activeProof} onValueChange={setActiveProof} />
      <ArtifactSection data={data} />
    </div>
    <ExpertReviewDialog answer={reviewTarget} existing={reviewTarget ? reviews[reviewTarget.id] : undefined} open={Boolean(reviewTarget)} onOpenChange={(open) => { if (!open) setReviewTarget(null); }} onSave={saveReview} onDelete={deleteReview} />
  </section>;
}
