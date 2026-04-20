"""FPL Residential Service (RS-1) rate schedules — verified against PSC filings.

Authoritative sources (text-extracted via pdfplumber and retained in
``.tariff_research/`` for audit trail):

- 2024 rates:
  ``fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2024.pdf``
- 2025 rates (Jan):
  ``fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2025.pdf``
- 2025 rates (Feb onwards — mid-year update):
  ``fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-feb-2025.pdf``
- 2026 rates (peninsular FPL):
  ``fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2026.pdf``
- 2026 rates (NW Florida, former Gulf Power territory):
  ``fpl.com/content/dam/fplgp/us/en/rates/pdf/jan-2026-res-eff-rates-rules-and-regulations.pdf``
- Full tariff Section 8 (cross-referenced):
  ``fpl.com/rates/pdf/electric-tariff-section8.pdf``

Reconciliation note — "typical bill" figures:
FPL publishes typical-bill marketing numbers ($134.14 for 2025, $136.64 for
2026 peninsular, $141.36 for 2026 NW Florida) that INCLUDE the Florida Gross
Receipts Tax (~2.5641%, grossed-up). The ``subtotal_tariff`` this engine
returns is the PRE-TAX tariff-regulated portion, per the architecture rule
that taxes are handled separately by ``engine.line_items``. Verify:
- 2025 Feb subtotal $130.68 × 1.02632 = $134.12 ≈ published $134.14 ✓
- 2026 peninsular subtotal $133.10 × 1.02632 = $136.60 ≈ published $136.64 ✓
- 2026 NW Florida subtotal $137.71 × 1.02632 = $141.33 ≈ published $141.36 ✓

Territory note: the 2026 rate agreement unified most RS-1 rates across
peninsular FPL and former-Gulf NW Florida, but the **Transition Rider**
differs:
- Peninsular FPL: Transition Credit = −0.040 ¢/kWh
- NW Florida (former Gulf): Transition Charge = +0.421 ¢/kWh
Use ``rate_schedule="RS-1"`` for peninsular and ``"RS-1-NWFL"`` for NW Florida.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from tariff_audit.tariffs.models import EnergyTier, FuelTier, TariffSchedule
from tariff_audit.tariffs.registry import register_tariff

# ---------------------------------------------------------------------------
# Effective January 2024
# ---------------------------------------------------------------------------

FPL_RS1_2024 = TariffSchedule(
    utility="FPL",
    rate_schedule="RS-1",
    effective_date=date(2024, 1, 1),
    expiration_date=date(2024, 12, 31),
    psc_docket="20230001-EI (fuel) / 20210015-EI (base) / others",
    base_charge_monthly=Decimal("9.48"),
    minimum_bill=Decimal("25.00"),
    energy_tiers=[
        EnergyTier(max_kwh=1000, rate_cents_per_kwh=Decimal("7.063")),
        EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("8.055")),
    ],
    fuel_tiers=[
        FuelTier(max_kwh=1000, rate_cents_per_kwh=Decimal("3.462")),
        FuelTier(max_kwh=None, rate_cents_per_kwh=Decimal("4.462")),
    ],
    conservation=Decimal("0.124"),
    capacity=Decimal("0.170"),
    environmental=Decimal("0.332"),
    storm_protection=Decimal("0.557"),
    storm_restoration_surcharge=Decimal("0.665"),
    transition_credit=Decimal("-0.119"),
    source_url="https://www.fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2024.pdf",
    notes=(
        "Effective Jan 2024. Storm restoration line item published as "
        "'Consolidated Interim Storm Restoration Recovery' at 0.665 ¢/kWh. "
        "Transition credit labeled '2022 Transition Credit' at −0.119 ¢/kWh."
    ),
)

# ---------------------------------------------------------------------------
# Effective January 2025 (superseded by Feb 2025 update)
# ---------------------------------------------------------------------------

FPL_RS1_2025_JAN = TariffSchedule(
    utility="FPL",
    rate_schedule="RS-1",
    effective_date=date(2025, 1, 1),
    expiration_date=date(2025, 1, 31),
    psc_docket="20210015-EI / 20240001-EI / 20240002-EI / others",
    base_charge_monthly=Decimal("9.55"),
    minimum_bill=Decimal("25.00"),
    energy_tiers=[
        EnergyTier(max_kwh=1000, rate_cents_per_kwh=Decimal("7.117")),
        EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("8.116")),
    ],
    fuel_tiers=[
        FuelTier(max_kwh=1000, rate_cents_per_kwh=Decimal("2.446")),
        FuelTier(max_kwh=None, rate_cents_per_kwh=Decimal("3.446")),
    ],
    conservation=Decimal("0.138"),
    capacity=Decimal("0.103"),
    environmental=Decimal("0.361"),
    storm_protection=Decimal("0.810"),
    storm_restoration_surcharge=Decimal("1.202"),
    transition_credit=Decimal("-0.079"),
    source_url="https://www.fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2025.pdf",
    notes=(
        "Effective Jan 1–Jan 31 2025. Storm restoration line published as "
        "'2025 Interim Storm Restoration Recovery Surcharge' at 1.202 ¢/kWh. "
        "Transition credit labeled '2025 Interim Transition Credit'. "
        "Superseded by the Feb 2025 schedule — energy and fuel rates were "
        "adjusted slightly."
    ),
)

# ---------------------------------------------------------------------------
# Effective February 2025 (through end of 2025)
# ---------------------------------------------------------------------------

FPL_RS1_2025_FEB = TariffSchedule(
    utility="FPL",
    rate_schedule="RS-1",
    effective_date=date(2025, 2, 1),
    expiration_date=date(2025, 12, 31),
    psc_docket="20210015-EI / 20220165-EI / 20240001-EI / 20240002-EI / 20240007-EI / 20240010-EI / 20240149",
    base_charge_monthly=Decimal("9.61"),
    minimum_bill=Decimal("25.00"),
    energy_tiers=[
        EnergyTier(max_kwh=1000, rate_cents_per_kwh=Decimal("7.164")),
        EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("8.170")),
    ],
    fuel_tiers=[
        FuelTier(max_kwh=1000, rate_cents_per_kwh=Decimal("2.408")),
        FuelTier(max_kwh=None, rate_cents_per_kwh=Decimal("3.408")),
    ],
    conservation=Decimal("0.138"),
    capacity=Decimal("0.103"),
    environmental=Decimal("0.361"),
    storm_protection=Decimal("0.810"),
    storm_restoration_surcharge=Decimal("1.202"),
    transition_credit=Decimal("-0.079"),
    source_url="https://www.fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-feb-2025.pdf",
    notes=(
        "Effective Feb 1 – Dec 31 2025. Typical-bill reference: $134.14 for "
        "1,000 kWh (includes GRT). Tariff-regulated subtotal computes to "
        "$130.68; × 1.02632 (GRT gross-up) ≈ $134.12."
    ),
)

# ---------------------------------------------------------------------------
# Effective January 2026 — Peninsular FPL service territory
# ---------------------------------------------------------------------------

FPL_RS1_2026_PENINSULAR = TariffSchedule(
    utility="FPL",
    rate_schedule="RS-1",
    effective_date=date(2026, 1, 1),
    expiration_date=None,
    psc_docket="20250011-EI / 20210015-EI / 20250001-EI / 20250002-EG / 20250007-EI / 20250010-EI",
    base_charge_monthly=Decimal("10.52"),
    minimum_bill=Decimal("30.00"),
    energy_tiers=[
        EnergyTier(max_kwh=1000, rate_cents_per_kwh=Decimal("7.865")),
        EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("8.865")),
    ],
    fuel_tiers=[
        FuelTier(max_kwh=1000, rate_cents_per_kwh=Decimal("2.893")),
        FuelTier(max_kwh=None, rate_cents_per_kwh=Decimal("3.893")),
    ],
    conservation=Decimal("0.148"),
    capacity=Decimal("0.052"),
    environmental=Decimal("0.345"),
    storm_protection=Decimal("0.995"),
    # The 2025 Interim Storm Restoration Recovery Surcharge expired end of 2025.
    storm_restoration_surcharge=Decimal("0"),
    transition_credit=Decimal("-0.040"),
    source_url="https://www.fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2026.pdf",
    notes=(
        "Peninsular FPL territory (everywhere EXCEPT the NW Florida panhandle). "
        "Minimum bill raised to $30 per new rate agreement. Typical-bill "
        "reference: $136.64 for 1,000 kWh (includes GRT). Subtotal $133.10; "
        "× 1.02632 ≈ $136.60. Transition Rider is a CREDIT (−0.040 ¢/kWh) "
        "for peninsular customers."
    ),
)

# ---------------------------------------------------------------------------
# Effective January 2026 — NW Florida (former Gulf Power territory)
# ---------------------------------------------------------------------------

FPL_RS1_2026_NWFL = TariffSchedule(
    utility="FPL",
    rate_schedule="RS-1-NWFL",
    effective_date=date(2026, 1, 1),
    expiration_date=None,
    psc_docket="20250011-EI / 20210015-EI / 20250001-EI / 20250002-EG / 20250007-EI / 20250010-EI",
    base_charge_monthly=Decimal("10.52"),
    minimum_bill=Decimal("30.00"),
    energy_tiers=[
        EnergyTier(max_kwh=1000, rate_cents_per_kwh=Decimal("7.865")),
        EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("8.865")),
    ],
    fuel_tiers=[
        FuelTier(max_kwh=1000, rate_cents_per_kwh=Decimal("2.893")),
        FuelTier(max_kwh=None, rate_cents_per_kwh=Decimal("3.893")),
    ],
    conservation=Decimal("0.148"),
    capacity=Decimal("0.052"),
    environmental=Decimal("0.345"),
    storm_protection=Decimal("0.995"),
    storm_restoration_surcharge=Decimal("0"),
    # NW Florida has a Transition Rider CHARGE (positive) — recovers legacy
    # Gulf Power cost differentials. Source: Section 8 tariff, "Transition
    # Rider Charge applicable to all accounts within the service area
    # previously served by Gulf Power."
    transition_credit=Decimal("0.421"),
    source_url="https://www.fpl.com/content/dam/fplgp/us/en/rates/pdf/jan-2026-res-eff-rates-rules-and-regulations.pdf",
    notes=(
        "Former Gulf Power territory (NW Florida panhandle). Identical to "
        "peninsular RS-1 EXCEPT transition rider is a CHARGE of +0.421 "
        "¢/kWh rather than a credit. Typical-bill reference: $141.36 for "
        "1,000 kWh (includes GRT). Subtotal $137.71; × 1.02632 ≈ $141.33."
    ),
)


register_tariff(FPL_RS1_2024)
register_tariff(FPL_RS1_2025_JAN)
register_tariff(FPL_RS1_2025_FEB)
register_tariff(FPL_RS1_2026_PENINSULAR)
register_tariff(FPL_RS1_2026_NWFL)
