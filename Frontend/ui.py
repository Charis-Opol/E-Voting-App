"""
ui.py

Shared UI helpers for the E-Voting console application.
Every screen in the app uses these functions for a consistent look-and-feel.
"""

from colors import (
    RESET, BOLD, DIM, ITALIC, GRAY,
    RED, GREEN, YELLOW, CYAN, BRIGHT_CYAN,
    BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_WHITE,
    BG_GREEN, BLACK,
)

import os, sys


class UI:
    """Reusable terminal UI primitives."""

    # ── Screen control ────────────────────────────────────────────────────

    @staticmethod
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def pause():
        input(f"\n  {DIM}Press Enter to continue...{RESET}")

    # ── Headers ───────────────────────────────────────────────────────────

    @staticmethod
    def header(title, theme_color=BRIGHT_CYAN):
        width = 60
        print(f"\n  {theme_color}{BOLD}{'═' * width}{RESET}")
        print(f"  {theme_color}{BOLD}{title.center(width)}{RESET}")
        print(f"  {theme_color}{BOLD}{'═' * width}{RESET}")

    @staticmethod
    def subheader(title, theme_color=YELLOW):
        print(f"\n  {theme_color}{BOLD}── {title} ──{RESET}")

    # ── Formatted output ──────────────────────────────────────────────────

    @staticmethod
    def table_header(format_str, theme_color=BRIGHT_GREEN):
        print(f"  {theme_color}{BOLD}{format_str}{RESET}")

    @staticmethod
    def table_divider(width=70, theme_color=BRIGHT_GREEN):
        print(f"  {theme_color}{'─' * width}{RESET}")

    @staticmethod
    def status_badge(text, is_good):
        if is_good:
            return f"{GREEN}{BOLD}{text}{RESET}"
        return f"{RED}{BOLD}{text}{RESET}"

    # ── Menu helpers ──────────────────────────────────────────────────────

    @staticmethod
    def menu_item(number, text, color=BRIGHT_CYAN):
        print(f"  {color}{BOLD}{number}.{RESET} {text}")

    # ── Input helpers ─────────────────────────────────────────────────────

    @staticmethod
    def prompt(text):
        return input(f"  {BRIGHT_CYAN}▸{RESET} {text}").strip()

    @staticmethod
    def get_input(message):
        return input(message).strip()

    @staticmethod
    def masked_input(prompt_text="Password: "):
        """Cross-platform password input with masking."""
        try:
            import getpass
            return getpass.getpass(f"  {BRIGHT_CYAN}▸{RESET} {prompt_text}")
        except Exception:
            return input(f"  {BRIGHT_CYAN}▸{RESET} {prompt_text}")

    # ── Messages ──────────────────────────────────────────────────────────

    @staticmethod
    def success(msg):
        print(f"  {GREEN}{BOLD}✓{RESET} {GREEN}{msg}{RESET}")

    @staticmethod
    def error(msg):
        print(f"  {RED}{BOLD}✗{RESET} {RED}{msg}{RESET}")

    @staticmethod
    def warning(msg):
        print(f"  {YELLOW}{BOLD}⚠{RESET} {YELLOW}{msg}{RESET}")

    @staticmethod
    def info(msg):
        print(f"  {CYAN}ℹ {msg}{RESET}")

    # ── Login menu ────────────────────────────────────────────────────────

    def show_login_menu(self):
        from colors import THEME_LOGIN
        self.clear_screen()
        self.header("E-VOTING SYSTEM", THEME_LOGIN)
        print()
        self.menu_item(1, "Login as Admin", THEME_LOGIN)
        self.menu_item(2, "Login as Voter", THEME_LOGIN)
        self.menu_item(3, "Register as Voter", THEME_LOGIN)
        self.menu_item(4, "Exit", THEME_LOGIN)
        print()