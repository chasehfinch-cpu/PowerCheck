"""Per-utility bill layout guides for manual data entry.

The goal of this module is practical: given that automatic PDF parsing is
brittle and highly utility-specific, the primary end-user flow is manual
entry of values from their bill. These guides tell the user (or the UI)
exactly where on each utility's bill to find every ``ParsedBill`` field.

Each :class:`BillLayoutGuide` catalogs:

- Utility identity markers (logo text, boilerplate phrases) for detection
- Field-by-field location guides (which section, what the label reads)
- Common layout gotchas (bundled clauses, tiered displays, etc.)
- Links to the utility's public "How to read your bill" reference

Sources:

- FPL: ``fpl.com/content/dam/fplgp/us/en/northwest/pdf/rates/how-to-read-your-bill.pdf``
- Duke Energy: ``duke-energy.com/customer-service/billing-and-payment``
- TECO: ``tampaelectric.com/residential/billing/understandingyourbill/``
- FPU: consolidated tariff + sample bills retained in ``.tariff_research/``
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BillFieldLocation:
    """Where on a utility's bill a particular :class:`ParsedBill` field lives."""

    field_name: str  # matches ParsedBill attribute name
    bill_section: str  # e.g. "Bill Summary", "Bill Details", "Meter Summary"
    label_on_bill: str  # exact or near-exact text that precedes the value
    page: int | None = None  # bill page number when known
    notes: str = ""


@dataclass(frozen=True)
class BillLayoutGuide:
    """Complete guide to one utility's residential bill layout."""

    utility: str
    display_name: str
    detection_markers: tuple[str, ...]  # strings that uniquely identify this utility
    layout_reference_url: str
    locations: tuple[BillFieldLocation, ...]
    structural_notes: str = ""
    bundled_clauses: tuple[str, ...] = field(default_factory=tuple)

    def locate(self, field_name: str) -> BillFieldLocation | None:
        """Return the location entry for a field, or None if not documented."""
        for loc in self.locations:
            if loc.field_name == field_name:
                return loc
        return None


# ---------------------------------------------------------------------------
# FPL — peninsular Florida AND NW Florida (former Gulf Power)
# ---------------------------------------------------------------------------

