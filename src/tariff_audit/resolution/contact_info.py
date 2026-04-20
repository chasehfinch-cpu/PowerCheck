"""Dispute-department contact info for each Florida IOU and the PSC.

Each :class:`UtilityContact` contains the customer-facing channels a
resident would use to initiate a billing dispute. The Florida Public
Service Commission is the regulatory backstop once utility-level
escalation fails.

Sources: each utility's official "Contact Us" page and the Florida PSC.
Contact details change over time — a production audit workflow should
re-verify before mailing a certified-mail dispute letter.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UtilityContact:
    """Dispute-channel contact info for one utility (or the PSC)."""

    utility: str  # "FPL" | "DUKE" | "TECO" | "FPU" | "PSC"
    display_name: str
    customer_service_phone: str
    customer_service_hours: str = ""
    billing_dispute_phone: str = ""
    billing_dispute_email: str = ""
    billing_dispute_mailing_address: str = ""  # multi-line, for certified mail
    outage_phone: str = ""
    online_portal: str = ""
    corporate_hq: str = ""
    relay_service: str = "711 (Florida Relay Service for hearing/speech impaired)"
    notes: str = ""


# ---------------------------------------------------------------------------
# Florida Public Service Commission (regulatory escalation)
# ---------------------------------------------------------------------------

FLORIDA_PSC = UtilityContact(
    utility="PSC",
    display_name="Florida Public Service Commission",
    customer_service_phone="1-800-342-3552",
    customer_service_hours="Monday–Friday 8:00 AM – 5:00 PM ET",
    billing_dispute_phone="1-800-342-3552",
    billing_dispute_email="contact@psc.state.fl.us",
    billing_dispute_mailing_address=(
        "Florida Public Service Commission\n"
        "Office of Consumer Assistance\n"
        "2540 Shumard Oak Boulevard\n"
        "Tallahassee, FL 32399-0850"
    ),
    online_portal="https://www.floridapsc.com/consumer-complaint-form",
    notes=(
        "The PSC does not adjust a customer's bill directly; it investigates "
        "whether the utility complied with tariff and FAC 25-6 rules and can "
        "order the utility to refund or correct. Complaints are logged and "
        "tracked — obtain the tracking number after submission. Customers "
        "MUST have first contacted the utility and allowed a reasonable "
        "resolution window before the PSC will intervene."
    ),
)


# ---------------------------------------------------------------------------
# Florida Power & Light (FPL)
# ---------------------------------------------------------------------------

FPL_CONTACT = UtilityContact(
    utility="FPL",
    display_name="Florida Power & Light",
    customer_service_phone="1-800-226-3545",
    customer_service_hours="24 hours / 7 days for billing inquiries",
    billing_dispute_phone="1-800-226-3545",
    billing_dispute_email="fpl-account-management@info.fpl.com",
    billing_dispute_mailing_address=(
        "Florida Power & Light Company\n"
        "Customer Care\n"
        "PO Box 029100\n"
        "Miami, FL 33102-9100"
    ),
    outage_phone="1-800-468-8243",
    online_portal="https://www.fpl.com/support/contact.html",
    corporate_hq=(
        "Florida Power & Light Company\n"
        "700 Universe Boulevard\n"
        "Juno Beach, FL 33408"
    ),
    notes=(
        "FPL customer service is 24/7 for billing issues. For formal written "
        "disputes (required before PSC escalation), send by certified mail to "
        "the Customer Care PO Box in Miami. Separate NW Florida (former Gulf) "
        "support is available at fpl.com/northwest."
    ),
)


# ---------------------------------------------------------------------------
# Duke Energy Florida
# ---------------------------------------------------------------------------

DUKE_CONTACT = UtilityContact(
    utility="DUKE",
    display_name="Duke Energy Florida",
    customer_service_phone="1-800-700-8744",
    customer_service_hours="Monday–Friday 7:00 AM – 7:00 PM ET",
    billing_dispute_phone="1-800-700-8744",
    billing_dispute_mailing_address=(
        "Duke Energy Florida\n"
        "PO Box 70516\n"
        "Charlotte, NC 28272-0516"
    ),
    online_portal="https://www.duke-energy.com/customer-service",
    notes=(
        "Duke Energy Florida's billing mail is handled through the parent "
        "company's Charlotte, NC address. For expedited dispute handling "
        "call during business hours Mon–Fri. Alternative residential line: "
        "1-800-777-9898 (broader Duke Energy, will route to FL billing)."
    ),
)


# ---------------------------------------------------------------------------
# Tampa Electric (TECO)
# ---------------------------------------------------------------------------

TECO_CONTACT = UtilityContact(
    utility="TECO",
    display_name="Tampa Electric",
    customer_service_phone="1-877-588-1010",
    customer_service_hours="Monday–Friday 7:30 AM – 6:00 PM ET",
    billing_dispute_phone="1-877-588-1010",
    billing_dispute_email="wecare@tecoenergy.com",
    billing_dispute_mailing_address=(
        "Tampa Electric\n"
        "PO Box 111\n"
        "Tampa, FL 33601-0111"
    ),
    outage_phone="1-877-588-1010",
    online_portal="https://www.tampaelectric.com/contact/",
    notes=(
        "PO Box 111 is the address for written questions, concerns, and "
        "complaints (NOT the payment address — payments go to PO Box 31318). "
        "Email wecare@tecoenergy.com is monitored by the Customer Care team."
    ),
)


# ---------------------------------------------------------------------------
# Florida Public Utilities (FPU)
# ---------------------------------------------------------------------------

FPU_CONTACT = UtilityContact(
    utility="FPU",
    display_name="Florida Public Utilities",
    customer_service_phone="1-888-220-9356",
    customer_service_hours="Monday–Friday 8:00 AM – 5:00 PM ET",
    billing_dispute_phone="1-888-220-9356",
    billing_dispute_mailing_address=(
        "Florida Public Utilities Company\n"
        "Customer Care\n"
        "1635 Meathe Drive\n"
        "West Palm Beach, FL 33411"
    ),
    outage_phone="1-800-427-7712",
    online_portal="https://fpuc.com/customer-care/",
    notes=(
        "FPU is a small utility (~30,000 electric customers in NW + NE "
        "Florida divisions). Their parent company is Chesapeake Utilities. "
        "For accessibility concerns, contact accessibility@chpk.com."
    ),
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

UTILITY_CONTACTS: dict[str, UtilityContact] = {
    "FPL": FPL_CONTACT,
    "DUKE": DUKE_CONTACT,
    "TECO": TECO_CONTACT,
    "FPU": FPU_CONTACT,
    "PSC": FLORIDA_PSC,
}


def get_utility_contact(utility: str) -> UtilityContact:
    """Return the contact record for a utility or the PSC.

    Raises ``KeyError`` for unknown utilities. Municipal / cooperative
    utilities are not covered because they are not PSC-regulated —
    disputes for those go directly through the municipality.
    """
    key = utility.upper()
    if key not in UTILITY_CONTACTS:
        raise KeyError(
            f"No contact record for {utility!r}. Registered: "
            f"{sorted(UTILITY_CONTACTS)}. Municipal and cooperative "
            f"utilities are not covered (not PSC-regulated)."
        )
    return UTILITY_CONTACTS[key]
