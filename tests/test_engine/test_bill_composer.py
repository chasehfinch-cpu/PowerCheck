"""Tests for the end-to-end bill composer."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from tariff_audit.engine.bill_composer import compose_expected_bill


def test_fpl_residential_single_period_no_local_taxes():
    """A 30-day FPL peninsular bill entirely within Jan 2026."""
    bill = compose_expected_bill(
        "FPL",
        "RS-1",
        billing_period_start=date(2026, 1, 1),
        billing_period_end=date(2026, 1, 30),
        total_kwh=1000,
        is_residential=True,
    )

    assert bill.billing_days == 30
    assert len(bill.segments) == 1
    assert bill.tariff_subtotal == Decimal("133.10")
    assert bill.taxes.sales_tax == Decimal("0.00")  # residential exempt
    assert bill.taxes.gross_receipts_tax == Decimal("3.41")
    assert bill.total_due == Decimal("136.51")


def test_fpl_residential_miami_includes_municipal_and_franchise():
    """Same bill but in Miami with 10% PST + 6% franchise."""
    bill = compose_expected_bill(
        "FPL",
        "RS-1",
        billing_period_start=date(2026, 1, 1),
        billing_period_end=date(2026, 1, 30),
        total_kwh=1000,
        is_residential=True,
        municipal_utility_tax_rate=Decimal("0.10"),
        franchise_fee_rate=Decimal("0.06"),
    )
    # 133.10 + GRT 3.41 + MUT 13.31 + Franchise 7.99 = 157.81
    assert bill.total_due == Decimal("157.81")


def test_fpl_bill_spanning_year_end_prorates_across_2025_and_2026():
    """A billing period Dec 15 2025 – Jan 14 2026 crosses the rate boundary.

    Feb 2025 schedule (effective through Dec 31 2025) → $130.68 / 1,000 kWh
    2026 peninsular schedule (effective Jan 1 2026) → $133.10 / 1,000 kWh

    17 days in 2025 / 31-day cycle = 0.5484 share
    14 days in 2026 / 31-day cycle = 0.4516 share

    Expected prorated subtotal ≈ 0.5484 × 130.68 + 0.4516 × 133.10 ≈ $131.77
    """
    bill = compose_expected_bill(
        "FPL",
        "RS-1",
        billing_period_start=date(2025, 12, 15),
        billing_period_end=date(2026, 1, 14),
        total_kwh=1000,
        is_residential=True,
    )

    assert bill.billing_days == 31
    assert len(bill.segments) == 2
    # Segment 1: Dec 15–31, 2025 (17 days), Feb 2025 schedule
    assert bill.segments[0].start == date(2025, 12, 15)
    assert bill.segments[0].end == date(2025, 12, 31)
    assert bill.segments[0].days == 17
    # Segment 2: Jan 1–14, 2026 (14 days), 2026 peninsular schedule
    assert bill.segments[1].start == date(2026, 1, 1)
    assert bill.segments[1].end == date(2026, 1, 14)
    assert bill.segments[1].days == 14
    # Subtotal falls between the two single-period subtotals
    assert Decimal("130") < bill.tariff_subtotal < Decimal("134")


def test_teco_30_day_bill_uses_monthly_base_consistent_with_daily_tariff():
    """TECO's daily-base tariff ($0.45/day) should yield $13.50 over 30 days."""
    bill = compose_expected_bill(
        "TECO",
        "RS",
        billing_period_start=date(2026, 2, 1),
        billing_period_end=date(2026, 3, 2),  # 30 days
        total_kwh=1000,
        is_residential=True,
    )
    assert bill.billing_days == 30
    assert bill.segments[0].calculated.base_charge == Decimal("13.50")


def test_teco_31_day_bill_prorates_base_via_daily_rate():
    """A 31-day cycle bills 31 × $0.45 = $13.95 base."""
    bill = compose_expected_bill(
        "TECO",
        "RS",
        billing_period_start=date(2026, 2, 1),
        billing_period_end=date(2026, 3, 3),  # 31 days
        total_kwh=1000,
        is_residential=True,
    )
    assert bill.billing_days == 31
    assert bill.segments[0].calculated.base_charge == Decimal("13.95")


