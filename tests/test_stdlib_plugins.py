"""Tests for stdlib_plugins module"""

import pytest
import re
from pathlib import Path
from html.parser import HTMLParser
from typing import Any

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


class HTMLClassExtractor(HTMLParser):
    """Simple HTML parser to extract elements with specific classes"""

    def __init__(self) -> None:
        super().__init__()
        self.elements: list[dict[str, Any]] = []
        self.current_tag: str | None = None
        self.current_attrs: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.current_tag = tag
        self.current_attrs = {k: v or '' for k, v in attrs}
        self.elements.append({
            'tag': tag,
            'attrs': {k: v or '' for k, v in attrs}
        })

    def get_elements_by_class(self, class_name: str) -> list[dict[str, Any]]:
        """Get all elements with a specific class"""
        result: list[dict[str, Any]] = []
        for elem in self.elements:
            if 'class' in elem['attrs']:
                classes = elem['attrs']['class'].split()
                if class_name in classes:
                    result.append(elem)
        return result

    def get_elements_with_attribute(self, attr_name: str) -> list[dict[str, Any]]:
        """Get all elements with a specific attribute"""
        result: list[dict[str, Any]] = []
        for elem in self.elements:
            if attr_name in elem['attrs']:
                result.append(elem)
        return result


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

    plugin_fn = slide_navigation_plugin()
    result = plugin_fn(slide)

    assert result is slide

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


