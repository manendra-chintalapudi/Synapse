import * as React from "react";
import {
  BookOpenCheck, CheckCircle2, CircleUserRound, ClipboardCheck, FileSearch,
  Headphones, Mic, MicOff, RotateCcw, Search, Send, ShieldCheck, Sparkles,
  Volume2,
} from "lucide-react";
import { toast } from "sonner";
import { Badge, Button, Card, CardContent, CardHeader, CardTitle, PillarHeader, apiPost } from "./ui";

type Verification = "Unverified" | "Peer Confirmed" | "Approved";
interface TranscriptEntry { question: string; answer: string; }
interface KnowledgeCard {
  title: string;
  asset: string;
  situation: string;
  symptoms: string[];
  diagnostic_reasoning: string;
  recommended_checks: string[];
  exceptions: string;
  safety_warning: string;
  contributor: string;
  source: string;
  verification: Verification;
}
interface InterviewResponse { message: string; complete: boolean; model: string; }
interface ExtractionResponse { cards: KnowledgeCard[]; model: string; }

interface SpeechRecognitionEventLike {
  results: ArrayLike<{ isFinal: boolean; 0: { transcript: string } }>;
}
interface SpeechRecognitionLike {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  start: () => void;
  stop: () => void;
}
type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;
declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

const PROFILE = {
  name: "Arvind Rao",
  role: "Senior Furnace Equipment Engineer",
  equipment: ["Reheating Furnace #1", "Reheating Furnace #2", "Cooling-water circuit"],
  years_of_experience: 34,
  known_rcas: ["RCA1186 — insufficient heat dissipation", "RCA1120 — burner instability"],
};
const PLAN = [
  "Background and expertise",
  "Case-specific furnace incidents",
  "Tacit diagnostic reasoning",
  "Exceptions and safety boundaries",
];
const STORAGE_KEY = "synapse_knowledge_transfer_demo";
const VERIFICATION_ORDER: Verification[] = ["Unverified", "Peer Confirmed", "Approved"];

function speak(text: string) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text.replace("[INTERVIEW_COMPLETE]", "").trim());
  utterance.lang = "en-IN";
  utterance.rate = .96;
  window.speechSynthesis.speak(utterance);
}

function cardText(card: KnowledgeCard): string {
  return [card.title, card.asset, card.situation, ...card.symptoms, card.diagnostic_reasoning,
    ...card.recommended_checks, card.exceptions, card.safety_warning].join(" ");
}

function tokens(value: string): string[] {
  return value.toLowerCase().match(/[a-z0-9]+/g)?.filter((word) => word.length > 2) || [];
}

function VerificationBadge({ value }: { value: Verification }) {
  const tone = value === "Approved" ? "green" : value === "Peer Confirmed" ? "cyan" : "amber";
  return <Badge tone={tone}>{value}</Badge>;
}

function KnowledgeCardView({ card, index, onVerify }: { card: KnowledgeCard; index: number; onVerify: () => void }) {
  return <Card className="sp-kt-card">
    <CardHeader>
      <div><span className="sp-kt-card__number">Knowledge card {String(index + 1).padStart(2, "0")}</span><CardTitle>{card.title || "Untitled operational knowledge"}</CardTitle></div>
      <button className="sp-kt-verification" onClick={onVerify} title="Click to advance verification"><VerificationBadge value={card.verification} /></button>
    </CardHeader>
    <CardContent>
      <div className="sp-kt-facts"><div><span>Asset</span><strong>{card.asset || "Not specified"}</strong></div><div><span>Situation</span><strong>{card.situation || "Not specified"}</strong></div></div>
      {card.symptoms.length > 0 && <section><h4>Symptoms</h4><ul>{card.symptoms.map((item, i) => <li key={i}>{item}</li>)}</ul></section>}
      <section><h4>Diagnostic reasoning</h4><p>{card.diagnostic_reasoning || "No explicit diagnostic criteria captured."}</p></section>
      {card.recommended_checks.length > 0 && <section><h4>Recommended checks</h4><ol>{card.recommended_checks.map((item, i) => <li key={i}>{item}</li>)}</ol></section>}
      {(card.exceptions || card.safety_warning) && <div className="sp-kt-guardrails">
        {card.exceptions && <div><span>Exception</span><p>{card.exceptions}</p></div>}
        {card.safety_warning && <div className="is-safety"><span>Safety warning</span><p>{card.safety_warning}</p></div>}
      </div>}
      <footer><span><CircleUserRound size={13} /> {card.contributor || PROFILE.name}</span><span><FileSearch size={13} /> {card.source || "Interview transcript"}</span></footer>
    </CardContent>
  </Card>;
}

