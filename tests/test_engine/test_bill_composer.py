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
