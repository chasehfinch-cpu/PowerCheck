"""Florida Public Utilities Company (FPUC) Residential Service — PENDING DATA ENTRY.

FPUC is the smallest of Florida's PSC-regulated investor-owned electric
utilities (~30,000 electric customers in Marianna, Fernandina Beach, and
Indiantown service areas). Its tariff schedule is simpler than the big
three IOUs but must be verified before this module registers any rates.

This module intentionally registers no tariff schedules. Lookups raise
``LookupError`` until rates are entered from the authoritative PSC filing.

**Research status (as of 2026-04)**:

- The FPU tariffs landing page (``fpuc.com/tariffs/``) lists seven
  schedule PDFs labeled 08592–08599 under PSC Docket 20240099-EI. The
  page is JavaScript-rendered; PDFs require a headless browser to
  discover URLs reliably.
- Annual ECCR filings are at
  ``psc.state.fl.us/library/filings/2026/00557-2026/00557-2026.pdf`` and
  can be pulled directly.

**PSC Docket references**:

- **20240099-EI** — 2024 FPUC rate case (increase in rates and updated
  schedules A–G).
- **00557-2026** — 2026 annual electric cost recovery rates effective
  January 2026 through December 2026.

**To complete this module**:

1. Download the A-labeled schedule PDF from ``fpuc.com/tariffs/`` (likely
   the residential schedule). Tree structure:
   - Schedule A: Residential (RS)
   - Schedule B: Small General Service
   - Schedule C: General Service Demand
   - Schedule D–G: specialty / large service
2. Extract text via ``pdfplumber``; retain at ``.tariff_research/
   fpu_schedule_a_<year>.txt``.
3. Populate one ``TariffSchedule`` per effective-date window.
4. Register via ``register_tariff``.

**Note**: FPU's service territories are NOT contiguous — verify rate
class availability by ZIP code or county before audit. An FPU customer
in Fernandina Beach (Nassau County) pays different rates than one in
Marianna (Jackson County) for some rate classes.
"""

# Intentionally empty — no schedules registered.
