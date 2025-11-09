"""Tests for stdlib_plugins module"""

import pytest
from pathlib import Path

from yogrt import (
    create_slide,
    Page,
    Header,
    Text,
    Code,
    SpeakerNote,
    slide_navigation_plugin,
    speaker_notes_plugin,
    syntax_highlighting_plugin,
)
from yogrt.stdlib_plugins import SpeakerNoteComponent


def test_speaker_note_component() -> None:
    """Test SpeakerNote component creation"""
    note = SpeakerNote("This is a speaker note")

    assert isinstance(note, SpeakerNoteComponent)
    assert note.content == "This is a speaker note"
    assert note.tag == "speaker-note"
    assert note.key is None


def test_speaker_note_with_key() -> None:
    """Test SpeakerNote with key"""
    note = SpeakerNote("Note content", key="test-key")

    assert note.key == "test-key"


def test_slide_navigation_plugin() -> None:
    """Test slide navigation plugin integration"""
    slide = create_slide()

    # Use the plugin
    plugin_fn = slide_navigation_plugin()
    result = plugin_fn(slide)

    # Should return the slide (for chaining)
    assert result is slide

    # Add a simple page
    slide.add_page(Page(Header("Test", level=1)))

    # Export and check HTML contains navigation JS
    output = Path("test_nav.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Check for navigation elements
        assert 'slide-container' in html
        assert 'slide-page' in html
        assert 'ArrowLeft' in html or 'ArrowRight' in html
        assert 'slide-indicator' in html
    finally:
        if output.exists():
            output.unlink()


def test_speaker_notes_plugin() -> None:
    """Test speaker notes plugin integration"""
    slide = create_slide()

    # Use the plugin
    plugin_fn = speaker_notes_plugin()
    result = plugin_fn(slide)

    assert result is slide

    # Add page with speaker note
    slide.add_page(Page(
        Header("Test", level=1),
        SpeakerNote("This is a note")  # type: ignore[arg-type]
    ))

    # Export and check HTML contains presenter mode
    output = Path("test_speaker.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Check for speaker note elements
        assert 'speaker-note' in html
        assert 'presenter-mode' in html
        assert 'This is a note' in html
    finally:
        if output.exists():
            output.unlink()


def test_syntax_highlighting_plugin_default() -> None:
    """Test syntax highlighting plugin with default theme"""
    slide = create_slide()

    # Use the plugin with default theme
    plugin_fn = syntax_highlighting_plugin()
    result = plugin_fn(slide)

    assert result is slide

    # Add page with code
    slide.add_page(Page(
        Code("print('hello')", lang="python")
    ))

    # Export and check HTML contains highlight.js
    output = Path("test_highlight_default.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Check for highlight.js
        assert 'highlight.js' in html
        assert 'atom-one-dark' in html  # default theme
        assert 'hljs.highlightElement' in html
    finally:
        if output.exists():
            output.unlink()


def test_syntax_highlighting_plugin_monokai() -> None:
    """Test syntax highlighting plugin with monokai theme"""
    slide = create_slide()

    # Use the plugin with monokai theme
    plugin_fn = syntax_highlighting_plugin('monokai')
    slide.use(plugin_fn)

    slide.add_page(Page(
        Code("const x = 42;", lang="javascript")
    ))

    output = Path("test_highlight_monokai.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Check for monokai theme
        assert 'monokai' in html
    finally:
        if output.exists():
            output.unlink()


def test_syntax_highlighting_plugin_github() -> None:
    """Test syntax highlighting plugin with github theme"""
    slide = create_slide()

    plugin_fn = syntax_highlighting_plugin('github')
    slide.use(plugin_fn)

    slide.add_page(Page(
        Code("fn main() {}", lang="rust")
    ))

    output = Path("test_highlight_github.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        assert 'github' in html
    finally:
        if output.exists():
            output.unlink()


def test_syntax_highlighting_plugin_vs() -> None:
    """Test syntax highlighting plugin with vs theme"""
    slide = create_slide()

    plugin_fn = syntax_highlighting_plugin('vs')
    slide.use(plugin_fn)

    slide.add_page(Page(
        Code("public class Test {}", lang="java")
    ))

    output = Path("test_highlight_vs.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        assert 'styles/vs' in html
    finally:
        if output.exists():
            output.unlink()


def test_all_plugins_together() -> None:
    """Test using all plugins together"""
    slide = create_slide()

    # Use all plugins
    slide.use(slide_navigation_plugin())
    slide.use(speaker_notes_plugin())
    slide.use(syntax_highlighting_plugin('atom-one-dark'))

    # Add pages with all features
    slide.add_page(Page(
        Header("Page 1", level=1),
        Text("Content"),
        SpeakerNote("Note for page 1")  # type: ignore[arg-type]
    ))

    slide.add_page(Page(
        Header("Page 2", level=1),
        Code("x = 1 + 2", lang="python"),
        SpeakerNote("Note for page 2")  # type: ignore[arg-type]
    ))

    # Export and verify all features present
    output = Path("test_all_plugins.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Navigation
        assert 'slide-container' in html
        assert 'ArrowLeft' in html or 'ArrowRight' in html

        # Speaker notes
        assert 'speaker-note' in html
        assert 'presenter-mode' in html

        # Syntax highlighting
        assert 'highlight.js' in html
        assert 'hljs.highlightElement' in html

        # Content
        assert 'Page 1' in html
        assert 'Page 2' in html
        assert 'Note for page 1' in html
        assert 'Note for page 2' in html
    finally:
        if output.exists():
            output.unlink()


def test_code_block_with_copy_button() -> None:
    """Test that code blocks have copy button"""
    slide = create_slide()

    slide.add_page(Page(
        Code("test code", lang="python")
    ))

    output = Path("test_copy_button.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Check for copy button elements
        assert 'code-container' in html
        assert 'code-header' in html
        assert 'code-copy-btn' in html
        assert 'Copy' in html
    finally:
        if output.exists():
            output.unlink()


def test_speaker_note_tag() -> None:
    """Test speaker note tag property"""
    note = SpeakerNote("Test")
    assert note.tag == "speaker-note"


def test_speaker_note_frozen() -> None:
    """Test that SpeakerNoteComponent is frozen"""
    note = SpeakerNote("Test")

    with pytest.raises(Exception):  # FrozenInstanceError
        note.content = "Changed"  # type: ignore
