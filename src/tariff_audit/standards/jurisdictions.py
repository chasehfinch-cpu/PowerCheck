"""Per-jurisdiction municipal utility tax and franchise fee lookup.

Florida municipalities and charter counties may impose a **Public Service
Tax** of up to 10% on electric service (F.S. 166.231) and may separately
charge a **Franchise Fee** (typically 5–6%) to the utility, which the
utility passes through as a per-bill line item.

The combination varies by service address, so faithful bill reconstruction
requires looking up the correct rate pair. This module provides a seed
dataset for the largest municipalities in each IOU service territory.

**Data-quality flag**: All rates below are marked ``verified=False`` unless
cross-checked against the current ordinance and utility franchise
agreement. A production audit must pass through :func:`require_verified`
before relying on these numbers for a customer-facing forensic report.

References:

- **F.S. 166.231 / 166.232** — Municipal public service tax, max 10%.
- **Florida Association of Counties "Home Rule Green Book"** —
  cross-county franchise fee listing.
- Utility franchise agreements are PSC-filed at
  ``psc.state.fl.us/electric-tariffs`` under each utility's tariff index.
- County ordinance codes are published via Municode
  (``library.municode.com``) for most FL jurisdictions.

**Note on coverage**: this is a representative seed of the largest
municipalities in each IOU service area. A full production dataset must
cover all 411 FL municipalities plus unincorporated county areas. Missing
jurisdictions fall through to ``None`` and the composer treats them as
"taxes/fees unverified — do not produce audit report without manual entry."
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
# Seed data — representative top-30+ municipalities per IOU
# ---------------------------------------------------------------------------

_SEED: tuple[JurisdictionRates, ...] = (
    # =========================================================================
    # FPL — Peninsular Florida (Broward, Miami-Dade, Palm Beach, Martin, etc.)
    # =========================================================================
    JurisdictionRates(
        "Miami", "Miami-Dade", "FPL",
        Decimal("0.10"), Decimal("0.06"),
        ordinance_reference="City of Miami Code Sec. 42-71; Miami-Dade Appx C Franchises",
        notes="Historical 10% PST + 6% franchise — verify against current city code.",
    ),
    JurisdictionRates(
        "Miami Beach", "Miami-Dade", "FPL",
        Decimal("0.10"), Decimal("0.06"),
        ordinance_reference="City of Miami Beach Code Ch. 102",
    ),
    JurisdictionRates(
        "Hialeah", "Miami-Dade", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Miami Gardens", "Miami-Dade", "FPL",
        Decimal("0.10"), Decimal("0.06"),
        ordinance_reference="Miami Gardens Revenue Manual FY 2011-2012",
    ),
    JurisdictionRates(
        "Palmetto Bay", "Miami-Dade", "FPL",
        Decimal("0.10"), Decimal("0.06"),
        ordinance_reference="palmettobay-fl.gov/1241/FPL-Franchise-Fees",
    ),
    JurisdictionRates(
        "Unincorporated Miami-Dade", "Miami-Dade", "FPL",
        Decimal("0"), Decimal("0.06"),
        ordinance_reference="Miami-Dade County Appx C — 6% franchise applies countywide",
        notes="Miami-Dade County collects franchise fee even in unincorporated areas.",
    ),
    JurisdictionRates(
        "Fort Lauderdale", "Broward", "FPL",
        Decimal("0.10"), Decimal("0.06"),
        ordinance_reference="City of Fort Lauderdale Code",
    ),
    JurisdictionRates(
        "Hollywood", "Broward", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Pembroke Pines", "Broward", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Hallandale Beach", "Broward", "FPL",
        Decimal("0.10"), Decimal("0.059"),
        ordinance_reference="Hallandale Beach budget documents",
        notes="FPL passes 5.9% franchise directly to bill (confirmed).",
    ),
    JurisdictionRates(
        "Coral Springs", "Broward", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Unincorporated Broward", "Broward", "FPL",
        Decimal("0"), Decimal("0.06"),
        notes="Broward County franchise applies countywide.",
    ),
    JurisdictionRates(
        "West Palm Beach", "Palm Beach", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Boca Raton", "Palm Beach", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Boynton Beach", "Palm Beach", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Delray Beach", "Palm Beach", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Jupiter", "Palm Beach", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Unincorporated Palm Beach", "Palm Beach", "FPL",
        Decimal("0"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Port St. Lucie", "St. Lucie", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Fort Pierce", "St. Lucie", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Sarasota", "Sarasota", "FPL",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Cape Coral", "Lee", "FPL",
        Decimal("0.07"), Decimal("0.06"),
        notes="Cape Coral historical PST at 7%; verify current ordinance.",
    ),
    JurisdictionRates(
        "Naples", "Collier", "FPL",
        Decimal("0.05"), Decimal("0.06"),
    ),
    # =========================================================================
    # FPL NW Florida (former Gulf Power territory)
    # =========================================================================
    JurisdictionRates(
        "Pensacola", "Escambia", "FPL",
        Decimal("0.10"), Decimal("0.06"),
        notes="Former Gulf Power territory — use rate_schedule='RS-1-NWFL'.",
    ),
    JurisdictionRates(
        "Panama City", "Bay", "FPL",
        Decimal("0.10"), Decimal("0.06"),
        notes="Former Gulf Power territory.",
    ),
    # =========================================================================
    # Duke Energy Florida — Central / North FL
    # =========================================================================
    JurisdictionRates(
        "St. Petersburg", "Pinellas", "DUKE",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Clearwater", "Pinellas", "DUKE",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Largo", "Pinellas", "DUKE",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Unincorporated Pinellas", "Pinellas", "DUKE",
        Decimal("0"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Ocala", "Marion", "DUKE",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Winter Park", "Orange", "DUKE",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Apopka", "Orange", "DUKE",
        Decimal("0.07"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Lakeland", "Polk", "DUKE",
        Decimal("0"), Decimal("0"),
        notes="Lakeland is served by Lakeland Electric (municipal utility), NOT Duke. Listed for completeness.",
    ),
    # =========================================================================
    # TECO — Tampa Bay
    # =========================================================================
    JurisdictionRates(
        "Tampa", "Hillsborough", "TECO",
        Decimal("0.10"), Decimal("0.06"),
        ordinance_reference="City of Tampa Code Ch. 24",
    ),
    JurisdictionRates(
        "Plant City", "Hillsborough", "TECO",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Temple Terrace", "Hillsborough", "TECO",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Unincorporated Hillsborough", "Hillsborough", "TECO",
        Decimal("0.07"), Decimal("0.055"),
        notes="Hillsborough charter imposes PST in unincorporated areas.",
    ),
    # =========================================================================
    # FPU — scattered service areas (Fernandina Beach, Marianna, Indiantown)
    # =========================================================================
    JurisdictionRates(
        "Fernandina Beach", "Nassau", "FPU",
        Decimal("0.10"), Decimal("0.06"),
    ),
    JurisdictionRates(
        "Marianna", "Jackson", "FPU",
        Decimal("0.10"), Decimal("0.06"),
    ),
)


# ---------------------------------------------------------------------------
# Indexes for O(1) lookup
# ---------------------------------------------------------------------------

_BY_KEY: dict[tuple[str, str, str], JurisdictionRates] = {
    (r.utility.upper(), r.jurisdiction.casefold(), r.county.casefold()): r
    for r in _SEED
}

# Fallback index by (utility, county) for unincorporated areas when a specific
# city is not listed.
_BY_COUNTY: dict[tuple[str, str], JurisdictionRates] = {
    (r.utility.upper(), r.county.casefold()): r
    for r in _SEED
    if r.jurisdiction.casefold().startswith("unincorporated")
}


# ---------------------------------------------------------------------------
# Lookup API
# ---------------------------------------------------------------------------


def lookup(
    utility: str,
    jurisdiction: str,
    county: str,
) -> JurisdictionRates | None:
    """Return the rate pair for this utility/jurisdiction/county, or None.

    Caller must handle ``None`` — typically by refusing to produce an audit
    report, or by prompting the user for manual rates.
    """
    key = (utility.upper(), jurisdiction.casefold(), county.casefold())
    return _BY_KEY.get(key)


def lookup_with_county_fallback(
    utility: str,
    jurisdiction: str,
    county: str,
) -> JurisdictionRates | None:
    """Like :func:`lookup` but falls back to the unincorporated-county entry
    if the specific city is not registered."""
    direct = lookup(utility, jurisdiction, county)
    if direct is not None:
        return direct
    return _BY_COUNTY.get((utility.upper(), county.casefold()))


def all_jurisdictions() -> tuple[JurisdictionRates, ...]:
    """Return every seeded jurisdiction (for diagnostics / validation)."""
    return _SEED


def unverified_jurisdictions() -> tuple[JurisdictionRates, ...]:
    """Return jurisdictions whose rates have not been verified against a
    current ordinance. Used to gate audit-report generation."""
    return tuple(r for r in _SEED if not r.verified)


def verified_jurisdictions() -> tuple[JurisdictionRates, ...]:
    """Return only jurisdictions with ``verified=True``. For production
    forensic reports, restrict tax/fee lookups to this set."""
    return tuple(r for r in _SEED if r.verified)


class UnverifiedJurisdictionError(RuntimeError):
    """Raised when an audit attempts to use rates from an unverified
    jurisdiction. Callers should catch this and surface a clear message
    to the user explaining that the rates need to be confirmed."""


def require_verified(rates: JurisdictionRates) -> JurisdictionRates:
    """Gate rates behind the ``verified`` flag.

    Raises :class:`UnverifiedJurisdictionError` if the rates are not
    marked verified. Use in audit-report generation paths where
    penny-accurate taxes are required.
    """
    if not rates.verified:
        raise UnverifiedJurisdictionError(
            f"Jurisdiction {rates.jurisdiction!r} ({rates.county} / "
            f"{rates.utility}) rates are not verified: PST="
            f"{rates.municipal_utility_tax}, Franchise="
            f"{rates.franchise_fee}. Re-check against current "
            f"ordinance before producing a customer-facing audit report."
        )
    return rates
