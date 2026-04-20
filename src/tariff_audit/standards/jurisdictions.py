"""Per-jurisdiction municipal utility tax and franchise fee lookup.

Florida municipalities and charter counties may impose a **Public Service
Tax** of up to 10% on electric service (F.S. 166.231) and may separately
charge a **Franchise Fee** (typically 0–6%) to the utility, which the
utility passes through as a per-bill line item.

The combination of these two varies by service address, so a faithful bill
reconstruction requires looking up the right rate pair for the customer's
city/county. This module provides a **seed lookup** for the largest FL
municipalities served by each IOU. For jurisdictions not listed, fall back
to the unincorporated-county defaults (typically 0% both) or require manual
entry.

**Data-quality flag**: The rates below are best-known approximations and
MUST be verified against the current ordinance or franchise agreement
before being used in a customer-facing forensic report. Municipal ordinances
change frequently — there is no single authoritative machine-readable
source for all 400+ FL jurisdictions.

References:

- **F.S. 166.231** — Municipal public service tax, max 10%.
- Each utility's franchise agreements are PSC-filed and listed at
  ``psc.state.fl.us/electric-tariffs`` under franchise ordinances.
- FPL franchise summary (example): available to FPL tariff customers.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class JurisdictionRates:
    """Municipal tax + franchise fee pair for one city / county / utility."""

    jurisdiction: str
    county: str
    utility: str  # "FPL" | "DUKE" | "TECO" | "FPU" | "ANY"
    municipal_utility_tax: Decimal  # 0.00–0.10
    franchise_fee: Decimal  # 0.00–0.06 typical
    ordinance_reference: str = ""
    verified: bool = False
    notes: str = ""


# ---------------------------------------------------------------------------
# Seed data — representative jurisdictions, NOT exhaustive.
# ---------------------------------------------------------------------------
# The entries below are included to demonstrate the lookup structure and
# cover the highest-population municipalities in each IOU service area.
# Every rate flagged ``verified=False`` must be re-checked against the
# current ordinance before use in a forensic report.
# ---------------------------------------------------------------------------

_SEED: tuple[JurisdictionRates, ...] = (
    # ------------------------------- FPL ----------------------------------
    JurisdictionRates(
        jurisdiction="Miami",
        county="Miami-Dade",
        utility="FPL",
        municipal_utility_tax=Decimal("0.10"),
        franchise_fee=Decimal("0.06"),
        ordinance_reference="City of Miami Code Sec. 42-71",
        verified=False,
        notes="Miami historically at the statutory maximum 10% PST + 6% franchise.",
    ),
    JurisdictionRates(
        jurisdiction="Fort Lauderdale",
        county="Broward",
        utility="FPL",
        municipal_utility_tax=Decimal("0.10"),
        franchise_fee=Decimal("0.06"),
        ordinance_reference="Fort Lauderdale Code of Ordinances",
        verified=False,
    ),
    JurisdictionRates(
        jurisdiction="West Palm Beach",
        county="Palm Beach",
        utility="FPL",
        municipal_utility_tax=Decimal("0.10"),
        franchise_fee=Decimal("0.06"),
        verified=False,
    ),
    JurisdictionRates(
        jurisdiction="Unincorporated Miami-Dade",
        county="Miami-Dade",
        utility="FPL",
        municipal_utility_tax=Decimal("0"),
        franchise_fee=Decimal("0"),
        verified=False,
        notes="Unincorporated county areas typically have no PST or franchise.",
    ),

    # ------------------------------ Duke FL --------------------------------
    JurisdictionRates(
        jurisdiction="St. Petersburg",
        county="Pinellas",
        utility="DUKE",
        municipal_utility_tax=Decimal("0.10"),
        franchise_fee=Decimal("0.06"),
        verified=False,
    ),
    JurisdictionRates(
        jurisdiction="Clearwater",
        county="Pinellas",
        utility="DUKE",
        municipal_utility_tax=Decimal("0.10"),
        franchise_fee=Decimal("0.06"),
        verified=False,
    ),
    JurisdictionRates(
        jurisdiction="Ocala",
        county="Marion",
        utility="DUKE",
        municipal_utility_tax=Decimal("0.10"),
        franchise_fee=Decimal("0.06"),
        verified=False,
    ),

    # -------------------------------- TECO ---------------------------------
    JurisdictionRates(
        jurisdiction="Tampa",
        county="Hillsborough",
        utility="TECO",
        municipal_utility_tax=Decimal("0.10"),
        franchise_fee=Decimal("0.06"),
        ordinance_reference="City of Tampa Code Ch. 24",
        verified=False,
    ),
    JurisdictionRates(
        jurisdiction="Unincorporated Hillsborough",
        county="Hillsborough",
        utility="TECO",
        municipal_utility_tax=Decimal("0.07"),
        franchise_fee=Decimal("0.055"),
        verified=False,
        notes="Hillsborough County charter imposes a 7% PST in unincorporated areas.",
    ),
    JurisdictionRates(
        jurisdiction="Plant City",
        county="Hillsborough",
        utility="TECO",
        municipal_utility_tax=Decimal("0.10"),
        franchise_fee=Decimal("0.06"),
        verified=False,
    ),
)


# Index for O(1) lookup
_BY_KEY: dict[tuple[str, str, str], JurisdictionRates] = {
    (r.utility.upper(), r.jurisdiction.casefold(), r.county.casefold()): r
    for r in _SEED
}


def lookup(
    utility: str,
    jurisdiction: str,
    county: str,
) -> JurisdictionRates | None:
    """Return the rate pair for this utility/jurisdiction/county, or None.

    The caller is responsible for handling the None case — typically by
    falling back to zero rates and flagging the audit report as
    "taxes/fees unverified for this address."
    """
    key = (utility.upper(), jurisdiction.casefold(), county.casefold())
    return _BY_KEY.get(key)


def all_jurisdictions() -> tuple[JurisdictionRates, ...]:
    """Return every seeded jurisdiction (for diagnostics / validation)."""
    return _SEED


def unverified_jurisdictions() -> tuple[JurisdictionRates, ...]:
    """Return jurisdictions whose rates have not been verified against a
    current ordinance. Used to gate audit-report generation."""
    return tuple(r for r in _SEED if not r.verified)
