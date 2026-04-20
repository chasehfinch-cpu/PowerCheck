"""Tests for the tariff model and registry behavior."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from tariff_audit.tariffs.models import EnergyTier, FuelTier, TariffSchedule
from tariff_audit.tariffs.registry import get_tariff, register_tariff, registered_utilities


def test_tariff_schedule_covers_within_window():
    t = TariffSchedule(
        utility="TEST",
        rate_schedule="X-1",
        effective_date=date(2025, 1, 1),
        expiration_date=date(2025, 12, 31),
        psc_docket="TEST",
        base_charge_monthly=Decimal("1.00"),
        minimum_bill=Decimal("1.00"),
        energy_tiers=[EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("1.0"))],
        fuel_tiers=[FuelTier(max_kwh=None, rate_cents_per_kwh=Decimal("1.0"))],
    )
    assert t.covers(date(2025, 6, 1))
    assert t.covers(date(2025, 1, 1))
    assert t.covers(date(2025, 12, 31))
    assert not t.covers(date(2024, 12, 31))
    assert not t.covers(date(2026, 1, 1))


def test_tariff_schedule_open_ended_covers_future():
    t = TariffSchedule(
        utility="TEST",
        rate_schedule="X-1",
        effective_date=date(2026, 1, 1),
        expiration_date=None,
        psc_docket="TEST",
        base_charge_monthly=Decimal("1.00"),
        minimum_bill=Decimal("1.00"),
        energy_tiers=[EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("1.0"))],
    )
    assert t.covers(date(2026, 1, 1))
    assert t.covers(date(2099, 12, 31))
    assert not t.covers(date(2025, 12, 31))


def test_registry_unknown_utility_raises():
    with pytest.raises(LookupError, match="No tariff registered"):
        get_tariff("NONEXISTENT", "RS-1", date(2026, 1, 1))


def test_registry_unknown_rate_class_raises():
    with pytest.raises(LookupError, match="No tariff registered"):
        get_tariff("FPL", "NOPE", date(2026, 1, 1))


def test_fpl_registered_after_import():
    assert "FPL" in registered_utilities()


def test_register_duplicate_schedule_then_overlap_detected():
    """Registering an overlapping schedule yields a clear LookupError at query time."""
    dup = TariffSchedule(
        utility="DUPE_TEST",
        rate_schedule="R",
        effective_date=date(2026, 1, 1),
        expiration_date=None,
        psc_docket="A",
        base_charge_monthly=Decimal("1.00"),
        minimum_bill=Decimal("1.00"),
        energy_tiers=[EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("1.0"))],
    )
    dup2 = dup.model_copy(update={"psc_docket": "B"})
    register_tariff(dup)
    register_tariff(dup2)
    with pytest.raises(LookupError, match="Overlapping"):
        get_tariff("DUPE_TEST", "R", date(2026, 6, 1))
