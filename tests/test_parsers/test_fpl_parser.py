"""Tests for the FPL bill parser using the canonical sample bill fixture."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from tariff_audit.parsers.fpl import FPLBillParser
from tests.test_parsers.fixtures.fpl_sample_bill import FPL_SAMPLE_BILL_TEXT


@pytest.fixture
def parsed():
    return FPLBillParser().parse(FPL_SAMPLE_BILL_TEXT)


def test_parser_detects_fpl_bill():
    assert FPLBillParser().can_parse(FPL_SAMPLE_BILL_TEXT) is True


def test_parser_rejects_unrelated_text():
    assert FPLBillParser().can_parse("This is a Duke Energy bill.") is False


def test_rate_schedule_extracted(parsed):
    assert parsed.rate_schedule == "RS-1"


def test_billing_period_extracted(parsed):
    assert parsed.billing_period_end == date(2025, 7, 1)
    # Start should be Jun 3, 2025 (reconstructed from end − 28 days = Jun 3)
    # or Jun 2, 2025 from the "Service to ... Jun 2, 2025" line. Accept either.
    assert parsed.billing_period_start in (date(2025, 6, 2), date(2025, 6, 3))
    assert parsed.billing_days == 29


def test_kwh_consumed(parsed):
    assert parsed.kwh_consumed == Decimal("1079")


def test_meter_readings(parsed):
    assert parsed.current_meter_reading == Decimal("69792")
    assert parsed.previous_meter_reading == Decimal("68713")


def test_tariff_line_items(parsed):
    assert parsed.base_charge == Decimal("9.61")
    assert parsed.non_fuel_energy_charge == Decimal("115.39")
    assert parsed.fuel_charge == Decimal("26.77")
    assert parsed.electric_service_subtotal == Decimal("151.77")


def test_tax_and_fee_line_items(parsed):
    assert parsed.gross_receipts_tax == Decimal("3.89")
    assert parsed.franchise_fee == Decimal("9.90")
    assert parsed.utility_tax == Decimal("14.64")
    assert parsed.psc_regulatory_fee == Decimal("0.1416")
    assert parsed.taxes_and_fees_subtotal == Decimal("28.57")


def test_totals(parsed):
    assert parsed.current_charges_total == Decimal("180.34")
    assert parsed.total_amount_due == Decimal("180.34")


def test_payment_received_and_prior_balance(parsed):
    # Prior bill $206.11 paid in full → balance before new charges $0.00
    assert parsed.prior_balance == Decimal("0.00")
    assert parsed.payment_received == Decimal("-206.11")


def test_account_number(parsed):
    # Extracted with whitespace preserved
    assert parsed.account_number is not None
    assert "2112133485" in parsed.account_number


def test_parse_confidence_high_on_clean_bill(parsed):
    assert parsed.parse_confidence == 1.0


def test_parse_method_is_pdf_structured(parsed):
    assert parsed.parse_method == "pdf_structured"


def test_utility_is_fpl(parsed):
    assert parsed.utility == "FPL"


def test_tariff_subtotal_matches_components():
    """Verify the bill arithmetic: base + non_fuel + fuel = electric service."""
    parsed = FPLBillParser().parse(FPL_SAMPLE_BILL_TEXT)
    assert (
        parsed.base_charge + parsed.non_fuel_energy_charge + parsed.fuel_charge
        == parsed.electric_service_subtotal
    )


def test_tax_components_sum_to_taxes_total():
    parsed = FPLBillParser().parse(FPL_SAMPLE_BILL_TEXT)
    tax_sum = (
        parsed.gross_receipts_tax
        + parsed.franchise_fee
        + parsed.utility_tax
        + parsed.psc_regulatory_fee
    )
    # $3.89 + $9.90 + $14.64 + $0.1416 = $28.5716 ≈ $28.57 taxes_total
    assert abs(tax_sum - parsed.taxes_and_fees_subtotal) < Decimal("0.01")


def test_electric_plus_taxes_equals_total():
    parsed = FPLBillParser().parse(FPL_SAMPLE_BILL_TEXT)
    # 151.77 + 28.57 = 180.34
    assert (
        parsed.electric_service_subtotal + parsed.taxes_and_fees_subtotal
        == parsed.current_charges_total
    )
