"""Auto-detect which utility a bill belongs to from its extracted text.

Every concrete :class:`~tariff_audit.parsers.base.BillParser` implements
``can_parse(text)``. This module iterates through the registered parsers
and returns the first one that recognizes the text, or ``None`` if no
parser matches.

Add new parsers to :data:`REGISTERED_PARSERS` to enable auto-detection.
"""

from __future__ import annotations

from tariff_audit.parsers.base import BillParser
from tariff_audit.parsers.bill_layouts import BillLayoutGuide, detect_layout
from tariff_audit.parsers.fpl import FPLBillParser

#: Ordered list of registered FULL parsers (can produce a ``ParsedBill``).
#: Detection tries each in order and returns the first match.
REGISTERED_PARSERS: tuple[BillParser, ...] = (
    FPLBillParser(),
    # Duke, TECO, FPU parsers pending — identify via detect_utility_name()
    # instead (which falls back to layout markers) until full parsers are added.
)


def detect_utility(text: str) -> BillParser | None:
    """Return the first FULL parser that claims the text, or ``None``.

    This only returns a parser when we can fully extract a ``ParsedBill``.
    When only identification is needed (e.g. "which firm is billing this
    customer?"), use :func:`detect_utility_name` instead — it falls back to
    the layout guide's markers and covers all four FL IOUs.
    """
    for parser in REGISTERED_PARSERS:
        if parser.can_parse(text):
            return parser
    return None


def detect_utility_name(text: str) -> str | None:
    """Return the utility identifier ("FPL", "DUKE", "TECO", "FPU") or None.

    Tries full parsers first (when a bill is fully parseable) and falls
    back to the layout detection markers so every FL IOU is identifiable
    even if the full PDF parser isn't yet implemented.
    """
    parser = detect_utility(text)
    if parser is not None:
        return parser.name.upper()
    guide = detect_layout(text)
    return guide.utility if guide else None


def detect_utility_layout(text: str) -> BillLayoutGuide | None:
    """Return the bill layout guide for a detected utility.

    Useful when the UI needs to render a manual-entry form tailored to the
    utility's specific bill layout — even if full automatic parsing isn't
    available.
    """
    return detect_layout(text)