def test_navigation_html_css() -> None:
    """Test that navigation plugin generates correct CSS"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(Page(Header("Page 1", level=1)))
    slide.add_page(Page(Header("Page 2", level=1)))

    output = Path("test_nav_css.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Critical CSS rules for hiding pages
        assert '.page {' in html
        assert 'display: none !important;' in html

        # Critical CSS rules for slide containers
        assert '.slide-page {' in html
        assert 'display: none;' in html

        # Critical CSS rule for showing active slide
        assert '.slide-page.active {' in html
        assert 'display: block;' in html

        # CSS rule for showing page inside active slide
        assert '.slide-page.active .page {' in html
        assert 'display: flex !important;' in html

        # Container CSS
        assert '.slide-container {' in html
        assert 'position: fixed;' in html
    finally:
        if output.exists():
            output.unlink()


def test_navigation_html_javascript() -> None:
    """Test that navigation plugin generates correct JavaScript"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(Page(Header("Page 1", level=1)))
    slide.add_page(Page(Header("Page 2", level=1)))
    slide.add_page(Page(Header("Page 3", level=1)))

    output = Path("test_nav_js.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # JavaScript functions
        assert 'function initSlides()' in html
        assert 'function goToSlide(index)' in html

        # data-slide-index attribute setup
        assert 'slideDiv.dataset.slideIndex = index;' in html

        # Active class manipulation
        assert "slide.classList.remove('active')" in html
        assert "slides[currentSlide].classList.add('active')" in html

        # Keyboard event handling
        assert "e.key === 'ArrowLeft'" in html
        assert "e.key === 'ArrowRight'" in html

        # DOM manipulation
        assert "document.createElement('div')" in html
        assert "container.className = 'slide-container'" in html
    finally:
        if output.exists():
            output.unlink()


def test_navigation_multiple_pages_structure() -> None:
    """Test navigation with multiple pages creates correct HTML structure"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(Page(Header("First", level=1), Text("Content 1")))
    slide.add_page(Page(Header("Second", level=1), Text("Content 2")))
    slide.add_page(Page(Header("Third", level=1), Text("Content 3")))

    output = Path("test_nav_multi.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # All pages should exist in HTML
        assert 'First' in html
        assert 'Second' in html
        assert 'Third' in html
        assert 'Content 1' in html
        assert 'Content 2' in html
        assert 'Content 3' in html

        # Should have page divs
        assert html.count('class="page"') == 3

        # Should have indicator
        assert 'slide-indicator' in html

        # Should have controls
        assert 'prev-slide' in html
        assert 'next-slide' in html
    finally:
        if output.exists():
            output.unlink()


def test_presenter_mode_html_structure() -> None:
    """Test presenter mode plugin generates correct HTML structure"""
    slide = create_slide()
    slide.use(speaker_notes_plugin())

    slide.add_page(Page(
        Header("Test Slide", level=1),
        SpeakerNote("Important note")  # type: ignore[arg-type]
    ))

    output = Path("test_presenter_html.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Presenter mode container
        assert '<div class="presenter-mode" id="presenter-mode">' in html

        # Presenter mode grid sections
        assert 'presenter-current' in html
        assert 'presenter-notes' in html
        assert 'presenter-next' in html

        # Presenter mode IDs
        assert 'id="presenter-current-slide"' in html
        assert 'id="presenter-notes-content"' in html
        assert 'id="presenter-next-slide"' in html

        # Toggle button
        assert 'id="presenter-toggle"' in html
        assert "Press 'P' for Presenter View" in html
    finally:
        if output.exists():
            output.unlink()


def test_presenter_mode_javascript() -> None:
    """Test presenter mode plugin generates correct JavaScript"""
    slide = create_slide()
    slide.use(speaker_notes_plugin())

    slide.add_page(Page(Header("Test", level=1)))

    output = Path("test_presenter_js.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # JavaScript functions
        assert 'function togglePresenterMode()' in html
        assert 'function updatePresenterView()' in html

        # Presenter mode state
        assert 'let presenterMode = false;' in html

        # Keyboard shortcut
        assert "e.key === 'p' || e.key === 'P'" in html

        # DOM queries
        assert "document.querySelector('.slide-page.active')" in html
        assert "document.getElementById('presenter-mode')" in html

        # Null check
        assert 'if (!presenterDiv) return;' in html
    finally:
        if output.exists():
            output.unlink()


def test_combined_plugins_html() -> None:
    """Test that all plugins work together in generated HTML"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())
    slide.use(speaker_notes_plugin())
    slide.use(syntax_highlighting_plugin('atom-one-dark'))

    slide.add_page(Page(
        Header("Test Page", level=1),
        Code("x = 1", lang="python"),
        SpeakerNote("Test note")  # type: ignore[arg-type]
    ))

    output = Path("test_combined_plugins.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Navigation elements
        assert '.slide-page {' in html
        assert 'function goToSlide' in html

        # Presenter mode elements
        assert 'presenter-mode' in html
        assert 'function togglePresenterMode' in html

        # Syntax highlighting elements
        assert 'highlight.js' in html
        assert 'atom-one-dark' in html

        # All should coexist
        assert 'slide-container' in html
        assert 'speaker-note' in html
        assert 'code-container' in html
    finally:
        if output.exists():
            output.unlink()


def test_html_dom_page_classes() -> None:
    """Test that HTML DOM has correct classes on page elements"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(Page(Header("First", level=1)))
    slide.add_page(Page(Header("Second", level=1)))
    slide.add_page(Page(Header("Third", level=1)))

    output = Path("test_dom_classes.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        parser = HTMLClassExtractor()
        parser.feed(html)

        # Check for page divs
        page_divs = parser.get_elements_by_class('page')
        assert len(page_divs) == 3, f"Expected 3 page divs, got {len(page_divs)}"

        # Verify all page divs have the 'page' class
        for page_div in page_divs:
            assert 'page' in page_div['attrs']['class']
            assert page_div['tag'] == 'div'
    finally:
        if output.exists():
            output.unlink()


def test_html_dom_javascript_initialization() -> None:
    """Test that JavaScript properly initializes slides"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(Page(Header("Page 1", level=1)))
    slide.add_page(Page(Header("Page 2", level=1)))

    output = Path("test_js_init.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Verify goToSlide(0) is called on initialization
        assert 'goToSlide(0)' in html, "JavaScript should call goToSlide(0) on init"

        # Verify slides array is created
        assert 'let slides = []' in html or 'let slides=[]' in html

        # Verify currentSlide variable
        assert 'let currentSlide = 0' in html or 'let currentSlide=0' in html

        # Verify slide wrapping logic
        assert 'slideDiv.className = \'slide-page\'' in html or 'slideDiv.className="slide-page"' in html
    finally:
        if output.exists():
            output.unlink()


def test_html_css_display_rules() -> None:
    """Test that CSS has correct display rules for page visibility"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(Page(Header("Test", level=1)))

    output = Path("test_css_display.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Verify critical display rules in full HTML
        assert re.search(r'\.page\s*\{[^}]*display:\s*none\s*!important', html), \
            "CSS should hide .page with display: none !important"

        assert re.search(r'\.slide-page\s*\{[^}]*display:\s*none', html), \
            "CSS should hide .slide-page with display: none"

        assert re.search(r'\.slide-page\.active\s*\{[^}]*display:\s*block', html), \
            "CSS should show .slide-page.active with display: block"

        assert re.search(r'\.slide-page\.active\s+\.page\s*\{[^}]*display:\s*flex\s*!important', html), \
            "CSS should show .slide-page.active .page with display: flex !important"
    finally:
        if output.exists():
            output.unlink()


def test_html_javascript_active_class_logic() -> None:
    """Test that JavaScript correctly manages active class"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(Page(Header("Page 1", level=1)))
    slide.add_page(Page(Header("Page 2", level=1)))

    output = Path("test_active_class.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Verify active class is removed from all slides
        assert "slide.classList.remove('active')" in html or \
               'slide.classList.remove("active")' in html, \
            "JavaScript should remove 'active' class from all slides"

        # Verify active class is added to current slide
        assert "slides[currentSlide].classList.add('active')" in html or \
               'slides[currentSlide].classList.add("active")' in html, \
            "JavaScript should add 'active' class to current slide"

        # Verify this happens in goToSlide function
        assert 'function goToSlide' in html
        go_to_slide_match = re.search(r'function goToSlide\([^)]*\)\s*\{(.*?)\n\s*\}', html, re.DOTALL)
        assert go_to_slide_match, "Should find goToSlide function"

        go_to_slide_body = go_to_slide_match.group(1)
        assert 'remove' in go_to_slide_body and 'active' in go_to_slide_body, \
            "goToSlide should remove active class"
        assert 'add' in go_to_slide_body and 'active' in go_to_slide_body, \
            "goToSlide should add active class"
    finally:
        if output.exists():
            output.unlink()


def test_html_presenter_mode_elements_exist() -> None:
    """Test that presenter mode creates required DOM elements"""
    slide = create_slide()
    slide.use(speaker_notes_plugin())

    slide.add_page(Page(
        Header("Test", level=1),
        SpeakerNote("Test note")  # type: ignore[arg-type]
    ))

    output = Path("test_presenter_dom.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        parser = HTMLClassExtractor()
        parser.feed(html)

        # Check for presenter-mode div
        presenter_divs = parser.get_elements_by_class('presenter-mode')
        assert len(presenter_divs) >= 1, "Should have at least one presenter-mode div"

        # Check for speaker-note div
        speaker_notes = parser.get_elements_by_class('speaker-note')
        assert len(speaker_notes) >= 1, "Should have at least one speaker-note div"

        # Check for presenter toggle button
        presenter_toggles = parser.get_elements_by_class('presenter-toggle')
        assert len(presenter_toggles) >= 1, "Should have presenter toggle button"
    finally:
        if output.exists():
            output.unlink()
