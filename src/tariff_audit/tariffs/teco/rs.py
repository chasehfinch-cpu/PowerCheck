"""Tampa Electric Company Standard Residential Service (RS) rate schedules.

Source for 2026:
- ``tampaelectric.com/4ad05f/siteassets/files/rates/resratesinsert_jan2026.pdf``
- Raw text retained at ``.tariff_research/teco_2026.txt``.

Structural notes (TECO differs from FPL):

1. **Base charge is published daily.** TECO lists the Basic Service Charge as
   $0.45/day (canonical monthly 30-day equivalent: $13.50). Use the
   ``base_charge_daily`` field; the calculator multiplies by ``billing_days``
   when provided.

2. **Energy charge is a bundled rate.** TECO's non-fuel energy charge
   includes 0.621 ¢/kWh for conservation, environmental, and capacity cost
   recovery. When auditing a TECO bill line-by-line, note that the bill
   may present these recoveries as separate line items totaling 0.621 ¢/kWh
   while the tariff here bundles them into ``energy_tiers``. The subtotal
   is still correct; line-item reconciliation will need a parser adapter
   in Phase 2.

3. **Storm Surcharge is temporary.** The 1.995 ¢/kWh storm surcharge
   spreads 2024 hurricane recovery (Debby, Helene, Milton) over 18 months
   from March 2025 through August 2026. After August 2026 this drops to 0.

4. **Clean Energy Transition Mechanism (CETM)** is a TECO-specific
   per-kWh rider (0.406 ¢/kWh for RS in 2026). Modeled via the
   ``additional_riders`` dict.

Historical 2024/2025 schedules are intentionally NOT registered — we do not
have verified per-component rates for those years. Audits of pre-2026 TECO
bills will raise ``LookupError`` until those tariffs are entered from the
corresponding PSC filings.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from tariff_audit.tariffs.models import EnergyTier, FuelTier, TariffSchedule
from tariff_audit.tariffs.registry import register_tariff

# ---------------------------------------------------------------------------
# TECO RS — Jan 2026 through Aug 2026 (storm surcharge active)
# ---------------------------------------------------------------------------

TECO_RS_2026_STORM_ACTIVE = TariffSchedule(
    utility="TECO",
    rate_schedule="RS",
    effective_date=date(2026, 1, 1),
    expiration_date=date(2026, 8, 31),
    psc_docket="20240026-EI / 20250001-EI (fuel) / 20240149-EI (storm)",
    base_charge_monthly=Decimal("13.50"),
    base_charge_daily=Decimal("0.45"),
    minimum_bill=Decimal("0"),
    energy_tiers=[
        EnergyTier(max_kwh=1000, rate_cents_per_kwh=Decimal("9.569")),
        EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("10.569")),
    ],
    fuel_tiers=[
        FuelTier(max_kwh=1000, rate_cents_per_kwh=Decimal("3.210")),
        FuelTier(max_kwh=None, rate_cents_per_kwh=Decimal("4.210")),
    ],
    # Conservation, environmental, and capacity are bundled INTO the energy
    # charge (0.621 ¢/kWh of the 9.569 figure), so we leave these individual
    # fields at zero to avoid double-counting.
    conservation=Decimal("0"),
    capacity=Decimal("0"),
    environmental=Decimal("0"),
    storm_protection=Decimal("0.717"),
    storm_restoration_surcharge=Decimal("1.995"),
    transition_credit=Decimal("0"),
    additional_riders={
        "Clean Energy Transition Mechanism": Decimal("0.406"),
    },
    source_url="https://www.tampaelectric.com/4ad05f/siteassets/files/rates/resratesinsert_jan2026.pdf",
    notes=(
        "Effective Jan 1 – Aug 31 2026 (storm surcharge expires after Aug 2026). "
        "Energy tier rates include 0.621 ¢/kWh bundled conservation + "
        "environmental + capacity recovery — these clause fields are 0 here "
        "to avoid double-counting. Storm Surcharge (1.995 ¢/kWh) is temporary "
        "recovery for 2024 hurricane restoration (Debby, Helene, Milton)."
    ),
)

# ---------------------------------------------------------------------------
# TECO RS — Sep–Dec 2026 (storm surcharge expired)
# ---------------------------------------------------------------------------

TECO_RS_2026_POST_STORM = TECO_RS_2026_STORM_ACTIVE.model_copy(
    update={
        "effective_date": date(2026, 9, 1),
        "expiration_date": date(2026, 12, 31),
        "storm_restoration_surcharge": Decimal("0"),
        "notes": (
            "Effective Sep 1 – Dec 31 2026. Identical to Jan–Aug 2026 schedule "
            "except the 2024-hurricane Storm Surcharge (1.995 ¢/kWh) drops "
            "off the bill after Aug 31 2026 per PSC-approved 18-month "
            "recovery window."
        ),
    }
)


register_tariff(TECO_RS_2026_STORM_ACTIVE)
register_tariff(TECO_RS_2026_POST_STORM)
