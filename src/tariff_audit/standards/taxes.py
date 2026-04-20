"""Florida tax and fee layer applied on top of tariff-regulated charges.

A full electric bill is the sum of:

1. The tariff-regulated subtotal (computed by ``engine.calculator``)
2. Florida Gross Receipts Tax (state-level, grossed-up onto the bill)
3. Municipal Public Service Tax (city/county, up to 10%, address-dependent)
4. Franchise Fee (city-specific, per franchise agreement, 0–6% typical)
5. Sales and Use Tax — **exempt for residential**, 4.35% otherwise
6. PSC Regulatory Assessment Fee (for IOUs, ~0.072% — usually absorbed, but
   may appear as a pass-through line item on some utilities' bills)

This module provides the canonical rates and a ``apply_florida_taxes``
helper that composes them into a ``TaxApplication`` result.

Authoritative citations:

- **F.S. 203.01** — Gross Receipts Tax on utility services. Rate: 2.5% of
  gross receipts. Because the tax is typically grossed up onto the customer
  bill (utility collects tax on the tax-inclusive price), the effective
  multiplier on the pre-tax subtotal is ``1 / (1 - 0.025) = 1.025641...``.
- **F.S. 212.08(7)(j)** — Electricity sold for use in residential households
  is **exempt** from Florida sales and use tax.
- **F.S. 166.231 / 166.232** — Authorizes municipalities and charter counties
  to levy a Public Service Tax on electric service of up to 10%.
- **FAC 25-6.0131** — PSC Regulatory Assessment Fee on IOUs.

Sales tax reference: ``Fla. Admin. Code 12A-1.053(1)(a)``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

# ---------------------------------------------------------------------------
# Florida Gross Receipts Tax (F.S. 203.01)
# ---------------------------------------------------------------------------

#: Statutory GRT rate on electric gross receipts.
FL_GROSS_RECEIPTS_TAX_STATUTORY_RATE: Decimal = Decimal("0.025")

#: Grossed-up multiplier: when the utility adds the tax on top of the
#: pre-tax subtotal and then the tax is computed on the tax-inclusive price,
#: the effective factor to apply to the pre-tax subtotal is
#: ``1 / (1 - 0.025) ≈ 1.025641``.
FL_GROSS_RECEIPTS_TAX_GROSSUP_MULTIPLIER: Decimal = Decimal("1.025641")

#: The incremental percentage-of-subtotal added to a bill to recover the
#: grossed-up GRT. Equals multiplier minus 1.
FL_GROSS_RECEIPTS_TAX_EFFECTIVE_RATE: Decimal = Decimal("0.025641")


# ---------------------------------------------------------------------------
# Florida Sales and Use Tax (F.S. 212.05 / 212.08(7)(j))
# ---------------------------------------------------------------------------

#: Florida state sales tax rate on non-residential electricity per F.S. 212.05.
#: (Higher than the general 6% rate; electricity has its own chapter-specific
#: treatment.) Residential sales are exempt per 212.08(7)(j).
FL_NON_RESIDENTIAL_SALES_TAX_RATE: Decimal = Decimal("0.0435")


# ---------------------------------------------------------------------------
# PSC Regulatory Assessment Fee (FAC 25-6.0131)
# ---------------------------------------------------------------------------

#: Regulatory assessment fee levied on IOU gross operating revenues.
#: Currently ~0.072% (verify annually at
#: ``psc.state.fl.us`` — this is statutorily variable).
FL_PSC_REGULATORY_ASSESSMENT_FEE_IOU: Decimal = Decimal("0.00072")


# ---------------------------------------------------------------------------
# Municipal Public Service Tax — ceiling (F.S. 166.231)
# ---------------------------------------------------------------------------

#: Maximum municipal public service tax rate authorized under F.S. 166.231.
#: Actual rate is jurisdiction-dependent — look up via
#: :mod:`tariff_audit.standards.jurisdictions`.
MUNICIPAL_UTILITY_TAX_STATUTORY_MAX: Decimal = Decimal("0.10")


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TaxApplication:
    """Result of applying Florida tax layer to a tariff subtotal."""

    tariff_subtotal: Decimal
    gross_receipts_tax: Decimal
    municipal_utility_tax: Decimal
    franchise_fee: Decimal
    sales_tax: Decimal
    psc_regulatory_assessment_fee: Decimal
    total: Decimal

    def pretty(self) -> str:  # pragma: no cover — diagnostic
        return (
            f"Tariff subtotal:              ${self.tariff_subtotal}\n"
            f"+ Gross Receipts Tax (GRT):   ${self.gross_receipts_tax}\n"
            f"+ Municipal Utility Tax:      ${self.municipal_utility_tax}\n"
            f"+ Franchise Fee:              ${self.franchise_fee}\n"
            f"+ Sales Tax:                  ${self.sales_tax}\n"
            f"+ PSC Regulatory Fee:         ${self.psc_regulatory_assessment_fee}\n"
            f"= Total:                      ${self.total}"
        )


# ---------------------------------------------------------------------------
# Application logic
# ---------------------------------------------------------------------------

_CENT = Decimal("0.01")


def _round_cents(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def apply_florida_taxes(
    tariff_subtotal: Decimal,
    *,
    is_residential: bool,
    municipal_utility_tax_rate: Decimal = Decimal("0"),
    franchise_fee_rate: Decimal = Decimal("0"),
    include_psc_regulatory_fee: bool = False,
) -> TaxApplication:
    """Compose the full Florida tax layer onto a pre-tax tariff subtotal.

    The stacking order follows the F.S. 203.01 + 212.05 + 166.231 framework:

    1. Gross Receipts Tax is computed on the pre-tax subtotal (grossed-up
       effective rate of ~2.5641%).
    2. Municipal Utility Tax is computed on the pre-tax subtotal
       (jurisdiction-dependent rate, 0–10%). It is NOT added to the GRT base
       when separately itemized, per Fla. Admin. Code 12A-1.022.
    3. Franchise Fee is computed on the pre-tax subtotal (utility-and-
       jurisdiction-dependent, 0–6% typical).
    4. Sales Tax: **zero for residential** (F.S. 212.08(7)(j)). For
       non-residential, 4.35% of the pre-tax subtotal.
    5. PSC Regulatory Assessment Fee: normally absorbed by the utility, but
       when passed through, 0.072% of the pre-tax subtotal.

    Each component is rounded to the cent independently.

    Parameters
    ----------
    tariff_subtotal : Decimal
        Output of ``engine.calculator.calculate_bill(...).subtotal_tariff``.
    is_residential : bool
        True → sales tax is zero (F.S. 212.08(7)(j) exemption).
    municipal_utility_tax_rate : Decimal
        Fractional rate (0.0–0.10) for the service address's city/county.
        Look up via :mod:`tariff_audit.standards.jurisdictions`.
    franchise_fee_rate : Decimal
        Fractional rate (0.0–0.06 typical) for the service address.
    include_psc_regulatory_fee : bool
        True if the specific utility passes through the PSC RAF as a line
        item (rare — most utilities absorb this).
    """
    subtotal = Decimal(tariff_subtotal)

    grt = _round_cents(subtotal * FL_GROSS_RECEIPTS_TAX_EFFECTIVE_RATE)
    mut = _round_cents(subtotal * Decimal(municipal_utility_tax_rate))
    franchise = _round_cents(subtotal * Decimal(franchise_fee_rate))
    sales = (
        Decimal("0.00")
        if is_residential
        else _round_cents(subtotal * FL_NON_RESIDENTIAL_SALES_TAX_RATE)
    )
    psc = (
        _round_cents(subtotal * FL_PSC_REGULATORY_ASSESSMENT_FEE_IOU)
        if include_psc_regulatory_fee
        else Decimal("0.00")
    )

    total = _round_cents(subtotal + grt + mut + franchise + sales + psc)

    return TaxApplication(
        tariff_subtotal=subtotal,
        gross_receipts_tax=grt,
        municipal_utility_tax=mut,
        franchise_fee=franchise,
        sales_tax=sales,
        psc_regulatory_assessment_fee=psc,
        total=total,
    )
