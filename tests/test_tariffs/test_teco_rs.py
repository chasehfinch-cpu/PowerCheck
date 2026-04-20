"""Deterministic tests for TECO RS-1 bill reconstruction (2026 rates)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from tariff_audit.engine.calculator import calculate_bill
from tariff_audit.tariffs.registry import get_tariff


def test_teco_rs_2026_jan_storm_active_1000kwh():
    """Storm-active schedule (Jan–Aug 2026) includes the 1.995¢ storm surcharge."""
    tariff = get_tariff("TECO", "RS", date(2026, 3, 15))
    bill = calculate_bill(tariff, kwh=1000)

    # Base = 30 days × $0.45 fallback when billing_days not supplied
    assert bill.base_charge == Decimal("13.50")
    # Energy tier 1: 1,000 × 9.569¢ = $95.69
    assert bill.energy_charge_by_tier == {"Tier 1 (≤1000)": Decimal("95.69")}
    # Fuel tier 1: 1,000 × 3.210¢ = $32.10
    assert bill.fuel_charge_by_tier == {"Tier 1 (≤1000)": Decimal("32.10")}
    # Storm Protection: 1,000 × 0.717¢ = $7.17
    assert bill.storm_protection == Decimal("7.17")
    # Storm Surcharge (2024 hurricanes): 1,000 × 1.995¢ = $19.95
    assert bill.storm_restoration_surcharge == Decimal("19.95")
    # CETM rider: 1,000 × 0.406¢ = $4.06
    assert bill.additional_riders == {"Clean Energy Transition Mechanism": Decimal("4.06")}
    # TECO's energy charge is BUNDLED — separate clauses are zero
    assert bill.conservation == Decimal("0")
    assert bill.capacity == Decimal("0")
    assert bill.environmental == Decimal("0")
    # Total
    assert bill.subtotal_tariff == Decimal("172.47")


def test_teco_rs_2026_billing_days_affects_base():
    """A 31-day billing period must bill 31 × daily-rate, not the 30-day monthly."""
    tariff = get_tariff("TECO", "RS", date(2026, 3, 15))
    bill31 = calculate_bill(tariff, kwh=1000, billing_days=31)
    assert bill31.base_charge == Decimal("13.95")  # 31 × $0.45
    assert bill31.subtotal_tariff == Decimal("172.92")

    bill28 = calculate_bill(tariff, kwh=1000, billing_days=28)
    assert bill28.base_charge == Decimal("12.60")  # 28 × $0.45


def test_teco_rs_2026_sep_post_storm_drops_surcharge():
    """After Aug 31 2026, storm surcharge is zero."""
    tariff = get_tariff("TECO", "RS", date(2026, 10, 15))
    bill = calculate_bill(tariff, kwh=1000)
    assert bill.storm_restoration_surcharge == Decimal("0.00")
    # $172.47 - $19.95 = $152.52
    assert bill.subtotal_tariff == Decimal("152.52")


def test_teco_rs_2026_tier_break_at_1000():
    """Usage above 1,000 kWh bills at the Tier 2 energy AND fuel rates."""
    tariff = get_tariff("TECO", "RS", date(2026, 3, 15))
    bill = calculate_bill(tariff, kwh=1200)

    tier2_energy = [v for k, v in bill.energy_charge_by_tier.items() if "Tier 2" in k]
    assert tier2_energy == [Decimal("21.14")]  # 200 × 10.569¢
    tier2_fuel = [v for k, v in bill.fuel_charge_by_tier.items() if "Tier 2" in k]
    assert tier2_fuel == [Decimal("8.42")]  # 200 × 4.210¢
    assert bill.subtotal_tariff == Decimal("208.26")


def test_teco_storm_and_post_storm_schedules_do_not_overlap():
    """Aug 31 -> storm schedule; Sep 1 -> post-storm schedule."""
    aug = get_tariff("TECO", "RS", date(2026, 8, 31))
    sep = get_tariff("TECO", "RS", date(2026, 9, 1))
    assert aug.storm_restoration_surcharge == Decimal("1.995")
    assert sep.storm_restoration_surcharge == Decimal("0")
