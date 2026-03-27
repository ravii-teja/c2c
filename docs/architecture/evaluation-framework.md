# Evaluation Framework

## Evaluation Thesis

The platform should be evaluated as a production analytical system, not just as an LLM demo.

We care about four things:

- breadth of source coverage,
- quality of semantic synthesis,
- usefulness and correctness of BI outputs,
- operational safety and sustainability.

## Primary Evaluation Axes

### 1. Source Coverage

Measure:

- number of connector types supported,
- percentage of enterprise source classes covered,
- asset discovery completeness,
- successful profiling rate,
- drift-detection latency.

### 2. Semantic Layer Quality

Measure:

- entity precision and recall,
- metric precision and recall,
- relationship correctness,
- synonym quality,
- policy annotation coverage,
- human hours required to reach acceptable quality.

### 3. Insight Quality

Measure:

- execution success rate,
- result correctness,
- semantic intent match,
- citation quality,
- actionable-insight rate,
- time-to-first-acceptable-answer.

### 4. Governance And Safety

Measure:

- blocked unsafe query rate,
- policy violation leakage,
- unsupported-claim rate,
- audit completeness,
- sensitive-data exposure incidents.

### 5. Operational Performance

Measure:

- P50, P95, P99 latency,
- token cost,
- backend execution cost,
- cache hit rate,
- replan rate,
- recovery after drift.

## Benchmark Types

### Offline Gold Benchmarks

Use curated subsets where entities, metrics, relationships, and answers are hand-labeled.

### Replay Workloads

Re-run historical BI tasks, analyst requests, and dashboard questions against evolving system versions.

### Drift Benchmarks

Inject renamed columns, moved assets, changed schemas, and new sources to test resilience.

### Governance Benchmarks

Simulate restricted access, PII presence, and high-cost queries to verify enforcement.

### User Outcome Studies

Measure:

- task completion,
- trust,
- clarity,
- reduction in analyst dependency,
- decision support usefulness.

## Recommended Evaluation Assets In This Repo

The `evaluation/` tree should eventually contain:

- `benchmarks/` for benchmark definitions,
- `gold/` for gold semantic and answer sets,
- `workloads/` for realistic question suites and replay traces,
- `rubrics/` for expert grading and user-study instruments.

The Python runtime now includes a starter semantic-quality scorer that can compare generated semantic contracts against a small gold benchmark. This is the first step toward repo-native evaluation rather than documentation-only evaluation plans.

The scorer now includes relationship precision and recall so cross-source semantic unification can be evaluated alongside entities and metrics. It also includes governance tag recall so sensitivity and policy annotations can be measured as part of semantic quality.

## Minimum Viable Evaluation Before GA

Before calling the platform production-ready, we should have:

1. at least one gold semantic benchmark for a realistic business domain,
2. at least one multi-source BI workload,
3. drift tests for renamed schemas and new-source onboarding,
4. governance tests for restricted fields and high-risk queries,
5. latency and cost dashboards for the main orchestration paths.
