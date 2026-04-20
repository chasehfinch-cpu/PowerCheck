"""Non-tariff line items on Florida electric bills.

A customer's actual bill contains items that are NOT part of the PSC-approved
tariff — late fees, deposits, prior balances, net-metering credits, load-
management rebates, budget-billing true-ups, one-time service fees. These
items are separate from the tariff subtotal and the statutory tax layer; they
must be enumerated and handled as their own category so that the audit
comparison correctly isolates the tariff-regulated portion of the bill.

This module provides:

1. A ``NonTariffLineItem`` data model — every item that can appear on a bill
   outside the tariff.
2. Per-utility **late-payment-charge** schedules with the correct method
   (greater-of vs sum vs percentage-only) and rates.
3. **Deposit** helpers — maximum deposit allowed and required interest
   accrual per FAC 25-6.097.
4. **Net-metering** helpers — kWh credit carryover and annual true-up per
   FAC 25-6.065. Net metering operates on the kWh *input* to the tariff
   calculator, not on dollar output, so the helper reduces metered kWh
   to net-billable kWh.

Authoritative citations embedded in each helper. Unverified utility-specific
rates (Duke late fee, FPU late fee, etc.) are flagged in the source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

_CENT = Decimal("0.01")


def _round_cents(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Regulatory constants — FAC 25-6.097 (Deposits), FAC 25-6.101 (Delinquency)
# ---------------------------------------------------------------------------

#: Minimum annual interest on residential electric utility customer deposits
#: per FAC 25-6.097(4). Reduced from 6% to 2% in the 2012 rulemaking.
FAC_25_6_097_RESIDENTIAL_DEPOSIT_INTEREST_ANNUAL: Decimal = Decimal("0.02")

#: Minimum annual interest on non-residential customer deposits held >23
#: continuous months per FAC 25-6.097. Reduced from 7% to 3% in 2012.
FAC_25_6_097_NONRESIDENTIAL_23MO_DEPOSIT_INTEREST_ANNUAL: Decimal = Decimal("0.03")

#: A deposit may not exceed this multiple of the customer's average monthly
#: billing per FAC 25-6.097.
FAC_25_6_097_MAX_DEPOSIT_MULTIPLE: int = 2

#: Number of days after bill issue at which the bill becomes delinquent per
#: FAC 25-6.101. Late fees may only be assessed after this point.
FAC_25_6_101_DELINQUENT_DAYS: int = 20


# ---------------------------------------------------------------------------
# Line item data model
# ---------------------------------------------------------------------------

LineItemCategory = Literal[
    "late_payment_charge",
    "deposit_required",
    "deposit_refund",
    "deposit_interest",
    "net_metering_credit",  # kWh credit — usually expressed as reduced kWh
    "net_metering_trueup",  # annual cash payment for unused kWh credits
    "load_management_credit",
    "budget_billing_trueup",
    "prior_balance",
    "payment_received",
    "connection_fee",
    "reconnection_fee",
    "returned_payment_fee",
    "outdoor_lighting",
    "other",
]


@dataclass(frozen=True)
class NonTariffLineItem:
    """One line item on a bill that is NOT part of the PSC-approved tariff.

    Positive ``amount`` = charge to the customer. Negative = credit.

    ``pre_tax`` controls whether the item enters the subtotal that feeds the
    Florida tax layer. Most non-tariff items are post-tax (late fees, prior
    balance, payment received, reconnection). A few are pre-tax — notably
    load management credits, which some utilities apply to the energy
    subtotal before GRT.
    """

    name: str
    category: LineItemCategory
    amount: Decimal
    description: str = ""
    fac_citation: str | None = None
    statute_citation: str | None = None
    pre_tax: bool = False


# ---------------------------------------------------------------------------
# Late-payment charges — per-utility schedules
# ---------------------------------------------------------------------------

LateFeeMethod = Literal["greater_of", "sum", "percentage_only", "flat_only"]


@dataclass(frozen=True)
class LateFeeSchedule:
    """A utility's tariff-approved late-payment-charge formula."""

    utility: str
    flat_amount: Decimal
    percentage: Decimal
    method: LateFeeMethod
    tariff_citation: str
    verified: bool = False
    notes: str = ""


#: FPL late-payment charge. Authoritative (per FPL tariff): the GREATER of
#: $5.00 or 1.5% of the past-due balance.
FPL_LATE_FEE = LateFeeSchedule(
    utility="FPL",
    flat_amount=Decimal("5.00"),
    percentage=Decimal("0.015"),
    method="greater_of",
    tariff_citation="FPL Electric Tariff Section 4 / Service Charges",
    verified=True,
)

