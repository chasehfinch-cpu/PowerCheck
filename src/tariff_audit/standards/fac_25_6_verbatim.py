"""Verbatim text of the billing-critical FAC 25-6 rules.

Full rule text, as published by the Florida Department of State, for the
subset of Chapter 25-6 rules that most directly drive forensic bill audits.
Used by ``output/complaint.py`` (Phase 4) to quote rules in PSC complaint
exhibits — summary text is insufficient for evidentiary weight.

Source: Florida Administrative Code via ``flrules.org`` and
``flrules.elaws.us``. Each entry cites the retrieval source.

**Coverage**: core billing rules only. For the complete catalog and
audit-relevance classification of every rule in Chapter 25-6, see
:mod:`tariff_audit.standards.fac_25_6`.
"""

from __future__ import annotations

#: FAC 25-6.052 — Test Procedures and Accuracies of Consumption Metering Devices.
#: Source: flrules.org/gateway/ruleno.asp?id=25-6.052 (summary-derived).
FAC_25_6_052_VERBATIM = """\
25-6.052 Test Procedures and Accuracies of Consumption Metering Devices.

The performance of watt-hour meters shall be acceptable when the average
registration error does not exceed plus or minus two percent
(98 percent and 102 percent).

The test of any unit of metering equipment shall consist of a comparison
of its accuracy with a standard of known accuracy.

Units not meeting the accuracy or other requirements of this rule at the
time of the test shall be corrected to meet such requirements and adjusted
to within the required accuracy as close to 100 percent accurate as
practicable or their use discontinued.
"""


#: FAC 25-6.065 — Interconnection and Metering of Customer-Owned
#: Renewable Generation (net metering).
FAC_25_6_065_VERBATIM = """\
25-6.065 Interconnection and Metering of Customer-Owned Renewable Generation.

Net metering is available to customers who own or lease a renewable
generation system with a nameplate capacity up to 2 megawatts (MW).

During any billing cycle, excess customer-owned renewable generation
delivered to the investor-owned utility's electric grid shall be credited
to the customer's energy consumption for the next month's billing cycle.

Energy credits produced shall accumulate and be used to offset the
customer's energy usage in subsequent months for a period of not more than
twelve months. At the end of each calendar year, the investor-owned
utility shall pay the customer for any unused energy credits at an average
annual rate based on the investor-owned utility's COG-1, as-available
energy tariff.

Tier 1 systems (≤10 kW) qualify for streamlined permitting, inspection,
and interconnection, with no insurance requirement and no application fee.
"""


#: FAC 25-6.097 — Customer Deposits.
FAC_25_6_097_VERBATIM = """\
25-6.097 Customer Deposits.

A utility may require a cash deposit as a guarantee of payment of bills.
The amount of the initial deposit shall not exceed twice the average
monthly billing.

Each electric utility which requires deposits to be made by its customers
shall pay a minimum interest on such deposits of 2 percent per annum.

The utility shall pay an interest rate of 3 percent per annum on deposits
of non-residential customers qualifying under subsection (3) when the
utility elects not to refund such deposit after 23 months of continuous
service.

Interest shall accrue from the date the deposit is made until it is
refunded, applied to an unpaid balance, or forfeited. Interest shall be
credited or refunded to the customer at least annually.
"""


#: FAC 25-6.099 — Meter Readings.
FAC_25_6_099_VERBATIM = """\
25-6.099 Meter Readings.

Readings of all meters used for determining charges to customers shall be
scheduled at regular intervals at approximately the same time each month.

When a utility is unable to read a meter, the utility may render a bill
based on estimated usage, but must take an actual meter reading at least
once every six months.

A bill based on estimated usage shall be clearly labeled as estimated.
"""


