"""Tests for the FAC 25-6 rule catalog."""

from __future__ import annotations

import pytest

from tariff_audit.standards.fac_25_6 import (
    FAC_25_6_RULES,
    rule,
    rules_by_category,
)


def test_every_rule_has_unique_id():
    ids = [r.rule_id for r in FAC_25_6_RULES]
    assert len(ids) == len(set(ids)), "Duplicate rule IDs in FAC 25-6 catalog"


def test_critical_billing_rules_present():
    """The rules that drive our calculator/audit must all be catalogued."""
    critical = ["25-6.052", "25-6.100", "25-6.101", "25-6.103", "25-6.106", "25-6.065"]
    for rid in critical:
        assert rule(rid).rule_id == rid


def test_rules_by_category_returns_correct_members():
    billing = rules_by_category("BILLING")
    assert rule("25-6.100") in billing
    assert rule("25-6.106") in billing
    # 25-6.039 (Safety) is OPERATIONAL, not BILLING
    safety = rule("25-6.039")
    assert safety not in billing


def test_implemented_by_references_resolve():
    """Every 'implemented_by' pointer should name an attribute that exists.

    Walks dotted paths that may reference module → class → field (e.g.
    ``tariffs.models.TariffSchedule.storm_protection``).
    """
    import importlib

    for r in FAC_25_6_RULES:
        if not r.implemented_by:
            continue
        parts = r.implemented_by.split(".")
        # Find the longest importable module prefix
        module = None
        module_end = 0
        for i in range(len(parts), 0, -1):
            try:
                module = importlib.import_module("tariff_audit." + ".".join(parts[:i]))
                module_end = i
                break
            except ModuleNotFoundError:
                continue
        assert module is not None, (
            f"FAC rule {r.rule_id} implemented_by {r.implemented_by!r}: "
            f"no importable module prefix found"
        )
        # Walk any remaining attribute lookups. For Pydantic BaseModel
        # classes, check ``model_fields`` since fields are not plain class
        # attributes in Pydantic v2.
        target = module
        for name in parts[module_end:]:
            if hasattr(target, name):
                target = getattr(target, name)
                continue
            pydantic_fields = getattr(target, "model_fields", None)
            if pydantic_fields is not None and name in pydantic_fields:
                # Field exists on the Pydantic model — don't descend further.
                target = pydantic_fields[name]
                continue
            raise AssertionError(
                f"FAC rule {r.rule_id} implemented_by {r.implemented_by!r}: "
                f"{target!r} has no attribute {name!r}"
            )


def test_unknown_rule_lookup_raises():
    with pytest.raises(KeyError):
        rule("25-6.999")


def test_rules_are_frozen_dataclasses():
    r = rule("25-6.106")
    with pytest.raises(AttributeError):
        # FacRule is frozen — direct mutation must fail.
        r.summary = "mutated"  # type: ignore[misc]


def test_rule_25_6_106_documents_backbilling_limit():
    r = rule("25-6.106")
    assert "12 months" in r.summary or "twelve" in r.summary.lower()


def test_rule_25_6_052_documents_meter_tolerance():
    r = rule("25-6.052")
    assert "2%" in r.summary or "2 percent" in r.summary.lower()


def test_rule_25_6_100_is_billing_not_operational():
    assert rule("25-6.100").audit_relevance == "BILLING"
