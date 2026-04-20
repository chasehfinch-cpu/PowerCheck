"""Bill document parsers — extract structured data from utility bills.

Every parser returns a :class:`ParsedBill` pydantic model (see
:mod:`tariff_audit.parsers.base`) that downstream code (auditor, composer)
consumes.

Supported input forms:

- ``parsers.fpl`` — FPL PDF bills (residential peninsular + NW Florida)
- ``parsers.csv_import`` — manual entry and bulk CSV imports
- ``parsers.detector`` — auto-detect utility from an unknown PDF

Phase 2 work in progress: Duke, TECO, FPU parsers; OCR fallback.
"""

from tariff_audit.parsers.base import BillParser, ParsedBill
from tariff_audit.parsers.csv_import import parse_csv_row
from tariff_audit.parsers.detector import detect_utility
from tariff_audit.parsers.fpl import FPLBillParser

__all__ = [
    "BillParser",
    "FPLBillParser",
    "ParsedBill",
    "detect_utility",
    "parse_csv_row",
]
