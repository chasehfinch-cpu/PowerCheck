"""Auto-detect which utility a bill belongs to from its extracted text.

Every concrete :class:`~tariff_audit.parsers.base.BillParser` implements
``can_parse(text)``. This module iterates through the registered parsers
and returns the first one that recognizes the text, or ``None`` if no
parser matches.

Add new parsers to :data:`REGISTERED_PARSERS` to enable auto-detection.
"""

from __future__ import annotations

from tariff_audit.parsers.base import BillParser
from tariff_audit.parsers.fpl import FPLBillParser

#: Ordered list of registered parsers. Detection tries each in order and
#: returns the first match. Order: largest utility first (FPL, Duke, TECO,
#: FPU) to minimize false-positive risk on shared keywords.
REGISTERED_PARSERS: tuple[BillParser, ...] = (
    FPLBillParser(),
    # Duke, TECO, FPU parsers pending Phase 2 completion.
)


def detect_utility(text: str) -> BillParser | None:
    """Return the first parser that claims the text, or ``None``.

    Use the returned parser directly to get a :class:`ParsedBill`::

        parser = detect_utility(bill_text)
        if parser is None:
            raise ValueError("Could not detect utility from bill text")
        parsed = parser.parse(bill_text)
    """
    for parser in REGISTERED_PARSERS:
        if parser.can_parse(text):
            return parser
    return None


def detect_utility_name(text: str) -> str | None:
    """Convenience wrapper returning just the utility identifier."""
    parser = detect_utility(text)
    return parser.name.upper() if parser else None
