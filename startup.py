import time
import sys
import os
from rich.console import Console
from rich.text import Text
import pyfiglet

console = Console()

COLORS = [
    "dark_red",
    "red",
    "bold red",
    "orange1",
    "yellow",
    "bold yellow",
]

def play_startup():
    os.system('clear')

    logo = pyfiglet.figlet_format('JARVIS', font='banner3-D')
    lines = logo.split('\n')

    # Animate color sweep red → gold
    for color in COLORS:
        sys.stdout.write("\033[H")  # move cursor to top
        sys.stdout.flush()
        for line in lines:
            console.print(f"[{color}]{line}[/{color}]")
        time.sleep(0.1)

    time.sleep(0.2)

    # Final render in gold
    sys.stdout.write("\033[H")
    sys.stdout.flush()
    for line in lines:
        console.print(f"[bold yellow]{line}[/bold yellow]")

    # Subtitle type-out
    print()
    subtitle = "     Just A Rather Very Intelligent System     "
    powered  = "            Powered by AWS Bedrock            "

    for char in subtitle:
        sys.stdout.write(f"\033[2;37m{char}\033[0m")
        sys.stdout.flush()
        time.sleep(0.025)
    print()

    for char in powered:
        sys.stdout.write(f"\033[36m{char}\033[0m")
        sys.stdout.flush()
        time.sleep(0.025)
    print()
    print()
    time.sleep(0.3)
