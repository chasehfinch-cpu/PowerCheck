"""Duke Energy Florida Residential Service (RS-1) — PENDING DATA ENTRY.

This module intentionally registers no tariff schedules. Attempting to look
up a Duke Energy FL RS-1 rate will raise ``LookupError`` — which is the
correct behavior until every rate component is verified against the
PSC-filed tariff. We do not approximate.

What we know without full verification (useful for sanity checks once the
full tariff is entered):

- **2026 ECCR factor**: 0.386 ¢/kWh for residential (secondary voltage).
  Source: PSC filing 07095-2025 (Docket 20250001-EI fuel + 20250002-EG
  ECCR). Retained at ``.tariff_research/duke_psc_filing.txt``.
- **March 2026 rate event**: Storm Cost Recovery charge removed, resulting
  in approximately a $44 decrease per 1,000 kWh vs February 2026.
  Source: Duke Energy press release (Feb 2026).
- **PSC Docket references for 2026 tariff**:
  - 20240160-EI (Duke Energy Florida multiyear rate agreement 2024–2027)
  - 20250001-EI (annual fuel cost recovery)
  - 20250002-EG (energy conservation cost recovery)

To complete this module:

1. Obtain the current RS-1 tariff PDF from
   ``duke-energy.com/home/billing/rates/index-of-rate-schedules?jur=FL01``
   (the 403 response seen in research likely requires a user-agent; download
   via ``curl -A`` or a headless browser).
2. Extract with ``pdfplumber`` and retain the text at
   ``.tariff_research/duke_rs1_<year>.txt``.
3. Populate a ``TariffSchedule`` for each effective date window (Jan–Feb 2026
   pre-storm-removal, Mar 2026+ post-storm-removal) with:
   - Customer charge (monthly)
   - Energy charge (tiered or flat)
   - Fuel charge (tiered or flat)
   - Storm Protection charge
   - Storm Cost Recovery charge (Jan–Feb 2026 only)
   - ECCR (0.386 ¢/kWh confirmed)
   - Capacity cost recovery
   - Environmental cost recovery
   - Any riders (Asset Securitization, Clean Energy Connection, etc.)
4. Call ``register_tariff`` for each schedule.
5. Add tests to ``tests/test_tariffs/test_duke_rs1.py`` verifying:
   - 1,000 kWh subtotals reconcile to Duke's published "typical bill" figures
     (adjusted for Florida Gross Receipts Tax gross-up of ~1.02632)
   - Schedule date windows do not overlap
"""

# Intentionally empty — no schedules registered.
