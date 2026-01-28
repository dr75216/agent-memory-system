"""CLI for the Agent Memory System."""

import click
from rich.console import Console
from rich.panel import Panel

from .issue import Issue
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


if __name__ == "__main__":
    ams()
