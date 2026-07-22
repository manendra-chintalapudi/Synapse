<div align="center">

# 🧠 Synapse
### AI-Powered Industrial Knowledge Intelligence Platform

**Unifying 7+ disconnected plant systems into one intelligent brain**

*Built for ET AI Hackathon 2026 — Problem Statement 8: "AI for Industrial Knowledge Intelligence: Unified Asset & Operations Brain"*

`DuckDB` · `Chroma` · `Neo4j AuraDB` · `FastAPI` · `React` · `OpenRouter LLMs`

</div>

---

## 🏭 The Problem

Steel plants run on fragmented islands of knowledge — a CMMS for equipment, a QMS for quality tests, SCADA for live telemetry, an ERP for materials, document repositories for SOPs, and compliance registers for standards. Answering one operational question today means manually stitching together **7+ systems**.

| Role | The pain, today |
|---|---|
| 🔧 **Maintenance** (e.g. Ramesh) | Digs through manuals and memory for equipment history and past RCAs |
| 🧪 **QA Leads** | Manually joins deviations to coils, raw materials, and process data |
| 📋 **Compliance** | Traces standards to deviations with static reports and no root-cause visibility |

**Synapse's thesis:** this isn't three problems — it's *one* problem (fragmented knowledge, no unified retrieval layer) wearing three different uniforms.

---

## ✨ What Synapse Does

Synapse federates structured data, documents, and relationships into a single conversational layer — and, where appropriate, safely *acts* on what it finds.

- 💬 **Ask once, get a synthesized answer** — not a pile of links to go verify yourself
- 🏷️ **Every claim is source-tagged** — see exactly which system produced each part of the answer
- ✅ **Human-approved actions** — recurring findings become draft system updates, never silent writes

---

## 🏗️ Architecture — Three Retrieval Layers, One Brain

No single retrieval method is enough for industrial knowledge. Synapse runs all three in parallel, behind one router and one synthesizer.

| Layer | Tech | Answers questions like… |
|---|---|---|
| 🗄️ **DFS** *(structured)* | DuckDB — federated over 7 plant systems | *"How many coils failed spec last month?"* |
| 📚 **RAG** *(semantic)* | Chroma — vectorized manuals, SOPs, reports | *"What does the manual say about bearing lube intervals?"* |
| 🕸️ **Graph** *(relational)* | Neo4j AuraDB — 3,797 nodes · 6,724 relationships | *"What past failures & RCAs connect to this equipment?"* |

```
┌─────────────────────────────────────────────────────────┐
│                     User Query                           │
└───────────────────────┬───────────────────────────────────┘
                         ▼
         ┌───────────────────────────────┐
         │      Tiered Hybrid Router      │
         │  Tier 1: Entity match          │
         │  Tier 2: Rule-based intent      │
         │  Tier 3: LLM fallback (last)     │
         └───────────────┬───────────────┘
                         ▼
        ┌────────────┬────────────┬────────────┐
        │    DFS     │    RAG     │   Graph    │
        │  (DuckDB)  │  (Chroma)  │  (Neo4j)   │
        └────────────┴────────────┴────────────┘
                         ▼
         ┌───────────────────────────────┐
         │         Synthesizer            │
         │  Direct Answer → Correlation    │
         │  → Implication → Action         │
         │  (source-cited, per sentence)   │
         └───────────────────────────────┘
```

---

## 🛡️ Why It's Technically Sound

- **Ontology-first:** the 11-entity graph schema was locked *before* any data generation, built in strict dependency order → zero broken references
- **No hallucinated numbers:** the synthesizer is system-prompt-barred from generating stats — every figure traces to a live DuckDB/Neo4j query
- **No hallucinated actions:** a **closed taxonomy of 6 action types**, with every field verified against real entity IDs before a human ever sees a confirm card
- **Human-in-the-loop:** "Draft + commit" — the agent proposes, a person approves, only then does it write
- **Free-tier-honest engineering:** Trino was dropped for DuckDB when its JVM footprint broke free-tier hosting; a 4-model LLM fallback chain (Hy3 → Nemotron 120B → gpt-oss-120b → Gemma 4 31B) keeps inference resilient with zero paid dependency

---

## 📊 Business Impact

- Eliminates manual cross-system search for the plant's three highest-friction roles
- Compliance dashboard evolves from static reporting → real decision support (deviation-to-failure funnels, graph-derived root-cause candidates, unresolved-deviation worklists)
- Every answer is auditable — traceable to the exact layer and record behind it

---

## 🚀 Scalability

- Retrieval/synthesis core is **domain-agnostic** — this project started in pharma and was re-pointed at steel without touching the pipeline
- New source systems slot in as new DuckDB catalogs / graph entity types, no router redesign needed
- Action taxonomy scales safely — new action types still inherit the same ID-verification guardrail

---

## 🎛️ Tech Stack

| | |
|---|---|
| **Structured data** | DuckDB |
| **Semantic search** | Chroma |
| **Knowledge graph** | Neo4j AuraDB |
| **LLM inference** | OpenRouter (Hy3 · Nemotron 120B · gpt-oss-120b · Gemma 4 31B) |
| **Backend** | FastAPI (Python) |
| **Frontend** | React |
| **Hosting** | Vercel (frontend) · Railway (backend + persistent volume) · Neo4j AuraDB |
| **Auth** | JWT, httpOnly cookies, RBAC (admin / qa / maintenance / ops) |

---

## 🎬 Demo Flow

Three queries, chosen so every retrieval layer gets screen time:

1. **🕸️ Graph-heavy** — RCA/failure question requiring multi-hop traversal
2. **🗄️ DFS-heavy** — structured QMS question over federated coil/quality data
3. **📚 RAG + Graph** — knowledge-retention question pulling manuals and correlating with graph relationships

---

## 🔍 Honest Open Items

We'd rather show you the punch list than hide it:

- ⏱️ **Latency** — ~26 of ~31s/query comes from the Nemotron 120B free-tier bottleneck. Fixes in flight: format-adaptive synthesis + tighter Tier-2 routing.
- 📈 **Compliance dashboard** is the least mature surface vs. Chat/RCA — actively being brought up to parity.

---

<div align="center">

### Built with real free-tier constraints, an internally consistent 3,797-node knowledge graph, and zero hand-waving.

</div>
