# Config Examples

This directory holds example source-run configuration files for CLI workflows.

Copy an example, adjust the connection and executor settings for your environment, and run:

```bash
PYTHONPATH=src python3 -m cli run-postgres --config ./configs/postgres.example.json
PYTHONPATH=src python3 -m cli run-bigquery --config ./configs/bigquery.example.json
```

Do not commit real credentials into these files.
