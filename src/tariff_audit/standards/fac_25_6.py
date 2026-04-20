"""Florida Administrative Code Chapter 25-6 — Electric Service by Electric Public Utilities.

Structured catalog of every rule in FAC Chapter 25-6, classified by
audit-relevance. Each rule has a citation, short title, effective summary,
and a category flag indicating how (if at all) it affects bill
reconstruction and forensic audit output.

Authoritative source: ``flrules.org/gateway/ChapterHome.asp?Chapter=25-6``

Audit relevance categories:

- ``BILLING`` — the rule directly dictates how a bill must be computed,
  formatted, or presented. Violations are auditable.
- ``METERING`` — the rule governs meter accuracy, testing, or reading
  frequency. Affects whether consumption is correctly measured.
- ``CUSTOMER_RIGHTS`` — the rule protects customer rights (deposits,
  disconnection, refunds). Violations are reportable to the PSC.
- ``COST_RECOVERY`` — the rule governs a utility cost-recovery clause
  (fuel, conservation, capacity, environmental, storm protection). Affects
  which ¢/kWh surcharges are legitimate on a bill.
- ``RATE_PROCEEDING`` — the rule governs how the PSC approves or adjusts
  rates. Not directly auditable per-bill but determines tariff provenance.
- ``OPERATIONAL`` — reliability, construction, safety, records retention.
  Generally not bill-auditable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

AuditRelevance = Literal[
    "BILLING",
    "METERING",
    "CUSTOMER_RIGHTS",
    "COST_RECOVERY",
    "RATE_PROCEEDING",
    "OPERATIONAL",
]


@dataclass(frozen=True)
class FacRule:
    """One rule from Florida Administrative Code Chapter 25-6."""

    rule_id: str
    title: str
    audit_relevance: AuditRelevance
    summary: str
    # Link back to a bill-audit mechanism in this codebase that implements
    # or enforces the rule, when one exists. Empty for rules we do not yet
    # programmatically audit (operational / rate-proceeding rules).
    implemented_by: str = ""


# Ordered catalog — rules are sorted by rule number within each category for
# readability. Every rule in the current FAC 25-6 index is represented.
FAC_25_6_RULES: tuple[FacRule, ...] = (
    # ----------------------- General Provisions -----------------------
    FacRule("25-6.002", "Application and Scope", "OPERATIONAL",
            "Defines which electric utilities are subject to Chapter 25-6."),
    FacRule("25-6.003", "Definitions", "OPERATIONAL",
            "Chapter-wide terminology definitions."),
    FacRule("25-6.0131", "Regulatory Assessment Fees", "BILLING",
            "Establishes PSC regulatory assessment fees on IOUs, municipals, "
            "and cooperatives. IOU rate is ~0.072% of gross operating revenues. "
            "May appear as a pass-through line item on bills.",
            implemented_by="standards.taxes.FL_PSC_REGULATORY_ASSESSMENT_FEE_IOU"),

    # ----------------------- Records and Reports -----------------------
    FacRule("25-6.014", "Records and Reports in General", "OPERATIONAL", ""),
    FacRule("25-6.0141", "Allowance for Funds Used During Construction (AFUDC)",
            "RATE_PROCEEDING", ""),
    FacRule("25-6.0142", "Uniform Retirement Units for Electric Utilities",
            "OPERATIONAL", ""),
    FacRule("25-6.0143", "Use of Accumulated Provision Accounts",
            "RATE_PROCEEDING", ""),
    FacRule("25-6.0144", "Fair Value of Energy Produced While Testing Units",
            "OPERATIONAL", ""),
    FacRule("25-6.015", "Location and Preservation of Records", "OPERATIONAL", ""),
    FacRule("25-6.0151", "Audit Access to Records", "OPERATIONAL", ""),
    FacRule("25-6.016", "Maps and Records", "OPERATIONAL", ""),
    FacRule("25-6.018", "Records of Interruptions and Commission Notification",
            "OPERATIONAL", ""),
    FacRule("25-6.0183", "Generating Capacity Shortage Emergencies",
            "OPERATIONAL", ""),
    FacRule("25-6.0185", "Long-Term Energy Emergencies", "OPERATIONAL", ""),
    FacRule("25-6.019", "Notification of Events", "OPERATIONAL", ""),
    FacRule("25-6.020", "Record of Applications for Service", "CUSTOMER_RIGHTS",
            "Utilities must record every service application."),
    FacRule("25-6.021", "Records of Complaints", "CUSTOMER_RIGHTS",
            "Utilities must maintain complaint records — supports PSC complaint chain of evidence."),
    FacRule("25-6.022", "Record of Metering Devices and Device Tests", "METERING",
            "Utilities must keep records of every meter test. Critical for "
            "meter-error back-billing disputes."),

    # ----------------------- Storm Protection -----------------------
    FacRule("25-6.030", "Storm Protection Plan", "COST_RECOVERY",
            "Framework for utility storm hardening plans."),
    FacRule("25-6.031", "Storm Protection Plan Cost Recovery Clause",
            "COST_RECOVERY",
            "Authorizes per-kWh Storm Protection Charge — one of the "
            "clause-based cost recovery line items on residential bills.",
            implemented_by="tariffs.models.TariffSchedule.storm_protection"),

    # ----------------------- Tariffs and Construction -----------------------
    FacRule("25-6.033", "Tariffs", "RATE_PROCEEDING",
            "Requires every utility to file and maintain an approved tariff. "
            "This is the authoritative source for all rate data the engine encodes."),
    FacRule("25-6.034", "Standard of Construction", "OPERATIONAL", ""),
    FacRule("25-6.0341", "Location of Electric Distribution Facilities",
            "OPERATIONAL", ""),
    FacRule("25-6.0343", "Municipal / Cooperative Reporting Requirements",
            "OPERATIONAL", ""),
    FacRule("25-6.0345", "Safety Standards for New Transmission/Distribution",
            "OPERATIONAL", ""),
    FacRule("25-6.0346", "Quarterly Work Order and Safety Reports",
            "OPERATIONAL", ""),
    FacRule("25-6.035", "Adequacy of Resources", "OPERATIONAL", ""),
    FacRule("25-6.037", "Plant Inspection, Operation, and Maintenance",
            "OPERATIONAL", ""),
    FacRule("25-6.038", "Change in Character of Service", "OPERATIONAL", ""),
    FacRule("25-6.039", "Safety", "OPERATIONAL", ""),
    FacRule("25-6.040", "Grounding of Distribution Circuits", "OPERATIONAL", ""),

    # ----------------------- Rate Proceedings -----------------------
    FacRule("25-6.0423", "Nuclear / IGCC Power Plant Cost Recovery",
            "COST_RECOVERY", "Cost recovery for specified generation projects."),
    FacRule("25-6.0424", "Petition for Mid-Course Correction", "RATE_PROCEEDING", ""),
    FacRule("25-6.0425", "Rate Adjustment Applications and Procedures",
            "RATE_PROCEEDING", ""),
    FacRule("25-6.0426", "Recovery of Economic Development Expenses",
            "COST_RECOVERY", ""),
    FacRule("25-6.043", "Petition for Rate Increase; Commission Designee",
            "RATE_PROCEEDING", ""),
    FacRule("25-6.0431", "Petition for a Limited Proceeding", "RATE_PROCEEDING", ""),
    FacRule("25-6.0435", "Interim Rate Relief", "RATE_PROCEEDING", ""),
    FacRule("25-6.0436", "Depreciation", "RATE_PROCEEDING", ""),
    FacRule("25-6.04361", "Subcategorization of Electric Plant", "RATE_PROCEEDING", ""),
    FacRule("25-6.04364", "Dismantlement Studies", "RATE_PROCEEDING", ""),
    FacRule("25-6.04365", "Nuclear Decommissioning", "RATE_PROCEEDING", ""),
    FacRule("25-6.0437", "Cost of Service Load Research", "RATE_PROCEEDING", ""),
    FacRule("25-6.0438", "Non-Firm Electric Service — Terms and Conditions",
            "BILLING",
            "Governs interruptible / non-firm rate schedules (commercial)."),

    # ----------------------- Territorial / Continuity -----------------------
    FacRule("25-6.0439", "Territorial Agreements — Definitions", "OPERATIONAL", ""),
    FacRule("25-6.044", "Continuity of Service", "CUSTOMER_RIGHTS", ""),
    FacRule("25-6.0440", "Territorial Agreements for Electric Utilities",
            "OPERATIONAL", ""),
    FacRule("25-6.0441", "Territorial Disputes for Electric Utilities",
            "OPERATIONAL", ""),
    FacRule("25-6.0442", "Customer Participation", "CUSTOMER_RIGHTS", ""),
    FacRule("25-6.0455", "Annual Distribution Service Reliability Report",
            "OPERATIONAL", ""),

    # ----------------------- Voltage / Load -----------------------
    FacRule("25-6.046", "Voltage Standards", "OPERATIONAL",
            "Service must be delivered within prescribed voltage ranges."),
    FacRule("25-6.048", "Limiting Connected Load", "OPERATIONAL", ""),

    # ----------------------- METERING (core billing inputs) -----------------------
    FacRule("25-6.049", "Measuring Customer Service", "METERING",
            "Requires service to be measured by an accurate meter."),
    FacRule("25-6.050", "Location of Meters", "METERING", ""),
    FacRule("25-6.052", "Test Procedures and Accuracies of Metering Devices",
            "METERING",
            "Watt-hour meter accuracy tolerance is ±2% (98%–102% of actual). "
            "Meters outside this range must be corrected or removed from service.",
            implemented_by="standards.billing_mechanics.METER_TOLERANCE_PCT"),
    FacRule("25-6.054", "Laboratory Standards", "METERING", ""),
    FacRule("25-6.055", "Portable Standards", "METERING", ""),
    FacRule("25-6.056", "Metering Device Test Plans", "METERING",
            "Utilities must file periodic meter-test plans with the PSC."),
    FacRule("25-6.058", "Determination of Average Meter Error", "METERING",
            "Procedure for computing the applicable meter-error percentage when "
            "a test shows non-zero error."),
    FacRule("25-6.059", "Meter Test by Request", "CUSTOMER_RIGHTS",
            "Customer may request a meter test. Utility may charge a fee only if "
            "the meter tests within tolerance AND was tested in the prior 12 months."),
    FacRule("25-6.060", "Meter Test — Refereed Dispute", "CUSTOMER_RIGHTS",
            "PSC may referee a disputed meter test."),

    # ----------------------- Other Physical -----------------------
    FacRule("25-6.061", "Relocation of Poles", "OPERATIONAL", ""),
    FacRule("25-6.062", "Inspection of Wires and Equipment", "OPERATIONAL", ""),
    FacRule("25-6.064", "Extension of Facilities; CIAC", "OPERATIONAL",
            "Contribution in Aid of Construction."),

    # ----------------------- NET METERING -----------------------
    FacRule("25-6.065", "Interconnection and Metering of Customer-Owned "
            "Renewable Generation", "BILLING",
            "Net metering: excess generation credited in kWh to the next month's "
            "billing cycle. Credits carry for up to 12 months, then utility pays "
            "unused credits at its COG-1 as-available rate. Available up to 2 MW "
            "nameplate (Tier 1 ≤10 kW for residential).",
            implemented_by="standards.billing_mechanics.NET_METERING_CREDIT_CARRYOVER_MONTHS"),

    # ----------------------- Underground Distribution -----------------------
    FacRule("25-6.074", "Applicability (Underground Distribution)", "OPERATIONAL", ""),
    FacRule("25-6.075", "Definitions (Underground)", "OPERATIONAL", ""),
    FacRule("25-6.076", "Rights of Way and Easements", "OPERATIONAL", ""),
    FacRule("25-6.077", "Installation of Underground Distribution in New Subdivisions",
            "OPERATIONAL", ""),
    FacRule("25-6.078", "Schedule of Charges (Underground)", "OPERATIONAL", ""),
    FacRule("25-6.080", "Advances by Applicant", "OPERATIONAL", ""),

    # ----------------------- CUSTOMER SERVICE (billing-critical) -----------------------
    FacRule("25-6.093", "Information to Customers", "CUSTOMER_RIGHTS",
            "Utilities must provide rate schedules, service rules, and bill-dispute "
            "procedures to customers upon request."),
    FacRule("25-6.094", "Complaints and Service Requests", "CUSTOMER_RIGHTS",
            "Utility complaint-handling procedure; supports chain of evidence for "
            "PSC escalation."),
    FacRule("25-6.095", "Initiation of Service", "CUSTOMER_RIGHTS", ""),
    FacRule("25-6.097", "Customer Deposits", "CUSTOMER_RIGHTS",
            "Governs deposits, interest accrual on deposits, and refund timing. "
            "Deposits cannot exceed two months of average billings."),

    # ----------------------- METERING AND BILLING CORE -----------------------
    FacRule("25-6.099", "Meter Readings", "METERING",
            "Utility must take an actual meter reading at least once every six "
            "months. Between actual reads, estimates are permitted but must be "
            "clearly marked on the bill.",
            implemented_by="standards.billing_mechanics.ACTUAL_METER_READ_REQUIRED_EVERY_MONTHS"),
    FacRule("25-6.100", "Customer Billings", "BILLING",
            "Required bill content: total electric cost; Asset Securitization "
            "Charge (if applicable); rate schedule identifier; payment deadline "
            "for discount / to avoid penalty; delinquent date; average daily kWh "
            "for current and previous year; meter-reading conversion factors; "
            "budget-billing separate display; utility contact and surcharge-free "
            "payment location info. Actual read required every 6 months."),
    FacRule("25-6.101", "Delinquent Bills", "BILLING",
            "Establishes delinquent-bill procedures, notice requirements, and the "
            "authority for late-payment charges (late-fee rates are specified in "
            "each utility's approved tariff, not this rule)."),
    FacRule("25-6.102", "Conjunctive Billing", "BILLING",
            "Commercial customers with multiple adjacent premises may elect "
            "conjunctive billing (multiple meters treated as one account)."),
    FacRule("25-6.103", "Adjustment of Bills for Meter Error", "BILLING",
            "If a meter tests outside the 25-6.052 tolerance, the utility must "
            "refund (over-registering) or recover (under-registering) for ONE HALF "
            "the period since the last test, capped at twelve (12) months.",
            implemented_by="standards.billing_mechanics.OVER_REGISTERING_METER_MAX_REFUND_MONTHS"),
    FacRule("25-6.104", "Unauthorized Use of Energy", "BILLING",
            "Theft / diversion cases. Not subject to the 12-month cap in 25-6.106."),
    FacRule("25-6.105", "Refusal or Discontinuance of Service by Utility",
            "CUSTOMER_RIGHTS",
            "Grounds and procedures for service disconnection. Requires prior "
            "written notice and limits disconnection during extreme weather."),
    FacRule("25-6.106", "Underbillings and Overbillings of Energy", "BILLING",
            "Utility may NOT back-bill customers for >12 months for undercharges "
            "caused by utility mistake. Customer can pay back over same time period "
            "or mutual agreement. For overbillings, utility must refund for the "
            "entire period of overcharge based on records; customer elects credit "
            "or one-time payment.",
            implemented_by="standards.billing_mechanics.MAX_BACKBILLING_MONTHS"),
    FacRule("25-6.109", "Refunds", "CUSTOMER_RIGHTS",
            "General refund procedures."),

    # ----------------------- Facility / Reporting -----------------------
    FacRule("25-6.115", "Facility Charges for Overhead-to-Underground Conversion",
            "BILLING",
            "Charges for converting existing overhead distribution to underground. "
            "One-time charges that may appear on bills."),
    FacRule("25-6.135", "Annual Reports", "OPERATIONAL", ""),
    FacRule("25-6.1351", "Cost Allocation and Affiliate Transactions",
            "RATE_PROCEEDING", ""),
    FacRule("25-6.1352", "Earnings Surveillance Report", "RATE_PROCEEDING", ""),
    FacRule("25-6.1353", "Forecasted Earnings Surveillance Report",
            "RATE_PROCEEDING", ""),
    FacRule("25-6.140", "Test Year Notification; Proposed Agency Action",
            "RATE_PROCEEDING", ""),
)


def rules_by_category(category: AuditRelevance) -> tuple[FacRule, ...]:
    """Return all rules with the given audit-relevance category."""
    return tuple(r for r in FAC_25_6_RULES if r.audit_relevance == category)


def rule(rule_id: str) -> FacRule:
    """Look up a rule by its rule number (e.g. ``"25-6.106"``)."""
    for r in FAC_25_6_RULES:
        if r.rule_id == rule_id:
            return r
    raise KeyError(f"No FAC 25-6 rule with id {rule_id!r}")
