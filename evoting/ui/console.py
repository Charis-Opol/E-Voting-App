"""
ui/console.py
Responsibility: All terminal output formatting — colors, headers, prompts.
No business logic here. Pure display concerns only.
"""

import sys
import os

if sys.platform == "win32":
    os.system("")

# ── ANSI codes ──────────────────────────────────────────────────────────────
RESET          = "\033[0m"
BOLD           = "\033[1m"
DIM            = "\033[2m"
ITALIC         = "\033[3m"

BLACK          = "\033[30m"
RED            = "\033[31m"
GREEN          = "\033[32m"
YELLOW         = "\033[33m"
BLUE           = "\033[34m"
MAGENTA        = "\033[35m"
CYAN           = "\033[36m"
WHITE          = "\033[37m"
GRAY           = "\033[90m"
BRIGHT_RED     = "\033[91m"
BRIGHT_GREEN   = "\033[92m"
BRIGHT_YELLOW  = "\033[93m"
BRIGHT_BLUE    = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN    = "\033[96m"
BRIGHT_WHITE   = "\033[97m"

BG_RED     = "\033[41m"
BG_GREEN   = "\033[42m"
BG_YELLOW  = "\033[43m"
BG_BLUE    = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN    = "\033[46m"
BG_WHITE   = "\033[47m"
BG_GRAY    = "\033[100m"

# ── Theme aliases ────────────────────────────────────────────────────────────
THEME_LOGIN        = BRIGHT_CYAN
THEME_ADMIN        = BRIGHT_GREEN
THEME_ADMIN_ACCENT = YELLOW
THEME_VOTER        = BRIGHT_BLUE
THEME_VOTER_ACCENT = MAGENTA


class Console:
    """Console wrapper for all UI outputs."""

    def colored(self, text, color):
        return f"{color}{text}{RESET}"

    def print(self, text=""):
        """Simple wrapper to allow object-style print calls."""
        print(text)

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    # ── Input/Prompt ─────────────────────────────────────────────────────────
    def prompt(self, text):
        """Primary method for input prompts."""
        return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()

    def input(self, text=""):
        """Alias for prompt() to maintain compatibility with older code."""
        return self.prompt(text)

    def pause(self):
        input(f"\n  {DIM}Press Enter to continue...{RESET}")

    def masked_input(self, prompt_text="Password: "):
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
            import tty
            import termios
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

    # ── Display methods ──────────────────────────────────────────────────────
    def header(self, title, theme_color):
        width = 58
        top = f"  {theme_color}{'═' * width}{RESET}"
        mid = f"  {theme_color}{BOLD} {title.center(width - 2)} {RESET}{theme_color} {RESET}"
        bot = f"  {theme_color}{'═' * width}{RESET}"
        self.print(top)
        self.print(mid)
        self.print(bot)

    def subheader(self, title, theme_color):
        self.print(f"\n  {theme_color}{BOLD}▸ {title}{RESET}")

    def table_header(self, format_str, theme_color):
        self.print(f"  {theme_color}{BOLD}{format_str}{RESET}")

    def table_divider(self, width, theme_color):
        self.print(f"  {theme_color}{'─' * width}{RESET}")

    def print_error(self, msg):
        self.print(f"  {RED}{BOLD} {msg}{RESET}")

    def print_success(self, msg):
        self.print(f"  {GREEN}{BOLD} {msg}{RESET}")

    def print_warning(self, msg):
        self.print(f"  {YELLOW}{BOLD} {msg}{RESET}")

    def print_info(self, msg):
        self.print(f"  {GRAY}{msg}{RESET}")

    def menu_item(self, number, text, color):
        self.print(f"  {color}{BOLD}{number:>3}.{RESET}  {text}")

    def status_badge(self, text, is_good):
        if is_good:
            return f"{GREEN}{text}{RESET}"
        return f"{RED}{text}{RESET}"