import os
from rich.console import Console
import pyfiglet

console = Console()

def play_startup():
    os.system('clear')

    logo = pyfiglet.figlet_format('JARVIS', font='banner3-D')
    lines = logo.split('\n')

    for line in lines:
        console.print(f"[bold #A78BFA]{line}[/bold #A78BFA]")

    print()
    console.print("[#A78BFA]     Just A Rather Very Intelligent System     [/#A78BFA]")
    console.print("[#7C6FAE]            Powered by AWS Bedrock            [/#7C6FAE]")
    print()
