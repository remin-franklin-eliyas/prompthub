import typer
from pathlib import Path
from rich.console import Console
from core.db import (
    init_db, add_prompt, get_prompt,
    get_all_prompts, add_version,
    get_latest_version, get_all_versions,
    get_version
)
from core.versioning import get_next_version_tag
from core.renderer import (
    render_success, render_error,
    render_commit_success, render_log,
    render_rollback_success, render_prompt_list,
    render_init_success, render_banner, render_diff
)

console = Console()

def custom_help():
    render_banner()
    console.print(" [bold]Usage:[/bold] prompthub [OPTIONS] COMMAND [ARGS]...\n")
    console.print(" [bold]Options:[/bold]")
    console.print("   --help    Show this message and exit.\n")
    console.print(" [bold]Commands:[/bold]")
    console.print("   [cyan]init[/cyan]      Initialise a PromptHub repository")
    console.print("   [cyan]add[/cyan]       Track a prompt file")
    console.print("   [cyan]commit[/cyan]    Commit the current version of a tracked prompt")
    console.print("   [cyan]log[/cyan]       Show version history")
    console.print("   [cyan]rollback[/cyan]  Roll back a prompt to a previous version")
    console.print("")

app = typer.Typer(
    help="PromptHub -- version control for prompts",
    rich_markup_mode="rich",
    add_completion=False
)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        custom_help()
        raise typer.Exit()
    
@app.command()
def init(
    name: str = typer.Option("my-project", help="Repository name"),
    description: str = typer.Option("", help="Repository description")
):
    """Initialise a PromptHub repository in the current directory."""
    db_path = Path(".prompthub/prompthub.db")
    if db_path.exists():
        render_error("Repository already initialised.")
        raise typer.Exit(1)
    init_db()
    render_init_success(name)


@app.command()
def add(
    filepath: str = typer.Argument(..., help="Path to prompt file")
):
    """Track a prompt file."""
    path = Path(filepath)
    if not path.exists():
        render_error(f"File not found: {filepath}")
        raise typer.Exit(1)
    if not Path(".prompthub/prompthub.db").exists():
        render_error("No repository found. Run: prompthub init")
        raise typer.Exit(1)

    name = path.stem
    existing = get_prompt(name)
    if existing:
        render_error(f"Prompt '{name}' is already being tracked.")
        raise typer.Exit(1)

    add_prompt(name, str(path))
    render_success(f"Tracking prompt: [bold cyan]{name}[/bold cyan] ({filepath})")


@app.command()
def commit(
    message: str = typer.Option(..., "-m", help="Commit message"),
    prompt: str = typer.Option(None, "--prompt", "-p", help="Prompt name")
):
    """Commit the current version of a tracked prompt."""
    if not Path(".prompthub/prompthub.db").exists():
        render_error("No repository found. Run: prompthub init")
        raise typer.Exit(1)

    if prompt:
        p = get_prompt(prompt)
        if not p:
            render_error(f"Prompt '{prompt}' not found.")
            raise typer.Exit(1)
        prompts = [p]
    else:
        prompts = get_all_prompts()
        if not prompts:
            render_error("No prompts being tracked. Run: prompthub add <file>")
            raise typer.Exit(1)
        if len(prompts) > 1:
            render_error("Multiple prompts tracked. Specify one with --prompt <name>")
            raise typer.Exit(1)

    p = prompts[0]
    content = Path(p.filepath).read_text()
    version_tag = get_next_version_tag(p.id)

    from core.semantic import generate_embedding
    render_success("Generating embedding...")
    embedding = generate_embedding(content)

    add_version(p.id, version_tag, content, message, embedding)
    render_commit_success(p.name, version_tag, message)


@app.command()
def log(
    prompt: str = typer.Option(None, "--prompt", "-p", help="Prompt name")
):
    """Show version history."""
    if not Path(".prompthub/prompthub.db").exists():
        render_error("No repository found. Run: prompthub init")
        raise typer.Exit(1)

    if prompt:
        p = get_prompt(prompt)
        if not p:
            render_error(f"Prompt '{prompt}' not found.")
            raise typer.Exit(1)
    else:
        prompts = get_all_prompts()
        if not prompts:
            render_error("No prompts being tracked.")
            raise typer.Exit(1)
        if len(prompts) > 1:
            render_error("Multiple prompts tracked. Specify one with --prompt <name>")
            raise typer.Exit(1)
        p = prompts[0]

    versions = get_all_versions(p.id)
    render_log(p.name, versions)

@app.command()
def diff(
    v1: str = typer.Argument(..., help="First version tag e.g. v1"),
    v2: str = typer.Argument(..., help="Second version tag e.g. v2"),
    prompt: str = typer.Option(None, "--prompt", "-p", help="Prompt name")
):
    """Show semantic diff between two versions."""
    if not Path(".prompthub/prompthub.db").exists():
        render_error("No repository found. Run: prompthub init")
        raise typer.Exit(1)

    if prompt:
        p = get_prompt(prompt)
        if not p:
            render_error(f"Prompt '{prompt}' not found.")
            raise typer.Exit(1)
    else:
        prompts = get_all_prompts()
        if not prompts:
            render_error("No prompts being tracked.")
            raise typer.Exit(1)
        if len(prompts) > 1:
            render_error("Multiple prompts tracked. Specify one with --prompt <name>")
            raise typer.Exit(1)
        p = prompts[0]

    version1 = get_version(p.id, v1)
    version2 = get_version(p.id, v2)

    if not version1:
        render_error(f"Version '{v1}' not found.")
        raise typer.Exit(1)
    if not version2:
        render_error(f"Version '{v2}' not found.")
        raise typer.Exit(1)

    from core.semantic import diff_versions
    result = diff_versions(version1, version2)
    render_diff(result)


@app.command()
def rollback(
    version: str = typer.Argument(..., help="Version tag to roll back to e.g. v1"),
    prompt: str = typer.Option(None, "--prompt", "-p", help="Prompt name")
):
    """Roll back a prompt to a previous version."""
    if not Path(".prompthub/prompthub.db").exists():
        render_error("No repository found. Run: prompthub init")
        raise typer.Exit(1)

    if prompt:
        p = get_prompt(prompt)
        if not p:
            render_error(f"Prompt '{prompt}' not found.")
            raise typer.Exit(1)
    else:
        prompts = get_all_prompts()
        if not prompts:
            render_error("No prompts being tracked.")
            raise typer.Exit(1)
        if len(prompts) > 1:
            render_error("Multiple prompts tracked. Specify one with --prompt <name>")
            raise typer.Exit(1)
        p = prompts[0]

    target = get_version(p.id, version)
    if not target:
        render_error(f"Version '{version}' not found for prompt '{p.name}'")
        raise typer.Exit(1)

    Path(p.filepath).write_text(target.content)
    new_tag = get_next_version_tag(p.id)
    add_version(p.id, new_tag, target.content, f"rollback to {version}")
    render_rollback_success(version, new_tag)


if __name__ == "__main__":
    app()