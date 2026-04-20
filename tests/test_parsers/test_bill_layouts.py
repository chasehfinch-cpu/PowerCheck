"""Tests for per-utility bill layout guides."""

from __future__ import annotations

import pytest

from tariff_audit.parsers.bill_layouts import (
    all_layouts,
    detect_layout,
    get_layout,
)


def test_all_four_iou_layouts_registered():
    utilities = {g.utility for g in all_layouts()}
    assert utilities == {"FPL", "DUKE", "TECO", "FPU"}


def test_fpl_layout_documents_core_fields():
    g = get_layout("FPL")
    assert g.locate("base_charge") is not None
    assert g.locate("fuel_charge") is not None
    assert g.locate("total_amount_due") is not None
    assert g.locate("gross_receipts_tax") is not None
    assert g.locate("franchise_fee") is not None
    assert g.locate("utility_tax") is not None
    assert g.locate("psc_regulatory_fee") is not None


def test_duke_layout_separates_all_clauses():
    """Duke itemizes each clause separately — that's its defining trait."""
    g = get_layout("DUKE")
    for fld in ("energy_charge", "fuel_charge", "conservation_charge",
                "capacity_charge", "environmental_charge", "storm_protection_charge"):
        assert g.locate(fld) is not None, f"Duke layout missing {fld}"


def test_teco_layout_flags_bundled_conservation():
    g = get_layout("TECO")
    assert g.bundled_clauses != ()
    # The bundled note should reference the embedded 0.621 figure
    assert any("0.621" in c for c in g.bundled_clauses)


def test_fpu_layout_flags_customer_facilities_charge():
    g = get_layout("FPU")
    base = g.locate("base_charge")
    assert base is not None
    assert "Customer Facilities Charge" in base.label_on_bill


def test_fpu_layout_flags_bundled_purchased_power():
    g = get_layout("FPU")
    assert g.bundled_clauses != ()
    assert any("Purchased Power" in c for c in g.bundled_clauses)


def test_unknown_utility_raises():
    with pytest.raises(KeyError):
        get_layout("NOPE")


def test_detect_layout_identifies_fpl():
    g = detect_layout("Florida Power & Light is your utility provider.")
    assert g is not None
    assert g.utility == "FPL"


def test_detect_layout_identifies_duke():
    g = detect_layout("Thank you for being a Duke Energy Florida customer.")
    assert g is not None
    assert g.utility == "DUKE"


def test_detect_layout_identifies_teco():
    g = detect_layout("Tampa Electric account statement.")
    assert g is not None
    assert g.utility == "TECO"


def test_detect_layout_identifies_fpu():
    g = detect_layout("Florida Public Utilities billing statement.")
    assert g is not None
    assert g.utility == "FPU"


def test_detect_layout_returns_none_for_unrelated_text():
    assert detect_layout("This is not a utility bill.") is None


def test_every_layout_has_reference_url():
    for g in all_layouts():
        assert g.layout_reference_url.startswith("http")


def test_every_layout_has_total_amount_due_field():
    """The end user must always know where the final total is."""
    for g in all_layouts():
        assert g.locate("total_amount_due") is not None, (
            f"{g.utility} layout missing total_amount_due location"
        )
