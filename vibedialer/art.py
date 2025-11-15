"""ASCII/ANSI art assets for VibeDialer."""

from rich.console import Console
from rich.text import Text

# Vaporwave color scheme
VAPORWAVE_PINK = "#FF71CE"
VAPORWAVE_CYAN = "#01CDFE"
VAPORWAVE_PURPLE = "#B967FF"
VAPORWAVE_YELLOW = "#FFFB96"
VAPORWAVE_BLUE = "#05FFA1"


def get_welcome_banner() -> Text:
    """
    Get the welcome banner with vaporwave styling.

    Returns:
        Rich Text object with styled banner
    """
    banner = Text()
    banner.append(
        "╔═══════════════════════════════════════════════════════╗\n",
        style=VAPORWAVE_CYAN,
    )
    banner.append(
        "║                                                       ║\n",
        style=VAPORWAVE_CYAN,
    )
    banner.append("║  ", style=VAPORWAVE_CYAN)
    banner.append(
        "██╗   ██╗██╗██████╗ ███████╗██████╗ ██╗ █████╗ ██╗     ", style=VAPORWAVE_PINK
    )
    banner.append("  ║\n", style=VAPORWAVE_CYAN)
    banner.append("║  ", style=VAPORWAVE_CYAN)
    banner.append(
        "██║   ██║██║██╔══██╗██╔════╝██╔══██╗██║██╔══██╗██║     ", style=VAPORWAVE_PINK
    )
    banner.append("  ║\n", style=VAPORWAVE_CYAN)
    banner.append("║  ", style=VAPORWAVE_CYAN)
    banner.append(
        "██║   ██║██║██████╔╝█████╗  ██║  ██║██║███████║██║     ",
        style=VAPORWAVE_PURPLE,
    )
    banner.append("  ║\n", style=VAPORWAVE_CYAN)
    banner.append("║  ", style=VAPORWAVE_CYAN)
    banner.append(
        "╚██╗ ██╔╝██║██╔══██╗██╔══╝  ██║  ██║██║██╔══██║██║     ",
        style=VAPORWAVE_PURPLE,
    )
    banner.append("  ║\n", style=VAPORWAVE_CYAN)
    banner.append("║   ", style=VAPORWAVE_CYAN)
    banner.append(
        "╚████╔╝ ██║██████╔╝███████╗██████╔╝██║██║  ██║███████╗", style=VAPORWAVE_BLUE
    )
    banner.append(" ║\n", style=VAPORWAVE_CYAN)
    banner.append("║    ", style=VAPORWAVE_CYAN)
    banner.append(
        "╚═══╝  ╚═╝╚═════╝ ╚══════╝╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝", style=VAPORWAVE_BLUE
    )
    banner.append(" ║\n", style=VAPORWAVE_CYAN)
    banner.append(
        "║                                                       ║\n",
        style=VAPORWAVE_CYAN,
    )
    banner.append("║              ", style=VAPORWAVE_CYAN)
    banner.append("✧･ﾟ: *✧･ﾟ:* WAR DIALER TUI *:･ﾟ✧*:･ﾟ✧", style=VAPORWAVE_YELLOW)
    banner.append("              ║\n", style=VAPORWAVE_CYAN)
    banner.append("║                      ", style=VAPORWAVE_CYAN)
    banner.append("v0.1.0", style=VAPORWAVE_PURPLE)
    banner.append("                      ║\n", style=VAPORWAVE_CYAN)
    banner.append(
        "║                                                       ║\n",
        style=VAPORWAVE_CYAN,
    )
    banner.append(
        "╚═══════════════════════════════════════════════════════╝",
        style=VAPORWAVE_CYAN,
    )
    return banner