export default function KnowledgeTransferApp() {
  const [phase, setPhase] = React.useState<"ready" | "interview" | "extracting" | "complete">("ready");
  const [question, setQuestion] = React.useState("");
  const [answer, setAnswer] = React.useState("");
  const [transcript, setTranscript] = React.useState<TranscriptEntry[]>([]);
  const [cards, setCards] = React.useState<KnowledgeCard[]>([]);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState("");
  const [listening, setListening] = React.useState(false);
  const [ragQuestion, setRagQuestion] = React.useState("");
  const [ragResult, setRagResult] = React.useState<KnowledgeCard | null | undefined>(undefined);
  const recognitionRef = React.useRef<SpeechRecognitionLike | null>(null);
  const answerBaseRef = React.useRef("");
  const speechAvailable = Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);

  React.useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (saved?.cards?.length) { setCards(saved.cards); setTranscript(saved.transcript || []); setPhase("complete"); }
    } catch { /* A broken demo cache should never block the page. */ }
  }, []);
  React.useEffect(() => {
    if (!cards.length) return;
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ cards, transcript })); } catch { /* localStorage may be unavailable */ }
  }, [cards, transcript]);
  React.useEffect(() => () => { recognitionRef.current?.stop(); window.speechSynthesis?.cancel(); }, []);

  async function requestQuestion(entries: TranscriptEntry[]) {
    const result = await apiPost<InterviewResponse>("/api/knowledge-transfer/interview", { profile: PROFILE, plan: PLAN, transcript: entries });
    const clean = result.message.replace("[INTERVIEW_COMPLETE]", "").trim();
    if (clean) speak(clean);
    if (result.complete) {
      await finishInterview(entries);
    } else {
      setQuestion(clean);
      setPhase("interview");
    }
  }

  async function startInterview() {
    setBusy(true); setError(""); setCards([]); setTranscript([]); setRagResult(undefined);
    try { await requestQuestion([]); }
    catch (cause) { setError(cause instanceof Error ? cause.message : String(cause)); setPhase("ready"); }
    finally { setBusy(false); }
  }

  async function finishInterview(entries: TranscriptEntry[]) {
    setPhase("extracting"); setQuestion(""); setBusy(true);
    try {
      const result = await apiPost<ExtractionResponse>("/api/knowledge-transfer/extract", { profile: PROFILE, transcript: entries });
      setCards(result.cards.map((card) => ({ ...card, verification: "Unverified" })));
      setPhase("complete");
      toast.success(`${result.cards.length} knowledge card${result.cards.length === 1 ? "" : "s"} extracted for review`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
      setPhase("interview");
    } finally { setBusy(false); }
  }

  async function submitAnswer() {
    const text = answer.trim();
    if (!text || !question || busy) return;
    recognitionRef.current?.stop(); setListening(false);
    const entries = [...transcript, { question, answer: text }];
    setTranscript(entries); setAnswer(""); setBusy(true); setError("");
    try {
      if (entries.length >= 10) await finishInterview(entries);
      else await requestQuestion(entries);
    } catch (cause) { setError(cause instanceof Error ? cause.message : String(cause)); }
    finally { setBusy(false); }
  }

  function toggleListening() {
    if (!speechAvailable) return;
    if (listening) { recognitionRef.current?.stop(); setListening(false); return; }
    const Constructor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Constructor) return;
    const recognition = new Constructor();
    answerBaseRef.current = answer.trim() ? `${answer.trim()} ` : "";
    recognition.continuous = true; recognition.interimResults = true; recognition.lang = "en-IN";
    recognition.onresult = (event) => {
      let finalText = "", interimText = "";
      for (let i = 0; i < event.results.length; i += 1) {
        const value = event.results[i][0]?.transcript || "";
        if (event.results[i].isFinal) finalText += `${value} `; else interimText += value;
      }
      if (finalText) answerBaseRef.current += finalText;
      setAnswer(`${answerBaseRef.current}${interimText}`.trim());
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => { setListening(false); setError("Voice recognition stopped. You can continue in the text box."); };
    recognitionRef.current = recognition;
    try { recognition.start(); setListening(true); setError(""); }
    catch { setError("The microphone could not start. Type your answer instead."); }
  }

  function cycleVerification(index: number) {
    setCards((current) => current.map((card, i) => i === index
      ? { ...card, verification: VERIFICATION_ORDER[(VERIFICATION_ORDER.indexOf(card.verification) + 1) % VERIFICATION_ORDER.length] }
      : card));
  }

  function askCards(event: React.FormEvent) {
    event.preventDefault();
    const queryTokens = new Set(tokens(ragQuestion));
    const ranked = cards.map((card) => ({ card, score: tokens(cardText(card)).reduce((sum, word) => sum + (queryTokens.has(word) ? 1 : 0), 0) }))
      .sort((a, b) => b.score - a.score);
    setRagResult(ranked[0]?.score > 0 ? ranked[0].card : null);
  }

  function resetDemo() {
    recognitionRef.current?.stop(); window.speechSynthesis?.cancel(); localStorage.removeItem(STORAGE_KEY);
    setPhase("ready"); setQuestion(""); setAnswer(""); setTranscript([]); setCards([]); setError(""); setRagQuestion(""); setRagResult(undefined);
  }

  const progress = Math.min(100, Math.round(transcript.length / 10 * 100));
  return <main className="sp-kt">
    <div className="sp-kt__inner">
      <PillarHeader eyebrow="Institutional knowledge" title="Knowledge Transfer Interview" description="Capture hard-earned furnace expertise through an adaptive voice interview, then turn it into reviewable and governed knowledge cards.">
        <Badge tone="violet"><Sparkles size={12} /> Tencent HY3 · OpenRouter</Badge>
        {(phase !== "ready" || cards.length > 0) && <Button size="sm" variant="outline" onClick={resetDemo}><RotateCcw size={13} /> Reset demo</Button>}
      </PillarHeader>

      <div className="sp-kt-profile">
        <Card><CardContent><div className="sp-kt-profile__avatar">AR</div><div><span>Retiring employee</span><h2>{PROFILE.name}</h2><p>{PROFILE.role} · {PROFILE.years_of_experience} years</p></div><Badge tone="amber">High knowledge risk</Badge></CardContent></Card>
        <Card><CardContent><span>Known operational context</span><strong>{PROFILE.equipment.length} critical systems</strong><p>{PROFILE.equipment.join(" · ")}</p></CardContent></Card>
        <Card><CardContent><span>Interview plan</span><strong>{PLAN.length} structured topics</strong><p>Background · Cases · Reasoning · Safety</p></CardContent></Card>
      </div>

      {phase === "ready" && <Card className="sp-kt-start"><CardContent>
        <div className="sp-kt-start__icon"><Headphones size={30} /></div><h2>Ready to preserve Arvind's expertise?</h2>
        <p>Synapse will use his verified profile and RCA history to ask one focused question at a time. Answers can be spoken or typed.</p>
        <div className="sp-kt-plan">{PLAN.map((topic, index) => <div key={topic}><span>{index + 1}</span><strong>{topic}</strong><CheckCircle2 size={15} /></div>)}</div>
        <Button onClick={startInterview} disabled={busy}><Mic size={16} /> {busy ? "Preparing interview…" : "Start voice interview"}</Button>
      </CardContent></Card>}

      {(phase === "interview" || phase === "extracting") && <div className="sp-kt-interview">
        <section className="sp-kt-conversation">
          <div className="sp-kt-progress"><div><span>Interview progress</span><strong>{transcript.length} of 10 maximum exchanges</strong></div><div><i style={{ width: `${progress}%` }} /></div></div>
          {transcript.map((entry, index) => <div className="sp-kt-exchange" key={index}><div className="is-ai"><Sparkles size={15} /><p>{entry.question}</p></div><div className="is-person"><CircleUserRound size={15} /><p>{entry.answer}</p></div></div>)}
          {phase === "extracting" ? <div className="sp-kt-extracting"><Sparkles size={24} /><strong>Structuring the interview into knowledge cards…</strong><p>The original Q/A transcript remains unchanged.</p></div> : <>
            <div className="sp-kt-current"><div className="sp-kt-current__label"><span><Sparkles size={14} /> Synapse interviewer</span><button onClick={() => speak(question)} aria-label="Read question aloud"><Volume2 size={15} /></button></div><p>{busy && !question ? "Preparing the next question…" : question}</p></div>
            <div className="sp-kt-answer"><label htmlFor="kt-answer">Your answer</label><textarea id="kt-answer" value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="Speak or type your experience here…" rows={5} disabled={busy} onKeyDown={(event) => { if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) submitAnswer(); }} />
              <div><span>{speechAvailable ? "Mic and text are both available" : "Speech recognition unavailable — text still works"}</span><div><Button variant={listening ? "danger" : "outline"} onClick={toggleListening} disabled={!speechAvailable || busy}>{listening ? <MicOff size={15} /> : <Mic size={15} />}{listening ? "Stop listening" : "Speak"}</Button><Button onClick={submitAnswer} disabled={!answer.trim() || busy}><Send size={15} /> {busy ? "Thinking…" : "Submit answer"}</Button></div></div>
            </div>
          </>}
        </section>
        <aside><Card><CardHeader><CardTitle>Evidence context</CardTitle></CardHeader><CardContent><div className="sp-kt-context"><span>Profile</span><strong>{PROFILE.role}</strong><span>Equipment</span><strong>{PROFILE.equipment.join(", ")}</strong><span>Known RCAs</span>{PROFILE.known_rcas.map((rca) => <strong key={rca}>{rca}</strong>)}</div></CardContent></Card><Card><CardHeader><CardTitle>Capture safeguards</CardTitle></CardHeader><CardContent><ul className="sp-kt-safeguards"><li><ClipboardCheck size={14} /> Original Q/A is retained</li><li><ShieldCheck size={14} /> Cards begin unverified</li><li><BookOpenCheck size={14} /> Human approval stays separate</li></ul></CardContent></Card></aside>
      </div>}

      {error && <div className="sp-kt-error" role="alert"><strong>Knowledge Transfer could not continue.</strong><span>{error}</span></div>}

      {phase === "complete" && <>
        <div className="sp-kt-results-head"><div><span>Extraction complete</span><h2>{cards.length} knowledge cards ready for review</h2><p>Click a verification badge to cycle from Unverified to Peer Confirmed to Approved.</p></div><div><Badge tone="amber">{cards.filter((card) => card.verification === "Unverified").length} unverified</Badge><Badge tone="green">{cards.filter((card) => card.verification === "Approved").length} approved</Badge></div></div>
        <div className="sp-kt-cards">{cards.map((card, index) => <KnowledgeCardView key={`${card.title}-${index}`} card={card} index={index} onVerify={() => cycleVerification(index)} />)}</div>
        <Card className="sp-kt-rag"><CardHeader><div><CardTitle>Ask the captured knowledge</CardTitle><p>Demo governed retrieval using a transparent keyword match across these cards.</p></div><Badge tone="indigo"><Search size={12} /> Local card retrieval</Badge></CardHeader><CardContent>
          <form onSubmit={askCards}><input value={ragQuestion} onChange={(event) => setRagQuestion(event.target.value)} placeholder="What should I check when furnace temperature rises unevenly?" /><Button type="submit" disabled={!ragQuestion.trim()}><Search size={15} /> Ask</Button></form>
          {ragResult === null && <div className="sp-kt-rag__empty">No captured knowledge card shares meaningful keywords with that question.</div>}
          {ragResult && <div className="sp-kt-rag__answer"><strong>{ragResult.title}</strong><p>{ragResult.diagnostic_reasoning}</p>{ragResult.recommended_checks.length > 0 && <ol>{ragResult.recommended_checks.map((item, i) => <li key={i}>{item}</li>)}</ol>}<footer><span>Citation: {ragResult.contributor || PROFILE.name} · {ragResult.source || "Interview transcript"}</span><VerificationBadge value={ragResult.verification} /></footer></div>}
        </CardContent></Card>
      </>}
    </div>
  </main>;
}
