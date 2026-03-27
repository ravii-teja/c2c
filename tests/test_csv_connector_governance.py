from connectors.files import CsvConnector
from models import SensitivityClass, SourceDefinition, SourceType


def test_csv_connector_infers_sensitivity_and_policy_tags(tmp_path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "customers.csv").write_text(
        "customer_id,email,ssn\n1,a@example.com,111-22-3333\n",
        encoding="utf-8",
    )

    connector = CsvConnector(
        SourceDefinition(
            source_id="csv-governance",
            name="CSV Governance",
            source_type=SourceType.FILE_SYSTEM,
            connection_ref=str(data_dir),
        )
    )

    assets = connector.discover_assets()

    assert len(assets) == 1
    assert assets[0].sensitivity == SensitivityClass.RESTRICTED
    fields = {field.name: field for field in assets[0].fields}
    assert fields["email"].policy_tags == ["pii:email"]
    assert fields["ssn"].sensitivity == SensitivityClass.RESTRICTED
