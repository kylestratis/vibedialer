"""Tests for ASCII/ANSI art module."""

from io import StringIO

from rich.console import Console
from rich.text import Text

from vibedialer.art import (
    display_keypad,
    display_welcome_screen,
    get_telephone_keypad,
    get_telephone_keypad_with_highlight,
    get_welcome_banner,
)


def test_get_welcome_banner_returns_text():
    """Test that welcome banner returns a Rich Text object."""
    banner = get_welcome_banner()
    assert isinstance(banner, Text)
    assert len(banner) > 0


def test_welcome_banner_contains_vibedialer():
    """Test that welcome banner contains app name."""
    banner = get_welcome_banner()
    banner_str = banner.plain
    # Should contain some representation of the name
    assert "VIBE" in banner_str or "DIAL" in banner_str or "█" in banner_str


def test_welcome_banner_contains_version():
    """Test that welcome banner contains version."""
    banner = get_welcome_banner()
    banner_str = banner.plain
    assert "0.1.0" in banner_str


def test_get_telephone_keypad_returns_text():
    """Test that telephone keypad returns a Rich Text object."""
    keypad = get_telephone_keypad()
    assert isinstance(keypad, Text)
    assert len(keypad) > 0


def test_telephone_keypad_contains_all_numbers():
    """Test that keypad contains all digits 0-9."""
    keypad = get_telephone_keypad()
    keypad_str = keypad.plain

    for digit in "0123456789":
        assert digit in keypad_str


def test_telephone_keypad_contains_special_chars():
    """Test that keypad contains * and # symbols."""
    keypad = get_telephone_keypad()
    keypad_str = keypad.plain

    assert "*" in keypad_str
    assert "#" in keypad_str


def test_telephone_keypad_contains_letters():
    """Test that keypad contains letter groups (ABC, DEF, etc.)."""
    keypad = get_telephone_keypad()
    keypad_str = keypad.plain

    # Check for some letter groups
    assert "ABC" in keypad_str
    assert "DEF" in keypad_str
    assert "GHI" in keypad_str


def test_display_welcome_screen_renders():
    """Test that display_welcome_screen renders without errors."""
    console = Console(file=StringIO(), force_terminal=True)
    # Should not raise any exceptions
    display_welcome_screen(console)
    output = console.file.getvalue()
    assert len(output) > 0


def test_display_keypad_renders():
    """Test that display_keypad renders without errors."""
    console = Console(file=StringIO(), force_terminal=True)
    # Should not raise any exceptions
    display_keypad(console)
    output = console.file.getvalue()
    assert len(output) > 0
    # Should contain some numbers
    assert any(str(i) in output for i in range(10))


def test_get_telephone_keypad_with_highlight_returns_text():
    """Test that highlighted keypad returns a Rich Text object."""
    keypad = get_telephone_keypad_with_highlight("5")
    assert isinstance(keypad, Text)
    assert len(keypad) > 0


def test_telephone_keypad_with_highlight_no_digit():
    """Test that highlighted keypad works with no active digit."""
    keypad = get_telephone_keypad_with_highlight(None)
    keypad_str = keypad.plain

    # Should still contain all numbers
    for digit in "0123456789":
        assert digit in keypad_str


def test_telephone_keypad_with_highlight_contains_digit():
    """Test that highlighted keypad contains the highlighted digit."""
    for digit in "0123456789":
        keypad = get_telephone_keypad_with_highlight(digit)
        keypad_str = keypad.plain
        assert digit in keypad_str


def test_telephone_keypad_with_highlight_special_chars():
    """Test that highlighted keypad works with * and #."""
    for char in ["*", "#"]:
        keypad = get_telephone_keypad_with_highlight(char)
        keypad_str = keypad.plain
        assert char in keypad_str


def test_telephone_keypad_with_highlight_has_styling():
    """Test that highlighted keypad has different styling for active digit."""
    # Create keypads with and without highlight
    normal_keypad = get_telephone_keypad_with_highlight(None)
    highlighted_keypad = get_telephone_keypad_with_highlight("5")

    # The plain text should be the same
    assert normal_keypad.plain == highlighted_keypad.plain

    # But the spans (styling) should be different
    # Highlighted version should have reverse style for the active digit
    highlighted_spans = list(highlighted_keypad.spans)

    # Find a span with "reverse" in the style for the highlighted version
    has_reverse = any("reverse" in str(span.style) for span in highlighted_spans)
    assert has_reverse, "Highlighted keypad should have reverse styling"
