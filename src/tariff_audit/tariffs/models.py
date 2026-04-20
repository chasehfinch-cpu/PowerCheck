"""Pydantic models describing a PSC-approved tariff schedule.

Every rate stored here must trace to a specific PSC docket number and effective date.
All monetary values use ``decimal.Decimal`` — never ``float`` — so that downstream
bill reconstruction is penny-accurate.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class EnergyTier(BaseModel):
    """A single energy-charge tier in ¢/kWh.

    ``max_kwh`` is the upper bound of this tier in kWh. ``None`` means unlimited
    (i.e. this is the top tier and all remaining kWh bill at this rate).
    """

    model_config = ConfigDict(frozen=True)

    max_kwh: int | None = Field(default=None, ge=0)
    rate_cents_per_kwh: Decimal


class FuelTier(BaseModel):
    """A single fuel-clause pass-through tier in ¢/kWh."""

    model_config = ConfigDict(frozen=True)

    max_kwh: int | None = Field(default=None, ge=0)
    rate_cents_per_kwh: Decimal


class TariffSchedule(BaseModel):
    """A complete tariff rate schedule as approved by the Florida PSC.

    One instance represents one utility's rate schedule for one contiguous
    effective-date period. Look up by ``(utility, rate_schedule, date)`` via
    :func:`tariff_audit.tariffs.registry.get_tariff`.
    """

    model_config = ConfigDict(frozen=True)

    # Identity
    utility: str
    rate_schedule: str
    effective_date: date
    expiration_date: date | None = None
    psc_docket: str

    # Base charge. Most Florida IOUs bill this as a flat monthly amount.
    # TECO publishes a daily basic service charge (e.g. $0.45/day) that, for
    # a 30-day month, equals the monthly figure. When ``base_charge_daily``
    # is set, the calculator bills ``daily × billing_days`` if the caller
    # provides ``billing_days``; otherwise it falls back to 30 × daily.
    # ``base_charge_monthly`` is always the canonical 30-day equivalent so
    # that cross-utility comparisons are consistent.
    base_charge_monthly: Decimal
    base_charge_daily: Decimal | None = None
    minimum_bill: Decimal

    # Energy charges (¢/kWh)
    energy_tiers: list[EnergyTier]

    # Demand charges ($/kW) — demand schedules only
    demand_charge_base: Decimal | None = None
    demand_charge_on_peak: Decimal | None = None
    demand_charge_max: Decimal | None = None
    demand_ratchet_pct: Decimal | None = None

    # Clause charges (¢/kWh) — apply to all rate schedules
    fuel_tiers: list[FuelTier] = Field(default_factory=list)
    conservation: Decimal = Decimal("0")
    capacity: Decimal = Decimal("0")
    environmental: Decimal = Decimal("0")
    storm_protection: Decimal = Decimal("0")
    # Transient / interim PSC-approved cost-recovery surcharge for storm
    # restoration costs from specific events (distinct from the ongoing
    # Storm Protection Plan charge above). Zero when no surcharge is active.
    storm_restoration_surcharge: Decimal = Decimal("0")
    # Transition rider: positive value = charge (former Gulf Power territory),
    # negative value = credit (peninsular FPL territory). Signed so the
    # calculator can apply it uniformly.
    transition_credit: Decimal = Decimal("0")
    # Escape hatch for rare additional per-kWh riders not covered by the
    # named fields above (e.g. one-off PSC-approved surcharges). Values are
    # ¢/kWh; applied to every metered kWh like other flat clauses.
    additional_riders: dict[str, Decimal] = Field(default_factory=dict)

    # Power factor adjustment — demand schedules
    power_factor_base: Decimal | None = None
    power_factor_penalty_per_pct: Decimal | None = None

    # TOU parameters
    on_peak_hours: str | None = None
    off_peak_multiplier: Decimal | None = None

    # Provenance
    source_url: str | None = None
    notes: str | None = None

    def covers(self, d: date) -> bool:
        """Return True if this schedule is effective on ``d``."""
        if d < self.effective_date:
            return False
        return not (self.expiration_date is not None and d > self.expiration_date)
