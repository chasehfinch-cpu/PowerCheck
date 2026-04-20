# Tariff research audit trail

Raw text extractions from authoritative FPL/PSC PDFs, retained so that every
rate encoded in `src/tariff_audit/tariffs/` is traceable to a primary source
snapshot rather than a transient marketing page.

| File | Source URL(s) |
|------|--------------|
| `fpl_pdfs.txt` | `fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2026.pdf` + `jan-2026-res-eff-rates-rules-and-regulations.pdf` |
| `fpl_2025.txt` | `fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2025.pdf` + `res-eff-feb-2025.pdf` |
| `fpl_2024.txt` | `fpl.com/content/dam/fplgp/us/en/rates/pdf/res-eff-jan-2024.pdf` |
| `fpl_section8.txt` | `fpl.com/rates/pdf/electric-tariff-section8.pdf` (full PSC-filed tariff) |

These are text extractions via `pdfplumber` — column spacing is imperfect
but every rate cited in `tariffs/fpl/rs1.py` can be located here.

When a new rate period publishes (typically January each year), add a new
extraction file and update `rs1.py` — then verify the overlap test in
`tests/test_tariffs/test_fpl_rs1.py::test_fpl_rs1_schedules_do_not_overlap`
still passes.
