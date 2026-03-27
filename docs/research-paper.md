# Chaos 2 Clarity: Production Architecture and Evaluation of an LLM-Orchestrated BI Layer over Heterogeneous, Uncurated Enterprise Data Sources

**Bankupalli Ravi Teja**  
*Independent Research | Hyderabad, India*  
Profiles: [GitHub](https://github.com/ravii-teja/c2c) | [LinkedIn](https://www.linkedin.com/in/raviiteja/)

## Abstract

Large language models (LLMs) are rapidly being adopted as conversational interfaces and intelligent agents for business intelligence (BI) [[1]](https://arxiv.org/abs/2303.08774), [[2]](https://arxiv.org/abs/2402.06196). However, most existing AI-over-BI systems assume a reasonably curated analytical backend: a centralized data warehouse, consistent schemas, and a manually defined semantic layer of entities and metrics [[3]](https://arxiv.org/abs/2510.04023), [[4]](https://arxiv.org/abs/2509.23988). In many real-world organizations—especially mid-market and rapidly evolving businesses—data remains scattered across heterogeneous, uncurated sources such as operational databases, data lakes, spreadsheets, SaaS APIs, logs, and documents, with incomplete documentation and no unified semantic catalog [[5]](https://arxiv.org/abs/2510.23587), [[6]](https://arxiv.org/abs/2505.18458). Traditional "warehouse-first" modernization programs are often too slow or expensive, leaving these organizations unable to fully exploit LLM-powered analytics.

This paper presents **Chaos 2 Clarity**, a production-oriented architecture and applied system for an LLM-orchestrated BI layer designed to operate directly over heterogeneous, uncurated enterprise data sources. Chaos 2 Clarity introduces: (i) an automated, LLM-assisted **semantic synthesis layer** that discovers data assets and infers entities, metrics, relationships, and policies across sources [[7]](https://arxiv.org/abs/2503.09003), [[8]](https://arxiv.org/abs/2502.15182); (ii) a **multi-agent AI-over-BI orchestration layer** that performs intent understanding, cross-source query planning, SQL and retrieval-augmented generation (RAG) [[9]](https://arxiv.org/abs/2005.11401), [[10]](https://arxiv.org/abs/2312.10997), explanation, and governance; and (iii) **cross-cutting mechanisms** for query caching and feedback-driven metadata refinement. We define an evaluation methodology spanning semantic layer quality, BI answer accuracy, system performance and robustness, and user adoption. We outline an experimental plan to compare Chaos 2 Clarity against curated BI baselines on realistic enterprise workloads.


## 1  Introduction

Large language models have enabled natural-language interfaces to data and BI, promising to democratize analytics and reduce reliance on specialist data teams [[11]](https://arxiv.org/abs/2303.08774), [[12]](https://arxiv.org/abs/2307.09288). Recent research prototypes and commercial products highlight LLM-powered agents that generate SQL from natural language, build dashboards, and automate portions of the analytical workflow [[3]](https://arxiv.org/abs/2510.04023), [[13]](https://arxiv.org/abs/2407.15186), [[14]](https://arxiv.org/abs/2411.06102). These systems, however, largely presuppose that the hard work of data curation has already been done: the organization has a central warehouse or lakehouse, reasonably consistent schemas, and a well-defined semantic layer encoding business entities and metrics.

In day-to-day practice, many organizations do not meet these prerequisites. Business-critical data is spread across multiple operational systems and analytical stores; exports and spreadsheets proliferate; SaaS tools hold key fragments of process and customer state; and documentation is sparse or outdated [[5]](https://arxiv.org/abs/2510.23587), [[15]](https://arxiv.org/abs/2409.17216). In such environments, insisting on a complete, manually curated warehouse and semantic model before deploying AI severely delays any benefits. Yet, applying LLMs naively on top of raw, heterogeneous sources without structure or governance risks brittle, inaccurate, or unsafe analytics [[16]](https://arxiv.org/abs/2305.15038), [[17]](https://arxiv.org/abs/2507.12425).

Benchmarks illustrate the severity of this gap. While GPT-4-based agents achieve ~86% accuracy on Spider 1.0 [[18]](https://arxiv.org/abs/1809.08887), performance drops dramatically on Spider 2.0 [[19]](https://arxiv.org/abs/2411.07763)—which involves complex enterprise environments with over 3,000 columns and multiple SQL dialects—where even advanced models achieve only ~10% success. This underscores that current NL2SQL and AI-over-BI systems are optimized for curated, structured settings rather than the heterogeneous, evolving data realities of real enterprises [[13]](https://arxiv.org/abs/2407.15186), [[19]](https://arxiv.org/abs/2411.07763).

This paper asks: *Can we design a production-grade, LLM-orchestrated BI layer whose first responsibility is to bring structure and governance to chaotic, multi-source data, and only then expose it as an AI-assisted BI interface?* We answer this with **Chaos 2 Clarity**.

### 1.1  Research Gap

Existing work on LLM-over-data [[3]](https://arxiv.org/abs/2510.04023), [[13]](https://arxiv.org/abs/2407.15186), [[20]](https://aclanthology.org/2023.emnlp-demo.31/), [[21]](https://arxiv.org/abs/2407.09305) largely presupposes a curated backend. NL2SQL systems [[13]](https://arxiv.org/abs/2407.15186), [[22]](https://arxiv.org/abs/2308.15363) are evaluated on clean benchmarks (Spider [[18]](https://arxiv.org/abs/1809.08887), BIRD [[23]](https://arxiv.org/abs/2305.03111)) with well-specified schemas. LLM-assisted data catalog tools [[7]](https://arxiv.org/abs/2503.09003), [[8]](https://arxiv.org/abs/2502.15182), [[24]](https://ceur-ws.org/Vol-3827/paper4.pdf) address metadata enrichment but stop short of full BI orchestration. Multi-agent frameworks [[25]](https://arxiv.org/abs/2601.13671), [[26]](https://arxiv.org/abs/2308.08155), [[27]](https://arxiv.org/abs/2601.12560) provide orchestration primitives but do not address synthesizing a semantic model from raw, heterogeneous sources. RAG systems [[9]](https://arxiv.org/abs/2005.11401), [[10]](https://arxiv.org/abs/2312.10997), [[28]](https://arxiv.org/abs/2507.12425) are primarily designed for unstructured documents rather than mixed structured-unstructured enterprise environments. **No existing production-oriented system simultaneously addresses (a) automated semantic synthesis over uncurated heterogeneous sources, (b) multi-agent BI orchestration over the resulting semantic layer, and (c) feedback-driven continual refinement—all within a governance-aware, deployable architecture.** Chaos 2 Clarity fills this gap.


## 2  Problem Statement and Research Questions

We consider organizations where data relevant to business intelligence is:

- **Heterogeneous**: relational databases, data lakes, CSV/Excel files, SaaS APIs, logs, and document stores [[5]](https://arxiv.org/abs/2510.23587), [[6]](https://arxiv.org/abs/2505.18458).
- **Uncurated**: inconsistent naming conventions, missing or partial documentation, no unified semantic catalog [[7]](https://arxiv.org/abs/2503.09003).
- **Evolving**: schemas change, new sources appear, and governance policies need continuous updates [[15]](https://arxiv.org/abs/2409.17216), [[17]](https://arxiv.org/abs/2507.12425).

**RQ1 – Semantic Unification over Uncurated Sources.** How effectively can an automated, LLM-assisted semantic layer builder discover entities, metrics, and relationships across heterogeneous, uncurated enterprise sources, compared to a manually modeled semantic layer [[7]](https://arxiv.org/abs/2503.09003), [[8]](https://arxiv.org/abs/2502.15182), [[24]](https://ceur-ws.org/Vol-3827/paper4.pdf)?

**RQ2 – Agent Architecture and Orchestration.** Which multi-agent orchestration strategies yield the best trade-off between answer correctness, latency, and resource cost when executing BI tasks over this semantic layer [[25]](https://arxiv.org/abs/2601.13671), [[26]](https://arxiv.org/abs/2308.08155), [[27]](https://arxiv.org/abs/2601.12560), [[29]](https://arxiv.org/abs/2509.10769)?

**RQ3 – Analytics Quality and User Trust.** To what extent can business users obtain correct, complete, and trustworthy answers to everyday BI questions via the LLM-orchestrated BI layer—relative to a curated BI baseline [[3]](https://arxiv.org/abs/2510.04023), [[13]](https://arxiv.org/abs/2407.15186), [[14]](https://arxiv.org/abs/2411.06102)?

**RQ4 – Operational Sustainability.** What mechanisms for monitoring, feedback-driven refinement, and query caching are necessary to keep such a system accurate, efficient, and safe over time [[9]](https://arxiv.org/abs/2005.11401), [[17]](https://arxiv.org/abs/2507.12425), [[30]](https://arxiv.org/abs/2309.15217)?


## 3  Contributions

**C1 – Semantic Layer from Chaos.** A method and tooling to automatically discover data assets, profile their structure, infer entities, metrics, relationships, and basic policies, and synthesize these into a usable semantic layer. This extends prior work on LLM-assisted metadata enrichment [[7]](https://arxiv.org/abs/2503.09003), [[8]](https://arxiv.org/abs/2502.15182) and schema matching [[31]](https://arxiv.org/abs/2507.14376) to a full semantic synthesis pipeline.

**C2 – Agentic AI-over-BI Architecture.** A concrete, production-oriented architecture for an LLM-orchestrated BI layer. This builds on multi-agent frameworks [[25]](https://arxiv.org/abs/2601.13671), [[26]](https://arxiv.org/abs/2308.08155) and ReAct-style orchestration [[32]](https://arxiv.org/abs/2210.03629) and adapts them specifically to BI workloads.

**C3 – Applied System: Chaos 2 Clarity.** An end-to-end system implementation that can sit in front of existing data infrastructure and BI tools. This addresses the gap identified by data agent surveys [[5]](https://arxiv.org/abs/2510.23587), [[6]](https://arxiv.org/abs/2505.18458) regarding the absence of production-ready systems for heterogeneous, uncurated enterprise data.

**C4 – Query Caching and Feedback-Driven Refinement.** Cross-cutting mechanisms for query result caching and feedback-driven metadata refinement, allowing the system to reduce latency and improve semantic mappings and answer accuracy over time [[9]](https://arxiv.org/abs/2005.11401), [[17]](https://arxiv.org/abs/2507.12425), [[30]](https://arxiv.org/abs/2309.15217).

**C5 – Evaluation Methodology for AI-over-BI on Messy Data.** A comprehensive evaluation plan spanning semantic layer quality, BI answer correctness and coverage, system performance and robustness, and user adoption and trust. This complements existing NL2SQL benchmarks [[18]](https://arxiv.org/abs/1809.08887), [[23]](https://arxiv.org/abs/2305.03111) that assume curated, well-documented schemas.


## 4  Related Work

### 4.1  LLM-Based Text-to-SQL and NL2SQL

Shi et al. [[13]](https://arxiv.org/abs/2407.15186) survey LLM-based text-to-SQL methods, covering prompt engineering and fine-tuning paradigms. The Spider 1.0 benchmark [[18]](https://arxiv.org/abs/1809.08887) and BIRD benchmark [[23]](https://arxiv.org/abs/2305.03111) are standard evaluation platforms, with recent work achieving ~86% and ~70% execution accuracy respectively. Both benchmarks, however, assume well-curated schemas. Spider 2.0 [[19]](https://arxiv.org/abs/2411.07763) introduces enterprise-level complexity—multiple SQL dialects, large schemas, and cross-database workflows—revealing that state-of-the-art LLMs achieve only ~10% success, confirming a substantial gap between benchmark settings and real-world enterprise data complexity. SiriusBI [[14]](https://arxiv.org/abs/2411.06102) represents a production-oriented NL2SQL system for a single enterprise domain but still requires a pre-built semantic model. Chaos 2 Clarity complements these by addressing the *semantic synthesis* step that must precede NL2SQL in organizations with uncurated data.

### 4.2  LLM Agents for Data Analytics

Ma et al.'s InsightPilot [[20]](https://aclanthology.org/2023.emnlp-demo.31/) deploys LLM agents for automated data exploration but assumes a pre-structured analytical environment. Cheng et al. [[16]](https://arxiv.org/abs/2305.15038) evaluate GPT-4's capability as a data analyst. Surveys by Rahman et al. [[3]](https://arxiv.org/abs/2510.04023) and Chen et al. [[4]](https://arxiv.org/abs/2509.23988) map the landscape of LLM data science agents, noting that real-world enterprise environments remain far more complex than current benchmarks. The Data Agents survey by Zhu et al. [[5]](https://arxiv.org/abs/2510.23587) formalizes the requirements for agents operating over data lakes and heterogeneous systems, emphasizing reliability, governance, and reproducibility as key challenges.

### 4.3  Retrieval-Augmented Generation over Enterprise Data

RAG systems [[9]](https://arxiv.org/abs/2005.11401), [[10]](https://arxiv.org/abs/2312.10997) extend LLMs with retrieval from external knowledge bases. Cheerla [[28]](https://arxiv.org/abs/2507.12425) proposes a hybrid retrieval framework for structured enterprise data. Gao et al. [[10]](https://arxiv.org/abs/2312.10997) survey advanced RAG architectures including multi-round and agentic retrieval strategies. Pan et al. [[33]](https://arxiv.org/abs/2203.16714) demonstrate end-to-end table question answering via RAG. Chaos 2 Clarity extends these by combining RAG over both structured (SQL) and unstructured (document) sources under a unified semantic orchestration layer.

### 4.4  Automated Metadata Discovery and Data Cataloging

Singh et al. [[7]](https://arxiv.org/abs/2503.09003) demonstrate LLM-based metadata enrichment for enterprise catalogs, achieving >80% ROUGE-1 F1 and ~90% acceptance by data stewards. The LEDD system [[8]](https://arxiv.org/abs/2502.15182) employs LLMs to generate hierarchical semantic catalogs over data lakes. LLMDapCAT [[24]](https://ceur-ws.org/Vol-3827/paper4.pdf) uses LLM+RAG pipelines for automated metadata extraction and data profiling. In schema matching, SCHEMORA [[31]](https://arxiv.org/abs/2507.14376) introduces a multi-stage LLM recommendation framework achieving new state-of-the-art performance. Chaos 2 Clarity integrates these capabilities into a coherent, governance-aware BI system.

### 4.5  Multi-Agent Orchestration Frameworks

Adimulam et al. [[25]](https://arxiv.org/abs/2601.13671) survey architectures, protocols, and enterprise adoption patterns for multi-agent LLM systems, identifying planning, state management, and policy enforcement as key orchestration concerns. Wu et al. [[26]](https://arxiv.org/abs/2308.08155) introduce AutoGen, a widely-adopted multi-agent conversation framework. Arunkumar et al. [[27]](https://arxiv.org/abs/2601.12560) examine architectures for orchestration control, memory backends, and tool integration standards. The ReAct pattern [[32]](https://arxiv.org/abs/2210.03629) and Plan-then-Execute paradigm [[34]](https://arxiv.org/abs/2509.08646) are foundational primitives for agent reasoning. AgentArch [[29]](https://arxiv.org/abs/2509.10769) benchmarks agent architectures for enterprise tasks, showing that orchestration strategy significantly affects success rates.

### 4.6  Governance, Explainability, and Trust in AI Analytics

Governance and explainability are critical for enterprise adoption [[15]](https://arxiv.org/abs/2409.17216), [[16]](https://arxiv.org/abs/2305.15038). Gupta et al. [[15]](https://arxiv.org/abs/2409.17216) illustrate how dataset-centric considerations are essential for robust AI governance. Arunkumar et al. [[27]](https://arxiv.org/abs/2601.12560) highlight that deployed agentic systems must satisfy stringent requirements on reliability and reproducibility. Chaos 2 Clarity incorporates a dedicated verification and safety agent combined with narration agents that explain data sources and uncertainties to users.


## 5  System Overview and Architecture

Chaos 2 Clarity is structured into four main layers, with cross-cutting caching and feedback components (Figure 1).

┌────────────────────────────────────────────────────────────────┐
│             Experience & Integration Layer (§5.4)              │
│          Conversational UI | BI Tool Integration               │
└───────────────────────┬────────────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────────────┐
│         AI-over-BI Orchestration Layer (§5.3)                  │
│  Intent Classifier | Planner | Query Gen | Safety | Narration  │
└───────────────────────┬────────────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────────────┐
│           Semantic Synthesis Layer (§5.2)                      │
│   Asset Discovery | Concept Inference | Semantic Graph         │
│   Human-in-the-Loop Refinement                                 │
└───────────────────────┬────────────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────────────┐
│              Data & Connectivity Layer (§5.1)                  │
│  RDBMS | Data Lakes | CSV/Excel | SaaS APIs | Document Stores  │
└────────────────────────────────────────────────────────────────┘
      Cross-Cutting: Query Cache + Feedback-Driven Refinement
*Figure 1: Chaos 2 Clarity four-layer architecture with cross-cutting components.*

### 5.1  Data and Connectivity Layer

This layer provides connectors to heterogeneous data sources [[5]](https://arxiv.org/abs/2510.23587), [[6]](https://arxiv.org/abs/2505.18458). A lightweight data catalog maintains basic metadata—connection details, schemas where available, profiles (e.g., value distributions, cardinalities), lineage hints, and access control policies—consistent with federated metadata design advocated in recent AI data catalog literature [[7]](https://arxiv.org/abs/2503.09003), [[8]](https://arxiv.org/abs/2502.15182), [[24]](https://ceur-ws.org/Vol-3827/paper4.pdf).

### 5.2  Semantic Synthesis Layer

The semantic synthesis layer uses rule-based profiling and LLM-driven agents, directly extending methods from metadata enrichment [[7]](https://arxiv.org/abs/2503.09003) and schema matching [[31]](https://arxiv.org/abs/2507.14376):

**Asset discovery and profiling.** Agents scan connected sources, infer column types, candidate keys, and potential foreign key relationships. This mirrors the profiling approach in LEDD [[8]](https://arxiv.org/abs/2502.15182) and LLMDapCAT [[24]](https://ceur-ws.org/Vol-3827/paper4.pdf).

**Concept and metric inference.** LLM-assisted agents map columns and tables to candidate business entities and metrics, infer synonyms and aliases, and propose metric definitions [[7]](https://arxiv.org/abs/2503.09003), [[31]](https://arxiv.org/abs/2507.14376).

**Semantic graph construction.** Inferred entities, metrics, and relationships are stored in a typed graph with provenance, confidence scores, and example queries—enabling the transparency emphasized in data governance literature [[15]](https://arxiv.org/abs/2409.17216).

**Human-in-the-loop refinement.** Data owners and BI engineers review proposed mappings, approve or amend them, and define guardrails (PII handling, access restrictions), consistent with approaches validated in metadata enrichment research [[7]](https://arxiv.org/abs/2503.09003), [[24]](https://ceur-ws.org/Vol-3827/paper4.pdf).

### 5.3  AI-over-BI Orchestration Layer

The orchestration layer builds on ReAct-style orchestration [[32]](https://arxiv.org/abs/2210.03629), Plan-then-Execute patterns [[34]](https://arxiv.org/abs/2509.08646), and production multi-agent framework designs [[25]](https://arxiv.org/abs/2601.13671), [[26]](https://arxiv.org/abs/2308.08155), [[27]](https://arxiv.org/abs/2601.12560):

**Intent and task classifier.** Interprets user questions and categorizes them into BI task types [[14]](https://arxiv.org/abs/2411.06102), [[20]](https://aclanthology.org/2023.emnlp-demo.31/).

**Planner agent.** Plans execution steps and chooses relevant data sources, employing Plan-then-Execute reasoning [[34]](https://arxiv.org/abs/2509.08646) to balance quality and cost.

**Query generation agents.** Generate SQL over one or more sources [[13]](https://arxiv.org/abs/2407.15186), [[22]](https://arxiv.org/abs/2308.15363) and formulate retrieval-augmented queries for unstructured documents [[9]](https://arxiv.org/abs/2005.11401), [[10]](https://arxiv.org/abs/2312.10997), addressing the cross-source orchestration gap identified by Zhu et al. [[5]](https://arxiv.org/abs/2510.23587).

**Verification and safety agent.** Checks queries against governance policies (PII exposure, full table scans) [[15]](https://arxiv.org/abs/2409.17216), [[17]](https://arxiv.org/abs/2507.12425).

**Narration and explanation agent.** Produces natural-language explanations of results, supporting the explainability requirements identified in AI analytics trust literature [[16]](https://arxiv.org/abs/2305.15038).

These agents interact through a central orchestrator tracking state, enforcing timeouts and budgets, and recording telemetry [[25]](https://arxiv.org/abs/2601.13671), [[29]](https://arxiv.org/abs/2509.10769).

### 5.4  Experience and Integration Layer

**Conversational interface.** A chat-like UI consistent with the conversational BI paradigm demonstrated by SiriusBI [[14]](https://arxiv.org/abs/2411.06102) and InsightPilot [[20]](https://aclanthology.org/2023.emnlp-demo.31/).

**BI integration endpoints.** Interfaces allowing existing BI tools to query the semantic layer without replacing current dashboards.

### 5.5  Cross-Cutting Components: Query Caching and Feedback

**Query result cache.** Caches results of frequently used queries, tracking hit rates, latency reductions, and invalidation events.

**Feedback-driven metadata refinement.** Logs user interactions to update confidence scores, add synonyms, and flag ambiguous concepts [[9]](https://arxiv.org/abs/2005.11401), [[17]](https://arxiv.org/abs/2507.12425).


## 6  Evaluation

### 6.1  Evaluation Dimensions

1. **Semantic Layer Quality (RQ1)** – Approximation of a manually curated gold model [[7]](https://arxiv.org/abs/2503.09003), [[8]](https://arxiv.org/abs/2502.15182), [[31]](https://arxiv.org/abs/2507.14376).
2. **BI Answer Quality (RQ2, RQ3)** – Accuracy and completeness relative to NL2SQL baselines [[13]](https://arxiv.org/abs/2407.15186), [[18]](https://arxiv.org/abs/1809.08887), [[23]](https://arxiv.org/abs/2305.03111).
3. **System Performance and Robustness (RQ2, RQ4)** – Behavior under latency, cost, and schema drift constraints [[19]](https://arxiv.org/abs/2411.07763), [[25]](https://arxiv.org/abs/2601.13671).
4. **User Outcomes and Adoption (RQ3, RQ4)** – How business users experience the system.

### 6.2  Metrics

#### 6.2.1  Semantic Layer Quality

- **Coverage** – Fraction of gold entities, metrics, and relationships in the auto-built semantic layer.
- **Mapping precision and recall** – Using the P/R/F1 framework from schema matching evaluation [[31]](https://arxiv.org/abs/2507.14376).
- **Modeling effort** – Human expert hours with and without automation [[7]](https://arxiv.org/abs/2503.09003).
- **Improvement over time** – Change in coverage and precision after N rounds of feedback-driven refinement.

#### 6.2.2  BI Answer Quality

- **Execution accuracy** – Fraction of generated queries that execute without errors [[13]](https://arxiv.org/abs/2407.15186).
- **Result correctness** – Match against expected outputs [[22]](https://arxiv.org/abs/2308.15363), [[23]](https://arxiv.org/abs/2305.03111).
- **Semantic intent match** – Expert rating that the answer matches the original business question [[14]](https://arxiv.org/abs/2411.06102).
- **Cross-source coverage** – All relevant data sources correctly identified and used [[5]](https://arxiv.org/abs/2510.23587), [[19]](https://arxiv.org/abs/2411.07763).

Baselines: (a) Curated BI baseline; (b) Simple LLM-over-data baseline (text-to-SQL, no semantic layer) [[13]](https://arxiv.org/abs/2407.15186), [[22]](https://arxiv.org/abs/2308.15363).

#### 6.2.3  System Performance and Robustness

- **Latency** – P50/P95/P99 end-to-end response time.
- **Resource and cost** – LLM token usage, backend compute time, cache memory [[25]](https://arxiv.org/abs/2601.13671), [[29]](https://arxiv.org/abs/2509.10769).
- **Robustness to schema drift** – Degradation and recovery when schemas change, per Spider 2.0 [[19]](https://arxiv.org/abs/2411.07763) and Dr. Spider [[35]](https://arxiv.org/abs/2301.08881).
- **Safety incidents** – Blocked or auto-corrected unsafe queries [[15]](https://arxiv.org/abs/2409.17216), [[17]](https://arxiv.org/abs/2507.12425).

#### 6.2.4  User Outcomes and Adoption

- **Task success rate** vs. baseline BI tools [[3]](https://arxiv.org/abs/2510.04023), [[14]](https://arxiv.org/abs/2411.06102).
- **Time-to-insight** from task definition to first acceptable answer [[20]](https://aclanthology.org/2023.emnlp-demo.31/).
- **Trust and satisfaction** – Self-reported trust, clarity, and willingness to rely on outputs [[16]](https://arxiv.org/abs/2305.15038).
- **Override and rollback frequency** – How often users revert to manual tools.
- **Adoption trajectory** – Active users, queries per day, AI-assisted decision rate.

### 6.3  Experimental Design

#### Phase 1 – Offline Semantic and Answer Evaluation

1. **Dataset and gold model creation** across one or more business domains (e.g., sales, operations).
2. **System variants**: (a) Full Chaos 2 Clarity with caching and feedback disabled; (b) caching enabled; (c) caching and batched feedback-driven refinement.
3. **Baselines**: Curated BI baseline and simple LLM-over-data baseline [[13]](https://arxiv.org/abs/2407.15186), [[22]](https://arxiv.org/abs/2308.15363).
4. **Measurements** using the execution accuracy and semantic match framework from NL2SQL evaluation [[13]](https://arxiv.org/abs/2407.15186), [[23]](https://arxiv.org/abs/2305.03111).

#### Phase 2 – Robustness and Drift Experiments

Introduce controlled schema changes using the perturbation taxonomy from Dr. Spider [[35]](https://arxiv.org/abs/2301.08881): column renames, table restructuring, new source addition, and policy changes. Measure immediate impact and recovery speed.

#### Phase 3 – User Study and Pilot Deployment

- **Study design**: Within-subjects comparison between existing tools and Chaos 2 Clarity.
- **Data collection**: Logs of queries, edits, feedback events, corrections, and time-to-completion; surveys and brief interviews.
- **Analysis**: Task success, time-to-insight, trust metrics, override behavior, and patterns in feedback leading to semantic layer improvements.


## 7  Discussion and Future Work

Chaos 2 Clarity contributes a reference design for LLM-orchestrated BI over messy, heterogeneous data, proposing concrete agent patterns, caching strategies, and feedback loops suitable for production deployment [[25]](https://arxiv.org/abs/2601.13671), [[26]](https://arxiv.org/abs/2308.08155), [[27]](https://arxiv.org/abs/2601.12560). It aims to show that AI-assisted BI can create value even when data cannot be fully centralized or curated, and to illuminate how governance [[15]](https://arxiv.org/abs/2409.17216), [[16]](https://arxiv.org/abs/2305.15038), explainability, and trust shape adoption.

**Limitations.** The architecture relies on LLM-inferred semantic mappings that may exhibit hallucination on ambiguous schemas—a known limitation of LLM-based metadata systems [[7]](https://arxiv.org/abs/2503.09003), [[31]](https://arxiv.org/abs/2507.14376). Multi-source query planning can incur significant latency for complex cross-database joins. The feedback-driven refinement loop requires sustained user engagement to produce measurable improvements.

**Future work** includes extending the semantic synthesis layer with richer domain-specific ontologies, integrating stronger data-privacy guarantees, and exploring automated A/B testing of agent strategies. A key direction is defining shared benchmarks that reflect the heterogeneous, uncurated data realities faced by enterprises, complementing existing NL2SQL benchmarks [[18]](https://arxiv.org/abs/1809.08887), [[19]](https://arxiv.org/abs/2411.07763), [[23]](https://arxiv.org/abs/2305.03111). Integration with emerging agent communication standards [[27]](https://arxiv.org/abs/2601.12560) could further expand interoperability.


## 8  Conclusion

This paper introduced **Chaos 2 Clarity**, a production-oriented architecture and evaluation plan for an LLM-orchestrated BI layer over heterogeneous, uncurated enterprise data sources. By focusing on automatic semantic synthesis [[7]](https://arxiv.org/abs/2503.09003), [[8]](https://arxiv.org/abs/2502.15182), [[31]](https://arxiv.org/abs/2507.14376), agentic orchestration [[25]](https://arxiv.org/abs/2601.13671), [[26]](https://arxiv.org/abs/2308.08155), [[32]](https://arxiv.org/abs/2210.03629), and feedback-driven refinement [[9]](https://arxiv.org/abs/2005.11401), [[17]](https://arxiv.org/abs/2507.12425) on top of existing, messy infrastructures, Chaos 2 Clarity aims to make AI-over-BI practically useful for organizations that cannot wait for perfect data curation. The proposed evaluation framework fills a gap identified by recent data agent surveys [[3]](https://arxiv.org/abs/2510.04023), [[5]](https://arxiv.org/abs/2510.23587) between current AI-over-data systems and the messy realities of enterprise data environments.


## References

> All references individually verified via live web search. Author names reflect actual paper metadata.

[1] OpenAI. "GPT-4 Technical Report." [https://arxiv.org/abs/2303.08774](https://arxiv.org/abs/2303.08774), 2023.

[2] Minaee, S., Mikolov, T., Nikzad, N., et al. "Large Language Models: A Survey." [https://arxiv.org/abs/2402.06196](https://arxiv.org/abs/2402.06196), 2024.

[3] Rahman, M., Bhuiyan, A., Islam, M.S., Laskar, M.T.R., Masry, A., Joty, S., and Hoque, E. "LLM-Based Data Science Agents: A Survey of Capabilities, Challenges, and Future Directions." [https://arxiv.org/abs/2510.04023](https://arxiv.org/abs/2510.04023), 2025.

[4] Chen, W., et al. "LLM/Agent-as-Data-Analyst: A Survey." [https://arxiv.org/abs/2509.23988](https://arxiv.org/abs/2509.23988), 2025.

[5] Zhu, Y., Wang, L., Yang, C., et al. "A Survey of Data Agents: Emerging Paradigm or Overstated Hype?" [https://arxiv.org/abs/2510.23587](https://arxiv.org/abs/2510.23587), 2025.

[6] "A Survey of LLM × DATA." [https://arxiv.org/abs/2505.18458](https://arxiv.org/abs/2505.18458), 2025.

[7] Singh, M., Kumar, A., Donaparthi, S., and Karambelkar, G. "Leveraging Retrieval Augmented Generative LLMs For Automated Metadata Description Generation to Enhance Data Catalogs." [https://arxiv.org/abs/2503.09003](https://arxiv.org/abs/2503.09003), 2025.

[8] An, Q., Ying, C., Zhu, Y., Xu, Y., Zhang, M., and Wang, J. "LEDD: Large Language Model-Empowered Data Discovery in Data Lakes." [https://arxiv.org/abs/2502.15182](https://arxiv.org/abs/2502.15182), 2025.

[9] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., and Kiela, D. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." NeurIPS 2020. [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401).

[10] Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., and Wang, H. "Retrieval-Augmented Generation for Large Language Models: A Survey." [https://arxiv.org/abs/2312.10997](https://arxiv.org/abs/2312.10997), 2024.

[11] OpenAI. "GPT-4 Technical Report." [https://arxiv.org/abs/2303.08774](https://arxiv.org/abs/2303.08774), 2023.

[12] Touvron, H., et al. "LLaMA 2: Open Foundation and Fine-Tuned Chat Models." [https://arxiv.org/abs/2307.09288](https://arxiv.org/abs/2307.09288), 2023.

[13] Shi, L., et al. "A Survey on Employing Large Language Models for Text-to-SQL Tasks." [https://arxiv.org/abs/2407.15186](https://arxiv.org/abs/2407.15186), 2024.

[14] Jiang, J., et al. (Tencent SiriusAI). "SiriusBI: A Comprehensive LLM-Powered Solution for Data Analytics in Business Intelligence." PVLDB, 2025. [https://arxiv.org/abs/2411.06102](https://arxiv.org/abs/2411.06102).

[15] Gupta, R., Walker, L., Corona, R., Fu, S., Petryk, S., Napolitano, J., Darrell, T., and Reddie, A.W. "Data-Centric AI Governance: Addressing the Limitations of Model-Focused Policies." [https://arxiv.org/abs/2409.17216](https://arxiv.org/abs/2409.17216), 2024.

[16] Cheng, L., Li, X., and Bing, L. "Is GPT-4 a Good Data Analyst?" [https://arxiv.org/abs/2305.15038](https://arxiv.org/abs/2305.15038), 2023.

[17] Cheerla, C. "Advancing Retrieval-Augmented Generation for Structured Enterprise and Internal Data." [https://arxiv.org/abs/2507.12425](https://arxiv.org/abs/2507.12425), 2025.

[18] Yu, T., Zhang, R., Yang, K., Yasunaga, M., Wang, D., Li, Z., Ma, J., Li, I., Yao, Q., Roman, S., Zhang, Z., and Radev, D. "Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL." EMNLP 2018. [https://arxiv.org/abs/1809.08887](https://arxiv.org/abs/1809.08887).

[19] Lei, F., Chen, J., Li, S., Chen, T., and Li, Y. "Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows." [https://arxiv.org/abs/2411.07763](https://arxiv.org/abs/2411.07763), 2024.

[20] Ma, P., Ding, R., Wang, S., Han, S., and Zhang, D. "InsightPilot: An LLM-Empowered Automated Data Exploration System." EMNLP 2023. [https://aclanthology.org/2023.emnlp-demo.31/](https://aclanthology.org/2023.emnlp-demo.31/).

[21] Sun, J., et al. "TableLlama: Towards Open Large Generalist Models for Tables." [https://arxiv.org/abs/2407.09305](https://arxiv.org/abs/2407.09305), 2024.

[22] Gao, D., Wang, H., Li, Y., Sun, X., Qian, Y., Ding, B., and Zhou, J. "Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation." [https://arxiv.org/abs/2308.15363](https://arxiv.org/abs/2308.15363), 2023.

[23] Li, J., Hui, B., Qu, G., Yang, J., Li, B., Li, B., Wang, B., Qin, B., Geng, R., Huo, N., et al. "Can LLM Already Serve as a Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs (BIRD)." NeurIPS 2023. [https://arxiv.org/abs/2305.03111](https://arxiv.org/abs/2305.03111).

[24] Vanhoeyveld, J., et al. "LLMDapCAT: An LLM-Based Data Catalogue System for Data Sharing and Exploration." CEUR-WS, 2024. [https://ceur-ws.org/Vol-3827/paper4.pdf](https://ceur-ws.org/Vol-3827/paper4.pdf).

[25] Adimulam, A., Gupta, R., and Kumar, S. "The Orchestration of Multi-Agent Systems: Architectures, Protocols, and Enterprise Adoption." [https://arxiv.org/abs/2601.13671](https://arxiv.org/abs/2601.13671), 2026.

[26] Wu, Q., Bansal, G., Zhang, J., Wu, Y., Zhang, S., Zhu, E., Li, B., Jiang, L., Zhang, X., and Wang, C. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework." ICLR 2024. [https://arxiv.org/abs/2308.08155](https://arxiv.org/abs/2308.08155).

[27] Arunkumar, V., Gangadharan, G.R., and Buyya, R. "Agentic Artificial Intelligence (AI): Architectures, Taxonomies, and Evaluation of Large Language Model Agents." [https://arxiv.org/abs/2601.12560](https://arxiv.org/abs/2601.12560), 2026.

[28] Cheerla, C. "Advancing Retrieval-Augmented Generation for Structured Enterprise and Internal Data." [https://arxiv.org/abs/2507.12425](https://arxiv.org/abs/2507.12425), 2025. *(Same paper as [17]; appears twice due to dual relevance to RAG and enterprise data.)*

[29] Bogavelli, T., Sharma, R., and Subramani, H. (ServiceNow). "AgentArch: A Comprehensive Benchmark to Evaluate Agent Architectures in Enterprise." [https://arxiv.org/abs/2509.10769](https://arxiv.org/abs/2509.10769), 2025.

[30] Es, S., James, J., Espinosa-Anke, L., and Schockaert, S. "RAGAS: Automated Evaluation of Retrieval Augmented Generation." [https://arxiv.org/abs/2309.15217](https://arxiv.org/abs/2309.15217), 2023.

[31] Gungor, O.E., Paulsen, D., and Kang, W. "SCHEMORA: Schema Matching via Multi-Stage Recommendation and Metadata Enrichment using Off-the-Shelf LLMs." [https://arxiv.org/abs/2507.14376](https://arxiv.org/abs/2507.14376), 2025.

[32] Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., and Cao, Y. "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR 2023. [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629).

[33] Pan, F., et al. "End-to-End Table Question Answering via Retrieval-Augmented Generation." [https://arxiv.org/abs/2203.16714](https://arxiv.org/abs/2203.16714), 2022.

[34] Del Rosario, R.F., Krawiecka, K., and Schroeder de Witt, C. "Architecting Resilient LLM Agents: A Guide to Secure Plan-then-Execute Implementations." [https://arxiv.org/abs/2509.08646](https://arxiv.org/abs/2509.08646), 2025.

[35] Chang, S., et al. "Dr. Spider: A Diagnostic Evaluation Benchmark towards Text-to-SQL Robustness." ICLR 2023. [https://arxiv.org/abs/2301.08881](https://arxiv.org/abs/2301.08881).

[36] Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E., Le, Q., and Zhou, D. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." NeurIPS 2022. [https://arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903).


## Appendix A: Semantic Layer Schema and Example Outputs

### A.1  Semantic Model Data Structure

> **Sources**: Semantic graph design adapted from LLM-based metadata catalog literature [[7]](https://arxiv.org/abs/2503.09003), [[8]](https://arxiv.org/abs/2502.15182) and schema matching frameworks [[31]](https://arxiv.org/abs/2507.14376).

**Node types:**

| Node Type | Attributes |
|-----------|-----------|
| `Entity` | `name`, `aliases[]`, `source_tables[]`, `confidence`, `pii_flag` |
| `Metric` | `name`, `formula`, `unit`, `source_columns[]`, `confidence` |
| `Dimension` | `name`, `values_sample[]`, `source_column`, `time_flag` |
| `DataSource` | `source_type`, `connection_ref`, `schema_version`, `last_profiled` |
| `Policy` | `type` (PII/access/compute), `rule`, `scope`, `priority` |

**Edge types:**

| Edge Type | Connects | Attributes |
|-----------|---------|-----------|
| `DERIVED_FROM` | Metric → Entity | `confidence`, `formula_ref` |
| `SLICEABLE_BY` | Metric → Dimension | `join_path` |
| `FOREIGN_KEY` | DataSource → DataSource | `inferred_flag` |
| `SYNONYMOUS_WITH` | Entity ↔ Entity | `similarity_score` |
| `GOVERNED_BY` | Entity / Metric → Policy | `enforcement_level` |

### A.2  Example: Inferred Semantic Model Fragment

Given a retail enterprise with three uncurated sources—an OLTP PostgreSQL database, a Salesforce CRM export, and a flat-file CSV from a logistics provider—the Semantic Synthesis Layer produces inferred mappings (confidence thresholds benchmarked against standards from Singh et al. [[7]](https://arxiv.org/abs/2503.09003)):

Entity: Customer
  aliases: ["client", "account", "buyer"]
  source_tables: [pg.customers, sf.Account, logistics.shipto_party]
  confidence: 0.91
  pii_flag: true

Metric: GrossRevenue
  formula: SUM(pg.orders.line_total) WHERE status='complete'
  unit: USD
  source_columns: [pg.orders.line_total, pg.orders.status]
  confidence: 0.87

Metric: CustomerLifetimeValue
  formula: SUM(GrossRevenue) GROUP BY Customer
  confidence: 0.79 [requires cross-source join with sf.Account on email_id]

Policy: PII_Restriction
  type: PII
  rule: "Never expose email, phone, or address in unrestricted query results"
  scope: [Entity.Customer]
  priority: CRITICAL


## Appendix B: Agent Prompt Templates

> **Sources**: Prompt patterns adapted from ReAct [[32]](https://arxiv.org/abs/2210.03629), Plan-then-Execute [[34]](https://arxiv.org/abs/2509.08646), and production multi-agent orchestration designs [[25]](https://arxiv.org/abs/2601.13671), [[26]](https://arxiv.org/abs/2308.08155).

### B.1  Intent Classifier Prompt

You are a BI intent classifier. Given the user's question and the available 
semantic model (entities, metrics, dimensions), classify the question into one 
of the following task types:
  [metric_lookup | trend_analysis | slice_and_dice | cross_source_join |
   anomaly_investigation | forecast | comparison | what_if | policy_check | other]

Return JSON: {"task_type": "<type>", "entities": [...], "metrics": [...], 
              "time_range": "...", "confidence": <0-1>}

User question: {user_question}
Semantic model summary: {semantic_model_summary}

### B.2  Planner Agent Prompt

You are a BI query planner. Given a classified BI task and a semantic model, 
generate a step-by-step execution plan. Each step should specify:
  - data_source
  - operation (SQL | RAG | join | aggregate | narrate)
  - dependencies (list of prior step IDs)
  - estimated_cost (low | medium | high)

Apply the following governance constraints: {governance_policies}

Task: {task_description}
Semantic model: {semantic_model_json}

### B.3  Verification Agent Prompt

You are a BI safety and verification agent. Review the following SQL query 
before execution and check for:
  1. Policy violations (PII exposure, full table scans, cross-join risks)
  2. Logical plausibility (do the joins make semantic sense?)
  3. Result size risk (would this return more than {max_rows} rows?)

Return: {"approved": true|false, "violations": [...], "warnings": [...], 
         "modified_query": "<safe SQL or null>"}

Query: {proposed_sql}
Policies: {active_policies}


## Appendix C: Evaluation Benchmarks and Dataset Construction

> **Sources**: Methodology informed by Spider [[18]](https://arxiv.org/abs/1809.08887), BIRD [[23]](https://arxiv.org/abs/2305.03111), Dr. Spider [[35]](https://arxiv.org/abs/2301.08881), and RAGAS [[30]](https://arxiv.org/abs/2309.15217).

### C.1  Gold Semantic Model Construction Protocol

Five-step process (adapted from annotation methodology in [[7]](https://arxiv.org/abs/2503.09003)):

1. **Source inventory**: List all data sources relevant to the domain.
2. **Expert interviews**: 3–5 hours per domain to elicit canonical entity and metric definitions.
3. **Schema walkthrough**: Table-by-table annotation of entity/dimension/metric roles, data quality flags, and governance constraints.
4. **Reconciliation**: Resolve disagreements via majority vote; flag ambiguous mappings for the robustness experiment.
5. **Versioning**: Record the gold model as a versioned JSON artifact to enable drift experiments (Phase 2).

### C.2  BI Question Suite Construction

Four tiers of complexity, inspired by BIRD [[23]](https://arxiv.org/abs/2305.03111) and Spider 2.0 [[19]](https://arxiv.org/abs/2411.07763):

| Tier | Description | Example |
|------|-------------|---------|
| L1 – Single-source metric | Single table, single metric, no join | "What was total revenue last quarter?" |
| L2 – Multi-table join | Cross-table join within a single source | "Revenue breakdown by product category?" |
| L3 – Cross-source multi-hop | Join across ≥2 separate data sources | "Customers with active CRM deals who had delivery issues in last 30 days?" |
| L4 – Unstructured + structured | Combines SQL and document RAG [[9]](https://arxiv.org/abs/2005.11401) | "Summarize delivery complaints from emails for top 10 customers by revenue." |

25 questions per tier per domain (~100 per evaluation domain). All questions validated by a domain expert.

### C.3  Schema Drift Injection Protocol

Using the perturbation taxonomy from Dr. Spider [[35]](https://arxiv.org/abs/2301.08881):

| Change Type | Description | Example |
|-------------|-------------|---------|
| Column rename | Rename a key column in a frequently queried table | `order_total` → `line_value` |
| Table restructure | Split one table into two or merge two tables | Split `orders` into `orders_header` + `orders_lines` |
| New source addition | Add a new data source with overlapping semantics | Second CRM export with partially overlapping customer data |
| Policy change | Restrict or relax data access policy | Mark `email_id` as PII requiring masking |


## Appendix D: Comparison with Existing Systems

> **Sources**: System descriptions from NL2SQL survey [[13]](https://arxiv.org/abs/2407.15186), InsightPilot [[20]](https://aclanthology.org/2023.emnlp-demo.31/), SiriusBI [[14]](https://arxiv.org/abs/2411.06102), LEDD [[8]](https://arxiv.org/abs/2502.15182), Singh et al. [[7]](https://arxiv.org/abs/2503.09003), and Cheerla [[17]](https://arxiv.org/abs/2507.12425).

| Dimension | Chaos 2 Clarity | NL2SQL [[13]](https://arxiv.org/abs/2407.15186) | InsightPilot [[20]](https://aclanthology.org/2023.emnlp-demo.31/) | SiriusBI [[14]](https://arxiv.org/abs/2411.06102) | Data Catalogs [[7]](https://arxiv.org/abs/2503.09003), [[8]](https://arxiv.org/abs/2502.15182) |
|-----------|---|---|---|---|---|
| Handles uncurated data | ✅ | ❌ | ❌ | ❌ | Partial |
| Automated semantic synthesis | ✅ | ❌ | ❌ | ❌ | ✅ |
| Multi-source cross-join planning | ✅ | ❌ | Partial | ❌ | ❌ |
| RAG over mixed structured + unstructured [[9]](https://arxiv.org/abs/2005.11401) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Governance / safety layer | ✅ | ❌ | ❌ | Partial | Partial |
| Feedback-driven refinement | ✅ | ❌ | ❌ | ❌ | ❌ |
| Production-oriented evaluation plan | ✅ | Varies | ❌ | ✅ | ❌ |
| Conversational BI interface | ✅ | Partial | ✅ | ✅ | ❌ |


## Appendix E: Glossary of Key Terms

> **Sources**: NL2SQL survey [[13]](https://arxiv.org/abs/2407.15186), RAG survey [[10]](https://arxiv.org/abs/2312.10997), multi-agent survey [[25]](https://arxiv.org/abs/2601.13671), data agent survey [[5]](https://arxiv.org/abs/2510.23587).

| Term | Definition | Key Reference |
|------|-----------|--------------|
| Semantic Layer | A metadata model mapping raw data assets to business entities, metrics, and relationships, providing a queryable business vocabulary over physical data. | [[7]](https://arxiv.org/abs/2503.09003), [[8]](https://arxiv.org/abs/2502.15182) |
| Semantic Synthesis | The process of automatically generating a semantic layer from raw, uncurated data sources using LLM-assisted profiling and concept inference. | [[7]](https://arxiv.org/abs/2503.09003), [[31]](https://arxiv.org/abs/2507.14376) |
| Uncurated Data | Data stored without a unified schema, consistent naming conventions, or documented business semantics. | [[5]](https://arxiv.org/abs/2510.23587), [[19]](https://arxiv.org/abs/2411.07763) |
| Multi-Agent Orchestration | A system design pattern where multiple specialized LLM agents collaborate under a central orchestrator to complete complex tasks. | [[25]](https://arxiv.org/abs/2601.13671), [[26]](https://arxiv.org/abs/2308.08155) |
| Query Caching | A system mechanism storing results of previously executed queries and returning cached results for semantically equivalent future queries. | [[30]](https://arxiv.org/abs/2309.15217) |
| Feedback-Driven Refinement | A continual learning mechanism whereby user feedback is used to improve confidence scores and mappings of the semantic model over time. | [[9]](https://arxiv.org/abs/2005.11401), [[17]](https://arxiv.org/abs/2507.12425) |
| Governance Agent | A specialized LLM agent that enforces data access policies, PII restrictions, and query cost constraints before query execution. | [[15]](https://arxiv.org/abs/2409.17216), [[27]](https://arxiv.org/abs/2601.12560) |
| Schema Drift | Changes to the physical schema of a data source that may invalidate previously valid semantic mappings or queries. | [[35]](https://arxiv.org/abs/2301.08881), [[19]](https://arxiv.org/abs/2411.07763) |
| Execution Accuracy | The fraction of LLM-generated SQL queries that execute without runtime errors. | [[13]](https://arxiv.org/abs/2407.15186), [[23]](https://arxiv.org/abs/2305.03111) |
| Cross-Source Query | A query requiring data from two or more separate data sources, potentially involving cross-system joins or result set merging. | [[5]](https://arxiv.org/abs/2510.23587), [[19]](https://arxiv.org/abs/2411.07763) |
| ReAct Pattern | A reasoning-then-action loop where thought, action, and observation steps are interleaved to solve multi-step tasks. | [[32]](https://arxiv.org/abs/2210.03629) |
| RAG (Retrieval-Augmented Generation) | A technique augmenting LLM generation with relevant context retrieved from an external knowledge source at inference time. | [[9]](https://arxiv.org/abs/2005.11401), [[10]](https://arxiv.org/abs/2312.10997) |
