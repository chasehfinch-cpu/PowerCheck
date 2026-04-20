# CLAUDE.md — Florida Tariff Forensics Engine (TariffAudit FL)

## FIRST: Repository Access

Repository confirmed: **https://github.com/chasehfinch-cpu/PowerCheck** (public). Local path: `C:\Users\ChaseFinch\PowerCheck`.

---

## Project Overview

**TariffAudit FL** is a local-first, zero-data-retention desktop application that performs forensic billing audits on Florida electric utility bills for both residential and commercial customers. It parses actual billing documents (PDF, image, CSV), reconstructs what the bill *should* be using the exact PSC-approved tariff schedules, identifies overcharges down to the line item, scores each finding by confidence tier, and generates ready-to-file PSC complaint forms and utility dispute letters.

### Core Value Proposition

Florida's investor-owned electric utilities (FPL, Duke Energy Florida, TECO, Florida Public Utilities Co., and the former Gulf Power territory now under FPL) bill customers using complex, multi-component tariff formulas published by the Florida Public Service Commission. Most customers have no way to verify their bills are calculated correctly. This tool performs that verification with mathematical precision.

### Design Philosophy

- **Zero data retention**: All processing happens locally. No cloud, no telemetry, no accounts, no cookies.
- **Deterministic-first**: Every calculation must trace back to a specific PSC docket number and tariff sheet.
- **Document-in, answer-out**: Drop a bill PDF (or image, or type numbers manually), get a forensic report.
- **Dual audience**: Residential consumers and commercial facility managers (demand, power factor, TOU).

---

## Architecture

### Technology Stack

```
Runtime:        Python 3.11+
UI Framework:   Textual (TUI) + optional Streamlit local web UI
PDF Parsing:    pdfplumber (primary), pytesseract + Pillow (OCR fallback)
Data:           DuckDB (embedded, ephemeral)
Grid Data:      EIA API v2 (free key)
Packaging:      pip-installable, optional `[desktop]` extra
VCS:            Git, GitHub-published, MIT license
CI:             GitHub Actions for lint + tests
```

### Directory Structure (target)

See `src/tariff_audit/` for the current scaffolding. The full target layout
(parsers/, tariffs/, engine/, grid/, output/, ui/) is built out across the
phased plan below. Phase 1 delivers only: `tariffs/models.py`, `tariffs/registry.py`,
`tariffs/fpl/rs1.py`, and `engine/calculator.py` plus tests.

---

## Phase Plan

### Phase 1 — Foundation (CURRENT)
1. Repo init, pyproject.toml, CI pipeline ✓
2. `tariffs/models.py` + `tariffs/registry.py` ✓
3. FPL RS-1 data for 2024, 2025, 2026 (2024/2025 stubbed) ✓
4. `engine/calculator.py` with bill reconstruction ✓
5. Unit tests verifying 1,000 kWh / 1,200 kWh / minimum bill ✓
6. **TODO: reconcile the $133.10 calculated sum vs FPL's published $136.64 typical-bill figure**
   — xfail test in `tests/test_tariffs/test_fpl_rs1.py` tracks this.

### Phase 2 — Parsing
- `parsers/base.py`, `parsers/fpl.py`, `parsers/csv_import.py`
- `parsers/detector.py` (auto-detect utility), `parsers/ocr.py` (fallback)

### Phase 3 — Audit Engine
- `engine/auditor.py` (comparison), `engine/anomalies.py` (6 detection vectors)
- `engine/confidence.py` (scoring), `engine/line_items.py` (non-tariff)
- `engine/multi_month.py` (trend analysis)

### Phase 4 — Output
- `output/complaint.py` (PSC form), `output/dispute_letter.py` (utility letter)
- `output/report.py` (forensic report), `output/export.py` (CSV/JSON)

### Phase 5 — Grid Data
- `grid/eia_client.py` (EIA API v2), `grid/demand.py`, `grid/fuel_mix.py`

