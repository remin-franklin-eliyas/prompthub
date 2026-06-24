from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box
from models.schemas import Version
import pyfiglet

console = Console()


def render_success(message: str):
    console.print(f"[bold green]✓[/bold green] {message}")


def render_error(message: str):
    console.print(f"[bold red]✗[/bold red] {message}")


def render_commit_success(prompt_name: str, version_tag: str, message: str):
    console.print(
        f"[bold green]✓[/bold green] Committed "
        f"[bold cyan]{version_tag}[/bold cyan] of "
        f"[bold]{prompt_name}[/bold] — {message}"
    )


def render_log(prompt_name: str, versions: list[Version]):
    if not versions:
        render_error(f"No versions found for '{prompt_name}'")
        return

    table = Table(
        title=f"Version History — {prompt_name}",
        box=box.ROUNDED,
        show_lines=True
    )

    table.add_column("Version", style="bold cyan", width=10)
    table.add_column("Message", style="white")
    table.add_column("Committed At", style="dim", width=22)

    for v in reversed(versions):
        table.add_row(
            v.version_tag,
            v.message,
            str(v.committed_at)
        )

    console.print(table)


def render_rollback_success(target_tag: str, new_tag: str):
    console.print(
        f"[bold green]✓[/bold green] Rolled back to "
        f"[bold cyan]{target_tag}[/bold cyan]. "
        f"New commit created: [bold cyan]{new_tag}[/bold cyan]"
    )


def render_prompt_list(prompts):
    if not prompts:
        render_error("No prompts being tracked. Run: prompthub add <file>")
        return

    table = Table(
        title="Tracked Prompts",
        box=box.ROUNDED,
        show_lines=True
    )

    table.add_column("Name", style="bold cyan")
    table.add_column("Filepath", style="white")
    table.add_column("Created At", style="dim", width=22)

    for p in prompts:
        table.add_row(p.name, p.filepath, str(p.created_at))

    console.print(table)


def render_init_success(repo_name: str):
    console.print(
        Panel(
            f"[bold green]Initialised PromptHub repository[/bold green]\n"
            f"[dim]Name:[/dim] [bold]{repo_name}[/bold]\n"
            f"[dim]Database:[/dim] .prompthub/prompthub.db",
            title="[bold]PromptHub[/bold]",
            box=box.ROUNDED
        )
    )

def render_diff(diff: dict):
    distance = diff["distance"]
    description = diff["description"]
    structural = diff["structural_changes"]
    char_delta = diff["char_delta"]

    console.print(f"\n[bold]PROMPT DIFF[/bold]  "
                  f"[cyan]{diff['v1_tag']}[/cyan] → [cyan]{diff['v2_tag']}[/cyan]\n")
    console.print("─" * 45)

    if distance is not None:
        color = "green" if distance < 0.25 else "yellow" if distance < 0.45 else "red"
        console.print(f"Semantic distance:  [{color}]{distance}[/{color}]  "
                      f"[dim]({description})[/dim]\n")
    else:
        console.print("[yellow]No embeddings found. Commit both versions first.[/yellow]\n")

    if structural:
        console.print("[bold]STRUCTURAL CHANGES[/bold]")
        for change in structural:
            if change["type"] == "added":
                console.print(f"  [green]+[/green] Added: {change['category']} "
                              f"[dim]{change.get('detail', '')}[/dim]")
            elif change["type"] == "removed":
                console.print(f"  [red]-[/red] Removed: {change['category']} "
                              f"[dim]{change.get('detail', '')}[/dim]")
            elif change["type"] == "modified":
                console.print(f"  [yellow]~[/yellow] Modified: {change['category']} "
                              f"[dim]{change.get('detail', '')}[/dim]")
    else:
        console.print("[bold]STRUCTURAL CHANGES[/bold]")
        console.print("  [dim]No structural changes detected[/dim]")

    console.print(f"\n[bold]CHARACTER DELTA[/bold]")
    console.print(f"  v1: {diff['v1_chars']} chars")
    console.print(f"  v2: {diff['v2_chars']} chars")

    delta_color = "green" if char_delta < 0 else "red" if char_delta > 0 else "dim"
    sign = "+" if char_delta > 0 else ""
    console.print(f"  Δ:  [{delta_color}]{sign}{char_delta} chars[/{delta_color}]\n")

def render_banner():
    banner = pyfiglet.figlet_format("PromptHub", font="doom")
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print("[dim]  version control for prompts[/dim]")
    console.print("[dim]  v0.1.0 · built by Remin Franklin[/dim]\n")

def render_regression(comparisons: list[dict], v1_tag: str, v2_tag: str):
    console.print(f"\n[bold]REGRESSION REPORT[/bold]  "
                  f"[cyan]{v1_tag}[/cyan] → [cyan]{v2_tag}[/cyan]\n")
    console.print("─" * 45)

    for comp in comparisons:
        status_color = "green" if comp["status"] == "STABLE" else "yellow"
        console.print(f"\n[bold]Test:[/bold] [white]{comp['test_name']}[/white]")
        console.print(f"  Status:        [{status_color}]{comp['status']}[/{status_color}]")
        console.print(f"  Semantic shift: {comp['distance']}  "
                      f"[dim]({comp['description']})[/dim]")
        console.print(f"\n  [dim]v1 output:[/dim]")
        console.print(f"  [white]{comp['v1_output'][:200]}[/white]")
        console.print(f"\n  [dim]v2 output:[/dim]")
        console.print(f"  [cyan]{comp['v2_output'][:200]}[/cyan]")
        console.print("")