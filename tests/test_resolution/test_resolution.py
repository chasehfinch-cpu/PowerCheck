"""Tests for the resolution / dispute workflow package."""

from __future__ import annotations

import pytest

from tariff_audit.resolution import (
    DISPUTE_PROCESSES,
    FLORIDA_PSC,
    PSC_COMPLAINT_FORM,
    UTILITY_CONTACTS,
    get_dispute_process,
    get_forms_for_utility,
    get_utility_contact,
)

# ---------------------------------------------------------------------------
# Contact info
# ---------------------------------------------------------------------------


def test_all_four_iou_contacts_registered():
    iou_utilities = {"FPL", "DUKE", "TECO", "FPU"}
    registered = set(UTILITY_CONTACTS)
    assert iou_utilities <= registered


def test_psc_contact_present():
    assert FLORIDA_PSC.customer_service_phone == "1-800-342-3552"
    assert "psc.state.fl.us" in FLORIDA_PSC.billing_dispute_email
    assert "2540 Shumard Oak" in FLORIDA_PSC.billing_dispute_mailing_address


def test_fpl_contact_has_dispute_channels():
    c = get_utility_contact("FPL")
    assert c.customer_service_phone.startswith("1-800")
    assert c.billing_dispute_email.endswith("@info.fpl.com")
    assert "Customer Care" in c.billing_dispute_mailing_address


def test_duke_mailing_address_is_charlotte():
    c = get_utility_contact("DUKE")
    assert "Charlotte, NC" in c.billing_dispute_mailing_address


def test_teco_has_wecare_email():
    c = get_utility_contact("TECO")
    assert c.billing_dispute_email == "wecare@tecoenergy.com"
    # Non-payment PO Box is 111
    assert "PO Box 111" in c.billing_dispute_mailing_address


def test_fpu_phone_is_toll_free():
    c = get_utility_contact("FPU")
    assert c.customer_service_phone.startswith("1-888")


def test_unknown_utility_contact_raises():
    with pytest.raises(KeyError):
        get_utility_contact("NOPE")


# ---------------------------------------------------------------------------
# Dispute process
# ---------------------------------------------------------------------------


def test_every_iou_has_dispute_process():
    for utility in ("FPL", "DUKE", "TECO", "FPU"):
        proc = get_dispute_process(utility)
        assert len(proc.steps) >= 3


def test_dispute_steps_are_ordered():
    for proc in DISPUTE_PROCESSES.values():
        orders = [s.order for s in proc.steps]
        assert orders == sorted(orders), f"{proc.utility} steps out of order"


def test_every_dispute_process_escalates_to_psc():
    for proc in DISPUTE_PROCESSES.values():
        psc_step = [s for s in proc.steps if "PSC" in s.title]
        assert len(psc_step) == 1, (
            f"{proc.utility} dispute process must include exactly one "
            f"PSC-escalation step"
        )


def test_certified_mail_step_required_for_every_utility():
    """Certified mail is the evidentiary anchor required before PSC complaint."""
    for proc in DISPUTE_PROCESSES.values():
        certified = [s for s in proc.steps if s.contact_method == "certified_mail"]
        assert len(certified) >= 1, (
            f"{proc.utility} dispute process must include a certified-mail step"
        )


def test_standard_resolution_timeline_is_30_days():
    for proc in DISPUTE_PROCESSES.values():
        assert proc.typical_resolution_timeline_days == 30


def test_duke_escalation_notes_flag_march_2026_storm_removal():
    proc = get_dispute_process("DUKE")
    assert "March" in proc.escalation_notes or "storm" in proc.escalation_notes.lower()


def test_teco_escalation_notes_flag_august_2026_surcharge_sunset():
    proc = get_dispute_process("TECO")
    assert "August" in proc.escalation_notes or "2026" in proc.escalation_notes


# ---------------------------------------------------------------------------
# Forms
# ---------------------------------------------------------------------------


def test_psc_complaint_form_has_url():
    assert PSC_COMPLAINT_FORM.url == "https://www.floridapsc.com/consumer-complaint-form"
    assert "floridapsc.com" in PSC_COMPLAINT_FORM.url


def test_every_iou_lists_two_forms_in_order():
    """Dispute letter first, PSC complaint second."""
    for utility in ("FPL", "DUKE", "TECO", "FPU"):
        forms = get_forms_for_utility(utility)
        assert len(forms) == 2
        # First form is the utility's own dispute letter
        assert utility == forms[0].jurisdiction
        # Second form is the PSC complaint (escalation)
        assert forms[1].jurisdiction == "Florida PSC"


def test_unknown_utility_forms_raises():
    with pytest.raises(KeyError):
        get_forms_for_utility("NOPE")
