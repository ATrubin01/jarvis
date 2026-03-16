#!/usr/bin/env python3
import click
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print as rprint

console = Console()

def print_response(title: str, content: str):
    console.print(Panel(Markdown(content), title=f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))

@click.group()
def cli():
    """jarvis — AI DevOps Assistant powered by AWS Bedrock"""
    pass

@cli.command()
@click.argument("question", nargs=-1)
def devops(question):
    """Ask questions about your AWS infrastructure"""
    from agents.devops import run
    q = " ".join(question) if question else Prompt.ask("[cyan]Ask about your AWS infrastructure[/cyan]")
    with console.status("[cyan]Querying AWS and thinking...[/cyan]"):
        response = run(q)
    print_response("DevOps Agent", response)

@cli.command()
@click.option("--file", "-f", type=click.Path(exists=True), help="Path to code file")
@click.option("--language", "-l", default="auto-detect", help="Programming language")
def review(file, language):
    """Review code for bugs, security issues, and improvements"""
    from agents.code_reviewer import run
    if file:
        with open(file) as f:
            code = f.read()
    else:
        console.print("[cyan]Paste your code below. Press Ctrl+D when done:[/cyan]")
        code = sys.stdin.read()
    with console.status("[cyan]Reviewing code...[/cyan]"):
        response = run(code, language)
    print_response("Code Review", response)

@cli.command()
@click.argument("description", nargs=-1)
def ticket(description):
    """Generate a structured engineering ticket from a description"""
    from agents.ticket_creator import run
    desc = " ".join(description) if description else Prompt.ask("[cyan]Describe the feature or bug[/cyan]")
    with console.status("[cyan]Creating ticket...[/cyan]"):
        response = run(desc)
    print_response("Generated Ticket", response)

@cli.command()
def chat():
    """Interactive chat mode — ask anything"""
    from agents.bedrock import ask
    SYSTEM = "You are a helpful DevOps and software engineering assistant."
    console.print(Panel("[bold cyan]jarvis chat[/bold cyan] — type [bold]exit[/bold] to quit", border_style="cyan"))
    while True:
        user_input = Prompt.ask("[cyan]you[/cyan]")
        if user_input.lower() in ("exit", "quit"):
            break
        with console.status("[cyan]thinking...[/cyan]"):
            response = ask(SYSTEM, user_input)
        print_response("aion", response)

if __name__ == "__main__":
    cli()
