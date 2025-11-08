"""Tests for yogrt.slide module"""

import pytest
import tempfile
from pathlib import Path

from yogrt.slide import Slide, Plugin
from dataclasses import replace
from yogrt.core import Component, Context


# Test fixtures
@pytest.fixture
def empty_slide() -> Slide:
    """Create an empty slide"""
    return Slide()


@pytest.fixture
def simple_page() -> Component:
    """Create a simple page component"""
    text = Component(tag='text', props={'content': 'Hello'}, children=())
    return Component(tag='page', props={}, children=(text,))


# Test Slide initialization
def test_slide_initialization(empty_slide: Slide) -> None:
    """Test that Slide initializes correctly"""
    assert empty_slide.pages == []
    assert isinstance(empty_slide.context, Context)
    assert empty_slide.transforms == []
    assert empty_slide.html_transforms == []


# Test add_page
def test_add_page(empty_slide: Slide, simple_page: Component) -> None:
    """Test adding a page to slide"""
    result = empty_slide.add_page(simple_page)

    assert len(empty_slide.pages) == 1
    assert empty_slide.pages[0] == simple_page
    assert result is empty_slide  # Method chaining


def test_add_multiple_pages(empty_slide: Slide) -> None:
    """Test adding multiple pages"""
    page1 = Component(tag='page', props={}, children=())
    page2 = Component(tag='page', props={}, children=())

    empty_slide.add_page(page1).add_page(page2)

    assert len(empty_slide.pages) == 2
    assert empty_slide.pages[0] == page1
    assert empty_slide.pages[1] == page2


# Test add_renderer
def test_add_renderer(empty_slide: Slide) -> None:
    """Test adding a custom renderer"""
    def custom_renderer(comp: Component, ctx: Context) -> str:
        return "<custom />"

    result = empty_slide.add_renderer('custom', custom_renderer)

    assert 'custom' in empty_slide.context.renderers
    assert empty_slide.context.renderers['custom'] == custom_renderer
    assert result is empty_slide  # Method chaining


# Test add_transform
def test_add_transform(empty_slide: Slide) -> None:
    """Test adding a transform"""
    def my_transform(comp: Component) -> Component:
        return comp

    result = empty_slide.add_transform(my_transform)

    assert len(empty_slide.transforms) == 1
    assert empty_slide.transforms[0] == my_transform
    assert result is empty_slide  # Method chaining


# Test add_html_transform
def test_add_html_transform(empty_slide: Slide) -> None:
    """Test adding an HTML transform"""
    def my_html_transform(html: str) -> str:
        return html + "<!-- modified -->"

    result = empty_slide.add_html_transform(my_html_transform)

    assert len(empty_slide.html_transforms) == 1
    assert empty_slide.html_transforms[0] == my_html_transform
    assert result is empty_slide  # Method chaining


# Test use (plugin)
def test_use_plugin(empty_slide: Slide) -> None:
    """Test applying a plugin"""
    def my_plugin(slide: Slide) -> Slide:
        slide.add_renderer('plugin-tag', lambda c, ctx: "<plugin />")
        return slide

    result = empty_slide.use(my_plugin)

    assert 'plugin-tag' in empty_slide.context.renderers
    assert result is empty_slide


# Test build
def test_build_applies_transforms(empty_slide: Slide) -> None:
    """Test that build applies all transforms"""
    text = Component(tag='text', props={'count': 0}, children=())
    page = Component(tag='page', props={}, children=(text,))

    empty_slide.add_page(page)

    # Add transforms that increment count
    def increment_count(comp: Component) -> Component:
        if comp.tag == 'text':
            props = {**comp.props, 'count': comp.props['count'] + 1}
            return replace(comp, props=props)
        return comp

    empty_slide.add_transform(increment_count)
    empty_slide.add_transform(increment_count)

    built = empty_slide.build()

    # Check that transforms were applied
    text_comp = built.pages[0].children[0]
    assert text_comp.props['count'] == 2


