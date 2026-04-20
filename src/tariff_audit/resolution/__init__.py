"""Utility-specific dispute and resolution workflow data.

Answers three practical end-user questions:

1. **Who billed me?** — ``parsers.detector.detect_utility_name``
2. **Where do I find each value on my bill?** —
   ``parsers.bill_layouts.get_layout``
3. **How do I dispute it?** — this package.

Contents:

- :mod:`contact_info` — dispute-department phone / email / mailing
  addresses for each Florida IOU and the PSC.
- :mod:`dispute_process` — step-by-step resolution workflow for each
  utility, including timeline requirements and required enclosures.
- :mod:`forms` — links and filing instructions for the PSC consumer
  complaint form and any utility-specific required forms.
"""

from tariff_audit.resolution.contact_info import (
    FLORIDA_PSC,
    UTILITY_CONTACTS,
    UtilityContact,
    get_utility_contact,
)
from tariff_audit.resolution.dispute_process import (
    DISPUTE_PROCESSES,
    DisputeProcess,
    DisputeStep,
    get_dispute_process,
)
from tariff_audit.resolution.forms import (
    PSC_COMPLAINT_FORM,
    RESOLUTION_FORMS,
    ResolutionForm,
    get_forms_for_utility,
)

__all__ = [
    "DISPUTE_PROCESSES",
    "DisputeProcess",
    "DisputeStep",
    "FLORIDA_PSC",
    "PSC_COMPLAINT_FORM",
    "RESOLUTION_FORMS",
    "ResolutionForm",
    "UTILITY_CONTACTS",
    "UtilityContact",
    "get_dispute_process",
    "get_forms_for_utility",
    "get_utility_contact",
]
