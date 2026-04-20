"""Deterministic unit tests for FPL RS-1 bill reconstruction.

Every assertion in this file must pass to the penny. A failure here means
either (a) the calculator has a bug, or (b) the encoded tariff rates have
drifted from the PSC-approved values. Both are release-blockers.

All expected values are grounded in the authoritative rate PDFs listed in
``src/tariff_audit/tariffs/fpl/rs1.py``.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from tariff_audit.engine.calculator import calculate_bill
from tariff_audit.tariffs.registry import get_tariff

# Florida Gross Receipts Tax is 2.5641% of gross receipts; billed as a
# grossed-up rate of ~2.6316% on top of the tariff subtotal. FPL's published
# "typical bill" figures include this tax; our ``subtotal_tariff`` excludes it.
GRT_GROSSUP_MULTIPLIER = Decimal("1.02632")


# ---------------------------------------------------------------------------
# 2026 peninsular FPL
# ---------------------------------------------------------------------------


def test_fpl_rs1_2026_peninsular_1000kwh_component_breakdown():
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=1000)

    assert bill.base_charge == Decimal("10.52")
    assert bill.energy_charge_by_tier == {"Tier 1 (≤1000)": Decimal("78.65")}
    assert bill.fuel_charge_by_tier == {"Tier 1 (≤1000)": Decimal("28.93")}
    assert bill.conservation == Decimal("1.48")
    assert bill.capacity == Decimal("0.52")
    assert bill.environmental == Decimal("3.45")
    assert bill.storm_protection == Decimal("9.95")
    assert bill.storm_restoration_surcharge == Decimal("0.00")  # expired end of 2025
    assert bill.transition_credit == Decimal("-0.40")
    assert bill.subtotal_tariff == Decimal("133.10")
    assert bill.minimum_bill_applied is False


def test_fpl_rs1_2026_peninsular_1200kwh_tier_break():
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=1200)

    assert bill.energy_charge_by_tier["Tier 1 (≤1000)"] == Decimal("78.65")
    tier2_energy = [v for k, v in bill.energy_charge_by_tier.items() if "Tier 2" in k]
    assert tier2_energy == [Decimal("17.73")]
    tier2_fuel = [v for k, v in bill.fuel_charge_by_tier.items() if "Tier 2" in k]
    assert tier2_fuel == [Decimal("7.79")]
    assert bill.subtotal_tariff == Decimal("161.62")


def test_fpl_rs1_2026_peninsular_reconciles_to_published_typical_bill():
    """Subtotal + Florida Gross Receipts Tax ≈ FPL's $136.64 typical-bill figure.

    The $136.64 published figure is ``subtotal_tariff × (1 + GRT_grossup)``
    rounded. We assert the grossed-up value is within 10¢ of $136.64 — rounding
    differences (per-line vs total) account for single-cent drift.
    """
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=1000)
    grossed_up = (bill.subtotal_tariff * GRT_GROSSUP_MULTIPLIER).quantize(Decimal("0.01"))
    assert abs(grossed_up - Decimal("136.64")) < Decimal("0.10"), (
        f"Grossed-up subtotal {grossed_up} diverges from FPL published $136.64 "
        f"— either the tariff data drifted or the GRT multiplier is stale."
    )


def test_fpl_rs1_2026_minimum_bill_applies_below_threshold():
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=50)
    assert bill.minimum_bill_applied is True
    assert bill.subtotal_tariff == Decimal("30.00")


def test_fpl_rs1_2026_zero_kwh_still_charges_minimum():
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=0)
    assert bill.base_charge == Decimal("10.52")
    assert bill.subtotal_tariff == Decimal("30.00")
    assert bill.minimum_bill_applied is True


# ---------------------------------------------------------------------------
# 2026 NW Florida (former Gulf Power)
# ---------------------------------------------------------------------------


def test_fpl_rs1_nwfl_2026_uses_transition_rider_charge_not_credit():
    """Former Gulf Power customers pay a Transition Rider CHARGE (+0.421 ¢/kWh)."""
    tariff = get_tariff("FPL", "RS-1-NWFL", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=1000)

    # Transition rider is a positive charge, not a credit
    assert bill.transition_credit == Decimal("4.21")
    assert bill.subtotal_tariff == Decimal("137.71")


def test_fpl_rs1_nwfl_2026_reconciles_to_published_typical_bill():
    """NW Florida subtotal × GRT ≈ FPL's $141.36 published figure."""
    tariff = get_tariff("FPL", "RS-1-NWFL", date(2026, 1, 15))
    bill = calculate_bill(tariff, kwh=1000)
    grossed_up = (bill.subtotal_tariff * GRT_GROSSUP_MULTIPLIER).quantize(Decimal("0.01"))
    assert abs(grossed_up - Decimal("141.36")) < Decimal("0.10")