FPL_LAYOUT = BillLayoutGuide(
    utility="FPL",
    display_name="Florida Power & Light",
    detection_markers=(
        "Florida Power & Light",
        "FPL.com",
        "FPL NW",
        "Report Power Outages: 800-468-8243",
    ),
    layout_reference_url=(
        "https://www.fpl.com/content/dam/fplgp/us/en/northwest/pdf/rates/"
        "how-to-read-your-bill.pdf"
    ),
    locations=(
        BillFieldLocation("account_number", "Bill header", "Account Number", 1,
                          "Formatted as XX-XXXXX XXXXX"),
        BillFieldLocation("service_address", "Bill header", "Service Address", 1),
        BillFieldLocation("statement_date", "Bill header", "Statement Date", 1),
        BillFieldLocation("billing_period_start", "Bill header / Energy Use Comparison",
                          "Service period", 1,
                          "Format: 'Service period: Jun 3, 2025 to Jul 1, 2025'"),
        BillFieldLocation("billing_period_end", "Bill header / Energy Use Comparison",
                          "Service to", 2),
        BillFieldLocation("billing_days", "Energy Use Comparison", "Service days", 2),
        BillFieldLocation("meter_read_date", "Meter Summary", "Next meter reading date", 2),
        BillFieldLocation("rate_schedule", "Bill Details / New Charges", "Rate:", 2,
                          "Values: RS-1 (peninsular), RS-1 NWFL (former Gulf territory)"),
        BillFieldLocation("kwh_consumed", "Meter Summary / Energy Use Comparison",
                          "kWh used", 2),
        BillFieldLocation("previous_meter_reading", "Meter Summary",
                          "(number before the minus sign in 'Current - Previous = Usage')", 2),
        BillFieldLocation("current_meter_reading", "Meter Summary",
                          "(number before the minus sign, left-most)", 2),
        BillFieldLocation("base_charge", "Bill Details / New Charges", "Base charge", 2),
        BillFieldLocation("non_fuel_energy_charge", "Bill Details / New Charges", "Non-fuel", 2,
                          "Includes energy + conservation + capacity + environmental + "
                          "storm protection + transition rider, bundled per FPL's display."),
        BillFieldLocation("fuel_charge", "Bill Details / New Charges", "Fuel charge", 2),
        BillFieldLocation("electric_service_subtotal", "Bill Details / New Charges",
                          "Electric service charges", 2),
        BillFieldLocation("gross_receipts_tax", "Bill Details / Taxes and charges",
                          "Gross receipts tax (State tax)", 2),
        BillFieldLocation("franchise_fee", "Bill Details / Taxes and charges",
                          "Franchise fee (Reqd local fee)", 2),
        BillFieldLocation("utility_tax", "Bill Details / Taxes and charges",
                          "Utility tax (Local tax)", 2),
        BillFieldLocation("psc_regulatory_fee", "Bill Details / Taxes and charges",
                          "Regulatory fee (State fee)", 2),
        BillFieldLocation("taxes_and_fees_subtotal", "Bill Details / Taxes and charges",
                          "Taxes and charges", 2),
        BillFieldLocation("prior_balance", "Bill Summary", "Balance before new charges", 1),
        BillFieldLocation("payment_received", "Bill Summary", "Payment(s) received", 1,
                          "Shown as a negative number on the bill."),
        BillFieldLocation("current_charges_total", "Bill Details / Totals",
                          "Total new charges", 2),
        BillFieldLocation("total_amount_due", "Bill header / Bill Summary",
                          "Total amount you owe", 1,
                          "Also appears as 'TOTAL AMOUNT YOU OWE' in header."),
    ),
    structural_notes=(
        "FPL bundles the per-kWh tariff clauses (conservation, capacity, "
        "environmental, storm protection, transition rider) into a single "
        "'Non-fuel' line. To verify individual clause rates, multiply kWh × "
        "published ¢/kWh rate and sum — the total should equal the printed "
        "'Non-fuel' amount minus base charge. Fuel is separate. Tax layer is "
        "always itemized (GRT, franchise, utility tax, PSC RAF)."
    ),
    bundled_clauses=(
        "Non-fuel includes: Base energy + Conservation + Capacity + "
        "Environmental + Storm Protection + Transition Rider",
    ),
)


# ---------------------------------------------------------------------------
# Duke Energy Florida
# ---------------------------------------------------------------------------

DUKE_LAYOUT = BillLayoutGuide(
    utility="DUKE",
    display_name="Duke Energy Florida",
    detection_markers=(
        "Duke Energy Florida",
        "Duke Energy",
        "duke-energy.com",
        "duke-energy.com/FL",
    ),
    layout_reference_url="https://www.duke-energy.com/customer-service/billing-and-payment",
    locations=(
        BillFieldLocation("account_number", "Bill header", "Account Number"),
        BillFieldLocation("service_address", "Bill header", "Service address"),
        BillFieldLocation("statement_date", "Bill header", "Bill date"),
        BillFieldLocation("billing_period_start", "Details of Your Charges",
                          "Service from", None,
                          "Typically shown as 'For service from MM/DD/YYYY to MM/DD/YYYY'"),
        BillFieldLocation("billing_period_end", "Details of Your Charges", "to (second date)"),
        BillFieldLocation("billing_days", "Details of Your Charges", "Days billed"),
        BillFieldLocation("meter_read_date", "Meter reading details", "Read date"),
        BillFieldLocation("rate_schedule", "Rate information", "Rate schedule",
                          None, "Common values: RS-1 (Residential Service)"),
        BillFieldLocation("kwh_consumed", "Meter reading details",
                          "kWh (Usage column)"),
        BillFieldLocation("base_charge", "Details of Your Charges",
                          "Basic Customer Charge"),
        BillFieldLocation("energy_charge", "Details of Your Charges",
                          "Energy Charge"),
        BillFieldLocation("fuel_charge", "Details of Your Charges",
                          "Fuel Charge / Fuel Cost Recovery"),
        BillFieldLocation("conservation_charge", "Details of Your Charges",
                          "Energy Conservation Cost Recovery Charge"),
        BillFieldLocation("capacity_charge", "Details of Your Charges",
                          "Capacity Cost Recovery Charge"),
        BillFieldLocation("environmental_charge", "Details of Your Charges",
                          "Environmental Cost Recovery"),
        BillFieldLocation("storm_protection_charge", "Details of Your Charges",
                          "Storm Protection Charge"),
        BillFieldLocation("storm_restoration_charge", "Details of Your Charges",
                          "Storm Cost Recovery",
                          notes="Line item through February 2026 only; "
                          "removed effective March 2026 per Duke rate filing."),
        BillFieldLocation("gross_receipts_tax", "Taxes and Fees",
                          "Gross Receipts Tax"),
        BillFieldLocation("franchise_fee", "Taxes and Fees", "Franchise Fee"),
        BillFieldLocation("utility_tax", "Taxes and Fees",
                          "Local/Municipal Tax"),
        BillFieldLocation("total_amount_due", "Bill header", "Amount due"),
    ),
    structural_notes=(
        "Duke itemizes EVERY clause separately (unlike FPL which bundles "
        "into 'Non-fuel'). This makes per-clause verification easier. "
        "**Important 2026 event**: Storm Cost Recovery drops off bills "
        "effective March 1, 2026 — a ~$44/1,000 kWh reduction. Bills for "
        "Jan/Feb 2026 vs Mar 2026+ use different effective tariffs."
    ),
    bundled_clauses=(),
)


