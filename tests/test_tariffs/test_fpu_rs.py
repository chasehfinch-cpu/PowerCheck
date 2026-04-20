"""Tests for Florida Public Utilities Company RS tariff."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from tariff_audit.engine.calculator import calculate_bill
from tariff_audit.tariffs.registry import get_tariff


def test_fpu_rs_2026_base_charge():
    t = get_tariff("FPU", "RS", date(2026, 6, 15))
    assert t.base_charge_monthly == Decimal("24.40")
    assert t.minimum_bill == Decimal("24.40")


def test_fpu_rs_2026_1000_kwh_component_breakdown():
    t = get_tariff("FPU", "RS", date(2026, 6, 15))
    bill = calculate_bill(t, kwh=1000)
    assert bill.base_charge == Decimal("24.40")
    # Tier 1 energy: 1000 × 2.867¢ = $28.67
    assert bill.energy_charge_by_tier == {"Tier 1 (≤1000)": Decimal("28.67")}
    # Tier 1 purchased-power (bundled fuel/capacity/env): 1000 × 8.820¢ = $88.20
    assert bill.fuel_charge_by_tier == {"Tier 1 (≤1000)": Decimal("88.20")}
    # Conservation: 1000 × 0.321¢ = $3.21
    assert bill.conservation == Decimal("3.21")
    # No separate storm protection, capacity, environmental
    assert bill.storm_protection == Decimal("0.00")
    assert bill.capacity == Decimal("0.00")
    assert bill.environmental == Decimal("0.00")
    assert bill.subtotal_tariff == Decimal("144.48")


def test_fpu_rs_2026_1200_kwh_tier_break():
    t = get_tariff("FPU", "RS", date(2026, 6, 15))
    bill = calculate_bill(t, kwh=1200)
    # Tier 2 energy: 200 × 4.695¢ = $9.39
    t2_e = [v for k, v in bill.energy_charge_by_tier.items() if "Tier 2" in k]
    assert t2_e == [Decimal("9.39")]
    # Tier 2 purchased power: 200 × 10.070¢ = $20.14
    t2_f = [v for k, v in bill.fuel_charge_by_tier.items() if "Tier 2" in k]
    assert t2_f == [Decimal("20.14")]
    assert bill.subtotal_tariff == Decimal("174.65")


def test_fpu_rs_minimum_bill_applies_on_low_usage():
    t = get_tariff("FPU", "RS", date(2026, 6, 15))
    # 5 kWh × (2.867 + 8.820 + 0.321) / 100 = $0.60, plus $24.40 base = $25.00
    # $25.00 > $24.40 minimum, so no floor applied.
    bill = calculate_bill(t, kwh=5)
    assert bill.subtotal_tariff == Decimal("25.00")
    assert bill.minimum_bill_applied is False


def test_fpu_rs_zero_kwh_still_charges_customer_facilities():
    t = get_tariff("FPU", "RS", date(2026, 6, 15))
    bill = calculate_bill(t, kwh=0)
    # $24.40 customer facilities charge = minimum bill
    assert bill.subtotal_tariff == Decimal("24.40")
