"""
Browser tests for stdlib_plugins using Playwright

To run these tests, you need to install Playwright:
    pip install playwright pytest-playwright
    python -m playwright install chromium

Then run:
    pytest tests/test_stdlib_plugins_browser.py --headed  # To see browser
    pytest tests/test_stdlib_plugins_browser.py           # Headless mode
    pytest -m browser --headed                             # Run all browser tests
    pytest -m "not browser"                                # Skip browser tests
"""

import pytest

pytestmark = pytest.mark.browser
from pathlib import Path
from playwright.sync_api import Page, expect

from yogrt import (
    create_slide,
    Page as SlidePage,
    Header,
    Text,
    Code,
    SpeakerNote,
    slide_navigation_plugin,
    speaker_notes_plugin,
    syntax_highlighting_plugin,
)


def test_navigation_only_active_slide_visible(page: Page) -> None:
    """Test that only the active slide is visible in browser"""
    # Create a slide with navigation
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(SlidePage(Header("Page 1", level=1), Text("Content 1")))
    slide.add_page(SlidePage(Header("Page 2", level=1), Text("Content 2")))
    slide.add_page(SlidePage(Header("Page 3", level=1), Text("Content 3")))

    # Export to HTML
    output = Path("test_browser_nav.html")
    try:
        slide.export(str(output))

        # Load in browser
        page.goto(f"file://{output.absolute()}")

        # Wait for JavaScript to initialize
        page.wait_for_selector('.slide-page.active', timeout=5000)

        # Get all slide-page divs
        slides = page.locator('.slide-page').all()
        assert len(slides) == 3, "Should have 3 slides"

        # Check that only first slide is visible
        first_slide = page.locator('.slide-page').nth(0)
        second_slide = page.locator('.slide-page').nth(1)
        third_slide = page.locator('.slide-page').nth(2)

        # First slide should be visible (active)
        assert first_slide.is_visible(), "First slide should be visible"
        assert first_slide.evaluate("el => el.classList.contains('active')"), \
            "First slide should have 'active' class"

        # Other slides should not be visible
        assert not second_slide.is_visible(), "Second slide should not be visible"
        assert not third_slide.is_visible(), "Third slide should not be visible"

        # Verify .page elements
        page_elements = page.locator('.page').all()
        visible_pages = [p for p in page_elements if p.is_visible()]
        assert len(visible_pages) == 1, "Only one .page element should be visible"

    finally:
        if output.exists():
            output.unlink()


def test_navigation_arrow_key_changes_slide(page: Page) -> None:
    """Test that arrow keys change the visible slide"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(SlidePage(Header("Page 1", level=1), Text("Content 1")))
    slide.add_page(SlidePage(Header("Page 2", level=1), Text("Content 2")))
    slide.add_page(SlidePage(Header("Page 3", level=1), Text("Content 3")))

    output = Path("test_browser_arrows.html")
    try:
        slide.export(str(output))
        page.goto(f"file://{output.absolute()}")
        page.wait_for_selector('.slide-page.active')

        # Initially, first slide is active
        first_slide = page.locator('.slide-page').nth(0)
        second_slide = page.locator('.slide-page').nth(1)

        assert first_slide.is_visible()
        assert not second_slide.is_visible()

        # Press ArrowRight
        page.keyboard.press('ArrowRight')

        # Wait a bit for transition
        page.wait_for_timeout(500)

        # Now second slide should be visible
        assert not first_slide.is_visible(), "First slide should not be visible after ArrowRight"
        assert second_slide.is_visible(), "Second slide should be visible after ArrowRight"
        assert second_slide.evaluate("el => el.classList.contains('active')"), \
            "Second slide should have 'active' class"

        # Press ArrowLeft
        page.keyboard.press('ArrowLeft')
        page.wait_for_timeout(500)

        # Back to first slide
        assert first_slide.is_visible(), "First slide should be visible after ArrowLeft"
        assert not second_slide.is_visible(), "Second slide should not be visible after ArrowLeft"

    finally:
        if output.exists():
            output.unlink()


def test_navigation_indicator_shows_current_slide(page: Page) -> None:
    """Test that slide indicator shows current slide number"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(SlidePage(Header("Page 1", level=1)))
    slide.add_page(SlidePage(Header("Page 2", level=1)))
    slide.add_page(SlidePage(Header("Page 3", level=1)))

    output = Path("test_browser_indicator.html")
    try:
        slide.export(str(output))
        page.goto(f"file://{output.absolute()}")
        page.wait_for_selector('.slide-indicator')

        # Check initial indicator
        indicator = page.locator('#slide-indicator')
        assert indicator.text_content() == "1 / 3", "Indicator should show 1 / 3"

        # Navigate to next slide
        page.keyboard.press('ArrowRight')
        page.wait_for_timeout(500)

        assert indicator.text_content() == "2 / 3", "Indicator should show 2 / 3"

        # Navigate to next slide
        page.keyboard.press('ArrowRight')
        page.wait_for_timeout(500)

        assert indicator.text_content() == "3 / 3", "Indicator should show 3 / 3"

    finally:
        if output.exists():
            output.unlink()