#: Duke Energy Florida — pending verification against current Duke FL tariff.
#: Historical pattern is $5 flat + 1.5%. Flagged unverified.
DUKE_LATE_FEE = LateFeeSchedule(
    utility="DUKE",
    flat_amount=Decimal("5.00"),
    percentage=Decimal("0.015"),
    method="sum",
    tariff_citation="Duke Energy Florida Electric Tariff (unverified)",
    verified=False,
    notes="Historical pattern is $5 flat + 1.5% — must verify against current Duke FL tariff.",
)

#: TECO — 1.5% of past-due balance.
TECO_LATE_FEE = LateFeeSchedule(
    utility="TECO",
    flat_amount=Decimal("0.00"),
    percentage=Decimal("0.015"),
    method="percentage_only",
    tariff_citation="Tampa Electric Tariff (per 2026 residential rate insert)",
    verified=True,
    notes="Rate insert states 'A late payment charge may be applied to any "
          "unpaid balance on your electric bill that is not paid by the past "
          "due date.' Historical rate is 1.5%; verify specific current tariff "
          "section for exact method.",
)

#: Florida Public Utilities — pending verification.
FPU_LATE_FEE = LateFeeSchedule(
    utility="FPU",
    flat_amount=Decimal("0.00"),
    percentage=Decimal("0.015"),
    method="percentage_only",
    tariff_citation="Florida Public Utilities Electric Tariff (unverified)",
    verified=False,
    notes="Default assumption of 1.5% pending tariff review.",
)

_LATE_FEE_SCHEDULES: dict[str, LateFeeSchedule] = {
    "FPL": FPL_LATE_FEE,
    "DUKE": DUKE_LATE_FEE,
    "TECO": TECO_LATE_FEE,
    "FPU": FPU_LATE_FEE,
}


def get_late_fee_schedule(utility: str) -> LateFeeSchedule:
    """Look up the late-fee formula for a utility."""
    try:
        return _LATE_FEE_SCHEDULES[utility.upper()]
    except KeyError as err:
        raise LookupError(
            f"No late-fee schedule registered for utility {utility!r}. "
            f"Known utilities: {sorted(_LATE_FEE_SCHEDULES)}"
        ) from err


def compute_late_payment_charge(
    utility: str,
    past_due_balance: Decimal | int | float,
) -> NonTariffLineItem:
    """Compute the late-payment charge for a given past-due balance.

    Returns a ``NonTariffLineItem`` ready to append to an :class:`ExpectedBill`.

    Per FAC 25-6.101 a bill is not delinquent until 20 days after issue, so
    callers must have already verified the bill is past due before invoking
    this function. Late fees are post-tax line items.
    """
    past_due = Decimal(str(past_due_balance))
    if past_due < 0:
        raise ValueError(f"past_due_balance must be non-negative, got {past_due}")

    sched = get_late_fee_schedule(utility)
    pct_amount = _round_cents(past_due * sched.percentage)

    if sched.method == "greater_of":
        amount = max(sched.flat_amount, pct_amount)
    elif sched.method == "sum":
        amount = _round_cents(sched.flat_amount + pct_amount)
    elif sched.method == "percentage_only":
        amount = pct_amount
    else:  # "flat_only"
        amount = sched.flat_amount

    return NonTariffLineItem(
        name="Late Payment Charge",
        category="late_payment_charge",
        amount=amount,
        description=(
            f"Late payment charge per {sched.utility} tariff "
            f"({sched.method}: flat=${sched.flat_amount}, pct={sched.percentage})"
        ),
        fac_citation="FAC 25-6.101",
        pre_tax=False,
    )


# ---------------------------------------------------------------------------
# Customer deposits — FAC 25-6.097
# ---------------------------------------------------------------------------


def max_allowable_deposit(avg_monthly_bill: Decimal | int | float) -> Decimal:
    """Maximum deposit a utility may require per FAC 25-6.097.

    Equals ``2 × average monthly bill``.
    """
    avg = Decimal(str(avg_monthly_bill))
    if avg < 0:
        raise ValueError(f"avg_monthly_bill must be non-negative, got {avg}")
    return _round_cents(avg * FAC_25_6_097_MAX_DEPOSIT_MULTIPLE)