# ---------------------------------------------------------------------------
# 2025 (two sub-periods: Jan 2025, then Feb–Dec 2025)
# ---------------------------------------------------------------------------


def test_fpl_rs1_jan_2025_uses_initial_schedule():
    """A bill dated Jan 15, 2025 must resolve to the Jan schedule (base $9.55)."""
    tariff = get_tariff("FPL", "RS-1", date(2025, 1, 15))
    assert tariff.effective_date == date(2025, 1, 1)
    assert tariff.expiration_date == date(2025, 1, 31)
    assert tariff.base_charge_monthly == Decimal("9.55")

    bill = calculate_bill(tariff, kwh=1000)
    assert bill.subtotal_tariff == Decimal("130.53")


def test_fpl_rs1_feb_2025_uses_revised_schedule():
    """Feb 2025 onward uses the mid-year update (base $9.61, slightly different energy/fuel)."""
    tariff = get_tariff("FPL", "RS-1", date(2025, 6, 15))
    assert tariff.effective_date == date(2025, 2, 1)
    assert tariff.base_charge_monthly == Decimal("9.61")

    bill = calculate_bill(tariff, kwh=1000)
    assert bill.subtotal_tariff == Decimal("130.68")


def test_fpl_rs1_2025_feb_reconciles_to_published_typical_bill():
    """Feb 2025 subtotal × GRT ≈ $134.14 (published 2025 typical bill)."""
    tariff = get_tariff("FPL", "RS-1", date(2025, 6, 15))
    bill = calculate_bill(tariff, kwh=1000)
    grossed_up = (bill.subtotal_tariff * GRT_GROSSUP_MULTIPLIER).quantize(Decimal("0.01"))
    assert abs(grossed_up - Decimal("134.14")) < Decimal("0.10")


def test_fpl_rs1_2025_storm_restoration_surcharge_applied():
    """The 2025 Interim Storm Restoration Recovery Surcharge (1.202 ¢/kWh) must bill."""
    tariff = get_tariff("FPL", "RS-1", date(2025, 6, 15))
    bill = calculate_bill(tariff, kwh=1000)
    # 1,000 kWh × 1.202 ¢/kWh = $12.02
    assert bill.storm_restoration_surcharge == Decimal("12.02")


# ---------------------------------------------------------------------------
# 2024
# ---------------------------------------------------------------------------


def test_fpl_rs1_2024_1000kwh_calculates_correctly():
    tariff = get_tariff("FPL", "RS-1", date(2024, 6, 15))
    assert tariff.base_charge_monthly == Decimal("9.48")

    bill = calculate_bill(tariff, kwh=1000)
    assert bill.subtotal_tariff == Decimal("132.02")
    # Consolidated Interim Storm Restoration Recovery at 0.665 ¢/kWh
    assert bill.storm_restoration_surcharge == Decimal("6.65")
    # 2022 Transition Credit
    assert bill.transition_credit == Decimal("-1.19")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_fpl_rs1_date_outside_any_schedule_raises():
    with pytest.raises(LookupError):
        get_tariff("FPL", "RS-1", date(2020, 1, 1))


def test_negative_kwh_rejected():
    tariff = get_tariff("FPL", "RS-1", date(2026, 1, 15))
    with pytest.raises(ValueError):
        calculate_bill(tariff, kwh=-100)


def test_fpl_rs1_schedules_do_not_overlap():
    """Dates that span schedule boundaries must resolve unambiguously."""
    # Last day of Jan 2025 → Jan schedule
    assert get_tariff("FPL", "RS-1", date(2025, 1, 31)).base_charge_monthly == Decimal("9.55")
    # First day of Feb 2025 → Feb schedule
    assert get_tariff("FPL", "RS-1", date(2025, 2, 1)).base_charge_monthly == Decimal("9.61")
    # Last day of 2025 → Feb schedule (expires 2025-12-31)
    assert get_tariff("FPL", "RS-1", date(2025, 12, 31)).base_charge_monthly == Decimal("9.61")
    # First day of 2026 → peninsular 2026 schedule
    assert get_tariff("FPL", "RS-1", date(2026, 1, 1)).base_charge_monthly == Decimal("10.52")
