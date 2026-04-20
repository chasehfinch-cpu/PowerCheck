"""Florida Public Utilities Company (FPUC) Residential Service — PENDING DATA ENTRY.

FPUC is the smallest of Florida's PSC-regulated investor-owned electric
utilities (approximately 30,000 electric customers, concentrated in Marianna
and Fernandina Beach areas). Its tariff schedule is simpler than the big
three IOUs but must still be verified before this module registers any
rates.

This module intentionally registers no tariff schedules — lookups raise
``LookupError`` until rates are entered from the authoritative PSC filing.

References:

- **PSC Docket 20240099-EI**: 2024 FPUC rate case — filed for rate increase
  and updated schedules. Review the docket at:
  ``floridapsc.com -> Docket 20240099-EI``.
- **Rate schedules A–G**: FPUC publishes schedules at
  ``fpuc.com/tariffs/`` under labels 08592-2024 A/B/C/D/E/F/G.
- **Annual ECCR filing**: ``psc.state.fl.us/library/filings/2026/00557-2026/``

To complete this module:

1. Download each of the A–G schedule PDFs from ``fpuc.com/tariffs/``.
2. Extract with ``pdfplumber`` and retain text at
   ``.tariff_research/fpu_<schedule>_<year>.txt``.
3. Identify the residential schedule (typically Schedule A or labeled "RS")
   and populate a ``TariffSchedule`` with all rate components.
4. Register via ``register_tariff``.

Note: FPUC's service territories are NOT contiguous — verify rate class
availability by ZIP code or county before audit.
"""

# Intentionally empty — no schedules registered.