# ---------------------------------------------------------------------------
# TECO — Tampa Electric
# ---------------------------------------------------------------------------

TECO_LAYOUT = BillLayoutGuide(
    utility="TECO",
    display_name="Tampa Electric",
    detection_markers=(
        "Tampa Electric",
        "TampaElectric.com",
        "TECO",
        "tecoenergy.com",
    ),
    layout_reference_url="https://www.tampaelectric.com/residential/billing/understandingyourbill/",
    locations=(
        BillFieldLocation("account_number", "Bill header", "Account number"),
        BillFieldLocation("service_address", "Bill header", "Service address"),
        BillFieldLocation("statement_date", "Bill header", "Bill date"),
        BillFieldLocation("billing_period_start", "Meter Reading Information",
                          "From (service period)"),
        BillFieldLocation("billing_period_end", "Meter Reading Information", "To"),
        BillFieldLocation("billing_days", "Bill Details", "Days"),
        BillFieldLocation("rate_schedule", "Bill Details", "Rate schedule", None,
                          "Common values: RS (Residential Standard), RSVP-1 (Variable Pricing)"),
        BillFieldLocation("kwh_consumed", "Meter Reading Information", "kWh usage"),
        BillFieldLocation("base_charge", "Bill Details", "Basic Service Charge",
                          notes="Published as 'cents per day' × number of days; "
                                "for 30 days = ~$13.50 on the RS schedule."),
        BillFieldLocation("energy_charge", "Bill Details", "Energy charge",
                          notes="Includes bundled conservation + environmental + "
                                "capacity recovery (0.621 ¢/kWh embedded in the "
                                "9.569 ¢/kWh tier-1 rate as of 2026)."),
        BillFieldLocation("fuel_charge", "Bill Details", "Fuel charge"),
        BillFieldLocation("storm_protection_charge", "Bill Details",
                          "Storm Protection Charge"),
        BillFieldLocation("storm_restoration_charge", "Bill Details", "Storm Surcharge",
                          notes="Through August 31, 2026 only; drops off in Sept 2026."),
        BillFieldLocation("gross_receipts_tax", "Taxes and Fees", "Gross Receipts Tax"),
        BillFieldLocation("franchise_fee", "Taxes and Fees", "Franchise Fee"),
        BillFieldLocation("utility_tax", "Taxes and Fees", "Municipal Public Service Tax"),
        BillFieldLocation("total_amount_due", "Bill header", "Total amount due"),
    ),
    structural_notes=(
        "TECO's Basic Service Charge is published DAILY (e.g. $0.45/day in 2026). "
        "Multiply by number of days in the billing period to verify. Energy "
        "charge is bundled — includes 0.621 ¢/kWh of conservation + capacity + "
        "environmental recovery baked in; those don't appear as separate line "
        "items like Duke's bills. The Clean Energy Transition Mechanism "
        "(0.406 ¢/kWh in 2026) appears as its own line item."
    ),
    bundled_clauses=(
        "Energy charge includes: Base energy + Conservation + Capacity + "
        "Environmental (total 0.621 ¢/kWh embedded)",
    ),
)


