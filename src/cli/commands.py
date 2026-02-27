"""
CLI commands using Typer - API client mode.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from src.api.client import APIClient

console = Console()
app = typer.Typer(help="Stealth Browser CLI")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CLISession:
    """Manage API client for CLI."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.client = APIClient(base_url)

    def cleanup(self):
        self.client.close()


session = CLISession()


@app.callback()
def main():
    """Stealth Browser - Antidetect Browser System V2"""
    pass


@app.command()
def open(
    name: str = typer.Option(..., "--name", "-n", help="Profile name"),
    proxy: Optional[str] = typer.Option(None, "--proxy", "-p", help="Proxy URL"),
    user_agent: Optional[str] = typer.Option(None, "--ua", help="Custom User-Agent"),
    headless: bool = typer.Option(
        True, "--headless/--no-headless", help="Run headless"
    ),
):
    """Open a new browser session."""
    try:
        profile_data = {
            "name": name,
            "proxy": proxy,
            "user_agent": user_agent,
            "headless": headless,
        }
        session_info = session.client.create_session(profile_data=profile_data)
        if session_info:
            console.print(f"[green]Session created:[/green] {session_info.session_id}")
            console.print(f"[cyan]Profile:[/cyan] {session_info.profile_name}")
        else:
            console.print("[red]Failed to create session[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def navigate(
    session_id: str,
    url: str,
):
    """Navigate to a URL."""
    try:
        session.client.navigate(session_id, url)
        console.print(f"[green]Navigated to:[/green] {url}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def click(
    session_id: str,
    selector: str,
):
    """Click an element."""
    try:
        session.client.click(session_id, selector)
        console.print(f"[green]Clicked:[/green] {selector}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def type_text(
    session_id: str,
    selector: str,
    text: str,
):
    """Type text into an element."""
    try:
        session.client.type_text(session_id, selector, text)
        console.print(f"[green]Typed:[/green] {text} -> {selector}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def screenshot(
    session_id: str,
    path: str = "screenshot.png",
):
    """Take a screenshot."""
    try:
        session.client.screenshot(session_id, path)
        console.print(f"[green]Screenshot saved:[/green] {path}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def execute(
    session_id: str,
    script: str,
):
    """Execute JavaScript."""
    try:
        result = session.client.execute_script(session_id, script)
        console.print(f"[green]Result:[/green] {result}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def list_sessions():
    """List all active sessions."""
    try:
        sessions = session.client.list_sessions()

        if not sessions:
            console.print("[yellow]No active sessions[/yellow]")
            return

        table = Table(title="Active Sessions")
        table.add_column("Session ID", style="cyan")
        table.add_column("Profile", style="green")
        table.add_column("Started", style="blue")
        table.add_column("Status", style="magenta")

        for s in sessions:
            table.add_row(s.session_id, s.profile_name, s.started_at, s.status)

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def close(
    session_id: str,
):
    """Close a session."""
    try:
        session.client.close_session(session_id)
        console.print(f"[green]Session closed:[/green] {session_id}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command("list-profiles")
def list_profiles():
    """List all profiles."""
    try:
        profiles = session.client.get_profiles()

        if not profiles:
            console.print("[yellow]No profiles[/yellow]")
            return

        table = Table(title="Profiles")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Browser", style="blue")
        table.add_column("Proxy", style="magenta")
        table.add_column("Headless", style="yellow")

        for p in profiles:
            table.add_row(
                str(p.id), p.name, p.browser_engine, p.proxy or "None", str(p.headless)
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command("create-profile")
def create_profile(
    name: str = typer.Option(..., "--name", "-n", help="Profile name"),
    proxy: Optional[str] = typer.Option(None, "--proxy", "-p", help="Proxy URL"),
    user_agent: Optional[str] = typer.Option(None, "--ua", help="Custom User-Agent"),
    resolution: str = typer.Option(
        "1920x1080", "--resolution", "-r", help="Screen resolution"
    ),
    timezone: Optional[str] = typer.Option(None, "--timezone", "-t", help="Timezone"),
    language: Optional[str] = typer.Option(None, "--language", "-l", help="Language"),
    headless: bool = typer.Option(
        True, "--headless/--no-headless", help="Run headless"
    ),
):
    """Create a new profile."""
    try:
        profile_data = {
            "name": name,
            "proxy": proxy,
            "user_agent": user_agent,
            "resolution": resolution,
            "timezone": timezone,
            "language": language,
            "headless": headless,
        }
        result = session.client.create_profile(profile_data)
        if result:
            console.print(f"[green]Profile created:[/green] {name}")
        else:
            console.print("[red]Failed to create profile[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command("delete-profile")
def delete_profile(
    profile_id: int = typer.Argument(..., help="Profile ID"),
):
    """Delete a profile."""
    try:
        result = session.client.delete_profile(profile_id)
        if result:
            console.print(f"[green]Profile deleted:[/green] {profile_id}")
        else:
            console.print("[red]Failed to delete profile[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command("get-session")
def get_session(
    session_id: str = typer.Argument(..., help="Session ID"),
):
    """Get session details."""
    try:
        session_info = session.client.get_session(session_id)
        if session_info:
            console.print(f"[cyan]Session ID:[/cyan] {session_info.session_id}")
            console.print(f"[green]Profile:[/green] {session_info.profile_name}")
            console.print(f"[blue]Started:[/green] {session_info.started_at}")
            console.print(f"[magenta]Status:[/cyan] {session_info.status}")
        else:
            console.print("[red]Session not found[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def health():
    """Check API health status."""
    try:
        result = session.client.health_check()
        console.print(f"[green]Status:[/green] {result.get('status', 'unknown')}")
        console.print(f"[cyan]Sessions:[/green] {result.get('sessions', 0)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command("validate-proxy")
def validate_proxy(
    proxy: str = typer.Option(..., "--proxy", "-p", help="Proxy URL"),
):
    """Validate a proxy."""
    try:
        result = session.client.validate_proxy(proxy)
        if result.get("valid"):
            console.print(f"[green]Proxy is valid[/green]")
        else:
            console.print(
                f"[red]Proxy is invalid:[/red] {result.get('message', 'Unknown error')}"
            )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command("clone-profile")
def clone_profile(
    profile_id: int = typer.Argument(..., help="Source Profile ID"),
    new_name: str = typer.Option(..., "--name", "-n", help="New profile name"),
):
    """Clone a profile."""
    try:
        result = session.client.clone_profile(profile_id, new_name)
        if result:
            console.print(f"[green]Profile cloned:[/green] {new_name}")
        else:
            console.print("[red]Failed to clone profile[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command("export-profile")
def export_profile(
    profile_id: int = typer.Argument(..., help="Profile ID"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
):
    """Export a profile to JSON file."""
    try:
        result = session.client.export_profile(profile_id)
        if result:
            import json

            data = json.dumps(result.get("data", {}), indent=2)
            if output:
                Path(output).write_text(data)
                console.print(f"[green]Profile exported to:[/green] {output}")
            else:
                console.print(data)
        else:
            console.print("[red]Failed to export profile[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command("import-profile")
def import_profile(
    input_file: str = typer.Argument(..., help="Input JSON file path"),
):
    """Import a profile from JSON file."""
    try:
        import json

        profile_data = json.loads(Path(input_file).read_text())
        result = session.client.import_profile(profile_data)
        if result:
            console.print(
                f"[green]Profile imported:[/green] {profile_data.get('name')}"
            )
        else:
            console.print("[red]Failed to import profile[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()
