# Connector Catalog Strategy

## Purpose

Connectors should be treated as productized capability adapters, not one-off integrations.

Each connector should declare:

- asset types supported,
- query or retrieval capabilities,
- metadata fidelity,
- incremental sync support,
- auth pattern,
- governance considerations.

## Wave 1 Connectors

### Structured Data

- PostgreSQL
- MySQL
- Snowflake
- BigQuery
- Redshift
- Databricks

### Files And Lake Assets

- CSV
- Excel
- Parquet on object storage

### SaaS And Operational Tools

- Salesforce
- Zendesk
- Slack exports
- Google Drive

## Wave 2 Connectors

- SQL Server
- Oracle
- HubSpot
- Jira
- ServiceNow
- NetSuite
- SharePoint
- Confluence
- generic REST connector toolkit

## Common Connector Contract

Every connector implementation should provide:

- discovery of accessible assets,
- schema or content metadata extraction,
- lightweight profiling,
- representative sampling,
- governed execution or fetch,
- drift signal emission,
- capability descriptors.

## Python Connector Implementation Strategy

The Python runtime now uses a layered connector design:

- `Connector` for the global source contract,
- `DatabaseConnector` for shared behavior across queryable databases and warehouses,
- source-family packages for `databases`, `files`, `saas`, and `unstructured`,
- thin platform-specific connector classes that inherit common capability semantics.

This is important because PostgreSQL, BigQuery, Databricks, Redshift, Snowflake, MySQL, SQL Server, and Oracle should not each reinvent:

- capability declarations,
- profiling contract shape,
- drift detection semantics,
- asset typing behavior,
- governance handoff points.

The runtime now also includes:

- executor adapters for DB-API and BigQuery-style clients,
- shared freshness-column heuristics for safer profiling,
- schema snapshot comparison for drift detection.

## Current Python Database Connector Coverage

Implemented with query-driven logic in `src/connectors/databases/`:

- PostgreSQL
- BigQuery

Scaffolded in `src/connectors/databases/`:

- MySQL
- Snowflake
- Databricks
- Redshift
- SQL Server
- Oracle

Implemented for local execution in `src/connectors/files/`:

- CSV

The remaining database connectors are currently scaffolds with shared contracts. The next implementation layer should add:

- credential handling,
- production wiring for vendor SDK or driver adapters that satisfy the query executor protocol,
- production-safe system-catalog discovery queries,
- richer timestamp-aware freshness profiling,
- persisted schema drift comparison and alerting.

## Capability Matrix

Suggested dimensions:

- structured queryable,
- unstructured retrievable,
- incremental discoverable,
- lineage hints,
- supports policy propagation,
- supports row-level filtering,
- supports freshness metadata.

## Build Order Rationale

Wave 1 balances value and engineering leverage:

- relational sources prove text-to-SQL and semantic mapping,
- file sources prove ingestion on messy data,
- SaaS sources prove API and business-object variability,
- document and collaboration sources prove unstructured retrieval.

Together, they exercise the core thesis of the platform without waiting for full connector coverage.
