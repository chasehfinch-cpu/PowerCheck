"""Registry for looking up tariff schedules by utility, rate class, and date.

Individual utility/rate-class modules register their schedules at import time.
Lookups are deterministic: the registry selects the one schedule whose
``(effective_date, expiration_date)`` window contains the requested date.

If multiple schedules overlap, :func:`get_tariff` raises ``LookupError`` — this
is a data-integrity failure, not a runtime condition, and must be fixed in the
tariff data.
"""

from __future__ import annotations

from datetime import date

from tariff_audit.tariffs.models import TariffSchedule

_REGISTRY: dict[tuple[str, str], list[TariffSchedule]] = {}


def register_tariff(schedule: TariffSchedule) -> None:
    """Add a schedule to the registry. Called from tariff data modules at import."""
    key = (schedule.utility.upper(), schedule.rate_schedule.upper())
    _REGISTRY.setdefault(key, []).append(schedule)


def get_tariff(utility: str, rate_schedule: str, on_date: date) -> TariffSchedule:
    """Return the tariff schedule effective for ``utility``/``rate_schedule`` on ``on_date``.

    Raises
    ------
    LookupError
        If no schedule covers the date, or if multiple schedules overlap.
    """
    # Ensure utility tariff modules are loaded (lazy import to avoid cycles).
    _ensure_loaded()

    key = (utility.upper(), rate_schedule.upper())
    schedules = _REGISTRY.get(key, [])
    if not schedules:
        raise LookupError(
            f"No tariff registered for utility={utility!r} rate_schedule={rate_schedule!r}"
        )

    matches = [s for s in schedules if s.covers(on_date)]
    if not matches:
        available = ", ".join(
            f"{s.effective_date}→{s.expiration_date or 'open'}" for s in schedules
        )
        raise LookupError(
            f"No {utility} {rate_schedule} tariff covers {on_date}. Available: {available}"
        )
    if len(matches) > 1:
        raise LookupError(
            f"Overlapping {utility} {rate_schedule} tariffs cover {on_date}: "
            f"{[m.effective_date for m in matches]}. Fix tariff data."
        )
    return matches[0]


def registered_utilities() -> list[str]:
    """List all utilities with at least one registered rate schedule."""
    _ensure_loaded()
    return sorted({util for (util, _rate) in _REGISTRY})


_LOADED = False


def _ensure_loaded() -> None:
    global _LOADED
    if _LOADED:
        return
    # Import for side effects: each module calls register_tariff() at import time.
    # Keep this list explicit so test failures point at a specific module.
    from tariff_audit.tariffs.fpl import rs1 as _fpl_rs1  # noqa: F401

    _LOADED = True