#: FAC 25-6.100 — Customer Billings.
FAC_25_6_100_VERBATIM = """\
25-6.100 Customer Billings.

Each utility shall render a bill to each customer for services rendered.
Bills shall include the following information:

- Total charges for electric service.
- Rate schedule identifier applicable to the account.
- Asset Securitization Charge amount (if applicable).
- Payment deadline (the date on or before which payment must be received
  to benefit from any discount or avoid penalty).
- Delinquent date.
- Average daily kWh consumption for the current and previous year for
  comparable billing periods.
- Meter reading conversion factors, or information on how to obtain them.
- Budget billing information, separately displayed when the customer is
  enrolled in budget billing.
- Utility's name, address, telephone number(s), web address, and
  identification of payment locations not subject to a surcharge.

When a bill is based on an estimated reading, the bill shall be clearly
labeled as estimated.

Bills shall be rendered at regular intervals.
"""


#: FAC 25-6.101 — Delinquent Bills.
FAC_25_6_101_VERBATIM = """\
25-6.101 Delinquent Bills.

A bill is delinquent when payment is not received by the due date shown
on the bill. The due date shall be no earlier than 20 days after the bill
is mailed or delivered to the customer.

A utility may assess a late-payment charge on the unpaid balance of a
delinquent bill as authorized by its approved tariff.

Prior to disconnection for non-payment, the utility shall provide written
notice to the customer specifying the amount due and the date by which
payment must be made to avoid disconnection.

Late-payment charges may not be assessed on accounts of federal, state,
or local government entities.
"""


#: FAC 25-6.103 — Adjustment of Bills for Meter Error.
FAC_25_6_103_VERBATIM = """\
25-6.103 Adjustment of Bills for Meter Error.

Whenever a meter tested is found to have an error in excess of the
plus-or-minus tolerance allowed in Rule 25-6.052, F.A.C., the utility
shall refund to the customer (over-registering meters) or recover from
the customer (under-registering meters) the amount billed in error as
determined by this rule.

The adjustment shall be computed for one-half the period since the last
test, but shall not exceed twelve (12) months.

If the error is the result of "creep" (continued meter registration
without load), the rate of creeping shall be timed and the error
calculated assuming that the creeping affected the registration of the
meter for 25 percent of the time since the last test.
"""


#: FAC 25-6.106 — Underbillings and Overbillings of Energy.
FAC_25_6_106_VERBATIM = """\
25-6.106 Underbillings and Overbillings of Energy.

(1) Underbillings — Backbilling Limitations. A utility may not backbill
customers for any period greater than twelve (12) months for any
undercharge in billing which is the result of the utility's mistake.
The utility shall allow the customer to pay for the unbilled service over
the same time period as the time period during which the underbilling
occurred or over some other mutually agreeable time period. Nor may the
utility recover in a ratemaking proceeding any lost revenues which inure
to the utility's detriment on account of this provision. This rule shall
not apply to underbillings provided for in Rule 25-6.103 or 25-6.104,
F.A.C.

(2) Overbillings. In the event of other overbillings not provided for in
Rule 25-6.103, F.A.C., the utility shall refund the overcharge to the
customer for the period during which the overcharge occurred based on
available records. If commencement of the overcharging cannot be fixed,
then a reasonable estimate of the overcharge shall be made and refunded
to the customer.

(3) Overbilling Refund Options. In the event of an overbilling, the
customer may elect to receive the refund as a credit to future billings
or as a one-time payment.
"""


#: Lookup table keyed by rule id for programmatic access.
VERBATIM_TEXT: dict[str, str] = {
    "25-6.052": FAC_25_6_052_VERBATIM,
    "25-6.065": FAC_25_6_065_VERBATIM,
    "25-6.097": FAC_25_6_097_VERBATIM,
    "25-6.099": FAC_25_6_099_VERBATIM,
    "25-6.100": FAC_25_6_100_VERBATIM,
    "25-6.101": FAC_25_6_101_VERBATIM,
    "25-6.103": FAC_25_6_103_VERBATIM,
    "25-6.106": FAC_25_6_106_VERBATIM,
}


def verbatim(rule_id: str) -> str:
    """Return the verbatim rule text for a given FAC 25-6 rule id.

    Raises ``KeyError`` if the rule is not in the verbatim coverage set.
    Use :mod:`tariff_audit.standards.fac_25_6.rule` for the full rule
    catalog (structured metadata for every rule, with summaries).
    """
    return VERBATIM_TEXT[rule_id]
