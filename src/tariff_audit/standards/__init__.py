"""Regulatory and statutory standards governing Florida electric utility billing.

This package encodes the rules, statutes, and mechanics that dictate how a
Florida electric bill must be constructed — independent of any individual
utility's tariff. A correct "what the bill should be" answer requires
layering these standards on top of the tariff-regulated charges.

Modules:

- :mod:`fac_25_6` — Catalog of Florida Administrative Code Chapter 25-6
  (Electric Service by Electric Public Utilities) rules, with citations and
  audit-relevance classifications.
- :mod:`statutes` — Florida Statutes references governing electric service,
  taxation, and customer rights.
- :mod:`taxes` — Florida Gross Receipts Tax, residential sales tax exemption,
  municipal public service tax, franchise fees, PSC regulatory assessment.
- :mod:`billing_mechanics` — Hard numbers and helper functions for the
  mechanical rules: back-billing cutoff, meter tolerance, proration across
  mid-period rate changes, net-metering credit carryover.
- :mod:`jurisdictions` — Lookup data for city/county-specific tax and
  franchise rates (needed to compute total bill from tariff subtotal).
"""

from tariff_audit.standards.billing_mechanics import (
    ACTUAL_METER_READ_REQUIRED_EVERY_MONTHS,
    MAX_BACKBILLING_MONTHS,
    METER_ACCURACY_LOWER_BOUND,
    METER_ACCURACY_UPPER_BOUND,
    METER_TOLERANCE_PCT,
    NET_METERING_CREDIT_CARRYOVER_MONTHS,
    OVER_REGISTERING_METER_MAX_REFUND_MONTHS,
    back_billing_cutoff_date,
)
from tariff_audit.standards.fac_25_6 import FAC_25_6_RULES, FacRule
from tariff_audit.standards.taxes import (
    FL_GROSS_RECEIPTS_TAX_EFFECTIVE_RATE,
    FL_GROSS_RECEIPTS_TAX_GROSSUP_MULTIPLIER,
    FL_GROSS_RECEIPTS_TAX_STATUTORY_RATE,
    FL_NON_RESIDENTIAL_SALES_TAX_RATE,
    FL_PSC_REGULATORY_ASSESSMENT_FEE_IOU,
    apply_florida_taxes,
)

__all__ = [
    "ACTUAL_METER_READ_REQUIRED_EVERY_MONTHS",
    "FAC_25_6_RULES",
    "FL_GROSS_RECEIPTS_TAX_EFFECTIVE_RATE",
    "FL_GROSS_RECEIPTS_TAX_GROSSUP_MULTIPLIER",
    "FL_GROSS_RECEIPTS_TAX_STATUTORY_RATE",
    "FL_NON_RESIDENTIAL_SALES_TAX_RATE",
    "FL_PSC_REGULATORY_ASSESSMENT_FEE_IOU",
    "FacRule",
    "MAX_BACKBILLING_MONTHS",
    "METER_ACCURACY_LOWER_BOUND",
    "METER_ACCURACY_UPPER_BOUND",
    "METER_TOLERANCE_PCT",
    "NET_METERING_CREDIT_CARRYOVER_MONTHS",
    "OVER_REGISTERING_METER_MAX_REFUND_MONTHS",
    "apply_florida_taxes",
    "back_billing_cutoff_date",
]
