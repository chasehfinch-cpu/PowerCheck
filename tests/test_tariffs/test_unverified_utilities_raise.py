"""Unverified utility tariffs must raise LookupError, not silently return wrong data.

Duke Energy Florida, Florida Public Utilities (FPUC), and municipal utilities
are currently pending tariff data entry. Any attempt to audit a bill under
these utilities must fail loudly — a partial or fabricated tariff would
produce misleading forensic reports.
"""

from __future__ import annotations

from datetime import date

import pytest

from tariff_audit.tariffs.registry import get_tariff, registered_utilities


def test_duke_rs1_lookup_raises():
    with pytest.raises(LookupError, match="No tariff registered"):
        get_tariff("DUKE", "RS-1", date(2026, 6, 15))


def test_fpu_rs_lookup_raises():
    with pytest.raises(LookupError, match="No tariff registered"):
        get_tariff("FPU", "RS", date(2026, 6, 15))


def test_municipal_utilities_not_registered():
    """Municipal utilities are not PSC-regulated; this tool does not audit them."""
    for util in ("JEA", "OUC", "TALLAHASSEE", "LAKELAND", "GAINESVILLE"):
        with pytest.raises(LookupError):
            get_tariff(util, "RS", date(2026, 6, 15))


def test_registered_utilities_include_fpl_and_teco():
    utils = registered_utilities()
    assert "FPL" in utils
    assert "TECO" in utils
    # Duke and FPU intentionally NOT in the registered list until data is entered
    assert "DUKE" not in utils
    assert "FPU" not in utils