def test_build_creates_new_slide(empty_slide: Slide, simple_page: Component) -> None:
    """Test that build creates a new Slide instance"""
    empty_slide.add_page(simple_page)

    built = empty_slide.build()

    # Should be different instances
    assert built is not empty_slide
    # But pages should be transformed copies
    assert len(built.pages) == 1


def test_build_preserves_context_and_html_transforms(empty_slide: Slide) -> None:
    """Test that build preserves context and HTML transforms"""
    def my_renderer(comp: Component, ctx: Context) -> str:
        return "<test />"

    def my_html_transform(html: str) -> str:
        return html + "<!-- test -->"

    empty_slide.add_renderer('test', my_renderer)
    empty_slide.add_html_transform(my_html_transform)

    built = empty_slide.build()

    assert built.context is empty_slide.context
    assert built.html_transforms == empty_slide.html_transforms


# Test export
def test_export_creates_file(empty_slide: Slide, tmp_path: Path) -> None:
    """Test that export creates an HTML file"""
    # Add a simple page
    page = Component(tag='page', props={}, children=())
    empty_slide.add_page(page)

    # Add renderer
    def page_renderer(comp: Component, ctx: Context) -> str:
        return '<div class="page">Test Page</div>'

    empty_slide.add_renderer('page', page_renderer)

    # Export
    output_file = tmp_path / "test.html"
    empty_slide.export(str(output_file))

    # Check file exists
    assert output_file.exists()

    # Check content
    content = output_file.read_text()
    assert '<!DOCTYPE html>' in content
    assert '<div class="page">Test Page</div>' in content


def test_export_applies_html_transforms(empty_slide: Slide, tmp_path: Path) -> None:
    """Test that export applies HTML transforms"""
    page = Component(tag='page', props={}, children=())
    empty_slide.add_page(page)

    def page_renderer(comp: Component, ctx: Context) -> str:
        return '<div class="page" />'

    empty_slide.add_renderer('page', page_renderer)

    # Add HTML transform
    def add_comment(html: str) -> str:
        return html.replace('</body>', '<!-- Modified --></body>')

    empty_slide.add_html_transform(add_comment)

    # Export
    output_file = tmp_path / "test.html"
    empty_slide.export(str(output_file))

    content = output_file.read_text()
    assert '<!-- Modified -->' in content


def test_export_sets_context_page_numbers(empty_slide: Slide, tmp_path: Path) -> None:
    """Test that export sets correct page numbers in context"""
    # Create pages that record their page number
    page_numbers: list[int] = []

    def recording_renderer(comp: Component, ctx: Context) -> str:
        page_numbers.append(ctx.current_page)
        return f'<div class="page">Page {ctx.current_page}</div>'

    empty_slide.add_renderer('page', recording_renderer)

    # Add three pages
    for _ in range(3):
        empty_slide.add_page(Component(tag='page', props={}, children=()))

    # Export
    output_file = tmp_path / "test.html"
    empty_slide.export(str(output_file))

    # Check page numbers
    assert page_numbers == [1, 2, 3]

    # Check content
    content = output_file.read_text()
    assert 'Page 1' in content
    assert 'Page 2' in content
    assert 'Page 3' in content


# Test Plugin type
def test_plugin_type_compatibility() -> None:
    """Test that plugins work as expected"""
    def create_test_plugin() -> Plugin:
        def plugin(slide: Slide) -> Slide:
            slide.add_renderer('test', lambda c, ctx: "<test />")
            return slide
        return plugin

    plugin = create_test_plugin()
    slide = Slide()
    result = slide.use(plugin)

    assert 'test' in result.context.renderers


