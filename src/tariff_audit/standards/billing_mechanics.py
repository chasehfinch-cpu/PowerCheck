"""Mechanical billing rules derived from Florida Administrative Code Chapter 25-6.

These constants and helpers encode the hard numerical limits that govern how
a bill may be adjusted, back-billed, or reconciled — regardless of which
utility's tariff applies. Violations of these rules are auditable and can
support PSC complaint findings.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta

# ---------------------------------------------------------------------------
# Meter accuracy — FAC 25-6.052
# ---------------------------------------------------------------------------

#: Watt-hour meter accuracy tolerance per FAC 25-6.052. A meter whose average
#: registration error exceeds this (in absolute value) must be corrected or
#: removed from service.
METER_TOLERANCE_PCT: Decimal = Decimal("2.0")

#: Corresponding acceptable-accuracy range as fractions.
METER_ACCURACY_LOWER_BOUND: Decimal = Decimal("0.98")
METER_ACCURACY_UPPER_BOUND: Decimal = Decimal("1.02")


# ---------------------------------------------------------------------------
# Meter-error billing adjustment — FAC 25-6.103
# ---------------------------------------------------------------------------

#: Maximum refund / recovery period for meter-error adjustments under
#: FAC 25-6.103. When a meter tests outside the 25-6.052 tolerance, the
#: utility refunds or recovers for **one half** the period since the last
#: test, but never more than this cap.
OVER_REGISTERING_METER_MAX_REFUND_MONTHS: int = 12


# ---------------------------------------------------------------------------
# Under-/over-billing limits — FAC 25-6.106
# ---------------------------------------------------------------------------

#: Maximum period over which a utility may back-bill a customer for
#: undercharges caused by the utility's own mistake (FAC 25-6.106(1)).
#: Does not apply to meter-error adjustments (25-6.103) or unauthorized use
#: of energy (25-6.104), which follow their own rules.
MAX_BACKBILLING_MONTHS: int = 12


# ---------------------------------------------------------------------------
# Meter reading cadence — FAC 25-6.099 & 25-6.100
# ---------------------------------------------------------------------------

#: Maximum number of months a utility may go without taking an actual
#: (non-estimated) meter reading. Bills in the interim may be estimated but
#: must be clearly marked as such.
ACTUAL_METER_READ_REQUIRED_EVERY_MONTHS: int = 6


# ---------------------------------------------------------------------------
# Net metering — FAC 25-6.065
# ---------------------------------------------------------------------------

#: Duration for which unused customer-owned renewable generation kWh credits
#: carry forward before being cashed out at the utility's COG-1 rate.
NET_METERING_CREDIT_CARRYOVER_MONTHS: int = 12

#: System size cap (nameplate kW) for eligibility under FAC 25-6.065.
NET_METERING_MAX_NAMEPLATE_KW: Decimal = Decimal("2000")  # 2 MW

#: Tier 1 residential threshold — ≤10 kW qualifies for streamlined
#: interconnection.
NET_METERING_TIER_1_MAX_KW: Decimal = Decimal("10")


# ---------------------------------------------------------------------------
# Deposits — FAC 25-6.097
# ---------------------------------------------------------------------------

#: A customer deposit may not exceed this multiple of the customer's average
#: monthly billing per FAC 25-6.097.
MAX_DEPOSIT_MULTIPLE_OF_AVG_MONTHLY_BILL: int = 2


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def back_billing_cutoff_date(as_of: date) -> date:
    """Return the earliest date a utility may back-bill to, as of ``as_of``.

    Per FAC 25-6.106(1), the utility cannot recover undercharges caused by
    its own mistake for any period more than 12 months prior to the
    discovery date. This helper returns that cutoff.
    """
    return as_of - relativedelta(months=MAX_BACKBILLING_MONTHS)


def meter_error_refund_period(
    last_test_date: date,
    discovery_date: date,
) -> relativedelta:
    """Compute the FAC 25-6.103 refund period for an over-registering meter.

    Returns half the period between ``last_test_date`` and ``discovery_date``,
    capped at :data:`OVER_REGISTERING_METER_MAX_REFUND_MONTHS`. The utility
    must refund amounts billed in error over this period.

    Parameters
    ----------
    last_test_date : date
        Date of the prior meter test (or meter installation if never tested).
    discovery_date : date
        Date the current out-of-tolerance condition was discovered.
    """
    if discovery_date < last_test_date:
        raise ValueError("discovery_date must be on or after last_test_date")

    delta_days = (discovery_date - last_test_date).days
    half_days = delta_days // 2

    # Cap at 12 months (approximated as 365 days to be consistent with how
    # the PSC applies the limit). For exact month arithmetic, callers can
    # compute months themselves and cap at MAX.
    cap_days = OVER_REGISTERING_METER_MAX_REFUND_MONTHS * 30
    if half_days > cap_days:
        half_days = cap_days

    return relativedelta(days=half_days)


def is_meter_within_tolerance(accuracy_pct: Decimal) -> bool:
    """True if a meter-test accuracy reading is within FAC 25-6.052 tolerance.

    ``accuracy_pct`` is the registration accuracy expressed as a percent
    (e.g. ``Decimal("99.5")`` for a meter running at 99.5% of true).
    """
    error = abs(accuracy_pct - Decimal("100"))
    return error <= METER_TOLERANCE_PCT
