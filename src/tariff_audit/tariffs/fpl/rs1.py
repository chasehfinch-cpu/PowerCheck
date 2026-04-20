"""FPL Residential Service (RS-1) rate schedules.

Sources:
- 2026: PSC Dockets 20250011-EI, 20210015-EI, 20250001-EI, 20250002-EG,
  20250007-EI, 20250010-EI. Typical-bill reference:
  ``fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2026.pdf``.
- Full tariff (Section 8): ``fpl.com/rates/pdf/electric-tariff-section8.pdf``.

IMPORTANT — Data-integrity notes:
- The 2026 rates below are encoded exactly as specified in CLAUDE.md. Summing
  those rates for a 1,000 kWh bill yields $133.10, while FPL's published
  "typical bill" figure is $136.64. The $3.54 gap is unresolved and MUST be
  reconciled against the official Section 8 tariff PDF before Phase 1 closes.
  See ``tests/test_tariffs/test_fpl_rs1.py`` for the tracking test.
- The 2024 and 2025 schedules below are stubs: only the base charge is asserted
  by the existing test plan. Full clause-by-clause rates must be re-entered
  from the effective-dated tariff PDFs before these schedules are used in any
  audit report.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from tariff_audit.tariffs.models import EnergyTier, FuelTier, TariffSchedule
from tariff_audit.tariffs.registry import register_tariff

# ---------------------------------------------------------------------------
# Effective January 2026 — rates per CLAUDE.md spec
# ---------------------------------------------------------------------------

FPL_RS1_2026 = TariffSchedule(
    utility="FPL",
    rate_schedule="RS-1",
    effective_date=date(2026, 1, 1),
    expiration_date=None,
    psc_docket="20250011-EI",
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
    transition_credit=Decimal("-0.040"),
    source_url="https://www.fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2026.pdf",
    notes=(
        "Rates encoded from CLAUDE.md spec. Sum for 1,000 kWh = $133.10; "
        "FPL published typical bill = $136.64. Gap unreconciled — verify "
        "against Section 8 tariff PDF."
    ),
)

# ---------------------------------------------------------------------------
# Effective 2025 — STUB schedule
# ---------------------------------------------------------------------------
# Only the base charge is verified here (per CLAUDE.md historical-tariff test).
# All other rates are placeholders that MUST be replaced with real 2025 values
# before any audit report is generated using this schedule.
# ---------------------------------------------------------------------------

FPL_RS1_2025 = TariffSchedule(
    utility="FPL",
    rate_schedule="RS-1",
    effective_date=date(2025, 1, 1),
    expiration_date=date(2025, 12, 31),
    psc_docket="20240011-EI",
    base_charge_monthly=Decimal("8.58"),
    minimum_bill=Decimal("25.00"),
    energy_tiers=[
        EnergyTier(max_kwh=1000, rate_cents_per_kwh=Decimal("0")),
        EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("0")),
    ],
    fuel_tiers=[
        FuelTier(max_kwh=1000, rate_cents_per_kwh=Decimal("0")),
        FuelTier(max_kwh=None, rate_cents_per_kwh=Decimal("0")),
    ],
    notes="STUB — only base charge verified. Do NOT use for audit until clause rates are entered.",
)

# ---------------------------------------------------------------------------
# Effective 2024 — STUB schedule (structure only; rates pending verification)
# ---------------------------------------------------------------------------

FPL_RS1_2024 = TariffSchedule(
    utility="FPL",
    rate_schedule="RS-1",
    effective_date=date(2024, 1, 1),
    expiration_date=date(2024, 12, 31),
    psc_docket="20230011-EI",
    base_charge_monthly=Decimal("8.58"),
    minimum_bill=Decimal("25.00"),
    energy_tiers=[
        EnergyTier(max_kwh=1000, rate_cents_per_kwh=Decimal("0")),
        EnergyTier(max_kwh=None, rate_cents_per_kwh=Decimal("0")),
    ],
    fuel_tiers=[
        FuelTier(max_kwh=1000, rate_cents_per_kwh=Decimal("0")),
        FuelTier(max_kwh=None, rate_cents_per_kwh=Decimal("0")),
    ],
    notes="STUB — rates pending verification against 2024 PSC tariff PDF.",
)


register_tariff(FPL_RS1_2024)
register_tariff(FPL_RS1_2025)
register_tariff(FPL_RS1_2026)
