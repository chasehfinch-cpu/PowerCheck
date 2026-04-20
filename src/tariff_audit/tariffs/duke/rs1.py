"""Duke Energy Florida Residential Service (RS-1) — PENDING DATA ENTRY.

This module intentionally registers no tariff schedules. Attempting to look
up a Duke Energy FL RS-1 rate raises ``LookupError`` — the correct behavior
until every rate component is verified against the PSC-filed tariff.

**Research status (as of 2026-04)**:

- Duke Energy's rate schedule index
  (``duke-energy.com/home/billing/rates/index-of-rate-schedules?jur=FL01``
  and the un-parameterized variant) returns HTTP 200 with a JavaScript SPA
  shell (Sitecore-powered, inspected; no hardcoded PDF URLs in the 917 KB
  of rendered HTML). Rate PDFs are fetched client-side via a Sitecore
  Content API. A headless browser (Playwright / Selenium) is the practical
  path to automate retrieval.
- Known-good URL patterns
  (``/-/media/pdfs/for-your-home/rates/electricfl/*``) all return 404 —
  the tree has been reorganized.
- The Florida PSC tariff index (``psc.state.fl.us/electric-tariffs``) is
  also a JavaScript SPA and cannot be scraped via plain HTTP GET.
- Individual PSC filings at
  ``floridapsc.com/pscfiles/library/filings/YYYY/NNNNN-YYYY/NNNNN-YYYY.pdf``
  ARE directly downloadable and extractable via ``pdfplumber`` once the
  docket / filing number is known. This is the recommended Phase 2 path:
  query Docket 20240160-EI's exhibit list for the current tariff PDF.

**Partial verified data**:

- **2026 ECCR factor (residential, secondary)**: ``0.386 ¢/kWh``
  (Source: PSC filing 07095-2025, retained at ``.tariff_research/
  duke_psc_filing.txt``).
- **March 2026 rate event**: Storm Cost Recovery charge removed, reducing
  a typical 1,000 kWh bill by approximately $44/month vs Feb 2026.
  Implication: Duke's 2026 Jan–Feb and Mar+ schedules differ significantly
  and must be entered as two separate date-windowed ``TariffSchedule``
  entries.

**PSC docket references for 2026 tariff**:

- **20240160-EI** — Duke Energy Florida multiyear rate agreement 2024–2027
- **20250001-EI** — annual fuel cost recovery
- **20250002-EG** — energy conservation cost recovery

**To complete this module**:

1. Access each Duke Florida rate-schedule PDF via a headless browser or
   by looking up direct filing URLs in PSC Docket 20240160-EI's exhibit
   list. Target files:
   - RS-1 (Residential Service, standard)
   - RST-1 (Residential Service, Time-of-Use)
   - RSL-1, RSL-2 (lighting variants)
2. Extract text via ``pdfplumber``; retain at ``.tariff_research/
   duke_<schedule>_<year>.txt``.
3. Populate a pair of ``TariffSchedule`` entries per rate schedule:
   - Jan–Feb 2026 (storm cost recovery active)
   - Mar 2026 onward (storm cost recovery removed)
4. Verify each 1,000 kWh subtotal × FL Gross Receipts Tax (~1.02632)
   matches Duke's published typical-bill figures for the period.
5. Register via ``register_tariff``.
6. Add tests to ``tests/test_tariffs/test_duke_rs1.py``.
"""

# Intentionally empty — no schedules registered.
