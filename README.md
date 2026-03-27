![Chaos 2 Clarity header](ui/assets/c2c-banner.jpg)

# Chaos 2 Clarity

Production architecture and evaluation framework for an LLM-orchestrated BI layer over heterogeneous, uncurated enterprise data.

Research paper: [https://ravii-teja.github.io/c2c/](https://ravii-teja.github.io/c2c/)

Author: [Bankupalli Ravi Teja](https://www.linkedin.com/in/raviiteja/)

## Why This Repo Exists

Most AI-over-BI products assume a clean warehouse, a stable semantic layer, and well-modeled analytics assets. Real enterprises usually have something messier: SaaS tools, OLTP databases, spreadsheets, document stores, lake files, APIs, logs, and partial documentation spread across teams.

Chaos 2 Clarity is built for that reality.

The goal is to create a deployable platform that can:

- connect to fragmented enterprise data sources,
- discover and profile what exists,
- synthesize a semantic layer with entities, metrics, relationships, and policies,
- combine structured querying with retrieval over semi-structured and unstructured content,
- orchestrate LLM agents to produce trustworthy, actionable insights,
- evaluate the system on coverage, semantic quality, time-to-insight, safety, and operational robustness.

## Core Problem

We explicitly target non-unified, partly modeled, and often uncurated enterprise environments:

- files: CSV, Excel, PDFs, text exports, shared-drive dumps,
- APIs: CRM, ERP, ticketing, support, finance, marketing, collaboration tools,
- OLTP databases: PostgreSQL, MySQL, SQL Server, Oracle,
- analytical stores: warehouses, lakehouses, object storage tables,
- documents and knowledge: policies, runbooks, contracts, notes, support transcripts.

This means the system cannot rely on a single text-to-SQL layer alone. It needs a compound architecture:

- schema and source discovery,
- semantic and metric unification,
- RAG over unstructured and semi-structured assets,
- text-to-SQL over discovered schemas,
- cross-source planning and evidence fusion,
- governance, lineage, and verification.

## Product Thesis

The product thesis is simple:

1. Enterprises do not need to fully centralize data before getting AI-driven analytical value.
2. The first job of the AI layer is to reduce chaos by discovering and modeling what already exists.
3. A semantic layer should be synthesized and refined continuously, not treated as a one-time manual prerequisite.
4. Production readiness depends as much on governance, evaluation, and observability as it does on model quality.

## Target System

Chaos 2 Clarity is designed as a layered platform:

1. Connector layer
   Standardized ingestion and metadata adapters for databases, files, APIs, document systems, and lake storage.
2. Discovery and profiling layer
   Asset inventory, schema inference, profiling, sample extraction, lineage hints, and change detection.
3. Semantic synthesis layer
   Automatic inference of entities, metrics, dimensions, relationships, synonyms, business concepts, and access policies.
4. Retrieval and query execution layer
   Text-to-SQL, federated execution, document retrieval, chunking, embeddings, and evidence normalization.
5. Orchestration layer
   Agent workflows for intent understanding, source selection, plan generation, verification, narration, and feedback capture.
6. Governance and trust layer
   Policy enforcement, PII tagging, access control, lineage, explainability, and auditability.
7. Evaluation and operations layer
   Benchmarks, gold sets, replay workloads, drift tests, latency and cost metrics, and user outcome measurement.

More detail lives in [docs/architecture/platform-architecture.md](/Users/home/Development/c2c/docs/architecture/platform-architecture.md).

## Repository Design

This repository is structured so connectors, orchestration, semantic synthesis, and evaluation can evolve independently but still work as one deployment strategy.

The implementation language is Python, and the executable modules live directly under `src/`.

```text
.
|-- README.md
|-- docs/
|   |-- architecture/
|   |   |-- platform-architecture.md
|   |   |-- semantic-layer-strategy.md
|   |   `-- evaluation-framework.md
|   `-- connectors/
|       `-- connector-catalog.md
|-- configs/
|   |-- README.md
|   |-- bigquery.example.json
|   `-- postgres.example.json
|-- organization_context/
|   |-- README.md
|   |-- business_glossary.json
|   |-- governance_rules.json
|   `-- org_context.json
|-- src/
|   |-- artifacts.py
|   |-- cli.py
|   |-- config.py
|   |-- connectors/
|   |-- discovery/
|   |-- evaluation/
|   |-- examples/
|   |-- integrations.py
|   |-- models/
|   |-- org_context/
|   |-- workflows/
|   `-- semantic_layer/
|-- tests/
|   `-- test_semantic_synthesizer.py
|-- evaluation/
|   |-- benchmarks/
|   |-- gold/
|   |-- workloads/
|   `-- rubrics/
|-- scripts/
|   `-- build_pages.py
|-- ui/
|   |-- app.js
|   |-- index.html
|   |-- server.py
|   `-- styles.css
`-- .github/
    `-- workflows/
        `-- deploy-research-paper.yml
```

## Research Paper Publishing

The repository now treats [research-paper.md](/Users/home/Development/c2c/docs/research-paper.md) as the source of truth for the public paper.

GitHub Pages deployment is handled by [deploy-research-paper.yml](/Users/home/Development/c2c/.github/workflows/deploy-research-paper.yml), which:

- triggers on changes to the research paper or Pages build workflow,
- builds a static `index.html` from the markdown source using [build_pages.py](/Users/home/Development/c2c/scripts/build_pages.py),
- uploads the generated `site/` artifact, and
- deploys it to GitHub Pages.

To enable it in GitHub, set Pages to use `GitHub Actions` as the source in the repository settings.

## Python Implementation Status

The first Python runtime slice is now in place:

- shared typed metadata models for sources, assets, fields, profiles, and change events,
- shared semantic models for entities, metrics, relationships, and draft semantic layers,
- a base connector contract and connector registry,
- a shared database connector foundation for common database and warehouse families,
- a working local CSV connector,
- a filesystem connector for local folders containing documents, tables, and semi-structured files,
- implemented query-driven connectors for PostgreSQL and BigQuery,
- scaffolded connectors for MySQL, Snowflake, Databricks, Redshift, SQL Server, and Oracle,
- executor adapters for DB-API and BigQuery-style clients,
- a discovery service that assembles a metadata graph from registered connectors,
- a CLI and local workflow runner for `discover -> snapshot -> synthesize -> save`,
- config-driven workflow entry for PostgreSQL and BigQuery runs,
- example config templates for PostgreSQL and BigQuery,
- a deterministic semantic synthesizer that generates initial entity and metric candidates,
- semantic contract generation and persistence from synthesized drafts,
- starter semantic-quality evaluation helpers and benchmark fixtures,
- heuristic relationship inference and relationship-aware semantic contract scoring,
- governance-aware sensitivity and policy-tag annotations in metadata and contracts,
- an `organization_context/` folder pattern for company glossary, governance rules, and org context inputs,
- a semantic-layer repository for draft persistence,
- schema snapshot and drift comparison utilities for database sources,
- a starter example pipeline and a first unit test.

Current code entrypoints:

- source root: [src](/Users/home/Development/c2c/src)
- CLI entrypoint: [cli.py](/Users/home/Development/c2c/src/cli.py)
- artifact layout helper: [artifacts.py](/Users/home/Development/c2c/src/artifacts.py)
- source config loader: [config.py](/Users/home/Development/c2c/src/config.py)
- integration helpers: [integrations.py](/Users/home/Development/c2c/src/integrations.py)
- organization context loader: [loader.py](/Users/home/Development/c2c/src/org_context/loader.py)
- connector contract: [base.py](/Users/home/Development/c2c/src/connectors/base.py)
- shared database base: [base.py](/Users/home/Development/c2c/src/connectors/databases/base.py)
- query executor protocol: [executor.py](/Users/home/Development/c2c/src/connectors/databases/executor.py)
- schema snapshot utilities: [schema_snapshot.py](/Users/home/Development/c2c/src/connectors/databases/schema_snapshot.py)
- PostgreSQL connector: [postgres_connector.py](/Users/home/Development/c2c/src/connectors/databases/postgres_connector.py)
- BigQuery connector: [bigquery_connector.py](/Users/home/Development/c2c/src/connectors/databases/bigquery_connector.py)
- CSV connector: [csv_connector.py](/Users/home/Development/c2c/src/connectors/files/csv_connector.py)
- connector runner: [runner.py](/Users/home/Development/c2c/src/discovery/runner.py)
- metadata repository: [metadata_repository.py](/Users/home/Development/c2c/src/discovery/metadata_repository.py)
- snapshot repository: [snapshot_repository.py](/Users/home/Development/c2c/src/discovery/snapshot_repository.py)
- discovery service: [service.py](/Users/home/Development/c2c/src/discovery/service.py)
- local CSV workflow: [local_csv.py](/Users/home/Development/c2c/src/workflows/local_csv.py)
- local filesystem workflow: [local_filesystem.py](/Users/home/Development/c2c/src/workflows/local_filesystem.py)
- database workflows: [database.py](/Users/home/Development/c2c/src/workflows/database.py)
- semantic synthesis: [synthesizer.py](/Users/home/Development/c2c/src/semantic_layer/synthesizer.py)
- semantic contracts: [contracts.py](/Users/home/Development/c2c/src/semantic_layer/contracts.py)
- semantic draft storage: [storage.py](/Users/home/Development/c2c/src/semantic_layer/storage.py)
- local scan UI: [server.py](/Users/home/Development/c2c/ui/server.py)

## Python Package Layout

The current Python package is organized like this:

```text
src/
|-- artifacts.py
|-- cli.py
|-- config.py
|-- connectors/
|   |-- databases/
|   |   |-- base.py
|   |   |-- bigquery_connector.py
|   |   |-- databricks_connector.py
|   |   |-- executor.py
|   |   |-- mysql_connector.py
|   |   |-- oracle_connector.py
|   |   |-- postgres_connector.py
|   |   |-- redshift_connector.py
|   |   |-- schema_snapshot.py
|   |   |-- snowflake_connector.py
|   |   `-- sqlserver_connector.py
|   |-- files/
|   |   |-- csv_connector.py
|   |   `-- filesystem_connector.py
|   |-- base.py
|   `-- registry.py
|-- discovery/
|   |-- metadata_repository.py
|   |-- runner.py
|   |-- service.py
|   `-- snapshot_repository.py
|-- evaluation/
|   `-- semantic_quality.py
|-- examples/
|   `-- local_csv_pipeline.py
|-- integrations.py
|-- models/
|   |-- metadata.py
|   `-- semantic.py
|-- org_context/
|   `-- loader.py
|-- workflows/
|   |-- common.py
|   |-- database.py
|   `-- local_csv.py
|-- semantic_layer/
|   |-- contracts.py
|   |-- storage.py
|   `-- synthesizer.py
`-- version.py
```

This gives us a clean Python-first development path:

- connectors discover and sample source assets,
- shared database abstractions keep warehouse and OLTP connectors consistent,
- query executors decouple connector logic from vendor SDKs and drivers,
- schema snapshots make drift detection a first-class operational concern,
- connector runners make discovery reproducible and operationally consistent,
- workflows and the CLI make the pipeline runnable from the terminal,
- config files make live-source runs reproducible and environment-aware,
- policy artifacts make company-specific behavior explicit and reviewable,
- discovery normalizes everything into a metadata graph,
- semantic synthesis turns discovered assets into draft business concepts,
- semantic contracts turn draft semantics into reviewable business artifacts,
- relationship inference begins to expose cross-source join semantics as explicit artifacts,
- semantic storage makes draft layers versionable artifacts,
- orchestration, governance, retrieval, and serving can layer on top next.

## Step-By-Step Process

This is the intended end-to-end workflow for the platform.

### 1. Define a source

Create a `SourceDefinition` that describes the system to connect:

- source id,
- source type,
- connection reference,
- optional owner and tags.

### 1.1 Define organization context

Add company-specific artifacts under `organization_context/` for:

- business glossary and preferred terminology,
- governance and review rules,
- org-specific ownership and business context.

These should act as behavior inputs for semantic synthesis and contract generation.

### 2. Choose a connector

Pick the connector that matches the source type:

- `CsvConnector` for local file discovery,
- `PostgresConnector` for PostgreSQL,
- `BigQueryConnector` for BigQuery,
- other database families via the shared database connector framework.

### 3. Wire an executor

For queryable sources, attach an executor adapter:

- `DbApiQueryExecutor` for DB-API style connections,
- `BigQueryQueryExecutor` for BigQuery-style clients,
- test doubles for local development and unit tests.

This keeps connector behavior independent from driver choice.

### 4. Run discovery

Use `ConnectorRunner` to execute the connector workflow:

1. discover assets,
2. profile each asset,
3. sample each asset,
4. compare the current schema snapshot with the previous one,
5. persist the latest snapshot.

The output is a `MetadataGraph` plus any drift events.

For local file sources, use the workflow wrapper and CLI to run the whole sequence in one command.

### 5. Build the metadata graph

For multiple sources, register connectors in a `ConnectorRegistry` and use `DiscoveryService` to merge their outputs into one graph.

This graph becomes the control-plane representation of:

- sources,
- assets,
- fields,
- profiles,
- samples,
- change events.

### 6. Synthesize the semantic layer

Pass the `MetadataGraph` into `SemanticSynthesizer`.

The current implementation creates:

- candidate entities,
- candidate metrics,
- candidate relationships,
- semantic draft notes.

When an organization-context folder is provided, synthesis can also incorporate glossary synonyms and org context notes.

Later iterations will add richer relationship inference, glossary mapping, and LLM-assisted refinement.

### 7. Persist the semantic draft

Use `SemanticLayerRepository` to save synthesized semantic drafts as versioned JSON artifacts.

This gives us a first path toward:

- reviewable semantic versions,
- benchmarkable outputs,
- deployment-time semantic contracts.

The workflow also persists the metadata graph and a run summary artifact so every pipeline execution leaves an inspectable trail.

### 7.1 Generate semantic contracts

Use `SemanticContractGenerator` to convert draft entities and metrics into reviewable contracts with:

- status,
- owner,
- provenance,
- confidence,
- sensitivity and policy tags,
- validation notes.

The workflow now persists these contracts next to the semantic draft artifact.

When an organization-context folder is supplied, contracts can also inherit:

- glossary-driven synonyms,
- org-driven owners,
- governance-driven policy tags.

### 8. Evaluate and refine

Use the `evaluation/` structure to compare:

- source coverage,
- semantic quality,
- drift behavior,
- BI answer quality,
- safety and governance outcomes.

Corrections and usage feedback should later flow back into connector confidence, semantic mappings, and orchestration quality.

The repo now includes a starter semantic-quality scorer and a benchmark fixture so we can begin measuring:

- entity precision and recall,
- metric precision and recall,
- relationship precision and recall,
- governance tag recall,
- contract coverage against a gold set.

## Example Workflow

```python
from connectors import ConnectorRegistry
from connectors.databases import DbApiQueryExecutor, PostgresConnector
from discovery import ConnectorRunner, DiscoveryService, SchemaSnapshotRepository
from models import SourceDefinition, SourceType
from semantic_layer import (
    SemanticContractGenerator,
    SemanticContractRepository,
    SemanticLayerRepository,
    SemanticSynthesizer,
)

source = SourceDefinition(
    source_id="pg-prod",
    name="Production Postgres",
    source_type=SourceType.DATABASE,
    connection_ref="postgresql://warehouse",
)

executor = DbApiQueryExecutor(connection)
connector = PostgresConnector(source, executor=executor)

runner = ConnectorRunner(SchemaSnapshotRepository(".artifacts/schema"))
graph = runner.run(connector).graph
semantic_draft = SemanticSynthesizer().synthesize(graph, version="draft-v1")
contracts = SemanticContractGenerator().generate(semantic_draft)
SemanticLayerRepository(".artifacts/semantic").save(semantic_draft)
SemanticContractRepository(".artifacts/semantic").save(contracts)
```

## Local Scan UI

The repo now includes a lightweight local web app under [ui/](/Users/home/Development/c2c/ui) for scanning a folder on your machine and synthesizing a semantic layer over common enterprise file types.

Run it locally:

```bash
PYTHONPATH=src python3 ui/server.py --host 127.0.0.1 --port 8765
```

Then open `http://127.0.0.1:8765` and provide:

- a root folder to scan,
- an artifact output folder,
- an optional `organization_context/` path,
- a max file limit,
- the file extensions to include.

The local UI currently scans common artifacts such as:

- CSV and TSV tables,
- JSON exports,
- markdown and text notes,
- PDFs,
- spreadsheet and parquet file placeholders for future deeper parsing.

## CLI Workflow

The fastest runnable paths today are the local CSV workflow and the local filesystem workflow, with the same CLI shape also available for PostgreSQL and BigQuery through JSON configs.

### Command

```bash
PYTHONPATH=src python3 -m cli run-local-csv \
  --csv-root ./data \
  --artifact-root ./.artifacts \
  --context-root ./organization_context \
  --source-id local-csv \
  --source-name "Local CSV Source" \
  --semantic-version draft-v1
```

### Filesystem Command

```bash
PYTHONPATH=src python3 -m cli run-local-filesystem \
  --root-path ~/Documents \
  --artifact-root ./.artifacts/ui \
  --context-root ./organization_context \
  --extensions csv pdf md json txt \
  --max-files 500
```

### Postgres Command

```bash
PYTHONPATH=src python3 -m cli run-postgres --config ./configs/postgres.json
```

### BigQuery Command

```bash
PYTHONPATH=src python3 -m cli run-bigquery --config ./configs/bigquery.json
```

### What the CLI does

1. creates the artifact directory layout,
2. builds a `SourceDefinition`,
3. runs connector discovery through `ConnectorRunner`,
4. saves the metadata graph,
5. synthesizes the semantic layer draft,
6. saves the semantic draft,
7. saves semantic contracts,
8. writes a run summary JSON,
9. prints a JSON summary to stdout.

For PostgreSQL and BigQuery, the CLI also:

1. loads the source config,
2. builds the correct executor from the config,
3. runs the database connector,
4. writes the same artifact set and run summary.

### Config Format

PostgreSQL example:

```json
{
  "source_id": "pg-prod",
  "source_name": "Production Postgres",
  "source_type": "database",
  "connection_ref": "postgresql://warehouse",
  "artifact_root": ".artifacts/postgres",
  "context_root": "./organization_context",
  "semantic_version": "draft-v1",
  "executor": {
    "kind": "dbapi",
    "module": "psycopg",
    "kwargs": {
      "conninfo": "postgresql://warehouse"
    }
  }
}
```

BigQuery example:

```json
{
  "source_id": "bq-prod",
  "source_name": "Production BigQuery",
  "source_type": "database",
  "connection_ref": "bigquery://project",
  "artifact_root": ".artifacts/bigquery",
  "context_root": "./organization_context",
  "semantic_version": "draft-v1",
  "executor": {
    "kind": "bigquery_client",
    "module": "google.cloud.bigquery"
  }
}
```

The executor config keeps the core package dependency-light:

- `dbapi` imports a Python DB-API module and calls `connect(...)`,
- `bigquery_client` imports a BigQuery-style client factory,
- both flow into the same connector contract.

Ready-to-adapt templates live in [configs/README.md](/Users/home/Development/c2c/configs/README.md), [postgres.example.json](/Users/home/Development/c2c/configs/postgres.example.json), and [bigquery.example.json](/Users/home/Development/c2c/configs/bigquery.example.json).

### Artifact Layout

By default, the workflow writes artifacts under `.artifacts/`:

```text
.artifacts/
|-- metadata/
|   `-- <source-id>-metadata-graph.json
|-- runs/
|   `-- <source-id>-latest.json
|-- schema/
|   `-- <source-id>.json
`-- semantic/
    |-- <semantic-version>.json
    `-- <semantic-version>-contracts.json
```

This convention gives us a stable structure for local development now and for future scheduled connector runs later.

The run summary includes:

- source details,
- asset, entity, metric, and drift counts,
- whether a schema snapshot was saved,
- schema snapshot path when applicable,
- artifact paths,
- semantic contract artifact path,
- timing information.

## Core Modules

The active repo currently centers on these modules:

- `src/connectors/` for source adapters and discovery primitives
- `src/org_context/` for glossary, governance rules, and company context inputs
- `src/discovery/` for metadata graph assembly and drift tracking
- `src/semantic_layer/` for semantic drafts and contract generation
- `src/evaluation/` plus `evaluation/` for benchmark scoring and gold fixtures

## Initial Connector Strategy

We should not build every connector at once. The right first move is a capability-based connector program.

Wave 1:

- PostgreSQL
- MySQL
- Snowflake
- BigQuery
- Redshift
- Databricks
- CSV / Excel
- S3 / object storage parquet
- Salesforce
- Zendesk
- Slack export / message archive
- Google Drive / shared document corpus

Wave 2:

- SQL Server
- Oracle
- HubSpot
- Jira
- ServiceNow
- NetSuite
- SharePoint / Confluence
- Generic REST connector framework

Connector details live in [docs/connectors/connector-catalog.md](/Users/home/Development/c2c/docs/connectors/connector-catalog.md).

## Semantic Layer Strategy

The semantic layer is the core differentiator. It should not be a thin dbt-style metric registry only, and it should not be a purely LLM-generated artifact with no controls.

We want a hybrid semantic model:

- machine-synthesized first draft,
- confidence-scored mappings,
- explicit provenance back to source assets,
- versioned metric contracts,
- human override and approval for critical definitions,
- continuous improvement from usage and corrections.

Detailed design lives in [docs/architecture/semantic-layer-strategy.md](/Users/home/Development/c2c/docs/architecture/semantic-layer-strategy.md).

## Evaluation Focus

The platform should be judged on more than demo quality. We care about:

- coverage of heterogeneous sources,
- quality of synthesized semantic models,
- BI answer correctness,
- time-to-insight,
- governance and safety performance,
- robustness to schema drift,
- cost and latency,
- trust and adoption.

The evaluation framework lives in [docs/architecture/evaluation-framework.md](/Users/home/Development/c2c/docs/architecture/evaluation-framework.md).

## Recommended Build Sequence

1. Define the connector interface and source capability model.
2. Implement Wave 1 connectors and normalize all discovered assets into a common metadata graph.
3. Add shared database discovery logic for PostgreSQL, MySQL, Snowflake, BigQuery, Databricks, and Redshift.
4. Finish production implementations for PostgreSQL and BigQuery with real executors, auth, and catalog queries.
5. Add schema snapshot persistence and drift monitoring for database connectors.
6. Build semantic synthesis pipelines for entity, metric, and relationship inference.
7. Add retrieval pipelines for documents and semi-structured assets.
8. Implement orchestration flows for source selection, text-to-SQL, retrieval, verification, and answer composition.
9. Add governance enforcement and observability from the start, not after the fact.
10. Stand up the evaluation harness with offline tasks before building a polished user interface.

## Local Development

The repo now includes a minimal Python package definition in [pyproject.toml](/Users/home/Development/c2c/pyproject.toml).

Useful early commands:

```bash
python3 -m compileall src tests
python3 -m pytest
PYTHONPATH=src python3 -m examples.local_csv_pipeline
PYTHONPATH=src python3 -m cli run-local-csv --csv-root ./data --artifact-root ./.artifacts
PYTHONPATH=src python3 -m cli run-postgres --config ./configs/postgres.json
PYTHONPATH=src python3 -m cli run-bigquery --config ./configs/bigquery.json
```

The example pipeline expects a local `data/` folder with one or more CSV files and will:

1. register a local CSV source,
2. discover file assets,
3. profile and sample them,
4. synthesize a draft semantic layer.

For source-layout execution before installation, use:

```bash
PYTHONPATH=src python3 -m compileall src tests
```

## What I Changed In This Iteration

This repo now treats the original paper as a product and platform blueprint, not just a research narrative. The new docs and directory scaffold give us a stable place to implement:

- multi-source connectors,
- semantic layer synthesis,
- LLM orchestration,
- evaluation assets,
- deployment patterns.

This iteration also adds the first Python implementation layer so the architecture is no longer documentation-only. We now have an actual runtime foundation for:

- connector contracts,
- reusable database connector scaffolding across common enterprise databases and warehouses,
- metadata graph construction,
- early semantic synthesis,
- semantic-layer draft persistence,
- example local execution,
- testable package structure.

## Research Basis

The original research paper that anchors this repo now lives at [research-paper.md](/Users/home/Development/c2c/docs/research-paper.md).

## Research Paper Basis

The original research framing remains central: a production-oriented architecture and evaluation approach for an LLM-orchestrated BI layer over heterogeneous, uncurated enterprise data sources. This repository now extends that framing into an implementation strategy that can support real connector development, semantic unification, and production deployment work.
