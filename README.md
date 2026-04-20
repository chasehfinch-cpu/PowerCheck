# TariffAudit FL (PowerCheck)

**Florida Tariff Forensics Engine** — a local-first, zero-data-retention desktop tool that performs forensic billing audits on Florida electric utility bills against PSC-approved tariff schedules.

> **Status:** Phase 1 (foundation — tariff models, FPL RS-1 data, calculator, tests). See [CLAUDE.md](CLAUDE.md) for full project spec and phased build plan.

## What it does

Parses a Florida electric utility bill (FPL, Duke Energy Florida, TECO, FPU, legacy Gulf Power), reconstructs what the bill *should* be using the exact PSC-approved tariff, identifies overcharges down to the line item, scores each finding by confidence tier, and generates ready-to-file PSC complaint forms and utility dispute letters.

## Design principles

- **Zero data retention** — all processing happens locally. No cloud, no telemetry, no accounts.
- **Deterministic-first** — every calculation traces back to a specific PSC docket number and tariff sheet.
- **Penny-accurate** — all financial math uses `decimal.Decimal`, never `float`.
- **Document-in, answer-out** — drop a bill PDF, get a complete forensic report.

## Install (development)

```bash
git clone https://github.com/chasehfinch-cpu/PowerCheck.git
cd PowerCheck
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
pytest
```

## Phase 1 — what's here now

- `src/tariff_audit/tariffs/models.py` — Pydantic models for tariff schedules, energy tiers, fuel tiers
- `src/tariff_audit/tariffs/registry.py` — tariff lookup by utility + date + rate class
- `src/tariff_audit/tariffs/fpl/rs1.py` — FPL Residential Service rate schedule (2024, 2025, 2026)
- `src/tariff_audit/engine/calculator.py` — bill reconstruction engine
- `tests/` — deterministic unit tests for RS-1 calculations

## License

MIT — see [LICENSE](LICENSE).

## Business context

Built by [Finch Business Services, LLC](https://github.com/chasehfinch-cpu) as a consumer advocacy and commercial billing audit tool. See [CLAUDE.md](CLAUDE.md) for business model and engagement structure.
