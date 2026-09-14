"""
AgentOps Observatory - Command Line Interface (agentops-cli)
Interactive terminal tool for monitoring agent telemetry, streaming live runs,
running policy audits, and inspecting append-only cryptographic chains.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
import httpx

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

console = Console()


def display_banner():
    banner_text = """
================================================================
       AGENTOPS OBSERVATORY -- AGENT TELEMETRY & AUDIT CLI
================================================================
"""
    console.print(f"[bold cyan]{banner_text}[/bold cyan]")


def cmd_status(api_url: str):
    console.print(f"[bold green]Checking status of AgentOps Observatory at {api_url}...[/bold green]")
    try:
        with httpx.Client(timeout=3.0) as client:
            res = client.get(f"{api_url}/health")
            if res.status_code == 200:
                data = res.json()
                console.print(Panel.fit(
                    f"[bold]Service:[/bold] {data.get('service')}\n"
                    f"[bold]Version:[/bold] {data.get('version')}\n"
                    f"[bold]Database:[/bold] {data.get('database')}\n"
                    f"[bold]Timestamp:[/bold] {data.get('timestamp')}",
                    title="System Health: [bold green]OPERATIONAL[/bold green]",
                    border_style="green"
                ))
            else:
                console.print(f"[bold red]Service returned error status: {res.status_code}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Failed to connect to Observatory API: {e}[/bold red]")


def cmd_runs(api_url: str, limit: int = 10):
    try:
        with httpx.Client(timeout=4.0) as client:
            res = client.get(f"{api_url}/runs?limit={limit}")
            if res.status_code == 200:
                runs = res.json().get("runs", [])
                table = Table(title=f"Recent Agent Executions (Top {len(runs)})", border_style="cyan")
                table.add_column("Run ID", style="cyan font-mono")
                table.add_column("Agent Identity", style="white")
                table.add_column("Status", style="bold")
                table.add_column("Duration", justify="right")
                table.add_column("Tokens", justify="right")
                table.add_column("Cost ($)", justify="right")
                table.add_column("Integrity", style="magenta")

                for r in runs:
                    status_style = "green" if r["status"] == "success" else "red" if r["status"] == "violated" else "yellow"
                    integrity = "[yellow]PARTIAL[/yellow]" if r["is_partial"] else "[green]COMPLETE[/green]"
                    table.add_row(
                        r["run_id"],
                        r["agent_name"],
                        f"[{status_style}]{r['status'].upper()}[/{status_style}]",
                        f"{r['total_duration_ms']:.0f} ms",
                        f"{r['total_tokens']:,}",
                        f"${r['total_cost_usd']:.4f}",
                        integrity
                    )
                console.print(table)
            else:
                console.print(f"[bold red]API Error: {res.status_code}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Failed to fetch runs: {e}[/bold red]")


def main():
    display_banner()
    parser = argparse.ArgumentParser(description="AgentOps Observatory CLI Tool")
    parser.add_argument("--url", default="http://localhost:8000/api/v1", help="API URL")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Check observatory system health")
    run_parser = subparsers.add_parser("runs", help="List recent agent execution traces")
    run_parser.add_argument("--limit", type=int, default=10, help="Number of runs to show")

    args = parser.parse_args()
    if args.command == "status":
        cmd_status(args.url)
    elif args.command == "runs":
        cmd_runs(args.url, args.limit)
    else:
        cmd_status(args.url)


if __name__ == "__main__":
    main()