### Phase 6 — Additional Utilities
- Duke Energy FL (RS-1, GS-1, GSD-1), TECO (RS, GS, GSD)

### Phase 7 — Demand Schedules
- FPL GSD-1 and GSLD-1 (demand, ratchet, power factor, TOU)

### Phase 8 — UI
- Streamlit web UI, Textual TUI, CLI entry point

### Phase 9 — Polish
- README with screenshots, docs/ methodology, release pipeline, PyPI

---

## Tariff Data — FPL RS-1 Effective January 2026

Per CLAUDE.md spec (PSC Dockets 20250011-EI, 20210015-EI, 20250001-EI, 20250002-EG, 20250007-EI, 20250010-EI):

```
Base Charge:         $10.52/month
Energy ≤1,000 kWh:    7.865 ¢/kWh
Energy >1,000 kWh:    8.865 ¢/kWh
Conservation:          0.148 ¢/kWh
Capacity:              0.052 ¢/kWh
Environmental:         0.345 ¢/kWh
Storm Protection:      0.995 ¢/kWh
Fuel ≤1,000 kWh:       2.893 ¢/kWh
Fuel >1,000 kWh:       3.893 ¢/kWh
Transition Credit:    -0.040 ¢/kWh
Minimum Bill:         $30.00
```

**Reconciliation flag**: summing these rates for 1,000 kWh yields **$133.10**, not the $136.64 typical bill FPL publishes. Gap must be closed against the Section 8 tariff PDF before Phase 1 is considered done.

---

## Anomaly Detection Vectors (Phase 3)

| ID | Name | Confidence |
|----|------|-----------|
| RATE_CLASS | Wrong Rate Class | DETERMINISTIC (100%) |
| TIER_BREAK | Tier Threshold Error | DETERMINISTIC (100%) |
| BASE_CHARGE | Base Charge Mismatch | DETERMINISTIC (100%) |
| FUEL_VARIANCE | Fuel Pass-Through Anomaly | HIGH (90%) |
| STORM_PERSIST | Storm Surcharge Persistence | HIGH (85%) |
| SEASONAL | Seasonal Bill Anomaly | MODERATE (70%) |

---

## Non-Functional Requirements

- **Zero data retention** — no telemetry, no cloud (except EIA API for grid data, carries no customer info)
- **Decimal arithmetic** — `decimal.Decimal` only for financial math, never `float`
- **Auditability** — every calculated value traces to a specific tariff rate, docket number, and effective date
- **Offline-capable** — core audit engine works without internet; EIA integration is optional
- **Cross-platform** — macOS, Linux, Windows

---

## Business Context

Built under **Finch Business Services, LLC** as a consumer advocacy and commercial billing audit product.

- **Residential**: Free/low-cost self-service tool → brand awareness + leads
- **Small commercial (GS-1/GSD-1)**: Contingency (25–35% of recovered overcharges)
- **Large commercial (GSLD-1)**: Advisory (20–30% contingency)

Business handles: Limited Power of Attorney (FL Ch. 709), service agreements, certified-mail dispute letters, PSC complaint submission, refund collection.

---

## Reference Links

- FPL Residential Rates (Jan 2026): `fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2026.pdf`
- FPL Full Tariff (Section 8): `fpl.com/rates/pdf/electric-tariff-section8.pdf`
- PSC Electric Tariffs Index: `psc.state.fl.us/electric-tariffs`
- PSC Complaint Form: `psc.state.fl.us/consumer-complaint-form`
- EIA API v2: `eia.gov/opendata/documentation.php`
- EIA API Registration: `eia.gov/opendata/`
- EIA Grid Monitor (FPL): `eia.gov/electricity/gridmonitor/dashboard/electric_overview/balancing_authority/FPL`
- FL Power of Attorney Act: F.S. Chapter 709
- FL Utility Regulation: F.S. Chapters 366, 367
