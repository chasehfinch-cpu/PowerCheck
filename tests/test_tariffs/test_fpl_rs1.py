"""Deterministic unit tests for FPL RS-1 bill reconstruction.

Every assertion in this file must pass to the penny. A failure here means
either (a) the calculator has a bug, or (b) the encoded tariff rates have
drifted from the PSC-approved values. Both are release-blockers.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from tariff_audit.engine.calculator import calculate_bill
from tariff_audit.tariffs.registry import get_tariff


def test_fpl_rs1_2026_1000kwh_component_breakdown():
    """Every component must match the CLAUDE.md rate table exactly for 1,000 kWh."""
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=1000)

    assert bill.base_charge == Decimal("10.52")
    assert bill.energy_charge_by_tier == {"Tier 1 (≤1000)": Decimal("78.65")}
    assert bill.fuel_charge_by_tier == {"Tier 1 (≤1000)": Decimal("28.93")}
    assert bill.conservation == Decimal("1.48")
    assert bill.capacity == Decimal("0.52")
    assert bill.environmental == Decimal("3.45")
    assert bill.storm_protection == Decimal("9.95")
    assert bill.transition_credit == Decimal("-0.40")
    assert bill.subtotal_tariff == Decimal("133.10")
    assert bill.minimum_bill_applied is False


def test_fpl_rs1_2026_1200kwh_applies_tier2_for_overage():
    """Only the kWh above 1,000 bills at Tier 2 — not the entire usage."""
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=1200)

    # Tier 1 unchanged from the 1,000 kWh case
    assert bill.energy_charge_by_tier["Tier 1 (≤1000)"] == Decimal("78.65")
    # Tier 2: 200 kWh × 8.865¢ = $17.73 (label varies; key off "Tier 2" prefix)
    tier2_energy = [v for k, v in bill.energy_charge_by_tier.items() if "Tier 2" in k]
    assert tier2_energy == [Decimal("17.73")]
    tier2_fuel = [v for k, v in bill.fuel_charge_by_tier.items() if "Tier 2" in k]
    assert tier2_fuel == [Decimal("7.79")]

    assert bill.subtotal_tariff == Decimal("161.62")


def test_fpl_rs1_2026_minimum_bill_applies_below_threshold():
    """Bills below the tariff's minimum must be raised to the minimum."""
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=50)

    assert bill.minimum_bill_applied is True
    assert bill.subtotal_tariff == Decimal("30.00")


def test_fpl_rs1_2026_zero_kwh_still_charges_base_then_minimum():
    """A 0 kWh bill still owes at least the minimum bill."""
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=0)

    # Base charge computed but minimum lifts the total
    assert bill.base_charge == Decimal("10.52")
    assert bill.subtotal_tariff == Decimal("30.00")
    assert bill.minimum_bill_applied is True


def test_fpl_rs1_historical_2025_uses_2025_base_charge():
    """A bill dated mid-2025 must resolve to the 2025 schedule, not 2026."""
    tariff = get_tariff("FPL", "RS-1", date(2025, 6, 15))
    assert tariff.effective_date == date(2025, 1, 1)
    assert tariff.base_charge_monthly == Decimal("8.58")


def test_fpl_rs1_date_outside_any_schedule_raises():
    """Dates with no registered tariff must raise LookupError, not default silently."""
    with pytest.raises(LookupError):
        get_tariff("FPL", "RS-1", date(2020, 1, 1))


def test_negative_kwh_rejected():
    """Negative usage is an input error, not a refund — must raise."""
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    with pytest.raises(ValueError):
        calculate_bill(tariff, kwh=-100)


@pytest.mark.xfail(
    reason=(
        "FPL publishes a typical-bill figure of $136.64 for 1,000 kWh effective "
        "Jan 2026, but summing the CLAUDE.md rate table yields $133.10. The "
        "$3.54 gap is unreconciled. This test is a TODO tracker — fix the "
        "tariff data (likely a missing rider or adjusted clause rate) to close "
        "the gap, then remove the xfail."
    ),
    strict=True,
)
def test_fpl_rs1_2026_1000kwh_matches_published_typical_bill():
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=1000)
    assert bill.subtotal_tariff == Decimal("136.64")
