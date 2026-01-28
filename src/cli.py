"""CLI for the Agent Memory System."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .issue import Issue, Status
from .storage import IssueStore, StorageError

console = Console()


@click.group()
def ams() -> None:
    """Agent Memory System - Simple issue tracking for AI agents."""
    pass


@ams.command()
@click.argument("title")
@click.option("-d", "--description", default=None, help="Issue description")
@click.option(
    "--blocked-by",
    multiple=True,
    type=int,
    help="ID of issue that blocks this one (can be used multiple times)",
)
def create(title: str, description: str | None, blocked_by: tuple[int, ...]) -> None:
    """Create a new issue with the given TITLE."""
    try:
        store = IssueStore()

        # Get existing IDs for validation
        existing_ids = store.get_all_ids()

        # Validate blocked_by IDs exist
        blocked_by_list = list(blocked_by)
        if blocked_by_list:
            invalid_ids = set(blocked_by_list) - existing_ids
            if invalid_ids:
                console.print(
                    f"[red]Error:[/red] Cannot block by non-existent issue(s): "
                    f"{sorted(invalid_ids)}"
                )
                raise SystemExit(1)

        # Get next ID and create issue
        issue_id = store.get_next_id()
        issue = Issue.create(
            id=issue_id,
            title=title,
            description=description,
            blocked_by=blocked_by_list,
        )

        # Save to store
        store.save_issue(issue)

        # Success output
        console.print(
            Panel(
                f"[bold green]#{issue_id}[/bold green] {title}",
                title="Issue Created",
                border_style="green",
            )
        )

        if description:
            console.print(f"  Description: {description}")
        if blocked_by_list:
            console.print(f"  Blocked by: {blocked_by_list}")

    except StorageError as e:
        console.print(f"[red]Storage error:[/red] {e}")
        raise SystemExit(1)


def _status_style(status: Status) -> str:
    """Return Rich style for a status."""
    return {
        Status.OPEN: "yellow",
        Status.IN_PROGRESS: "cyan",
        Status.DONE: "green",
    }.get(status, "white")


@ams.command("list")
@click.option("--status", "-s", type=click.Choice(["open", "in-progress", "done"]))
def list_issues(status: str | None) -> None:
    """List all issues in a table."""
    try:
        store = IssueStore()
        issues = store.load_all()

        # Filter by status if provided
        if status:
            filter_status = Status(status)
            issues = [i for i in issues if i.status == filter_status]

        if not issues:
            console.print("[dim]No issues found.[/dim]")
            return

        table = Table(title="Issues")
        table.add_column("ID", style="bold", width=6)
        table.add_column("Status", width=12)
        table.add_column("Title")
        table.add_column("Blocked By", width=12)

        for issue in issues:
            style = _status_style(issue.status)
            blocked = ", ".join(f"#{b}" for b in issue.blocked_by) if issue.blocked_by else "-"
            table.add_row(
                f"#{issue.id}",
                f"[{style}]{issue.status.value}[/{style}]",
                issue.title,
                blocked,
            )

        console.print(table)

    except StorageError as e:
        console.print(f"[red]Storage error:[/red] {e}")
        raise SystemExit(1)


@ams.command()
@click.argument("id", type=int)
def show(id: int) -> None:
    """Show details of issue with given ID."""
    try:
        store = IssueStore()
        issue = store.get_by_id(id)

        if not issue:
            console.print(f"[red]Error:[/red] Issue #{id} not found.")
            raise SystemExit(1)

        # Find what this issue blocks (reverse lookup)
        all_issues = store.load_all()
        blocks = [i.id for i in all_issues if id in i.blocked_by]

        # Build content
        style = _status_style(issue.status)
        lines = [
            f"[bold]Status:[/bold] [{style}]{issue.status.value}[/{style}]",
            f"[bold]Created:[/bold] {issue.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"[bold]Updated:[/bold] {issue.updated_at.strftime('%Y-%m-%d %H:%M')}",
        ]

        if issue.description:
            lines.insert(0, f"\n{issue.description}\n")

        if issue.blocked_by:
            blocked_str = ", ".join(f"#{b}" for b in issue.blocked_by)
            lines.append(f"[bold]Blocked by:[/bold] {blocked_str}")

        if blocks:
            blocks_str = ", ".join(f"#{b}" for b in blocks)
            lines.append(f"[bold]Blocks:[/bold] {blocks_str}")

        console.print(
            Panel(
                "\n".join(lines),
                title=f"[bold]#{issue.id}[/bold] {issue.title}",
                border_style=style,
            )
        )

    except StorageError as e:
        console.print(f"[red]Storage error:[/red] {e}")
        raise SystemExit(1)


@ams.command()
def ready() -> None:
    """Show issues that are ready to work on (unblocked)."""
    try:
        store = IssueStore()
        issues = store.load_all()

        # Ready = open AND no blockers
        ready_issues = [
            i for i in issues
            if i.status == Status.OPEN and not i.blocked_by
        ]

        if not ready_issues:
            console.print("[dim]No ready work. All tasks are blocked or completed.[/dim]")
            return

        table = Table(title="Ready Work")
        table.add_column("ID", style="bold", width=6)
        table.add_column("Title")

        for issue in ready_issues:
            table.add_row(f"#{issue.id}", issue.title)

        console.print(table)

    except StorageError as e:
        console.print(f"[red]Storage error:[/red] {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    ams()
