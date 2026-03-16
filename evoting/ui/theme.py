# ui/theme.py  ─  ANSI colours and terminal helpers (display only, no logic)

import sys
import os

if sys.platform == "win32":
    os.system("")

# ── base styles ──────────────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
ITALIC  = "\033[3m"
UNDERLINE = "\033[4m"

# ── foreground colours ────────────────────────────────────────────────────────
BLACK         = "\033[30m"
RED           = "\033[31m"
GREEN         = "\033[32m"
YELLOW        = "\033[33m"
BLUE          = "\033[34m"
MAGENTA       = "\033[35m"
CYAN          = "\033[36m"
WHITE         = "\033[37m"
GRAY          = "\033[90m"
BRIGHT_RED    = "\033[91m"
BRIGHT_GREEN  = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE   = "\033[94m"
BRIGHT_MAGENTA= "\033[95m"
BRIGHT_CYAN   = "\033[96m"
BRIGHT_WHITE  = "\033[97m"

# ── background colours ────────────────────────────────────────────────────────
BG_RED     = "\033[41m"
BG_GREEN   = "\033[42m"
BG_YELLOW  = "\033[43m"
BG_BLUE    = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN    = "\033[46m"
BG_WHITE   = "\033[47m"
BG_GRAY    = "\033[100m"

# ── semantic theme colours ────────────────────────────────────────────────────
THEME_LOGIN        = BRIGHT_CYAN
THEME_ADMIN        = BRIGHT_GREEN
THEME_ADMIN_ACCENT = YELLOW
THEME_VOTER        = BRIGHT_BLUE
THEME_VOTER_ACCENT = MAGENTA


# ── rendering helpers ─────────────────────────────────────────────────────────

def colored(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def print_header(title: str, theme_color: str) -> None:
    width = 58
    print(f"  {theme_color}{'═' * width}{RESET}")
    print(f"  {theme_color}{BOLD} {title.center(width - 2)} {RESET}{theme_color} {RESET}")
    print(f"  {theme_color}{'═' * width}{RESET}")


def print_subheader(title: str, theme_color: str) -> None:
    print(f"\n  {theme_color}{BOLD}▸ {title}{RESET}")


def print_table_header(format_str: str, theme_color: str) -> None:
    print(f"  {theme_color}{BOLD}{format_str}{RESET}")


def print_table_divider(width: int, theme_color: str) -> None:
    print(f"  {theme_color}{'─' * width}{RESET}")


def print_error(msg: str) -> None:
    print(f"  {RED}{BOLD} {msg}{RESET}")


def print_success(msg: str) -> None:
    print(f"  {GREEN}{BOLD} {msg}{RESET}")


def print_warning(msg: str) -> None:
    print(f"  {YELLOW}{BOLD} {msg}{RESET}")


def print_info(msg: str) -> None:
    print(f"  {GRAY}{msg}{RESET}")


def print_menu_item(number: int, text: str, color: str) -> None:
    print(f"  {color}{BOLD}{number:>3}.{RESET}  {text}")


def status_badge(text: str, is_good: bool) -> str:
    return f"{GREEN}{text}{RESET}" if is_good else f"{RED}{text}{RESET}"


def prompt(text: str) -> str:
    return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()


def masked_input(prompt_text: str = "Password: ") -> str:
    """Read a password character-by-character, showing * for each character."""
    print(f"  {BRIGHT_WHITE}{prompt_text}{RESET}", end="", flush=True)
    password = ""
    if sys.platform == "win32":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                print()
                break
            elif ch in ("\x08", "\b"):
                if password:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":
                raise KeyboardInterrupt
            else:
                password += ch
                sys.stdout.write(f"{YELLOW}*{RESET}")
                sys.stdout.flush()
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    print()
                    break
                elif ch in ("\x7f", "\x08"):
                    if password:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif ch == "\x03":
                    raise KeyboardInterrupt
                else:
                    password += ch
                    sys.stdout.write(f"{YELLOW}*{RESET}")
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return password


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    input(f"\n  {DIM}Press Enter to continue...{RESET}")
