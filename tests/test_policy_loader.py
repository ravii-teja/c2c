from org_context import OrganizationContextLoader


def test_policy_loader_reads_policy_bundle(tmp_path) -> None:
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

    bundle = OrganizationContextLoader().load(context_dir)

    assert bundle.org_profile.company_name == "Example Enterprise"
    assert bundle.glossary["customers"].synonyms == ["clients"]
    assert bundle.governance_rules[0].policy_tags == ["policy:customer-data"]