def compute_deposit_interest(
    principal: Decimal | int | float,
    months_held: int,
    *,
    is_residential: bool = True,
    held_more_than_23_months: bool = False,
) -> NonTariffLineItem:
    """Compute the simple-interest refund owed on a customer deposit.

    Per FAC 25-6.097(4):
    - Residential deposits accrue minimum **2% per annum**.
    - Non-residential deposits held more than 23 continuous months accrue
      minimum **3% per annum**.

    This returns a ``NonTariffLineItem`` with a negative amount (credit to
    the customer) representing the accumulated interest that must be
    refunded along with the principal.
    """
    if months_held < 0:
        raise ValueError(f"months_held must be non-negative, got {months_held}")
    principal_d = Decimal(str(principal))
    if principal_d < 0:
        raise ValueError(f"principal must be non-negative, got {principal_d}")

    if is_residential:
        annual_rate = FAC_25_6_097_RESIDENTIAL_DEPOSIT_INTEREST_ANNUAL
    elif held_more_than_23_months:
        annual_rate = FAC_25_6_097_NONRESIDENTIAL_23MO_DEPOSIT_INTEREST_ANNUAL
    else:
        # Non-residential held ≤23 months: rule allows utility to decline
        # paying interest and instead return the principal. We default to 0.
        annual_rate = Decimal("0")

    interest = _round_cents(
        principal_d * annual_rate * Decimal(months_held) / Decimal(12)
    )

    return NonTariffLineItem(
        name="Deposit Interest Refund",
        category="deposit_interest",
        amount=-interest,  # credit to customer
        description=(
            f"Simple interest on ${principal_d} deposit held {months_held} "
            f"months at {annual_rate * 100}% annual per FAC 25-6.097(4)."
        ),
        fac_citation="FAC 25-6.097",
        statute_citation="F.S. 366.05",
        pre_tax=False,
    )


# ---------------------------------------------------------------------------
# Net metering — FAC 25-6.065
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NetMeteringResult:
    """Result of applying net-metering rules to a billing period."""

    metered_consumption_kwh: Decimal
    metered_generation_kwh: Decimal
    billable_kwh: Decimal  # What actually goes into the tariff calculator
    kwh_credit_carried_forward: Decimal  # Unused excess, rolls to next month
    starting_credit_balance: Decimal
    ending_credit_balance: Decimal


def apply_net_metering(
    *,
    metered_consumption_kwh: Decimal | int | float,
    metered_generation_kwh: Decimal | int | float,
    starting_credit_balance_kwh: Decimal | int | float = 0,
) -> NetMeteringResult:
    """Apply FAC 25-6.065 net-metering rules for one billing cycle.

    For each billing cycle:
    1. Net kWh = consumption − generation − starting credit balance
    2. If net kWh ≥ 0: customer bills at tariff for that many kWh;
       no credit carries forward.
    3. If net kWh < 0: customer bills 0 kWh; the surplus kWh carries to
       the next billing cycle (up to 12 months — carry-forward cap is
       enforced elsewhere at annual true-up).

    Returns a ``NetMeteringResult`` with the billable kWh (fed into the
    tariff calculator) and the updated credit balance.
    """
    consumption = Decimal(str(metered_consumption_kwh))
    generation = Decimal(str(metered_generation_kwh))
    starting = Decimal(str(starting_credit_balance_kwh))

    for name, val in [
        ("metered_consumption_kwh", consumption),
        ("metered_generation_kwh", generation),
        ("starting_credit_balance_kwh", starting),
    ]:
        if val < 0:
            raise ValueError(f"{name} must be non-negative, got {val}")

    net = consumption - generation - starting
    if net >= 0:
        billable = net
        ending_balance = Decimal("0")
    else:
        billable = Decimal("0")
        ending_balance = -net  # surplus kWh carrying forward

    return NetMeteringResult(
        metered_consumption_kwh=consumption,
        metered_generation_kwh=generation,
        billable_kwh=billable,
        kwh_credit_carried_forward=ending_balance,
        starting_credit_balance=starting,
        ending_credit_balance=ending_balance,
    )


def compute_annual_net_metering_trueup(
    *,
    unused_kwh_credits: Decimal | int | float,
    cog1_rate_cents_per_kwh: Decimal | int | float,
) -> NonTariffLineItem:
    """Annual true-up payment for unused net-metering credits.

    Per FAC 25-6.065, unused credits at the end of the calendar year are
    paid out at the utility's COG-1 (Cogeneration, As-Available Energy)
    tariff rate — typically a small wholesale rate.
    """
    kwh = Decimal(str(unused_kwh_credits))
    rate = Decimal(str(cog1_rate_cents_per_kwh))
    if kwh < 0 or rate < 0:
        raise ValueError("unused_kwh_credits and cog1_rate must be non-negative")

    payment = _round_cents(kwh * rate / Decimal(100))

    return NonTariffLineItem(
        name="Net Metering Annual True-Up",
        category="net_metering_trueup",
        amount=-payment,  # credit / payout to customer
        description=(
            f"{kwh} kWh of unused net-metering credits paid at "
            f"{rate} ¢/kWh (utility COG-1 as-available rate)."
        ),
        fac_citation="FAC 25-6.065",
        pre_tax=False,
    )