def get_telephone_keypad() -> Text:
    """
    Get ASCII art of a telephone keypad with vaporwave styling.

    Returns:
        Rich Text object with styled keypad
    """
    keypad = Text()

    # Top border
    keypad.append("         ╔═══════════════════════════╗\n", style=VAPORWAVE_PINK)
    keypad.append("         ║  ", style=VAPORWAVE_PINK)
    keypad.append("TELEPHONE KEYPAD", style=f"bold {VAPORWAVE_CYAN}")
    keypad.append("      ║\n", style=VAPORWAVE_PINK)
    keypad.append("         ╠═══════════════════════════╣\n", style=VAPORWAVE_PINK)

    # Row 1: 1, 2, 3
    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("┌───┐ ┌───┐ ┌───┐", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│ ", style=VAPORWAVE_CYAN)
    keypad.append("1", style=f"bold {VAPORWAVE_YELLOW}")
    keypad.append(" │ │ ", style=VAPORWAVE_CYAN)
    keypad.append("2", style=f"bold {VAPORWAVE_YELLOW}")
    keypad.append(" │ │ ", style=VAPORWAVE_CYAN)
    keypad.append("3", style=f"bold {VAPORWAVE_YELLOW}")
    keypad.append(" │", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│   │ │", style=VAPORWAVE_CYAN)
    keypad.append("ABC", style=f"dim {VAPORWAVE_PURPLE}")
    keypad.append("│ │", style=VAPORWAVE_CYAN)
    keypad.append("DEF", style=f"dim {VAPORWAVE_PURPLE}")
    keypad.append("│", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("└───┘ └───┘ └───┘", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    # Row 2: 4, 5, 6
    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("┌───┐ ┌───┐ ┌───┐", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│ ", style=VAPORWAVE_CYAN)
    keypad.append("4", style=f"bold {VAPORWAVE_YELLOW}")
    keypad.append(" │ │ ", style=VAPORWAVE_CYAN)
    keypad.append("5", style=f"bold {VAPORWAVE_YELLOW}")
    keypad.append(" │ │ ", style=VAPORWAVE_CYAN)
    keypad.append("6", style=f"bold {VAPORWAVE_YELLOW}")
    keypad.append(" │", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│", style=VAPORWAVE_CYAN)
    keypad.append("GHI", style=f"dim {VAPORWAVE_PURPLE}")
    keypad.append("│ │", style=VAPORWAVE_CYAN)
    keypad.append("JKL", style=f"dim {VAPORWAVE_PURPLE}")
    keypad.append("│ │", style=VAPORWAVE_CYAN)
    keypad.append("MNO", style=f"dim {VAPORWAVE_PURPLE}")
    keypad.append("│", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("└───┘ └───┘ └───┘", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    # Row 3: 7, 8, 9
    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("┌───┐ ┌───┐ ┌───┐", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│ ", style=VAPORWAVE_CYAN)
    keypad.append("7", style=f"bold {VAPORWAVE_YELLOW}")
    keypad.append(" │ │ ", style=VAPORWAVE_CYAN)
    keypad.append("8", style=f"bold {VAPORWAVE_YELLOW}")
    keypad.append(" │ │ ", style=VAPORWAVE_CYAN)
    keypad.append("9", style=f"bold {VAPORWAVE_YELLOW}")
    keypad.append(" │", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│", style=VAPORWAVE_CYAN)
    keypad.append("PRS", style=f"dim {VAPORWAVE_PURPLE}")
    keypad.append("│ │", style=VAPORWAVE_CYAN)
    keypad.append("TUV", style=f"dim {VAPORWAVE_PURPLE}")
    keypad.append("│ │", style=VAPORWAVE_CYAN)
    keypad.append("WXY", style=f"dim {VAPORWAVE_PURPLE}")
    keypad.append("│", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("└───┘ └───┘ └───┘", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    # Row 4: *, 0, #
    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("┌───┐ ┌───┐ ┌───┐", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│ ", style=VAPORWAVE_CYAN)
    keypad.append("*", style=f"bold {VAPORWAVE_BLUE}")
    keypad.append(" │ │ ", style=VAPORWAVE_CYAN)
    keypad.append("0", style=f"bold {VAPORWAVE_YELLOW}")
    keypad.append(" │ │ ", style=VAPORWAVE_CYAN)
    keypad.append("#", style=f"bold {VAPORWAVE_BLUE}")
    keypad.append(" │", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│   │ │", style=VAPORWAVE_CYAN)
    keypad.append(" + ", style=f"dim {VAPORWAVE_PURPLE}")
    keypad.append("│ │   │", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("└───┘ └───┘ └───┘", style=VAPORWAVE_CYAN)
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    # Bottom border
    keypad.append("         ╚═══════════════════════════╝", style=VAPORWAVE_PINK)

    return keypad


def display_welcome_screen(console: Console | None = None) -> None:
    """
    Display the welcome screen with banner.

    Args:
        console: Rich Console instance (creates new one if not provided)
    """
    if console is None:
        console = Console()

    console.print()
    console.print(get_welcome_banner())
    console.print()
    console.print(
        "Press any key to continue...", style=f"dim {VAPORWAVE_CYAN}", justify="center"
    )
    console.print()


def get_telephone_keypad_with_highlight(active_digit: str | None = None) -> Text:
    """
    Get ASCII art of a telephone keypad with an optional highlighted digit.

    Args:
        active_digit: The digit currently being pressed (0-9, *, or #)

    Returns:
        Rich Text object with styled keypad and highlighted active digit
    """
    keypad = Text()

    # Top border
    keypad.append("         ╔═══════════════════════════╗\n", style=VAPORWAVE_PINK)
    keypad.append("         ║  ", style=VAPORWAVE_PINK)
    keypad.append("TELEPHONE KEYPAD", style=f"bold {VAPORWAVE_CYAN}")
    keypad.append("      ║\n", style=VAPORWAVE_PINK)
    keypad.append("         ╠═══════════════════════════╣\n", style=VAPORWAVE_PINK)

    # Helper function to get style for a digit
    def get_digit_style(digit: str) -> str:
        if active_digit and digit == active_digit:
            return f"bold reverse {VAPORWAVE_PINK}"  # Highlighted style
        elif digit in "0123456789":
            return f"bold {VAPORWAVE_YELLOW}"
        else:
            return f"bold {VAPORWAVE_BLUE}"

    def get_letter_style(digit: str) -> str:
        if active_digit and digit == active_digit:
            return f"dim reverse {VAPORWAVE_PURPLE}"
        else:
            return f"dim {VAPORWAVE_PURPLE}"

    def get_border_style(digit: str) -> str:
        if active_digit and digit == active_digit:
            return f"bold {VAPORWAVE_PINK}"
        else:
            return VAPORWAVE_CYAN

    # Row 1: 1, 2, 3
    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("┌───┐ ", style=get_border_style("1"))
    keypad.append("┌───┐ ", style=get_border_style("2"))
    keypad.append("┌───┐", style=get_border_style("3"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│ ", style=get_border_style("1"))
    keypad.append("1", style=get_digit_style("1"))
    keypad.append(" │ ", style=get_border_style("1"))
    keypad.append("│ ", style=get_border_style("2"))
    keypad.append("2", style=get_digit_style("2"))
    keypad.append(" │ ", style=get_border_style("2"))
    keypad.append("│ ", style=get_border_style("3"))
    keypad.append("3", style=get_digit_style("3"))
    keypad.append(" │", style=get_border_style("3"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│   │ ", style=get_border_style("1"))
    keypad.append("│", style=get_border_style("2"))
    keypad.append("ABC", style=get_letter_style("2"))
    keypad.append("│ ", style=get_border_style("2"))
    keypad.append("│", style=get_border_style("3"))
    keypad.append("DEF", style=get_letter_style("3"))
    keypad.append("│", style=get_border_style("3"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("└───┘ ", style=get_border_style("1"))
    keypad.append("└───┘ ", style=get_border_style("2"))
    keypad.append("└───┘", style=get_border_style("3"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    # Row 2: 4, 5, 6
    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("┌───┐ ", style=get_border_style("4"))
    keypad.append("┌───┐ ", style=get_border_style("5"))
    keypad.append("┌───┐", style=get_border_style("6"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│ ", style=get_border_style("4"))
    keypad.append("4", style=get_digit_style("4"))
    keypad.append(" │ ", style=get_border_style("4"))
    keypad.append("│ ", style=get_border_style("5"))
    keypad.append("5", style=get_digit_style("5"))
    keypad.append(" │ ", style=get_border_style("5"))
    keypad.append("│ ", style=get_border_style("6"))
    keypad.append("6", style=get_digit_style("6"))
    keypad.append(" │", style=get_border_style("6"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│", style=get_border_style("4"))
    keypad.append("GHI", style=get_letter_style("4"))
    keypad.append("│ ", style=get_border_style("4"))
    keypad.append("│", style=get_border_style("5"))
    keypad.append("JKL", style=get_letter_style("5"))
    keypad.append("│ ", style=get_border_style("5"))
    keypad.append("│", style=get_border_style("6"))
    keypad.append("MNO", style=get_letter_style("6"))
    keypad.append("│", style=get_border_style("6"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("└───┘ ", style=get_border_style("4"))
    keypad.append("└───┘ ", style=get_border_style("5"))
    keypad.append("└───┘", style=get_border_style("6"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    # Row 3: 7, 8, 9
    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("┌───┐ ", style=get_border_style("7"))
    keypad.append("┌───┐ ", style=get_border_style("8"))
    keypad.append("┌───┐", style=get_border_style("9"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│ ", style=get_border_style("7"))
    keypad.append("7", style=get_digit_style("7"))
    keypad.append(" │ ", style=get_border_style("7"))
    keypad.append("│ ", style=get_border_style("8"))
    keypad.append("8", style=get_digit_style("8"))
    keypad.append(" │ ", style=get_border_style("8"))
    keypad.append("│ ", style=get_border_style("9"))
    keypad.append("9", style=get_digit_style("9"))
    keypad.append(" │", style=get_border_style("9"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│", style=get_border_style("7"))
    keypad.append("PRS", style=get_letter_style("7"))
    keypad.append("│ ", style=get_border_style("7"))
    keypad.append("│", style=get_border_style("8"))
    keypad.append("TUV", style=get_letter_style("8"))
    keypad.append("│ ", style=get_border_style("8"))
    keypad.append("│", style=get_border_style("9"))
    keypad.append("WXY", style=get_letter_style("9"))
    keypad.append("│", style=get_border_style("9"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("└───┘ ", style=get_border_style("7"))
    keypad.append("└───┘ ", style=get_border_style("8"))
    keypad.append("└───┘", style=get_border_style("9"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    # Row 4: *, 0, #
    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("┌───┐ ", style=get_border_style("*"))
    keypad.append("┌───┐ ", style=get_border_style("0"))
    keypad.append("┌───┐", style=get_border_style("#"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│ ", style=get_border_style("*"))
    keypad.append("*", style=get_digit_style("*"))
    keypad.append(" │ ", style=get_border_style("*"))
    keypad.append("│ ", style=get_border_style("0"))
    keypad.append("0", style=get_digit_style("0"))
    keypad.append(" │ ", style=get_border_style("0"))
    keypad.append("│ ", style=get_border_style("#"))
    keypad.append("#", style=get_digit_style("#"))
    keypad.append(" │", style=get_border_style("#"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("│   │ ", style=get_border_style("*"))
    keypad.append("│", style=get_border_style("0"))
    keypad.append(" + ", style=get_letter_style("0"))
    keypad.append("│ ", style=get_border_style("0"))
    keypad.append("│   │", style=get_border_style("#"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    keypad.append("         ║   ", style=VAPORWAVE_PINK)
    keypad.append("└───┘ ", style=get_border_style("*"))
    keypad.append("└───┘ ", style=get_border_style("0"))
    keypad.append("└───┘", style=get_border_style("#"))
    keypad.append("   ║\n", style=VAPORWAVE_PINK)

    # Bottom border
    keypad.append("         ╚═══════════════════════════╝", style=VAPORWAVE_PINK)

    return keypad


def display_keypad(console: Console | None = None) -> None:
    """
    Display the telephone keypad.

    Args:
        console: Rich Console instance (creates new one if not provided)
    """
    if console is None:
        console = Console()

    console.print(get_telephone_keypad())
