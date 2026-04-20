"""Tests for the jurisdictional tax/fee lookup."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tariff_audit.standards.jurisdictions import (
    UnverifiedJurisdictionError,
    all_jurisdictions,
    lookup,
    lookup_with_county_fallback,
    require_verified,
    unverified_jurisdictions,
    verified_jurisdictions,
)


def test_at_least_thirty_jurisdictions_seeded():
    """Sanity check: the seed dataset should cover top FL municipalities."""
    assert len(all_jurisdictions()) >= 30


def test_miami_fpl_lookup_finds_entry():
    r = lookup("FPL", "Miami", "Miami-Dade")
    assert r is not None
    assert r.municipal_utility_tax == Decimal("0.10")
    assert r.franchise_fee == Decimal("0.06")


def test_case_insensitive_lookup():
    assert lookup("fpl", "miami", "miami-dade") is not None
    assert lookup("FPL", "MIAMI", "MIAMI-DADE") is not None


def test_tampa_teco_lookup():
    r = lookup("TECO", "Tampa", "Hillsborough")
    assert r is not None
    assert r.utility == "TECO"


def test_unknown_jurisdiction_returns_none():
    assert lookup("FPL", "Narnia", "Neverland") is None


def test_county_fallback_uses_unincorporated_entry():
    """A small unlisted town in Broward should fall back to Unincorporated Broward."""
    r = lookup_with_county_fallback("FPL", "Tiny Unlisted Town", "Broward")
    assert r is not None
    assert r.jurisdiction.lower().startswith("unincorporated")


def test_county_fallback_returns_none_when_no_county_entry():
    """A county with no unincorporated fallback entry should return None."""
    r = lookup_with_county_fallback("FPL", "Nowhere", "Fakecounty")
    assert r is None


def test_all_seed_entries_flagged_unverified():
    """All current seed data must be flagged unverified until ordinance check."""
    assert len(verified_jurisdictions()) == 0
    assert len(unverified_jurisdictions()) == len(all_jurisdictions())


def test_require_verified_raises_for_unverified():
    r = lookup("FPL", "Miami", "Miami-Dade")
    assert r is not None
    with pytest.raises(UnverifiedJurisdictionError, match="not verified"):
        require_verified(r)


def test_franchise_fee_never_exceeds_statutory_ceiling():
    """No seeded franchise fee should exceed 6% (a soft ceiling for FL)."""
    for r in all_jurisdictions():
        assert r.franchise_fee <= Decimal("0.06"), (
            f"{r.jurisdiction} franchise fee {r.franchise_fee} exceeds 6%"
        )


def test_municipal_tax_never_exceeds_statutory_max():
    """F.S. 166.231 caps municipal PST at 10%."""
    for r in all_jurisdictions():
        assert r.municipal_utility_tax <= Decimal("0.10"), (
            f"{r.jurisdiction} PST {r.municipal_utility_tax} exceeds statutory max 10%"
        )


def test_every_utility_has_at_least_one_entry():
    utilities = {r.utility for r in all_jurisdictions()}
    assert {"FPL", "DUKE", "TECO", "FPU"} <= utilities


def test_former_gulf_territory_flagged():
    """Pensacola and Panama City should have NW Florida notes."""
    pensacola = lookup("FPL", "Pensacola", "Escambia")
    assert pensacola is not None
    assert "Gulf Power" in pensacola.notes or "NWFL" in pensacola.notes
