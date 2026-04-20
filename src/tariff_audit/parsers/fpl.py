"""Parser for Florida Power & Light (FPL) residential PDF bills.

Works on both peninsular FPL and NW Florida (former Gulf Power) bills —
both use the same bill layout post-2021 rate agreement. The parser extracts
every line item FPL prints on the bill so the auditor can isolate the
tariff-regulated portion from taxes and non-tariff items.

**Extraction strategy**: regex patterns anchored on FPL's literal line
labels. FPL's bill layout has been stable since the 2021 rate agreement
reorganization; parsers should be resilient to whitespace variation from
``pdfplumber`` column flattening.

**Reference layout**: the FPL "How to read your bill" PDF
(``fpl.com/content/dam/fplgp/us/en/northwest/pdf/rates/how-to-read-your-bill.pdf``),
retained at ``.tariff_research/fpl_howto_bill.txt`` — documents every
field and its position on the bill.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal

from tariff_audit.parsers.base import BillParser, ParsedBill

# ---------------------------------------------------------------------------
# Regex patterns anchored on FPL's literal line labels
# ---------------------------------------------------------------------------
# Decimal pattern — handles amounts like 9.61, 115.39, 180.34, 0.1416, 26.77
_DEC = r"(-?\d+(?:,\d{3})*\.\d+|-?\d+\.\d+)"

# Utility detection
_FPL_MARKERS = (
    "Florida Power & Light",
    "FPL.com",
    "fpl.com",
    "Report Power Outages: 800-468-8243",
)

# Date formats seen on FPL bills: "Jul 1, 2025" and "Jul 22, 2025"
_DATE_PATTERN = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{1,2}),?\s+(\d{4})"


def _parse_fpl_date(text: str) -> date | None:
    m = re.search(_DATE_PATTERN, text)
    if not m:
        return None
    month_abbr, day, year = m.group(1), int(m.group(2)), int(m.group(3))
    try:
        return datetime.strptime(f"{month_abbr} {day} {year}", "%b %d %Y").date()
    except ValueError:
        return None


def _find_decimal(text: str, label: str) -> Decimal | None:
    """Find a decimal amount immediately following a literal label.

    Uses a tolerant match that allows whitespace and line breaks between
    label and number — FPL's PDF extraction via pdfplumber often has
    whitespace artifacts from column flattening.
    """
    pattern = re.escape(label) + r"[\s:]*" + _DEC
    m = re.search(pattern, text)
    if not m:
        return None
    return Decimal(m.group(1).replace(",", ""))


def _find_integer(text: str, label: str) -> int | None:
    pattern = re.escape(label) + r"[\s:]*(\d{1,7})(?:\s|$)"
    m = re.search(pattern, text)
    return int(m.group(1)) if m else None


class FPLBillParser(BillParser):
    """Extract structured data from FPL residential PDF bill text."""

    name = "fpl"

    def can_parse(self, text: str) -> bool:
        hits = sum(1 for marker in _FPL_MARKERS if marker in text)
        return hits >= 1

    def parse(self, text: str) -> ParsedBill:  # noqa: C901 — wide label coverage
        # Rate schedule — "Rate: RS-1 RESIDENTIAL SERVICE"
        rate_match = re.search(r"Rate:\s*([A-Z]+-?\d+[A-Z]*)", text)
        rate_schedule = rate_match.group(1) if rate_match else "RS-1"

        # Service period — "Service to Jul 1, 2025 Jun 2, 2025 Jul 2, 2024"
        # The two dates after "Service to" are current-period end + prior-period end
        # (last year's date is in a third group, ignored here).
        period_match = re.search(
            r"Service\s+to\s+"
            r"(?P<end>" + _DATE_PATTERN + r")"
            r"\s+"
            r"(?P<start>" + _DATE_PATTERN + r")",
            text,
        )
        if period_match:
            billing_end = _parse_fpl_date(period_match.group("end"))
            billing_start = _parse_fpl_date(period_match.group("start"))
        else:
            billing_end = billing_start = None

        # Service days — "Service days 29"
        billing_days = _find_integer(text, "Service days") or 0
        if billing_start is None and billing_end is not None and billing_days:
            # Reconstruct start from end + billing_days
            from datetime import timedelta
            billing_start = billing_end - timedelta(days=billing_days - 1)

        # kWh used — "kWh used 1079" (may appear twice; take first)
        kwh = _find_integer(text, "kWh used") or 0

        # Account number — "Account Number: 2112133485-56178 82940"
        acct_match = re.search(
            r"Account\s+Number:?\s*([\d\-\s]{6,30})",
            text,
        )
        account = acct_match.group(1).strip() if acct_match else None

        # Tariff line items — FPL labels them exactly on the bill
        base_charge = _find_decimal(text, "Base charge")
        non_fuel = _find_decimal(text, "Non-fuel")
        fuel_charge = _find_decimal(text, "Fuel charge")
        electric_service = _find_decimal(text, "Electric service charges")

        # Tax / fee layer
        grt = _find_decimal(text, "Gross receipts tax (State tax)")
        if grt is None:
            grt = _find_decimal(text, "Gross receipts tax")
        franchise = _find_decimal(text, "Franchise fee (Reqd local fee)")
        if franchise is None:
            franchise = _find_decimal(text, "Franchise fee")
        utility_tax = _find_decimal(text, "Utility tax (Local tax)")
        if utility_tax is None:
            utility_tax = _find_decimal(text, "Utility tax")
        psc_raf = _find_decimal(text, "Regulatory fee (State fee)")
        if psc_raf is None:
            psc_raf = _find_decimal(text, "Regulatory fee")
        taxes_total = _find_decimal(text, "Taxes and charges")

        # Non-tariff items
        prior_balance = _find_decimal(text, "Balance before new charges")
        payment_received = _find_decimal(text, "Payment(s) received - thank you")
        if payment_received is None:
            payment_received = _find_decimal(text, "Payments received")

        # Totals
        total_new = _find_decimal(text, "Total new charges")
        total_amount = _find_decimal(text, "Total amount you owe")
        if total_amount is None:
            total_amount = _find_decimal(text, "TOTAL AMOUNT YOU OWE")

        # Meter readings — pattern: "Current - Previous = Usage"
        #                            "69792 - 68713 = 1079"
        meter_match = re.search(
            r"(\d{4,7})\s*-\s*(\d{4,7})\s*=\s*(\d+)",
            text,
        )
        current_reading = prev_reading = None
        if meter_match:
            current_reading = Decimal(meter_match.group(1))
            prev_reading = Decimal(meter_match.group(2))

        # Confidence: all critical fields present = 1.0; degrade proportionally.
        critical = [base_charge, fuel_charge, total_amount, kwh, billing_end]
        confidence = sum(1 for c in critical if c) / len(critical)

        if billing_start is None or billing_end is None:
            raise ValueError("Could not locate billing period dates in FPL bill text")
        if total_amount is None:
            raise ValueError("Could not locate 'Total amount you owe' in FPL bill text")

        return ParsedBill(
            utility="FPL",
            account_number=account,
            billing_period_start=billing_start,
            billing_period_end=billing_end,
            billing_days=billing_days or (billing_end - billing_start).days + 1,
            rate_schedule=rate_schedule,
            kwh_consumed=Decimal(kwh),
            previous_meter_reading=prev_reading,
            current_meter_reading=current_reading,
            base_charge=base_charge,
            non_fuel_energy_charge=non_fuel,
            fuel_charge=fuel_charge,
            electric_service_subtotal=electric_service,
            gross_receipts_tax=grt,
            franchise_fee=franchise,
            utility_tax=utility_tax,
            psc_regulatory_fee=psc_raf,
            taxes_and_fees_subtotal=taxes_total,
            prior_balance=prior_balance,
            # Preserve the bill's sign: FPL prints payments received as
            # negative (credit reducing what's owed). If the bill omits the
            # minus and the parser got a positive, flip it so the model
            # consistently shows credits as negative.
            payment_received=(
                payment_received
                if payment_received is None or payment_received < 0
                else -payment_received
            ),
            current_charges_total=total_new,
            total_amount_due=total_amount,
            parse_confidence=confidence,
            parse_method="pdf_structured",
            raw_text=text,
        )
