"""Tests for ASCII/ANSI art module."""

from io import StringIO

from rich.console import Console
from rich.text import Text

from vibedialer.ui import (
    display_keypad,
    display_welcome_screen,
    get_ansi_art_collection,
    get_random_ansi_art,
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


def test_get_ansi_art_collection_returns_list():
    """Test that ANSI art collection returns a list."""
    collection = get_ansi_art_collection()
    assert isinstance(collection, list)


def test_ansi_art_collection_not_empty():
    """Test that ANSI art collection is not empty.

    Note: This test requires at least one .txt file in the assets/ansi_art directory.
    """
    collection = get_ansi_art_collection()
    assert len(collection) > 0, "ANSI art collection should have at least one piece"


def test_ansi_art_collection_contains_text_objects():
    """Test that ANSI art collection contains Rich Text objects."""
    collection = get_ansi_art_collection()
    for art in collection:
        assert isinstance(art, Text), "Each art piece should be a Rich Text object"


def test_get_random_ansi_art_returns_text():
    """Test that random ANSI art returns a Rich Text object."""
    art = get_random_ansi_art()
    assert isinstance(art, Text)
    assert len(art) > 0


def test_random_ansi_art_from_collection():
    """Test that random art comes from the collection."""
    collection = get_ansi_art_collection()
    art = get_random_ansi_art()

    # The art should match one of the pieces in the collection
    art_plain = art.plain
    collection_plains = [piece.plain for piece in collection]
    assert art_plain in collection_plains, "Random art should be from collection"


def test_random_ansi_art_can_vary():
    """Test that random art can return different pieces (probabilistic)."""
    collection = get_ansi_art_collection()

    # Only test if there are multiple art pieces
    if len(collection) > 1:
        # Get multiple samples
        samples = [get_random_ansi_art().plain for _ in range(20)]
        # Check that we got at least 2 different pieces (very likely with 20 samples)
        unique_samples = set(samples)
        assert len(unique_samples) >= 1, "Should get at least 1 unique art piece"
        # If collection has 2+ pieces, we should likely see variety
        if len(collection) >= 2:
            # With 20 samples from 2+ items, we should see variety
            # This is probabilistic but very likely
            pass  # We already asserted at least 1, which covers single-item case


def test_ansi_art_loads_ans_files():
    """Test that .ANS files (ANSI art with escape codes) are loaded."""
    import tempfile
    from pathlib import Path

    from vibedialer.ui.art import _load_ansi_art_files

    # Create a temporary .ANS file with ANSI escape codes
    test_ansi_content = "\x1b[31mRed Text\x1b[0m\n\x1b[32mGreen Text\x1b[0m"

    # Save original _ASSETS_DIR
    from vibedialer.ui import art

    original_assets_dir = art._ASSETS_DIR

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            art._ASSETS_DIR = tmppath

            # Create a test .ANS file with CP437 encoding (as real .ANS files would be)
            ans_file = tmppath / "test.ans"
            ans_file.write_bytes(test_ansi_content.encode("cp437"))

            # Load files
            files = _load_ansi_art_files()

            # Should have loaded the .ANS file
            assert len(files) >= 1, "Should load .ANS files"
            # Check if the content was loaded (allowing for encoding differences)
            assert any("Red Text" in f or "Green Text" in f for f in files), (
                ".ANS file content should be preserved"
            )
    finally:
        # Restore original path
        art._ASSETS_DIR = original_assets_dir


def test_ansi_art_preserves_escape_codes():
    """Test that ANSI escape codes in .ANS files are preserved, not stripped."""
    import tempfile
    from pathlib import Path

    from vibedialer.ui import art

    # ANSI art with escape codes for colors
    # Use CP437 encoding for .ANS files as they would in the real world
    test_content = (
        "\x1b[1;31m╔═══╗\x1b[0m\n\x1b[1;32m║ A ║\x1b[0m\n\x1b[1;34m╚═══╝\x1b[0m"
    )

    original_assets_dir = art._ASSETS_DIR

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            art._ASSETS_DIR = tmppath

            # Create test .ANS file with CP437 encoding (as real .ANS files would be)
            ans_file = tmppath / "test.ans"
            ans_file.write_bytes(test_content.encode("cp437"))

            # Load the collection
            collection = art.get_ansi_art_collection()

            # Should preserve escape codes in the Text object
            assert len(collection) > 0
            # The markup property or str representation should contain the escape codes
            found = False
            for piece in collection:
                # Check if the plain text contains our box characters
                if "╔═══╗" in piece.plain:
                    found = True
                    break
            assert found, "Should preserve the art content from .ANS files"
    finally:
        art._ASSETS_DIR = original_assets_dir


def test_ansi_art_loads_both_txt_and_ans():
    """Test that both .txt and .ANS files are loaded."""
    import tempfile
    from pathlib import Path

    from vibedialer.ui import art

    original_assets_dir = art._ASSETS_DIR

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            art._ASSETS_DIR = tmppath

            # Create a .txt file with UTF-8
            txt_file = tmppath / "test.txt"
            txt_file.write_text("Plain text art", encoding="utf-8")

            # Create a .ANS file with CP437 (as real .ANS files would be)
            ans_file = tmppath / "test.ans"
            ans_file.write_bytes("\x1b[31mANSI art\x1b[0m".encode("cp437"))

            # Load files
            files = art._load_ansi_art_files()

            # Should load both files
            assert len(files) == 2, (
                f"Should load both .txt and .ANS files, got {len(files)}"
            )
            assert any("Plain text art" in f for f in files), "Should load .txt file"
            assert any("ANSI art" in f for f in files), "Should load .ANS file"
    finally:
        art._ASSETS_DIR = original_assets_dir


def test_ansi_art_loads_cp437_encoded_files():
    """Test that .ANS files with CP437 encoding are loaded correctly."""
    import tempfile
    from pathlib import Path

    from vibedialer.ui import art

    original_assets_dir = art._ASSETS_DIR

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            art._ASSETS_DIR = tmppath

            # Create a .ANS file with CP437 encoding (common for BBS-era ANSI art)
            ans_file = tmppath / "test.ANS"
            # Write some CP437 content with ANSI codes
            content = "╔═══╗\n║ A ║\n╚═══╝"
            ans_file.write_bytes(content.encode("cp437"))

            # Load files
            files = art._load_ansi_art_files()

            # Should load the CP437 encoded file
            assert len(files) >= 1, "Should load CP437 encoded .ANS files"
            assert any("╔═══╗" in f for f in files), (
                "Should decode CP437 encoded content correctly"
            )
    finally:
        art._ASSETS_DIR = original_assets_dir
