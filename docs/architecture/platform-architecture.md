# Platform Architecture

## Objective

Chaos 2 Clarity should behave like a production BI operating layer for messy enterprise data, not like a single prompt wrapped around a database.

The platform must support:

- heterogeneous source access,
- source discovery and drift handling,
- semantic unification across partial and conflicting models,
- structured and unstructured evidence access,
- governed orchestration,
- evaluation and continuous improvement.

## Architectural Principles

1. Metadata first
   Every downstream behavior should depend on a shared metadata graph rather than connector-specific logic.
2. Separate control plane from execution plane
   Planning, semantic reasoning, governance, and evaluation should be decoupled from actual query and retrieval execution.
3. Prefer synthesis plus review over blind generation
   LLMs propose mappings, metrics, joins, and explanations; deterministic validators and human review close the loop.
4. Treat unstructured and structured data as peers
   The answer engine should fuse SQL results, document evidence, and source metadata into one grounded response.
5. Make governance a first-class architectural layer
   Policy checks, access control, audit, and explainability must be in-band.

## Layered Design

### 1. Connectors

Each connector exposes a common contract:

- `discover_assets`
- `get_asset_schema`
- `profile_asset`
- `sample_records`
- `execute_query` or `fetch_content`
- `list_capabilities`
- `detect_changes`

Capabilities should include:

- structured queryable,
- batch extractable,
- document retrievable,
- supports incremental sync,
- supports lineage hints,
- contains sensitive classes.

### 2. Discovery and Metadata Graph

Discovery normalizes source-native metadata into a shared graph of:

- sources,
- assets,
- fields,
- document collections,
- endpoints,
- candidate relationships,
- sensitivity labels,
- freshness and quality indicators.

This layer also stores:

- profile statistics,
- examples and samples,
- schema versions,
- drift history,
- access scopes,
- connector health.

### 3. Semantic Synthesis

Semantic synthesis transforms raw assets into business abstractions:

- entities such as customer, order, invoice, ticket, campaign,
- metrics such as revenue, churn rate, resolution time,
- dimensions such as region, product, segment, team,
- relationships across sources,
- business synonyms and glossary terms,
- policy overlays and confidence scores.

The semantic layer must be versioned and reviewable.

### 4. Retrieval and Query Fabric

The execution plane supports both:

- text-to-SQL or federated SQL over structured assets,
- RAG over documents, transcripts, tickets, notes, and semi-structured records.

Both pipelines should return normalized evidence objects with:

- provenance,
- confidence,
- freshness,
- policy tags,
- citation-ready references.

### 5. Orchestration Plane

Recommended agents:

- intent agent,
- source selection agent,
- semantic mapping agent,
- SQL planning agent,
- retrieval planning agent,
- verifier agent,
- explanation agent,
- feedback agent.

The orchestrator should use a policy-aware execution graph instead of unconstrained free-form delegation.

### 6. Governance and Safety

Governance services enforce:

- role-aware access checks,
- row and column policies,
- sensitive field masking,
- high-cost query prevention,
- hallucination and unsupported-claim checks,
- audit trace generation.

### 7. Evaluation and Observability

Every answer should emit operational artifacts:

- selected sources,
- semantic objects used,
- generated queries,
- retrieved evidence,
- latency breakdown,
- token and execution cost,
- verification outcomes,
- user feedback hooks.

## Suggested Runtime Flow

1. User asks a business question.
2. Intent agent identifies task type and candidate semantic concepts.
3. Source router picks structured and unstructured sources using the metadata graph.
4. Semantic layer resolves entities, metrics, and filters into executable plans.
5. SQL and retrieval plans run through governed execution services.
6. Verification compares outputs against semantic constraints, policy rules, and evidence consistency.
7. Explanation service composes the final answer with citations, caveats, and suggested next actions.
8. Feedback updates confidence scores, glossary mappings, and benchmark traces.

## Deployment Model

Recommended deployable services:

- connector service,
- discovery scheduler,
- metadata graph store,
- semantic synthesis service,
- retrieval indexing service,
- orchestration API,
- policy service,
- evaluation runner,
- observability pipeline.

This lets enterprises adopt the platform incrementally:

- metadata-only first,
- semantic synthesis next,
- governed AI querying after,
- full BI workflow integration last.
