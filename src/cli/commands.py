"""
CLI commands using Typer.
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from src.browser.manager import BrowserManager, ProfileConfig

console = Console()
app = typer.Typer(help="Stealth Browser CLI")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SessionManager:
    """Manage browser sessions across CLI commands."""
    
    def __init__(self):
        self.manager: Optional[BrowserManager] = None
    
    async def get_manager(self) -> BrowserManager:
        if self.manager is None:
            self.manager = BrowserManager()
            await self.manager.start()
        return self.manager
    
    async def cleanup(self):
        if self.manager:
            await self.manager.stop()
            self.manager = None


session_manager = SessionManager()


@app.callback()
def main():
    """Stealth Browser - Antidetect Browser System V2"""
    pass


@app.command()
def open(
    name: str = typer.Option(..., "--name", "-n", help="Profile name"),
    proxy: Optional[str] = typer.Option(None, "--proxy", "-p", help="Proxy URL"),
    user_agent: Optional[str] = typer.Option(None, "--ua", help="Custom User-Agent"),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="Run headless"),
):
    """Open a new browser session."""
    async def run():
        manager = await session_manager.get_manager()
        
        config = ProfileConfig(
            name=name,
            proxy=proxy,
            user_agent=user_agent,
            headless=headless,
        )
        
        session = await manager.create_session(config)
        console.print(f"[green]Session created:[/green] {session.session_id}")
        console.print(f"[cyan]Profile:[/cyan] {session.profile_name}")
        
    asyncio.run(run())


@app.command()
def navigate(
    session_id: str,
    url: str,
):
    """Navigate to a URL."""
    async def run():
        manager = await session_manager.get_manager()
        try:
            await manager.navigate(session_id, url)
            console.print(f"[green]Navigated to:[/green] {url}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    asyncio.run(run())


@app.command()
def click(
    session_id: str,
    selector: str,
):
    """Click an element."""
    async def run():
        manager = await session_manager.get_manager()
        try:
            await manager.click(session_id, selector)
            console.print(f"[green]Clicked:[/green] {selector}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    asyncio.run(run())


@app.command()
def type(
    session_id: str,
    selector: str,
    text: str,
):
    """Type text into an element."""
    async def run():
        manager = await session_manager.get_manager()
        try:
            await manager.type_text(session_id, selector, text)
            console.print(f"[green]Typed:[/green] {text} -> {selector}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    asyncio.run(run())


@app.command()
def screenshot(
    session_id: str,
    path: str = "screenshot.png",
):
    """Take a screenshot."""
    async def run():
        manager = await session_manager.get_manager()
        try:
            await manager.screenshot(session_id, path)
            console.print(f"[green]Screenshot saved:[/green] {path}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    asyncio.run(run())


@app.command()
def execute(
    session_id: str,
    script: str,
):
    """Execute JavaScript."""
    async def run():
        manager = await session_manager.get_manager()
        try:
            result = await manager.execute_script(session_id, script)
            console.print(f"[green]Result:[/green] {result}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    asyncio.run(run())


@app.command()
def list_sessions():
    """List all active sessions."""
    async def run():
        manager = await session_manager.get_manager()
        sessions = manager.list_sessions()
        
        if not sessions:
            console.print("[yellow]No active sessions[/yellow]")
            return
        
        table = Table(title="Active Sessions")
        table.add_column("Session ID", style="cyan")
        table.add_column("Profile", style="green")
        table.add_column("Started", style="blue")
        table.add_column("Status", style="magenta")
        
        for s in sessions:
            table.add_row(
                s.session_id,
                s.profile_name,
                s.started_at.strftime("%Y-%m-%d %H:%M:%S"),
                s.status
            )
        
        console.print(table)
    
    asyncio.run(run())


@app.command()
def close(
    session_id: str,
):
    """Close a session."""
    async def run():
        manager = await session_manager.get_manager()
        try:
            await manager.close_session(session_id)
            console.print(f"[green]Session closed:[/green] {session_id}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    asyncio.run(run())


if __name__ == "__main__":
    app()
