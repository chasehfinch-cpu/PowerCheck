"""Bill reconstruction engine.

Given a :class:`TariffSchedule` and usage data, reconstructs the exact
tariff-regulated portion of a bill, component by component, using
``decimal.Decimal`` throughout.

Non-tariff items (gross receipts tax, municipal franchise fees, utility tax,
late fees, deposits, net-metering credits, etc.) are NOT calculated here — see
``engine.line_items`` (Phase 3).
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, ConfigDict

from tariff_audit.tariffs.models import EnergyTier, FuelTier, TariffSchedule

_CENT = Decimal("0.01")
_HUNDRED = Decimal("100")


def _round_cents(value: Decimal) -> Decimal:
    """Round to nearest cent using banker-safe half-up (matches utility billing)."""
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def _apply_tiers(
    kwh: Decimal,
    tiers: Iterable[EnergyTier | FuelTier],
) -> dict[str, Decimal]:
    """Split ``kwh`` across tiered ¢/kWh rates. Returns {label: dollars} per tier.

    Tiers are consumed in order: Tier 1 fills up to its ``max_kwh``, then Tier 2,
    etc. The top tier (``max_kwh is None``) absorbs all remaining kWh.

    Rounding: each tier's dollar amount is rounded to the cent independently.
    This matches how utility billing systems compute line items.
    """
    tier_list = list(tiers)
    if not tier_list:
        return {}

    result: dict[str, Decimal] = {}
    remaining = kwh
    consumed_so_far = Decimal("0")

    for idx, tier in enumerate(tier_list, start=1):
        if remaining <= 0:
            break

        if tier.max_kwh is None:
            tier_kwh = remaining
            label = f"Tier {idx} (>{int(consumed_so_far)})"
        else:
            tier_capacity = Decimal(tier.max_kwh) - consumed_so_far
            if tier_capacity <= 0:
                # This tier is already fully consumed by prior tiers (data error
                # or unusual spec); skip it.
                continue
            tier_kwh = min(remaining, tier_capacity)
            lower = int(consumed_so_far)
            upper = tier.max_kwh
            label = (
                f"Tier {idx} (≤{upper})" if lower == 0 else f"Tier {idx} ({lower + 1}–{upper})"
            )

        dollars = _round_cents(tier_kwh * tier.rate_cents_per_kwh / _HUNDRED)
        result[label] = dollars
        remaining -= tier_kwh
        consumed_so_far += tier_kwh

    return result


class CalculatedBill(BaseModel):
    """What the bill SHOULD be, calculated from tariff × usage.

    All monetary fields are ``Decimal`` rounded to the cent. The tariff-regulated
    subtotal in :attr:`subtotal_tariff` is the bottom line for comparison against
    a parsed bill's tariff-regulated charges.
    """

    model_config = ConfigDict(frozen=True)

    tariff_used: TariffSchedule
    kwh: Decimal
    demand_kw: Decimal | None = None
    power_factor: Decimal | None = None

    # Per-component results
    base_charge: Decimal
    energy_charge_by_tier: dict[str, Decimal]
    fuel_charge_by_tier: dict[str, Decimal]
    demand_charge: Decimal | None = None
    demand_charge_on_peak: Decimal | None = None
    conservation: Decimal
    capacity: Decimal
    environmental: Decimal
    storm_protection: Decimal
    storm_restoration_surcharge: Decimal
    transition_credit: Decimal
    additional_riders: dict[str, Decimal]
    power_factor_adjustment: Decimal | None = None

    subtotal_tariff: Decimal
    minimum_bill_applied: bool = False


def calculate_bill(
    tariff: TariffSchedule,
    kwh: Decimal | int | float,
    *,
    demand_kw: Decimal | int | float | None = None,
    power_factor: Decimal | float | None = None,
) -> CalculatedBill:
    """Reconstruct the tariff-regulated portion of a bill.

    Parameters
    ----------
    tariff : TariffSchedule
        Rate schedule to apply. Must cover the billing period.
    kwh : Decimal | int | float
        Total metered energy for the billing period.
    demand_kw : optional
        Metered demand for demand rate schedules (GSD-1, GSLD-1). Ignored for
        non-demand schedules (e.g. RS-1).
    power_factor : optional
        Metered power factor. If below ``tariff.power_factor_base``, a demand
        adjustment is applied per the tariff.

    Notes
    -----
    This function handles only PSC-regulated tariff components. It does NOT
    add gross receipts tax, franchise fees, utility taxes, late charges, or
    any non-tariff line items — those are isolated separately during audit
    comparison (see ``engine.line_items``).
    """
    kwh_d = _as_decimal(kwh)
    if kwh_d < 0:
        raise ValueError(f"kwh must be non-negative, got {kwh_d}")

    # Clause charges apply to every metered kWh as flat ¢/kWh rates.
    conservation = _round_cents(kwh_d * tariff.conservation / _HUNDRED)
    capacity = _round_cents(kwh_d * tariff.capacity / _HUNDRED)
    environmental = _round_cents(kwh_d * tariff.environmental / _HUNDRED)
    storm_protection = _round_cents(kwh_d * tariff.storm_protection / _HUNDRED)
    storm_restoration_surcharge = _round_cents(
        kwh_d * tariff.storm_restoration_surcharge / _HUNDRED
    )
    transition_credit = _round_cents(kwh_d * tariff.transition_credit / _HUNDRED)
    additional_riders = {
        name: _round_cents(kwh_d * rate / _HUNDRED)
        for name, rate in tariff.additional_riders.items()
    }

    energy_by_tier = _apply_tiers(kwh_d, tariff.energy_tiers)
    fuel_by_tier = _apply_tiers(kwh_d, tariff.fuel_tiers)

    # Demand (demand-rate schedules only)
    demand_charge: Decimal | None = None
    demand_charge_on_peak: Decimal | None = None
    power_factor_adjustment: Decimal | None = None
    if demand_kw is not None and tariff.demand_charge_base is not None:
        demand_d = _as_decimal(demand_kw)
        billed_demand = demand_d

        # Power factor adjustment: if PF below base, gross up billed demand.
        if (
            power_factor is not None
            and tariff.power_factor_base is not None
            and tariff.power_factor_base > 0
        ):
            pf_d = _as_decimal(power_factor)
            if pf_d > 0 and pf_d < tariff.power_factor_base:
                adjusted_demand = demand_d * tariff.power_factor_base / pf_d
                power_factor_adjustment = _round_cents(
                    (adjusted_demand - demand_d) * tariff.demand_charge_base
                )
                billed_demand = adjusted_demand

        demand_charge = _round_cents(billed_demand * tariff.demand_charge_base)
        if tariff.demand_charge_on_peak is not None:
            demand_charge_on_peak = _round_cents(
                billed_demand * tariff.demand_charge_on_peak
            )

    subtotal = (
        tariff.base_charge_monthly
        + sum(energy_by_tier.values(), Decimal("0"))
        + sum(fuel_by_tier.values(), Decimal("0"))
        + conservation
        + capacity
        + environmental
        + storm_protection
        + storm_restoration_surcharge
        + transition_credit
        + sum(additional_riders.values(), Decimal("0"))
    )
    if demand_charge is not None:
        subtotal += demand_charge
    if demand_charge_on_peak is not None:
        subtotal += demand_charge_on_peak

    subtotal = _round_cents(subtotal)

    minimum_bill_applied = False
    if subtotal < tariff.minimum_bill:
        subtotal = _round_cents(tariff.minimum_bill)
        minimum_bill_applied = True

    return CalculatedBill(
        tariff_used=tariff,
        kwh=kwh_d,
        demand_kw=_as_decimal(demand_kw) if demand_kw is not None else None,
        power_factor=_as_decimal(power_factor) if power_factor is not None else None,
        base_charge=_round_cents(tariff.base_charge_monthly),
        energy_charge_by_tier=energy_by_tier,
        fuel_charge_by_tier=fuel_by_tier,
        demand_charge=demand_charge,
        demand_charge_on_peak=demand_charge_on_peak,
        conservation=conservation,
        capacity=capacity,
        environmental=environmental,
        storm_protection=storm_protection,
        storm_restoration_surcharge=storm_restoration_surcharge,
        transition_credit=transition_credit,
        additional_riders=additional_riders,
        power_factor_adjustment=power_factor_adjustment,
        subtotal_tariff=subtotal,
        minimum_bill_applied=minimum_bill_applied,
    )


def _as_decimal(value: Decimal | int | float) -> Decimal:
    if isinstance(value, Decimal):
        return value
    # Route through str to avoid binary-float contamination.
    return Decimal(str(value))
