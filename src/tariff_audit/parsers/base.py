"""Abstract bill parser interface and structured bill data model."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ParsedBill(BaseModel):
    """Structured data extracted from a utility bill document.

    This is the canonical "one bill" data shape consumed by the auditor,
    anomaly engine, and bill composer. Every parser — PDF, OCR, CSV,
    manual entry — produces this model.

    Fields are ``Optional`` where the bill doesn't always include them; the
    parser should populate what it can and leave the rest as ``None``.
    """

    model_config = ConfigDict(frozen=True)

    # Identity
    utility: str
    account_number: str | None = None
    service_address: str | None = None

    # Billing period
    billing_period_start: date
    billing_period_end: date
    billing_days: int
    meter_read_date: date | None = None
    statement_date: date | None = None

    # Rate classification
    rate_schedule: str

    # Usage
    kwh_consumed: Decimal
    kwh_on_peak: Decimal | None = None
    kwh_off_peak: Decimal | None = None
    demand_kw: Decimal | None = None
    demand_on_peak_kw: Decimal | None = None
    power_factor: Decimal | None = None
    previous_meter_reading: Decimal | None = None
    current_meter_reading: Decimal | None = None

    # Billed amounts (as printed on the bill, before tax layer)
    base_charge: Decimal | None = None
    non_fuel_energy_charge: Decimal | None = None  # FPL-style bundled non-fuel
    energy_charge: Decimal | None = None
    fuel_charge: Decimal | None = None
    demand_charge: Decimal | None = None
    conservation_charge: Decimal | None = None
    capacity_charge: Decimal | None = None
    environmental_charge: Decimal | None = None
    storm_protection_charge: Decimal | None = None
    storm_restoration_charge: Decimal | None = None
    transition_credit: Decimal | None = None

    # Tariff-regulated subtotal as printed
    electric_service_subtotal: Decimal | None = None

    # Tax / fee layer as printed
    gross_receipts_tax: Decimal | None = None
    franchise_fee: Decimal | None = None
    utility_tax: Decimal | None = None  # municipal public service tax
    sales_tax: Decimal | None = None
    psc_regulatory_fee: Decimal | None = None
    taxes_and_fees_subtotal: Decimal | None = None

    # Non-tariff line items
    late_payment_charge: Decimal | None = None
    deposit_applied: Decimal | None = None
    prior_balance: Decimal | None = None
    payment_received: Decimal | None = None
    budget_billing_adjustment: Decimal | None = None
    solar_credit: Decimal | None = None
    load_management_credit: Decimal | None = None
    other_charges: Decimal | None = None
    other_charges_description: str | None = None

    # Totals
    current_charges_total: Decimal | None = None
    total_amount_due: Decimal

    # Metadata
    parse_confidence: float = Field(ge=0.0, le=1.0)
    parse_method: str  # "pdf_structured" | "pdf_ocr" | "manual" | "csv"
    raw_text: str | None = None


class BillParser(ABC):
    """Abstract base for parsers that extract :class:`ParsedBill` from bills.

    Concrete parsers (per-utility) implement :meth:`can_parse` and
    :meth:`parse`. The auto-detection flow in
    :mod:`tariff_audit.parsers.detector` iterates across registered parsers
    and dispatches to the first one whose ``can_parse`` returns True.
    """

    #: Human-readable identifier for error messages and diagnostics.
    name: str = "abstract"

    @abstractmethod
    def can_parse(self, text: str) -> bool:
        """Return True if this parser recognizes the bill's utility and layout."""

    @abstractmethod
    def parse(self, text: str) -> ParsedBill:
        """Parse the full extracted text of a bill PDF into a :class:`ParsedBill`.

        Implementations should be resilient to minor layout drift — FPL and
        TECO occasionally add / rename line items, and parsers should
        degrade gracefully (return None for missing fields) rather than
        raise.
        """
