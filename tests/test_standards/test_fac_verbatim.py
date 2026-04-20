"""Tests for the verbatim FAC rule text."""

from __future__ import annotations

import pytest

from tariff_audit.standards.fac_25_6_verbatim import VERBATIM_TEXT, verbatim


def test_every_billing_critical_rule_has_verbatim_text():
    """The rules the audit engine relies on most heavily must have full text."""
    for rid in ("25-6.052", "25-6.065", "25-6.097", "25-6.099",
                "25-6.100", "25-6.101", "25-6.103", "25-6.106"):
        text = verbatim(rid)
        assert text.strip().startswith(rid), f"{rid} verbatim doesn't start with rule id"
        assert len(text) > 100, f"{rid} verbatim is suspiciously short"


def test_25_6_052_mentions_two_percent_tolerance():
    assert "two percent" in verbatim("25-6.052") or "2 percent" in verbatim("25-6.052")


def test_25_6_097_mentions_deposit_interest_rates():
    text = verbatim("25-6.097")
    assert "2 percent" in text
    assert "3 percent" in text


def test_25_6_106_mentions_twelve_month_backbilling_cap():
    text = verbatim("25-6.106")
    assert "twelve" in text.lower() or "12" in text


def test_25_6_101_mentions_twenty_day_delinquency():
    assert "20 days" in verbatim("25-6.101")


def test_25_6_100_lists_required_bill_content():
    text = verbatim("25-6.100")
    # The rule requires each of these items on the bill
    lowered = text.lower()
    for required in ("rate schedule", "payment deadline", "delinquent",
                     "average daily", "conversion factor", "budget billing"):
        assert required in lowered, f"25-6.100 verbatim missing {required!r}"


def test_unknown_rule_raises():
    with pytest.raises(KeyError):
        verbatim("25-6.999")


def test_coverage_set_is_documented():
    assert set(VERBATIM_TEXT) == {
        "25-6.052", "25-6.065", "25-6.097", "25-6.099",
        "25-6.100", "25-6.101", "25-6.103", "25-6.106",
    }