def test_teco_bill_spans_storm_surcharge_expiration():
    """Aug 15 – Sep 15 2026 crosses the storm surcharge sunset (Aug 31 → Sep 1)."""
    bill = compose_expected_bill(
        "TECO",
        "RS",
        billing_period_start=date(2026, 8, 15),
        billing_period_end=date(2026, 9, 15),
        total_kwh=1000,
        is_residential=True,
    )
    assert len(bill.segments) == 2
    # Segment 1 has the storm surcharge; segment 2 does not
    assert bill.segments[0].calculated.storm_restoration_surcharge > Decimal("0")
    assert bill.segments[1].calculated.storm_restoration_surcharge == Decimal("0.00")


def test_invalid_date_range_rejected():
    import pytest

    with pytest.raises(ValueError):
        compose_expected_bill(
            "FPL",
            "RS-1",
            billing_period_start=date(2026, 2, 1),
            billing_period_end=date(2026, 1, 1),
            total_kwh=1000,
            is_residential=True,
        )


# ---------------------------------------------------------------------------
# Non-tariff line items integration
# ---------------------------------------------------------------------------


def test_composer_with_late_fee_adds_post_tax():
    """A $100 prior balance unpaid → FPL late fee $5 added AFTER taxes."""
    from tariff_audit.engine.line_items import (
        compute_late_payment_charge,
        prior_balance,
    )

    bill = compose_expected_bill(
        "FPL",
        "RS-1",
        billing_period_start=date(2026, 1, 1),
        billing_period_end=date(2026, 1, 30),
        total_kwh=1000,
        is_residential=True,
        non_tariff_items=[
            prior_balance(Decimal("100.00")),
            compute_late_payment_charge("FPL", Decimal("100.00")),
        ],
    )

    # Tariff + GRT unchanged
    assert bill.tariff_subtotal == Decimal("133.10")
    # taxes.total = $136.51; + prior balance $100 + late fee $5 = $241.51
    assert bill.total_due == Decimal("241.51")
    assert len(bill.post_tax_non_tariff_items) == 2


def test_composer_with_load_management_credit_reduces_tax_base():
    """FPL On-Call $7.50 credit, applied pre-tax, reduces GRT."""
    from tariff_audit.engine.line_items import load_management_credit

    lm = load_management_credit("FPL", Decimal("7.50"), "On-Call")
    # Force it pre-tax for this test
    lm = lm.__class__(
        name=lm.name,
        category=lm.category,
        amount=lm.amount,
        description=lm.description,
        fac_citation=lm.fac_citation,
        statute_citation=lm.statute_citation,
        pre_tax=True,
    )

    bill = compose_expected_bill(
        "FPL",
        "RS-1",
        billing_period_start=date(2026, 1, 1),
        billing_period_end=date(2026, 1, 30),
        total_kwh=1000,
        is_residential=True,
        non_tariff_items=[lm],
    )
    # pre_tax_subtotal = 133.10 - 7.50 = 125.60
    assert bill.pre_tax_subtotal == Decimal("125.60")
    # GRT on 125.60 = $3.22; total = 128.82
    assert bill.total_due == Decimal("128.82")


def test_composer_payment_received_reduces_total_due():
    from tariff_audit.engine.line_items import payment_received, prior_balance

    bill = compose_expected_bill(
        "FPL",
        "RS-1",
        billing_period_start=date(2026, 1, 1),
        billing_period_end=date(2026, 1, 30),
        total_kwh=1000,
        is_residential=True,
        non_tariff_items=[
            prior_balance(Decimal("50.00")),
            payment_received(Decimal("50.00")),
        ],
    )
    # Net effect of +50 and -50 = 0; bill equals pure tariff + tax
    assert bill.total_due == Decimal("136.51")


def test_composer_net_metering_reduces_billable_kwh():
    """A customer with solar exports 800 kWh against 1,000 kWh consumption
    bills the tariff on NET 200 kWh — not the full 1,000."""
    from tariff_audit.engine.line_items import apply_net_metering

    nm = apply_net_metering(
        metered_consumption_kwh=1000,
        metered_generation_kwh=800,
    )
    assert nm.billable_kwh == Decimal("200")

    # Compose using the net kWh
    bill = compose_expected_bill(
        "FPL",
        "RS-1",
        billing_period_start=date(2026, 1, 1),
        billing_period_end=date(2026, 1, 30),
        total_kwh=nm.billable_kwh,
        is_residential=True,
    )
    # 200 kWh bills << 1,000 kWh; subtotal should be well under $50 before
    # minimum-bill enforcement kicks in to raise to $30.
    assert bill.tariff_subtotal < Decimal("50")
    # The FPL minimum bill of $30 does NOT apply here because 200 kWh is
    # enough to exceed the $30 floor when clauses are added.
