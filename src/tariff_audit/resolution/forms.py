"""Required forms and filing references for Florida electric utility disputes.

Unlike many state regulatory commissions, the Florida PSC does not require
the consumer to file a specific paper form — a letter or their online
consumer complaint form is sufficient. However, the audit reports this
tool produces function as a **compelling factual exhibit** when attached
to either a utility dispute letter or a PSC complaint.

Individual utilities do not require a proprietary "dispute form" either;
they accept written correspondence that includes the standard elements.
This module catalogs the forms that ARE required and provides filing
instructions.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ResolutionForm:
    """One form a customer must (or should) file as part of dispute resolution."""

    name: str
    jurisdiction: str  # "Florida PSC" | "FPL" | "DUKE" | "TECO" | "FPU"
    url: str = ""
    paper_form_url: str = ""
    filing_instructions: str = ""
    required_for: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""


# ---------------------------------------------------------------------------
# Florida PSC Consumer Complaint Form — the primary regulatory form
# ---------------------------------------------------------------------------

PSC_COMPLAINT_FORM = ResolutionForm(
    name="Florida PSC Consumer Complaint Form",
    jurisdiction="Florida PSC",
    url="https://www.floridapsc.com/consumer-complaint-form",
    paper_form_url=(
        "https://www.floridapsc.com/pscfiles/website-files/PDF/publications/"
        "consumer/brochure/ifyouhaveaproblem.pdf"
    ),
    filing_instructions=(
        "Preferred method — ONLINE:\n"
        "1. Visit floridapsc.com/consumer-complaint-form\n"
        "2. Select 'Electric' under Industry\n"
        "3. Select Complaint Type (e.g. Billing / Overcharge)\n"
        "4. Select your utility from the company list\n"
        "5. Enter contact info (fields with * are required)\n"
        "6. Type your complaint — be specific; attach supporting documents\n"
        "7. Click Submit and RECORD THE TRACKING NUMBER\n"
        "\n"
        "Alternative methods:\n"
        " - Phone: 1-800-342-3552 (M–F 8 AM – 5 PM ET)\n"
        " - Email: contact@psc.state.fl.us\n"
        " - Fax: (850) 487-0509\n"
        " - Mail: FL PSC, Office of Consumer Assistance,\n"
        "         2540 Shumard Oak Blvd, Tallahassee, FL 32399-0850"
    ),
    required_for=(
        "Escalation after utility-level dispute is exhausted",
        "Any complaint where customer believes utility misapplied the PSC "
        "tariff or violated FAC 25-6 rules",
    ),
    notes=(
        "The PSC requires that the customer first attempted to resolve the "
        "dispute with the utility. Attach copies of the utility dispute "
        "letter and any response received (or lack thereof), plus a copy "
        "of the PowerCheck forensic audit report as an exhibit."
    ),
)


# ---------------------------------------------------------------------------
# Utility-level dispute letters
# ---------------------------------------------------------------------------
# Utilities do not publish a standard dispute FORM; a letter that includes
# the standard enclosures (see resolution.dispute_process) is sufficient.
# The entries below exist so the UI can present "required forms" uniformly
# for every step.
# ---------------------------------------------------------------------------

FPL_DISPUTE_LETTER = ResolutionForm(
    name="FPL Billing Dispute Letter",
    jurisdiction="FPL",
    url="",
    filing_instructions=(
        "FPL does not publish a proprietary dispute form. Send a written "
        "letter by USPS Certified Mail with Return Receipt to:\n\n"
        "Florida Power & Light Company\n"
        "Customer Care\n"
        "PO Box 029100\n"
        "Miami, FL 33102-9100\n\n"
        "Include all standard dispute enclosures (see "
        "resolution.dispute_process.FPL_DISPUTE.required_enclosures_for_written_dispute)."
    ),
    required_for=("Formal utility-level dispute prior to PSC escalation",),
)

DUKE_DISPUTE_LETTER = ResolutionForm(
    name="Duke Energy Florida Billing Dispute Letter",
    jurisdiction="DUKE",
    url="",
    filing_instructions=(
        "Duke Energy does not publish a proprietary FL dispute form. Send a "
        "written letter by USPS Certified Mail with Return Receipt to:\n\n"
        "Duke Energy Florida\n"
        "PO Box 70516\n"
        "Charlotte, NC 28272-0516\n\n"
        "Note: Duke Energy handles all FL billing correspondence through "
        "its Charlotte, NC parent-company PO Box."
    ),
    required_for=("Formal utility-level dispute prior to PSC escalation",),
)

TECO_DISPUTE_LETTER = ResolutionForm(
    name="Tampa Electric Billing Dispute Letter",
    jurisdiction="TECO",
    url="",
    filing_instructions=(
        "Tampa Electric does not publish a proprietary dispute form. Send "
        "by USPS Certified Mail with Return Receipt to:\n\n"
        "Tampa Electric\n"
        "PO Box 111\n"
        "Tampa, FL 33601-0111\n\n"
        "DO NOT send disputes to the payments PO Box (31318) — that will "
        "delay processing. Email alternative: wecare@tecoenergy.com."
    ),
    required_for=("Formal utility-level dispute prior to PSC escalation",),
)

FPU_DISPUTE_LETTER = ResolutionForm(
    name="Florida Public Utilities Billing Dispute Letter",
    jurisdiction="FPU",
    url="",
    filing_instructions=(
        "Florida Public Utilities does not publish a proprietary dispute "
        "form. Send by USPS Certified Mail with Return Receipt to:\n\n"
        "Florida Public Utilities Company\n"
        "Customer Care\n"
        "1635 Meathe Drive\n"
        "West Palm Beach, FL 33411"
    ),
    required_for=("Formal utility-level dispute prior to PSC escalation",),
)


# ---------------------------------------------------------------------------
# Registry (utility → applicable forms, in recommended filing order)
# ---------------------------------------------------------------------------

RESOLUTION_FORMS: dict[str, tuple[ResolutionForm, ...]] = {
    "FPL": (FPL_DISPUTE_LETTER, PSC_COMPLAINT_FORM),
    "DUKE": (DUKE_DISPUTE_LETTER, PSC_COMPLAINT_FORM),
    "TECO": (TECO_DISPUTE_LETTER, PSC_COMPLAINT_FORM),
    "FPU": (FPU_DISPUTE_LETTER, PSC_COMPLAINT_FORM),
}


def get_forms_for_utility(utility: str) -> tuple[ResolutionForm, ...]:
    """Return the ordered list of forms required for a dispute against this utility.

    The order is filing order: utility-level dispute first, then PSC
    escalation if unresolved. Raises ``KeyError`` for unknown utilities.
    """
    key = utility.upper()
    if key not in RESOLUTION_FORMS:
        raise KeyError(
            f"No forms registered for utility {utility!r}. "
            f"Registered: {sorted(RESOLUTION_FORMS)}"
        )
    return RESOLUTION_FORMS[key]
