import json

from workflows import run_local_csv_workflow


def test_local_csv_workflow_uses_context_folder_for_contract_context(tmp_path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "customers.csv").write_text(
        "customer_id,email\n1,a@example.com\n",
        encoding="utf-8",
    )

    context_dir = tmp_path / "organization_context"
    context_dir.mkdir(parents=True, exist_ok=True)
    (context_dir / "business_glossary.json").write_text(
        """
        {
          "entries": [
            {
              "canonical_name": "customers",
              "synonyms": ["clients"],
              "owner": "revops"
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    (context_dir / "governance_rules.json").write_text(
        """
        {
          "rules": [
            {
              "rule_id": "customer-data",
              "applies_to": ["customer"],
              "policy_tags": ["policy:customer-data"]
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    (context_dir / "org_context.json").write_text(
        """
        {
          "company_name": "Example Enterprise",
          "default_metric_owner": "finance"
        }
        """,
        encoding="utf-8",
    )

    result = run_local_csv_workflow(
        csv_root=str(data_dir),
        artifact_root=str(tmp_path / "artifacts"),
        source_id="csv-policy-test",
        semantic_version="draft-policy-test",
        context_root=str(context_dir),
    )

    contract_payload = json.loads(result.contract_path.read_text(encoding="utf-8"))
    assert "clients" in contract_payload["entities"][0]["synonyms"]
    assert contract_payload["entities"][0]["owner"] == "revops"
    assert "policy:customer-data" in contract_payload["entities"][0]["policy_tags"]
