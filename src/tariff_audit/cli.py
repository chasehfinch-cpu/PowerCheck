"""Interactive command-line interface for walking through a bill audit.

Run ``tariff-audit`` or ``python -m tariff_audit`` to launch the walkthrough:

1. Select (or auto-detect) the utility
2. See the per-utility bill layout guide
3. Enter values from your bill
4. See the tool's calculation of what the bill SHOULD be
5. See a line-item comparison flagging discrepancies
6. See the utility-specific dispute workflow if findings warrant
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

# Windows legacy consoles default to cp1252 and choke on Unicode such as ≤
# that appears in tariff tier labels. Reconfigure to UTF-8 at import so the
# CLI renders correctly on all Windows shells without user setup.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover — best effort
        pass

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import FloatPrompt, IntPrompt, Prompt
from rich.table import Table

from tariff_audit import __version__
from tariff_audit.engine.bill_composer import compose_expected_bill
from tariff_audit.parsers.bill_layouts import (
    BillLayoutGuide,
    all_layouts,
    detect_layout,
    get_layout,
)
from tariff_audit.resolution import (
    FLORIDA_PSC,
    get_dispute_process,
    get_forms_for_utility,
    get_utility_contact,
)

app = typer.Typer(
    name="tariff-audit",
    help="Forensic audit of Florida electric utility bills.",
    add_completion=False,
    no_args_is_help=False,
)
console = Console()


# ---------------------------------------------------------------------------
# Helper prompts
# ---------------------------------------------------------------------------


def _prompt_decimal(label: str, default: float | None = None) -> Decimal:
    """Prompt for a decimal, converting through str to avoid float drift."""
    value = FloatPrompt.ask(label, default=default, console=console)
    return Decimal(str(value))


def _prompt_date(label: str) -> date:
    """Prompt for a date in YYYY-MM-DD format."""
    while True:
        raw = Prompt.ask(label + " [dim](YYYY-MM-DD)[/dim]", console=console)
        try:
            return datetime.strptime(raw.strip(), "%Y-%m-%d").date()
        except ValueError:
            console.print("[red]  Invalid date. Use YYYY-MM-DD format.[/red]")


def _banner() -> None:
    console.print(
        Panel.fit(
            f"[bold cyan]PowerCheck — TariffAudit FL v{__version__}[/bold cyan]\n"
            "[dim]Florida electric utility bill forensic audit[/dim]\n\n"
            "[yellow]All processing is local. No data leaves your machine.[/yellow]",
            border_style="cyan",
        )
    )


def _pick_utility() -> BillLayoutGuide:
    """Let the user pick or auto-detect a utility."""
    console.print("\n[bold]Step 1 — Identify the utility billing you[/bold]")
    console.print("  [1] Florida Power & Light (FPL)")
    console.print("  [2] Duke Energy Florida")
    console.print("  [3] Tampa Electric (TECO)")
    console.print("  [4] Florida Public Utilities (FPU)")
    console.print("  [5] Auto-detect from pasted bill text")
    choice = Prompt.ask("Choose", choices=["1", "2", "3", "4", "5"], console=console)

    mapping = {"1": "FPL", "2": "DUKE", "3": "TECO", "4": "FPU"}
    if choice in mapping:
        return get_layout(mapping[choice])

    console.print(
        "\n[dim]Paste any portion of your bill text. Finish with an empty line.[/dim]"
    )
    lines: list[str] = []
    while True:
        line = input()
        if not line.strip() and lines:
            break
        lines.append(line)
    text = "\n".join(lines)
    guide = detect_layout(text)
    if guide is None:
        console.print(
            "[red]Could not detect utility from the text. "
            "Falling back to FPL — rerun and choose manually if wrong.[/red]"
        )
        return get_layout("FPL")
    console.print(f"[green]Detected: {guide.display_name}[/green]")
    return guide


def _show_layout_guide(guide: BillLayoutGuide) -> None:
    console.print(f"\n[bold]Step 2 — Where to find each value on your {guide.display_name} bill[/bold]")
    console.print(f"  [dim]Reference: {guide.layout_reference_url}[/dim]\n")

    table = Table(show_lines=False, box=box.SIMPLE_HEAD)
    table.add_column("What to look for", style="cyan", no_wrap=False)
    table.add_column("Where on the bill", style="white")
    table.add_column("Label on bill", style="yellow")
    for loc in guide.locations:
        table.add_row(loc.field_name, loc.bill_section, loc.label_on_bill)
    console.print(table)

    if guide.structural_notes:
        console.print(
            Panel(guide.structural_notes, title="[yellow]Bill structure notes[/yellow]",
                  border_style="yellow")
        )


def _prompt_bill_values(guide: BillLayoutGuide) -> dict:
    """Collect the values needed to run the audit."""
    console.print(f"\n[bold]Step 3 — Enter values from your {guide.display_name} bill[/bold]")
    console.print("[dim]Leave any optional field blank by pressing Enter.[/dim]\n")

    rate_schedule = Prompt.ask(
        "Rate schedule (RS-1 for FPL, RS for TECO/FPU, RS-1 for Duke)",
        default={"FPL": "RS-1", "DUKE": "RS-1", "TECO": "RS", "FPU": "RS"}[guide.utility],
        console=console,
    )
    start = _prompt_date("Billing period start")
    end = _prompt_date("Billing period end")
    kwh = IntPrompt.ask("kWh consumed (from bill)", console=console)
    is_residential = Prompt.ask(
        "Is this a residential account?", choices=["y", "n"], default="y", console=console
    ) == "y"
    total_due = _prompt_decimal("Total amount due on your bill ($)")

    # Optional tax/fee rates for jurisdiction (start conservative: zero)
    console.print(
        "\n[dim]Local tax/franchise rates depend on your city/county. "
        "If you don't know, enter 0 and the tool will compute without the "
        "local layer (state Gross Receipts Tax is always applied).[/dim]"
    )
    pst_rate_pct = FloatPrompt.ask(
        "Municipal Public Service Tax rate (%)", default=0.0, console=console
    )
    franchise_rate_pct = FloatPrompt.ask(
        "Franchise Fee rate (%)", default=0.0, console=console
    )

    return {
        "rate_schedule": rate_schedule,
        "start": start,
        "end": end,
        "kwh": kwh,
        "is_residential": is_residential,
        "total_due": total_due,
        "pst_rate": Decimal(str(pst_rate_pct / 100)),
        "franchise_rate": Decimal(str(franchise_rate_pct / 100)),
    }


def _run_audit(guide: BillLayoutGuide, values: dict) -> None:
    console.print("\n[bold]Step 4 — Computing what your bill should be per PSC tariff[/bold]")

    try:
        expected = compose_expected_bill(
            guide.utility,
            values["rate_schedule"],
            billing_period_start=values["start"],
            billing_period_end=values["end"],
            total_kwh=values["kwh"],
            is_residential=values["is_residential"],
            municipal_utility_tax_rate=values["pst_rate"],
            franchise_fee_rate=values["franchise_rate"],
        )
    except LookupError as err:
        console.print(f"[red]No tariff registered: {err}[/red]")
        console.print(
            "[yellow]This utility/rate-schedule/date combination does not yet have "
            "verified tariff data. See the module docstring for what's needed.[/yellow]"
        )
        return

    # Show segments (usually one, unless the period spans a rate change)
    console.print(f"[green]  Billing period: {expected.billing_days} days "
                  f"({expected.billing_period_start} to {expected.billing_period_end})[/green]")
    if len(expected.segments) > 1:
        console.print(
            f"[yellow]  Note: your billing period spans a rate change — "
            f"split into {len(expected.segments)} sub-periods.[/yellow]"
        )

    # Expected breakdown table
    table = Table(title="Expected bill (per PSC-approved tariff)", box=box.SIMPLE_HEAVY)
    table.add_column("Line item", style="cyan")
    table.add_column("Amount", justify="right", style="white")

    seg0 = expected.segments[0].calculated
    table.add_row("Base charge", f"${seg0.base_charge}")
    for label, amt in seg0.energy_charge_by_tier.items():
        table.add_row(f"Energy — {label}", f"${amt}")
    for label, amt in seg0.fuel_charge_by_tier.items():
        table.add_row(f"Fuel / Purchased Power — {label}", f"${amt}")
    if seg0.conservation:
        table.add_row("Conservation", f"${seg0.conservation}")
    if seg0.capacity:
        table.add_row("Capacity", f"${seg0.capacity}")
    if seg0.environmental:
        table.add_row("Environmental", f"${seg0.environmental}")
    if seg0.storm_protection:
        table.add_row("Storm Protection", f"${seg0.storm_protection}")
    if seg0.storm_restoration_surcharge:
        table.add_row("Storm Restoration Surcharge", f"${seg0.storm_restoration_surcharge}")
    if seg0.transition_credit:
        table.add_row("Transition Rider/Credit", f"${seg0.transition_credit}")
    for name, amt in seg0.additional_riders.items():
        table.add_row(name, f"${amt}")
    table.add_row("[bold]Tariff subtotal[/bold]",
                  f"[bold]${expected.tariff_subtotal}[/bold]")
    table.add_row(
        "+ Florida Gross Receipts Tax",
        f"${expected.taxes.gross_receipts_tax}",
    )
    if expected.taxes.municipal_utility_tax:
        table.add_row("+ Municipal Utility Tax",
                      f"${expected.taxes.municipal_utility_tax}")
    if expected.taxes.franchise_fee:
        table.add_row("+ Franchise Fee", f"${expected.taxes.franchise_fee}")
    if not expected.is_residential and expected.taxes.sales_tax:
        table.add_row("+ State Sales Tax", f"${expected.taxes.sales_tax}")
    table.add_row("[bold green]Expected total[/bold green]",
                  f"[bold green]${expected.total_due}[/bold green]")
    console.print(table)

    # Comparison
    actual = values["total_due"]
    delta = actual - expected.total_due
    pct = (delta / expected.total_due * 100) if expected.total_due else Decimal(0)

    console.print("\n[bold]Step 5 — Comparison[/bold]")
    console.print(f"  Your bill:     [white]${actual}[/white]")
    console.print(f"  Expected:      [white]${expected.total_due}[/white]")

    if delta > Decimal("0.50"):
        console.print(
            f"  Difference:    [red]+${delta} ({pct:.2f}% overcharge)[/red]"
        )
        _show_dispute_workflow(guide, overcharge=delta)
    elif delta < Decimal("-0.50"):
        console.print(
            f"  Difference:    [yellow]${delta} (bill is LESS than expected — "
            f"potential undercharge / missing line items)[/yellow]"
        )
    else:
        console.print(
            f"  Difference:    [green]${delta} — bill is consistent with PSC tariff.[/green]"
        )


def _show_dispute_workflow(guide: BillLayoutGuide, overcharge: Decimal) -> None:
    console.print(f"\n[bold red]Step 6 — Dispute workflow for {guide.display_name}[/bold red]")
    contact = get_utility_contact(guide.utility)
    process = get_dispute_process(guide.utility)
    forms = get_forms_for_utility(guide.utility)

    # Contact card
    console.print(
        Panel(
            f"[cyan]Phone:[/cyan]   {contact.customer_service_phone}\n"
            f"[cyan]Hours:[/cyan]   {contact.customer_service_hours}\n"
            f"[cyan]Email:[/cyan]   {contact.billing_dispute_email or '(none published)'}\n"
            f"[cyan]Mail:[/cyan]\n{contact.billing_dispute_mailing_address}\n\n"
            f"[cyan]Online:[/cyan] {contact.online_portal}",
            title=f"Contact {contact.display_name}",
            border_style="red",
        )
    )

    # Ordered steps
    console.print("\n[bold]Steps:[/bold]")
    for step in process.steps:
        console.print(f"  [cyan]{step.order}.[/cyan] [bold]{step.title}[/bold] "
                      f"[dim]({step.contact_method})[/dim]")
        console.print(f"     {step.description}")
        if step.timeline:
            console.print(f"     [dim]Timeline: {step.timeline}[/dim]")

    # Forms
    console.print("\n[bold]Forms you'll need (filing order):[/bold]")
    for form in forms:
        console.print(f"  • [cyan]{form.name}[/cyan] ({form.jurisdiction})")
        if form.url:
            console.print(f"    {form.url}")

    # PSC escalation contact
    console.print(
        Panel(
            f"[cyan]PSC complaint:[/cyan] {FLORIDA_PSC.online_portal}\n"
            f"[cyan]PSC phone:[/cyan]     {FLORIDA_PSC.customer_service_phone}\n"
            f"[dim]Required AFTER 30 days with no satisfactory utility response.[/dim]",
            title="Florida Public Service Commission — escalation",
            border_style="yellow",
        )
    )


# ---------------------------------------------------------------------------
# Typer commands
# ---------------------------------------------------------------------------


@app.command()
def audit() -> None:
    """Interactive end-to-end bill audit walkthrough (default command)."""
    _banner()
    guide = _pick_utility()
    _show_layout_guide(guide)
    values = _prompt_bill_values(guide)
    _run_audit(guide, values)


@app.command()
def utilities() -> None:
    """List all utilities with registered bill layout guides."""
    _banner()
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Layout documented", style="green")
    for g in all_layouts():
        table.add_row(g.utility, g.display_name, "yes" if g.locations else "no")
    console.print(table)


@app.command()
def contacts(
    utility: Annotated[
        str,
        typer.Argument(help="FPL, DUKE, TECO, FPU, or PSC"),
    ],
) -> None:
    """Show dispute-channel contact info for a utility."""
    try:
        c = get_utility_contact(utility)
    except KeyError as err:
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(1) from err
    console.print(
        Panel(
            f"[bold]{c.display_name}[/bold]\n\n"
            f"[cyan]Customer service:[/cyan] {c.customer_service_phone}\n"
            f"[cyan]Hours:[/cyan]            {c.customer_service_hours}\n"
            f"[cyan]Dispute email:[/cyan]    {c.billing_dispute_email or '(none)'}\n"
            f"[cyan]Dispute mail:[/cyan]\n{c.billing_dispute_mailing_address}\n\n"
            f"[cyan]Online:[/cyan] {c.online_portal}",
            border_style="cyan",
        )
    )


def main() -> None:
    """Entry point for the ``tariff-audit`` console script."""
    app()


if __name__ == "__main__":
    main()