# ---------------------------------------------------------------------------
# FPU — Florida Public Utilities
# ---------------------------------------------------------------------------

FPU_LAYOUT = BillLayoutGuide(
    utility="FPU",
    display_name="Florida Public Utilities",
    detection_markers=(
        "Florida Public Utilities",
        "FPUC",
        "fpuc.com",
        "Chesapeake Utilities",  # parent company sometimes appears
    ),
    layout_reference_url="https://fpuc.com/about/legal-notices-and-tariffs/",
    locations=(
        BillFieldLocation("account_number", "Bill header", "Account Number"),
        BillFieldLocation("service_address", "Bill header", "Service Address"),
        BillFieldLocation("statement_date", "Bill header", "Bill Date"),
        BillFieldLocation("billing_period_start", "Service Period", "From"),
        BillFieldLocation("billing_period_end", "Service Period", "To"),
        BillFieldLocation("billing_days", "Service Period", "Days"),
        BillFieldLocation("rate_schedule", "Bill Details", "Rate Schedule", None,
                          "Common value: RS (Residential Service)"),
        BillFieldLocation("kwh_consumed", "Meter Information", "kWh Used"),
        BillFieldLocation("base_charge", "Bill Details", "Customer Facilities Charge"),
        BillFieldLocation("energy_charge", "Bill Details", "Base Energy Charge"),
        BillFieldLocation("fuel_charge", "Bill Details",
                          "Total Purchased Power Cost Recovery",
                          notes="This one line combines fuel + capacity + environmental."),
        BillFieldLocation("conservation_charge", "Bill Details",
                          "Energy Conservation Cost Recovery"),
        BillFieldLocation("gross_receipts_tax", "Taxes and Fees",
                          "Gross Receipts Tax"),
        BillFieldLocation("franchise_fee", "Taxes and Fees", "Franchise Fee Adjustment"),
        BillFieldLocation("utility_tax", "Taxes and Fees",
                          "Municipal Public Service Tax"),
        BillFieldLocation("total_amount_due", "Bill header", "Amount Due"),
    ),
    structural_notes=(
        "FPU's bill structure differs materially from the big three IOUs. "
        "It uses a 'Customer Facilities Charge' instead of 'Base Charge' "
        "at a much higher $24.40/month. Purchased Power Cost Recovery "
        "bundles fuel + capacity + environmental into a single line "
        "(tiered: 8.820 ¢/kWh ≤1,000, 10.070 ¢/kWh >1,000 in 2026). "
        "No separate storm protection or transition rider line items."
    ),
    bundled_clauses=(
        "Purchased Power Cost Recovery = Fuel + Capacity + Environmental",
    ),
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_LAYOUTS: dict[str, BillLayoutGuide] = {
    "FPL": FPL_LAYOUT,
    "DUKE": DUKE_LAYOUT,
    "TECO": TECO_LAYOUT,
    "FPU": FPU_LAYOUT,
}


def get_layout(utility: str) -> BillLayoutGuide:
    """Return the bill layout guide for a utility.

    Raises ``KeyError`` if the utility is not one of the Florida IOUs.
    """
    key = utility.upper()
    if key not in _LAYOUTS:
        raise KeyError(
            f"No bill layout guide for utility {utility!r}. Known: "
            f"{sorted(_LAYOUTS)}"
        )
    return _LAYOUTS[key]


def all_layouts() -> tuple[BillLayoutGuide, ...]:
    """Return all registered utility layout guides."""
    return tuple(_LAYOUTS.values())


def detect_layout(text: str) -> BillLayoutGuide | None:
    """Identify which utility's bill the given text came from, via detection markers.

    Returns the first guide whose markers appear in the text, or ``None`` if
    no utility matches. Prefer this over calling full PDF parsers when all
    you need is "which firm billed the customer?".
    """
    for guide in _LAYOUTS.values():
        for marker in guide.detection_markers:
            if marker in text:
                return guide
    return None