# Integration tests
def test_full_slide_workflow(tmp_path: Path) -> None:
    """Test complete slide workflow: build, transform, render, export"""
    slide = Slide()

    # Add renderers
    def header_renderer(comp: Component, ctx: Context) -> str:
        text = comp.props['text']
        level = comp.props['level']
        return f"<h{level}>{text}</h{level}>"

    def text_renderer(comp: Component, ctx: Context) -> str:
        content = comp.props['content']
        return f"<p>{content}</p>"

    def page_renderer(comp: Component, ctx: Context) -> str:
        from yogrt.core import render
        children_html = [render(child, ctx) for child in comp.children]
        return f'<div class="page">{"".join(children_html)}</div>'

    slide.add_renderer('header', header_renderer)
    slide.add_renderer('text', text_renderer)
    slide.add_renderer('page', page_renderer)

    # Add transform
    def add_ids_to_headers(comp: Component) -> Component:
        if comp.tag == 'header':
            text = comp.props['text']
            id_value = text.lower().replace(' ', '-')
            props = {**comp.props, 'id': id_value}
            return replace(comp, props=props)
        return comp

    slide.add_transform(add_ids_to_headers)

    # Add HTML transform
    def add_meta_tag(html: str) -> str:
        return html.replace(
            '</head>',
            '<meta name="generator" content="yogrt" /></head>'
        )

    slide.add_html_transform(add_meta_tag)

    # Add pages
    header1 = Component(tag='header', props={'text': 'First Page', 'level': 1}, children=())
    text1 = Component(tag='text', props={'content': 'Content of first page'}, children=())
    page1 = Component(tag='page', props={}, children=(header1, text1))

    header2 = Component(tag='header', props={'text': 'Second Page', 'level': 1}, children=())
    text2 = Component(tag='text', props={'content': 'Content of second page'}, children=())
    page2 = Component(tag='page', props={}, children=(header2, text2))

    slide.add_page(page1).add_page(page2)

    # Export
    output_file = tmp_path / "full_test.html"
    slide.export(str(output_file))

    # Verify
    content = output_file.read_text()

    # Check HTML structure
    assert '<!DOCTYPE html>' in content
    assert '<meta name="generator" content="yogrt" />' in content

    # Check pages
    assert '<div class="page">' in content

    # Check headers (should have IDs from transform)
    assert '<h1>First Page</h1>' in content
    assert '<h1>Second Page</h1>' in content

    # Check content
    assert '<p>Content of first page</p>' in content
    assert '<p>Content of second page</p>' in content


def test_multiple_plugins_work_together(tmp_path: Path) -> None:
    """Test that multiple plugins can be composed"""
    slide = Slide()

    # Plugin 1: Adds header renderer
    def header_plugin(slide: Slide) -> Slide:
        def header_renderer(comp: Component, ctx: Context) -> str:
            return f"<h1>{comp.props['text']}</h1>"
        slide.add_renderer('header', header_renderer)
        return slide

    # Plugin 2: Adds text renderer
    def text_plugin(slide: Slide) -> Slide:
        def text_renderer(comp: Component, ctx: Context) -> str:
            return f"<p>{comp.props['content']}</p>"
        slide.add_renderer('text', text_renderer)
        return slide

    # Plugin 3: Adds page renderer
    def page_plugin(slide: Slide) -> Slide:
        def page_renderer(comp: Component, ctx: Context) -> str:
            from yogrt.core import render
            children_html = [render(child, ctx) for child in comp.children]
            return f'<div class="page">{"".join(children_html)}</div>'
        slide.add_renderer('page', page_renderer)
        return slide

    # Apply all plugins
    slide.use(header_plugin).use(text_plugin).use(page_plugin)

    # Add a page
    header = Component(tag='header', props={'text': 'Title'}, children=())
    text = Component(tag='text', props={'content': 'Body'}, children=())
    page = Component(tag='page', props={}, children=(header, text))

    slide.add_page(page)

    # Export
    output_file = tmp_path / "plugins_test.html"
    slide.export(str(output_file))

    content = output_file.read_text()

    assert '<h1>Title</h1>' in content
    assert '<p>Body</p>' in content