def test_presenter_mode_p_key_toggles_view(page: Page) -> None:
    """Test that 'P' key toggles presenter mode"""
    slide = create_slide()
    slide.use(speaker_notes_plugin())

    slide.add_page(SlidePage(
        Header("Test Slide", level=1),
        SpeakerNote("This is a speaker note")  # type: ignore[arg-type]
    ))

    output = Path("test_browser_presenter.html")
    try:
        slide.export(str(output))
        page.goto(f"file://{output.absolute()}")

        # Initially, presenter mode should not be visible
        presenter_mode = page.locator('#presenter-mode')
        assert not presenter_mode.is_visible(), "Presenter mode should not be visible initially"

        # Press 'P' key
        page.keyboard.press('p')
        page.wait_for_timeout(500)

        # Now presenter mode should be visible
        assert presenter_mode.is_visible(), "Presenter mode should be visible after pressing 'P'"
        assert presenter_mode.evaluate("el => el.classList.contains('active')"), \
            "Presenter mode should have 'active' class"

        # Press 'P' again to toggle off
        page.keyboard.press('P')  # Capital P should also work
        page.wait_for_timeout(500)

        # Presenter mode should be hidden again
        assert not presenter_mode.is_visible(), "Presenter mode should be hidden after second 'P'"

    finally:
        if output.exists():
            output.unlink()


def test_presenter_mode_shows_notes(page: Page) -> None:
    """Test that presenter mode shows speaker notes"""
    slide = create_slide()
    slide.use(speaker_notes_plugin())

    slide.add_page(SlidePage(
        Header("Test Slide", level=1),
        Text("Visible content"),
        SpeakerNote("Secret note for presenter")  # type: ignore[arg-type]
    ))

    output = Path("test_browser_notes.html")
    try:
        slide.export(str(output))
        page.goto(f"file://{output.absolute()}")

        # Enter presenter mode
        page.keyboard.press('p')
        page.wait_for_selector('#presenter-mode.active')

        # Check that notes are visible in presenter mode
        notes_content = page.locator('#presenter-notes-content')
        assert notes_content.is_visible(), "Notes content should be visible in presenter mode"

        # Check that the note text is present
        expect(notes_content).to_contain_text("Secret note for presenter")

    finally:
        if output.exists():
            output.unlink()


def test_combined_navigation_and_presenter_mode(page: Page) -> None:
    """Test that navigation works correctly with presenter mode"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())
    slide.use(speaker_notes_plugin())

    slide.add_page(SlidePage(
        Header("Page 1", level=1),
        SpeakerNote("Note for page 1")  # type: ignore[arg-type]
    ))
    slide.add_page(SlidePage(
        Header("Page 2", level=1),
        SpeakerNote("Note for page 2")  # type: ignore[arg-type]
    ))

    output = Path("test_browser_combined.html")
    try:
        slide.export(str(output))
        page.goto(f"file://{output.absolute()}")
        page.wait_for_selector('.slide-page.active')

        # Enter presenter mode
        page.keyboard.press('p')
        page.wait_for_selector('#presenter-mode.active')

        # Check initial note
        notes = page.locator('#presenter-notes-content')
        expect(notes).to_contain_text("Note for page 1")

        # Navigate to next slide
        page.keyboard.press('ArrowRight')
        page.wait_for_timeout(500)

        # Note should update
        expect(notes).to_contain_text("Note for page 2")
        expect(notes).not_to_contain_text("Note for page 1")

    finally:
        if output.exists():
            output.unlink()


def test_data_slide_index_attributes(page: Page) -> None:
    """Test that data-slide-index attributes are correctly set"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(SlidePage(Header("Page 1", level=1)))
    slide.add_page(SlidePage(Header("Page 2", level=1)))
    slide.add_page(SlidePage(Header("Page 3", level=1)))

    output = Path("test_browser_indices.html")
    try:
        slide.export(str(output))
        page.goto(f"file://{output.absolute()}")
        page.wait_for_selector('.slide-page[data-slide-index="0"]')

        # Check that all slides have correct data-slide-index
        slide_0 = page.locator('.slide-page[data-slide-index="0"]')
        slide_1 = page.locator('.slide-page[data-slide-index="1"]')
        slide_2 = page.locator('.slide-page[data-slide-index="2"]')

        assert slide_0.count() == 1, "Should have exactly one slide with index 0"
        assert slide_1.count() == 1, "Should have exactly one slide with index 1"
        assert slide_2.count() == 1, "Should have exactly one slide with index 2"

        # Verify attributes using JavaScript
        index_0 = slide_0.get_attribute('data-slide-index')
        index_1 = slide_1.get_attribute('data-slide-index')
        index_2 = slide_2.get_attribute('data-slide-index')

        assert index_0 == "0", "First slide should have data-slide-index='0'"
        assert index_1 == "1", "Second slide should have data-slide-index='1'"
        assert index_2 == "2", "Third slide should have data-slide-index='2'"

    finally:
        if output.exists():
            output.unlink()


def test_css_display_properties_applied(page: Page) -> None:
    """Test that CSS display properties are correctly applied by browser"""
    slide = create_slide()
    slide.use(slide_navigation_plugin())

    slide.add_page(SlidePage(Header("Page 1", level=1)))
    slide.add_page(SlidePage(Header("Page 2", level=1)))

    output = Path("test_browser_css.html")
    try:
        slide.export(str(output))
        page.goto(f"file://{output.absolute()}")
        page.wait_for_selector('.slide-page.active')

        # Check that .page elements have display: none initially (before JS wrapping)
        # After JS wraps them, check computed styles

        first_slide = page.locator('.slide-page').nth(0)
        second_slide = page.locator('.slide-page').nth(1)

        # First slide should have display: block (active)
        first_display = first_slide.evaluate("el => window.getComputedStyle(el).display")
        assert first_display == "block", "Active slide should have display: block"

        # Second slide should have display: none (not active)
        second_display = second_slide.evaluate("el => window.getComputedStyle(el).display")
        assert second_display == "none", "Inactive slide should have display: none"

        # Check .page inside active slide
        active_page = first_slide.locator('.page')
        page_display = active_page.evaluate("el => window.getComputedStyle(el).display")
        assert page_display == "flex", "Page inside active slide should have display: flex"

    finally:
        if output.exists():
            output.unlink()
