import time
import sys
import os
from rich.console import Console

console = Console()

# Iron Man mask - frame per eye brightness level
# Eyes: ░░ → ▒▒ → ▓▓ → ██ (glow up)
def get_mask(eye, eye_color, mask_color):
    E = eye
    return [
        (f"            ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄            ", mask_color),
        (f"         ▄██████████████████████████████▄         ", mask_color),
        (f"        ████████████████████████████████████        ", mask_color),
        (f"       ██████████████████████████████████████       ", mask_color),
        (f"      ████████████████████████████████████████      ", mask_color),
        (f"      ████████████████████████████████████████      ", mask_color),
        (f"      ██▄▄▄▄████████████████████████████▄▄▄▄██      ", mask_color),
        (f"      ███████▄▄▄▄████████████████▄▄▄▄███████████      ", mask_color),
        (f"      █████████  {E}{E}{E}{E}{E}{E}  ████  {E}{E}{E}{E}{E}{E}  █████████      ", eye_color),
        (f"      █████████  {E}{E}{E}{E}{E}{E}  ████  {E}{E}{E}{E}{E}{E}  █████████      ", eye_color),
        (f"      █████████  {E}{E}{E}{E}{E}{E}  ████  {E}{E}{E}{E}{E}{E}  █████████      ", eye_color),
        (f"      ███████▀▀▀▀████████████████▀▀▀▀███████████      ", mask_color),
        (f"      ████████████████████████████████████████      ", mask_color),
        (f"      ████████████████████████████████████████      ", mask_color),
        (f"       █████████  ████████████  █████████████       ", mask_color),
        (f"       ████████████████████████████████████        ", mask_color),
        (f"        ██  ██  ██  ████████  ██  ██  ██          ", mask_color),
        (f"         ████████████████████████████████          ", mask_color),
        (f"           ██████████████████████████████            ", mask_color),
        (f"              ████████████████████████               ", mask_color),
    ]

FRAMES = [
    ("░░", "dim red",    "dim red"),
    ("▒▒", "dark_orange","bold red"),
    ("▓▓", "orange1",   "bold red"),
    ("██", "yellow",    "bold red"),
    ("██", "bright_yellow", "bold red"),
]

def print_mask(eye, eye_color, mask_color):
    for line, color in get_mask(eye, eye_color, mask_color):
        console.print(f"[{color}]{line}[/{color}]")

def clear_mask():
    # Move cursor up 20 lines
    sys.stdout.write("\033[20A")
    sys.stdout.flush()

def play_startup():
    os.system('clear')

    # Draw initial dark mask
    print_mask("░░", "dim red", "dim red")
    time.sleep(0.3)

    # Animate eyes glowing up
    for i, (eye, eye_color, mask_color) in enumerate(FRAMES):
        clear_mask()
        print_mask(eye, eye_color, mask_color)
        time.sleep(0.15)

    # Flash effect
    for _ in range(3):
        clear_mask()
        print_mask("██", "white", "bold red")
        time.sleep(0.07)
        clear_mask()
        print_mask("██", "bright_yellow", "bold red")
        time.sleep(0.07)

    time.sleep(0.4)

    # J.A.R.V.I.S reveal
    print()
    title    = "        J . A . R . V . I . S        "
    subtitle = "   Just A Rather Very Intelligent System   "
    powered  = "         Powered by AWS Bedrock          "

    for char in title:
        sys.stdout.write(f"\033[1;93m{char}\033[0m")
        sys.stdout.flush()
        time.sleep(0.045)
    print()

    time.sleep(0.1)
    for char in subtitle:
        sys.stdout.write(f"\033[2;37m{char}\033[0m")
        sys.stdout.flush()
        time.sleep(0.02)
    print()

    time.sleep(0.1)
    for char in powered:
        sys.stdout.write(f"\033[36m{char}\033[0m")
        sys.stdout.flush()
        time.sleep(0.02)
    print()
    print()
    time.sleep(0.3)
