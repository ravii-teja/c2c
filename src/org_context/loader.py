from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class GlossaryEntry:
    canonical_name: str
    synonyms: list[str] = field(default_factory=list)
    owner: str | None = None
    description: str = ""


@dataclass(slots=True)
class GovernanceRule:
    rule_id: str
    applies_to: list[str] = field(default_factory=list)
    policy_tags: list[str] = field(default_factory=list)
    sensitivity: str | None = None
    description: str = ""


@dataclass(slots=True)
class OrgProfile:
    company_name: str = ""
    default_metric_owner: str | None = None
    business_units: list[str] = field(default_factory=list)
    preferred_terms: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class OrganizationContextBundle:
    glossary: dict[str, GlossaryEntry] = field(default_factory=dict)
    governance_rules: list[GovernanceRule] = field(default_factory=list)
    org_profile: OrgProfile = field(default_factory=OrgProfile)


class OrganizationContextLoader:
    """Load company glossary, governance rules, and org context from a context folder."""

    def load(self, root: str | Path) -> OrganizationContextBundle:
        root_path = Path(root)

        # Keep file names stable so non-engineering teams can update context
        # inputs without needing to understand the Python package layout.
        glossary_path = root_path / "business_glossary.json"
        governance_path = root_path / "governance_rules.json"
        context_path = root_path / "org_context.json"

        glossary = self._load_glossary(glossary_path) if glossary_path.exists() else {}
        governance_rules = (
            self._load_governance_rules(governance_path) if governance_path.exists() else []
        )
        org_profile = self._load_org_profile(context_path) if context_path.exists() else OrgProfile()

        return OrganizationContextBundle(
            glossary=glossary,
            governance_rules=governance_rules,
            org_profile=org_profile,
        )

    def _load_glossary(self, path: Path) -> dict[str, GlossaryEntry]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return {
            entry["canonical_name"]: GlossaryEntry(
                canonical_name=entry["canonical_name"],
                synonyms=entry.get("synonyms", []),
                owner=entry.get("owner"),
                description=entry.get("description", ""),
            )
            for entry in payload.get("entries", [])
        }

    def _load_governance_rules(self, path: Path) -> list[GovernanceRule]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [
            GovernanceRule(
                rule_id=entry["rule_id"],
                applies_to=entry.get("applies_to", []),
                policy_tags=entry.get("policy_tags", []),
                sensitivity=entry.get("sensitivity"),
                description=entry.get("description", ""),
            )
            for entry in payload.get("rules", [])
        ]

    def _load_org_profile(self, path: Path) -> OrgProfile:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return OrgProfile(
            company_name=payload.get("company_name", ""),
            default_metric_owner=payload.get("default_metric_owner"),
            business_units=payload.get("business_units", []),
            preferred_terms=payload.get("preferred_terms", {}),
        )
