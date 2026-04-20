"""Florida Public Utilities Company (FPUC) Residential Service (RS) rate schedule.

Source: ``fpuc.com/wp-content/uploads/FPU-Electric-Tariff_ADA-2.pdf``
(extracted text retained at ``.tariff_research/fpu_electric_tariff.txt``).

**Service territory**: Two non-contiguous divisions:

- **Northwest Florida Division**: Jackson, Calhoun, and Liberty Counties
  (Marianna area). Rate Adjustment Rider on Sheet No. 7.021.
- **Northeast Florida Division**: Amelia Island in Nassau County
  (Fernandina Beach). Rate Adjustment Rider on Sheet No. 7.022.

Both divisions use **identical** residential rate structure for 2026 —
they share the same Base Energy Charges and Purchased Power Cost Recovery
factors. The only difference (GSLD-1 large-demand generation charges for
commercial) does not affect residential customers.

**2026 rate structure differs from other FL IOUs**:

- FPU combines fuel, capacity, and environmental recovery into a single
  **"Total Purchased Power Cost Recovery Clause"** (levelized adjustment).
  Peer utilities separate these.
- **Storm Protection Plan charge is absent** (FPU is not subject to the
  same storm-hardening cost recovery as FPL/Duke/TECO).
- Base charge is labeled **"Customer Facilities Charge"** at $24.40/month
  — notably higher than peer utilities (FPL $10.52, TECO $13.50 equiv).
- **Franchise fee is described** in the tariff as a percentage added
  before taxes, variable by jurisdiction (see standards/jurisdictions).

PSC Docket references:

- **20240099-EI** — 2024 FPU rate case
- **00557-2026** — 2026 annual electric cost recovery rates
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from tariff_audit.tariffs.models import EnergyTier, FuelTier, TariffSchedule
from tariff_audit.tariffs.registry import register_tariff

# ---------------------------------------------------------------------------
# FPU Residential Service — Effective January 1 2026
# ---------------------------------------------------------------------------

FPU_RS_2026 = TariffSchedule(
    utility="FPU",
    rate_schedule="RS",
    effective_date=date(2026, 1, 1),
    expiration_date=date(2026, 12, 31),
    psc_docket="20240099-EI / 00557-2026",
    base_charge_monthly=Decimal("24.40"),
    minimum_bill=Decimal("24.40"),
    energy_tiers=[
        EnergyTier(max_kwh=1000, rate_cents_per_kwh=Decimal("2.867")),
        EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("4.695")),
    ],
    fuel_tiers=[
        # FPU's "Total Purchased Power Cost Recovery Clause" is the
        # functional equivalent of fuel + capacity + environmental combined.
        FuelTier(max_kwh=1000, rate_cents_per_kwh=Decimal("8.820")),
        FuelTier(max_kwh=None, rate_cents_per_kwh=Decimal("10.070")),
    ],
    conservation=Decimal("0.321"),
    # FPU does not separate capacity / environmental / storm protection —
    # those are rolled into Purchased Power above and the tariff does not
    # list a Storm Protection Plan clause for this small IOU.
    capacity=Decimal("0"),
    environmental=Decimal("0"),
    storm_protection=Decimal("0"),
    storm_restoration_surcharge=Decimal("0"),
    transition_credit=Decimal("0"),
    source_url="https://fpuc.com/wp-content/uploads/FPU-Electric-Tariff_ADA-2.pdf",
    notes=(
        "Effective 2026 for both NW Florida (Jackson/Calhoun/Liberty) and "
        "NE Florida (Amelia Island) divisions. Purchased Power Cost Recovery "
        "bundles fuel + capacity + environmental cost recovery into a "
        "single tiered ¢/kWh factor. Franchise fee is jurisdiction-dependent "
        "and handled by standards.jurisdictions. Tariff effective date per "
        "the Company of Jeffrey Sylvester, Chief Operating Officer."
    ),
)


register_tariff(FPU_RS_2026)