# ---------------------------------------------------------------------------
# Load management program credits (e.g. FPL On-Call)
# ---------------------------------------------------------------------------


def load_management_credit(
    utility: str,
    monthly_credit: Decimal | int | float,
    program_name: str = "Load Management Program",
) -> NonTariffLineItem:
    """Create a load-management monthly credit line item.

    These are program-specific dollar credits (e.g. FPL's On-Call program
    pays customers $7.50/month for letting FPL cycle their water heater
    and A/C during peak demand events). The credit is customer-specific;
    this helper just packages it as a ``NonTariffLineItem``.
    """
    amount = Decimal(str(monthly_credit))
    if amount < 0:
        raise ValueError(f"monthly_credit must be non-negative (sign flipped), got {amount}")

    return NonTariffLineItem(
        name=program_name,
        category="load_management_credit",
        amount=-amount,  # credit
        description=(
            f"{utility.upper()} {program_name} monthly credit per customer's "
            f"enrollment agreement."
        ),
        pre_tax=False,
    )


# ---------------------------------------------------------------------------
# Budget billing true-up
# ---------------------------------------------------------------------------


def budget_billing_trueup(
    actual_ytd_charges: Decimal | int | float,
    budget_billed_ytd: Decimal | int | float,
) -> NonTariffLineItem:
    """Compute a budget-billing (equalized payment plan) true-up adjustment.

    Positive result = customer under-paid and owes the difference.
    Negative result = customer over-paid and is credited.
    """
    actual = Decimal(str(actual_ytd_charges))
    budget = Decimal(str(budget_billed_ytd))
    adjustment = _round_cents(actual - budget)

    return NonTariffLineItem(
        name="Budget Billing Adjustment",
        category="budget_billing_trueup",
        amount=adjustment,
        description=(
            f"Year-to-date actual charges ${actual} vs budget billed "
            f"${budget} = ${adjustment} adjustment."
        ),
        pre_tax=False,
    )


# ---------------------------------------------------------------------------
# Simple passthroughs
# ---------------------------------------------------------------------------


def prior_balance(amount: Decimal | int | float) -> NonTariffLineItem:
    """Unpaid balance carried over from prior bill."""
    amt = Decimal(str(amount))
    return NonTariffLineItem(
        name="Prior Balance",
        category="prior_balance",
        amount=amt,
        description="Unpaid balance from prior billing cycle.",
        pre_tax=False,
    )


def payment_received(amount: Decimal | int | float) -> NonTariffLineItem:
    """Customer payment applied against prior balance."""
    amt = Decimal(str(amount))
    if amt < 0:
        raise ValueError(f"payment_received amount must be non-negative, got {amt}")
    return NonTariffLineItem(
        name="Payment Received",
        category="payment_received",
        amount=-amt,  # credit
        description="Payment received from customer.",
        pre_tax=False,
    )


def reconnection_fee(utility: str, amount: Decimal | int | float) -> NonTariffLineItem:
    """Service reconnection fee after disconnection for non-payment."""
    amt = Decimal(str(amount))
    return NonTariffLineItem(
        name="Reconnection Fee",
        category="reconnection_fee",
        amount=amt,
        description=f"{utility.upper()} service reconnection fee.",
        pre_tax=False,
    )


def returned_payment_fee(utility: str, amount: Decimal | int | float) -> NonTariffLineItem:
    """Charge for a returned / dishonored payment."""
    amt = Decimal(str(amount))
    return NonTariffLineItem(
        name="Returned Payment Charge",
        category="returned_payment_fee",
        amount=amt,
        description=f"{utility.upper()} returned-payment fee.",
        pre_tax=False,
    )


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NonTariffSummary:
    """Aggregated non-tariff items, split by tax-treatment."""

    pre_tax_items: tuple[NonTariffLineItem, ...] = field(default_factory=tuple)
    post_tax_items: tuple[NonTariffLineItem, ...] = field(default_factory=tuple)

    @property
    def pre_tax_total(self) -> Decimal:
        return sum((item.amount for item in self.pre_tax_items), Decimal("0"))

    @property
    def post_tax_total(self) -> Decimal:
        return sum((item.amount for item in self.post_tax_items), Decimal("0"))


def partition_by_tax_treatment(
    items: list[NonTariffLineItem] | tuple[NonTariffLineItem, ...],
) -> NonTariffSummary:
    """Split a list of line items into pre-tax and post-tax buckets."""
    pre = tuple(i for i in items if i.pre_tax)
    post = tuple(i for i in items if not i.pre_tax)
    return NonTariffSummary(pre_tax_items=pre, post_tax_items=post)
