"""Tests for the non-tariff line items module."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tariff_audit.engine.line_items import (
    FAC_25_6_097_MAX_DEPOSIT_MULTIPLE,
    FAC_25_6_097_NONRESIDENTIAL_23MO_DEPOSIT_INTEREST_ANNUAL,
    FAC_25_6_097_RESIDENTIAL_DEPOSIT_INTEREST_ANNUAL,
    FAC_25_6_101_DELINQUENT_DAYS,
    apply_net_metering,
    budget_billing_trueup,
    compute_annual_net_metering_trueup,
    compute_deposit_interest,
    compute_late_payment_charge,
    get_late_fee_schedule,
    load_management_credit,
    max_allowable_deposit,
    partition_by_tax_treatment,
    payment_received,
    prior_balance,
)

# ---------------------------------------------------------------------------
# Late payment charges
# ---------------------------------------------------------------------------


def test_fpl_late_fee_uses_greater_of_5_or_1_5pct():
    """FPL tariff — greater of $5.00 or 1.5%."""
    # Small past-due: $5 flat dominates (1.5% of $100 = $1.50 < $5)
    item = compute_late_payment_charge("FPL", Decimal("100"))
    assert item.amount == Decimal("5.00")

    # Large past-due: 1.5% dominates (1.5% of $500 = $7.50 > $5)
    item = compute_late_payment_charge("FPL", Decimal("500"))
    assert item.amount == Decimal("7.50")


def test_teco_late_fee_is_percentage_only():
    item = compute_late_payment_charge("TECO", Decimal("200"))
    assert item.amount == Decimal("3.00")  # 200 × 0.015


def test_duke_late_fee_is_flat_plus_percentage():
    """Duke tariff is flagged unverified but encoded as $5 + 1.5%."""
    item = compute_late_payment_charge("DUKE", Decimal("200"))
    # $5 + $3 = $8
    assert item.amount == Decimal("8.00")


def test_late_fee_unknown_utility_raises():
    with pytest.raises(LookupError):
        compute_late_payment_charge("NONEXISTENT", Decimal("100"))


def test_late_fee_rejects_negative_balance():
    with pytest.raises(ValueError):
        compute_late_payment_charge("FPL", Decimal("-50"))


def test_fpl_late_fee_schedule_is_verified():
    sched = get_late_fee_schedule("FPL")
    assert sched.verified is True


def test_duke_and_fpu_late_fees_flagged_unverified():
    assert get_late_fee_schedule("DUKE").verified is False
    assert get_late_fee_schedule("FPU").verified is False


# ---------------------------------------------------------------------------
# Deposits — FAC 25-6.097
# ---------------------------------------------------------------------------


def test_max_deposit_is_two_times_avg_monthly():
    assert max_allowable_deposit(Decimal("150")) == Decimal("300.00")
    assert FAC_25_6_097_MAX_DEPOSIT_MULTIPLE == 2


def test_residential_deposit_interest_is_2_percent_annual():
    assert Decimal("0.02") == FAC_25_6_097_RESIDENTIAL_DEPOSIT_INTEREST_ANNUAL
    # $200 deposit held 12 months at 2% = $4.00
    item = compute_deposit_interest(Decimal("200"), months_held=12)
    assert item.amount == Decimal("-4.00")  # credit to customer


def test_nonresidential_long_hold_deposit_interest_is_3_percent_annual():
    assert Decimal("0.03") == FAC_25_6_097_NONRESIDENTIAL_23MO_DEPOSIT_INTEREST_ANNUAL
    # $500 deposit held 24 months at 3% = $30.00
    item = compute_deposit_interest(
        Decimal("500"),
        months_held=24,
        is_residential=False,
        held_more_than_23_months=True,
    )
    assert item.amount == Decimal("-30.00")


def test_short_hold_nonresidential_accrues_no_interest_by_default():
    item = compute_deposit_interest(
        Decimal("500"),
        months_held=6,
        is_residential=False,
        held_more_than_23_months=False,
    )
    assert item.amount == Decimal("0.00")


def test_deposit_interest_rejects_negative():
    with pytest.raises(ValueError):
        compute_deposit_interest(Decimal("-100"), months_held=12)
    with pytest.raises(ValueError):
        compute_deposit_interest(Decimal("100"), months_held=-1)


# ---------------------------------------------------------------------------
# Net metering — FAC 25-6.065
# ---------------------------------------------------------------------------


def test_net_metering_consumption_exceeds_generation_bills_difference():
    """1,200 kWh used, 800 kWh generated → customer bills 400 kWh."""
    r = apply_net_metering(
        metered_consumption_kwh=1200,
        metered_generation_kwh=800,
    )
    assert r.billable_kwh == Decimal("400")
    assert r.ending_credit_balance == Decimal("0")


def test_net_metering_generation_exceeds_consumption_carries_kwh_forward():
    """500 kWh used, 800 kWh generated → bill 0, carry 300 kWh credit."""
    r = apply_net_metering(
        metered_consumption_kwh=500,
        metered_generation_kwh=800,
    )
    assert r.billable_kwh == Decimal("0")
    assert r.ending_credit_balance == Decimal("300")


def test_net_metering_applies_starting_credit_balance():
    """Previous-month credit of 200 kWh reduces current billing."""
    r = apply_net_metering(
        metered_consumption_kwh=1000,
        metered_generation_kwh=500,
        starting_credit_balance_kwh=200,
    )
    # net = 1000 - 500 - 200 = 300 kWh billable
    assert r.billable_kwh == Decimal("300")
    assert r.ending_credit_balance == Decimal("0")


def test_net_metering_trueup_pays_at_cog1_rate():
    # 500 leftover kWh × 2.5¢/kWh = $12.50
    item = compute_annual_net_metering_trueup(
        unused_kwh_credits=500,
        cog1_rate_cents_per_kwh=Decimal("2.5"),
    )
    assert item.amount == Decimal("-12.50")


# ---------------------------------------------------------------------------
# Other helpers
# ---------------------------------------------------------------------------


def test_load_management_credit_is_negative():
    item = load_management_credit("FPL", Decimal("7.50"), "On-Call")
    assert item.amount == Decimal("-7.50")
    assert item.category == "load_management_credit"


def test_budget_billing_trueup_positive_when_undercollected():
    item = budget_billing_trueup(actual_ytd_charges=1800, budget_billed_ytd=1500)
    assert item.amount == Decimal("300.00")


def test_budget_billing_trueup_negative_when_overcollected():
    item = budget_billing_trueup(actual_ytd_charges=1500, budget_billed_ytd=1800)
    assert item.amount == Decimal("-300.00")


def test_prior_balance_passthrough():
    assert prior_balance(Decimal("42.00")).amount == Decimal("42.00")


def test_payment_received_is_credit():
    assert payment_received(Decimal("100.00")).amount == Decimal("-100.00")


def test_payment_received_rejects_negative():
    with pytest.raises(ValueError):
        payment_received(Decimal("-100"))


# ---------------------------------------------------------------------------
# Partitioning
# ---------------------------------------------------------------------------


def test_partition_splits_pre_and_post_tax():
    items = [
        load_management_credit("FPL", Decimal("7.50")),  # post-tax
        prior_balance(Decimal("50")),
        compute_late_payment_charge("FPL", Decimal("100")),
        # Mark one as pre-tax manually (rare case)
    ]
    summary = partition_by_tax_treatment(items)
    assert len(summary.post_tax_items) == 3
    assert summary.pre_tax_total == Decimal("0")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_delinquent_days_is_twenty():
    """FAC 25-6.101 — bill delinquent 20 days after issue."""
    assert FAC_25_6_101_DELINQUENT_DAYS == 20
