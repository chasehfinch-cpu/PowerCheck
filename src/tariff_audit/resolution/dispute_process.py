"""Step-by-step dispute / resolution workflow per utility.

All Florida IOU billing disputes follow the same general structure:

1. Contact the utility first (required by PSC before they will intervene)
2. Send a written / certified-mail dispute letter if phone doesn't resolve
3. Wait a reasonable time for utility response (typically 30 days)
4. Escalate to PSC consumer complaint if unresolved

The specifics — which form is required, where to send certified mail,
how long to wait, what evidence to enclose — vary by utility. This
module encodes those specifics.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DisputeStep:
    """One step in the dispute workflow for a utility."""

    order: int
    title: str
    description: str
    required_evidence: tuple[str, ...] = ()
    timeline: str = ""
    contact_method: str = ""  # "phone" | "email" | "certified_mail" | "online_form"


@dataclass(frozen=True)
class DisputeProcess:
    """Complete dispute workflow for one utility."""

    utility: str
    display_name: str
    steps: tuple[DisputeStep, ...]
    required_enclosures_for_written_dispute: tuple[str, ...] = field(default_factory=tuple)
    typical_resolution_timeline_days: int = 30
    escalation_notes: str = ""


# ---------------------------------------------------------------------------
# Shared enclosures for a written utility dispute letter
# ---------------------------------------------------------------------------

_STANDARD_ENCLOSURES = (
    "Copy of disputed bill(s) — every page",
    "Account number and service address",
    "Customer name and contact information (phone, email, mailing)",
    "Itemized list of disputed charges with amounts and per-line explanation",
    "Requested remedy (refund amount, rate reclassification, meter test, etc.)",
    "Reference to applicable PSC tariff docket numbers and FAC 25-6 rules",
    "Multi-month billing history if alleging pattern (multi-month analysis "
    "from this tool can serve as an exhibit)",
    "Deadline for utility response (30 days from receipt, certified-mail "
    "return-receipt date)",
    "Notice of intent to file PSC complaint if unresolved",
)


# ---------------------------------------------------------------------------
# FPL
# ---------------------------------------------------------------------------

FPL_DISPUTE = DisputeProcess(
    utility="FPL",
    display_name="Florida Power & Light",
    steps=(
        DisputeStep(
            order=1,
            title="Call FPL Customer Care",
            description=(
                "Call 1-800-226-3545 (24/7). Identify the specific charges "
                "in dispute (line by line), cite the applicable PSC tariff "
                "rate, and request an adjustment. Note the representative's "
                "name and any reference number."
            ),
            timeline="Expect initial response within same call",
            contact_method="phone",
        ),
        DisputeStep(
            order=2,
            title="Escalate to a supervisor if not resolved",
            description=(
                "If the first-level representative cannot resolve, ask to "
                "speak to a supervisor. Document what was said, when, and by "
                "whom. Customer Care has authority to make billing "
                "adjustments up to a defined threshold."
            ),
            contact_method="phone",
        ),
        DisputeStep(
            order=3,
            title="Send a certified-mail dispute letter",
            description=(
                "If phone / supervisor escalation doesn't resolve, mail a "
                "formal dispute letter by USPS Certified Mail with Return "
                "Receipt to the Customer Care PO Box. This creates a dated "
                "paper record required for PSC complaint escalation."
            ),
            required_evidence=_STANDARD_ENCLOSURES,
            timeline="Allow 30 days for written response",
            contact_method="certified_mail",
        ),
        DisputeStep(
            order=4,
            title="File Florida PSC consumer complaint",
            description=(
                "If FPL fails to respond within 30 days or refuses the "
                "requested remedy, file a consumer complaint with the "
                "Florida PSC. Submit online at psc.state.fl.us/"
                "consumer-complaint-form or call 1-800-342-3552. Record "
                "the PSC-issued tracking number."
            ),
            required_evidence=(
                "Full copy of your dispute letter and any FPL response",
                "Certified-mail receipt + return receipt",
                "Bill copies covering the disputed period",
                "Forensic audit report (this tool) documenting the "
                "overcharge calculation line by line",
            ),
            timeline="PSC typically acknowledges within 5 business days",
            contact_method="online_form",
        ),
    ),
    required_enclosures_for_written_dispute=_STANDARD_ENCLOSURES,
    typical_resolution_timeline_days=30,
    escalation_notes=(
        "FPL is the largest FL IOU with ~5.9 million customers. Dispute "
        "volume is high; expect the phone queue to be busy at peak hours. "
        "The certified-mail step creates the evidentiary chain the PSC "
        "requires."
    ),
)


# ---------------------------------------------------------------------------
# Duke Energy Florida
# ---------------------------------------------------------------------------

DUKE_DISPUTE = DisputeProcess(
    utility="DUKE",
    display_name="Duke Energy Florida",
    steps=(
        DisputeStep(
            order=1,
            title="Call Duke Energy Florida customer service",
            description=(
                "Call 1-800-700-8744 Monday–Friday 7:00 AM – 7:00 PM ET. "
                "Identify the disputed charges and cite the Duke rate "
                "schedule. Ask for a written confirmation of any adjustment."
            ),
            timeline="Same-day response during business hours",
            contact_method="phone",
        ),
        DisputeStep(
            order=2,
            title="Request a written review",
            description=(
                "Ask the representative to document your dispute in their "
                "system and commit to a written response. Get the case / "
                "ticket number. If no adjustment is offered and you believe "
                "the tariff was misapplied, ask to escalate to the Duke "
                "Customer Advocate team."
            ),
            contact_method="phone",
        ),
        DisputeStep(
            order=3,
            title="Send certified-mail dispute letter",
            description=(
                "Mail a formal dispute letter to the Duke billing PO Box in "
                "Charlotte, NC. Note: Duke uses the Charlotte address for all "
                "Florida billing correspondence (centralized with the parent)."
            ),
            required_evidence=_STANDARD_ENCLOSURES,
            timeline="Allow 30 days for response",
            contact_method="certified_mail",
        ),
        DisputeStep(
            order=4,
            title="File Florida PSC consumer complaint",
            description=(
                "Same as for any FL IOU — file at psc.state.fl.us or call "
                "1-800-342-3552 once the 30-day utility response window has "
                "closed without satisfactory resolution."
            ),
            required_evidence=(
                "Dispute letter + certified-mail receipts",
                "Bill copies",
                "Forensic audit exhibit",
            ),
            contact_method="online_form",
        ),
    ),
    required_enclosures_for_written_dispute=_STANDARD_ENCLOSURES,
    typical_resolution_timeline_days=30,
    escalation_notes=(
        "Duke 2026 has a significant rate event: Storm Cost Recovery was "
        "removed effective March 1, 2026. Bills issued in Jan–Feb 2026 "
        "include this charge; bills issued Mar 2026+ should not. If a "
        "post-March bill still shows Storm Cost Recovery, that's a clear "
        "dispute basis."
    ),
)


# ---------------------------------------------------------------------------
# TECO
# ---------------------------------------------------------------------------

TECO_DISPUTE = DisputeProcess(
    utility="TECO",
    display_name="Tampa Electric",
    steps=(
        DisputeStep(
            order=1,
            title="Call or email TECO customer care",
            description=(
                "Call 1-877-588-1010 (Mon–Fri 7:30 AM – 6:00 PM) or email "
                "wecare@tecoenergy.com. The wecare@ inbox is monitored by "
                "the Customer Care team — expect written response."
            ),
            timeline="Email response typically 1–2 business days",
            contact_method="phone_or_email",
        ),
        DisputeStep(
            order=2,
            title="Escalate via written dispute to PO Box 111",
            description=(
                "Send certified mail to Tampa Electric, PO Box 111, Tampa, "
                "FL 33601-0111 — the dedicated address for questions, "
                "concerns, and complaints. Do NOT send to the payment PO "
                "Box (31318) — that will delay processing."
            ),
            required_evidence=_STANDARD_ENCLOSURES,
            timeline="Allow 30 days for response",
            contact_method="certified_mail",
        ),
        DisputeStep(
            order=3,
            title="File Florida PSC consumer complaint",
            description="Same PSC escalation path as all FL IOUs.",
            required_evidence=(
                "Dispute letter + certified-mail receipts",
                "TECO email correspondence if any",
                "Bill copies",
                "Forensic audit exhibit",
            ),
            contact_method="online_form",
        ),
    ),
    required_enclosures_for_written_dispute=_STANDARD_ENCLOSURES,
    typical_resolution_timeline_days=30,
    escalation_notes=(
        "TECO's 2026 Storm Surcharge (1.995 ¢/kWh) is a temporary recovery "
        "expiring August 31, 2026. Bills for September 2026 onward should "
        "NOT include this line item — if they do, that's a billing error. "
        "TECO's bundled energy-charge structure (which includes 0.621 ¢/kWh "
        "of conservation + capacity + environmental) often confuses "
        "customers; be precise about which line item you dispute."
    ),
)


# ---------------------------------------------------------------------------
# FPU
# ---------------------------------------------------------------------------

FPU_DISPUTE = DisputeProcess(
    utility="FPU",
    display_name="Florida Public Utilities",
    steps=(
        DisputeStep(
            order=1,
            title="Call FPU customer service",
            description=(
                "Call 1-888-220-9356 (Mon–Fri 8:00 AM – 5:00 PM). As a "
                "small utility, FPU generally has shorter queues and direct "
                "access to billing staff."
            ),
            timeline="Same-day resolution possible during business hours",
            contact_method="phone",
        ),
        DisputeStep(
            order=2,
            title="Send certified-mail dispute letter",
            description=(
                "If phone doesn't resolve, mail certified to the FPU "
                "Customer Care team in West Palm Beach. Due to FPU's small "
                "size, the customer care team can escalate directly to "
                "billing supervisors."
            ),
            required_evidence=_STANDARD_ENCLOSURES,
            timeline="Allow 30 days",
            contact_method="certified_mail",
        ),
        DisputeStep(
            order=3,
            title="File Florida PSC consumer complaint",
            description="Same as all FL IOUs.",
            required_evidence=(
                "Dispute letter + certified-mail receipts",
                "Bill copies",
                "Forensic audit exhibit",
            ),
            contact_method="online_form",
        ),
    ),
    required_enclosures_for_written_dispute=_STANDARD_ENCLOSURES,
    typical_resolution_timeline_days=30,
    escalation_notes=(
        "FPU serves only ~30,000 electric customers across two "
        "non-contiguous divisions (NW Florida and Amelia Island). Confirm "
        "the correct service division on your bill — rates are similar "
        "between divisions but not identical in all rate classes."
    ),
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

DISPUTE_PROCESSES: dict[str, DisputeProcess] = {
    "FPL": FPL_DISPUTE,
    "DUKE": DUKE_DISPUTE,
    "TECO": TECO_DISPUTE,
    "FPU": FPU_DISPUTE,
}


def get_dispute_process(utility: str) -> DisputeProcess:
    """Return the dispute workflow for a given utility.

    Raises ``KeyError`` for unregistered utilities. Municipals are outside
    PSC jurisdiction — their dispute paths go through their municipal
    utility board, not this tool.
    """
    key = utility.upper()
    if key not in DISPUTE_PROCESSES:
        raise KeyError(
            f"No dispute process registered for {utility!r}. Registered: "
            f"{sorted(DISPUTE_PROCESSES)}."
        )
    return DISPUTE_PROCESSES[key]
