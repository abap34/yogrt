"""Tests for yogrt.components and yogrt.renderers modules"""

import pytest
import io

from yogrt.components import (
    Text, Header, Image, Code, Link,
    Page, VStack, HStack, TwoColumn, Grid, Container,
    List as ListComp,
    RawHtml, Spacer, Divider
)
from yogrt.renderers import (
    render_text, render_header, render_image, render_code, render_link,
    render_page, render_vstack, render_hstack, render_two_column, render_grid, render_container,
    render_list,
    render_raw_html, render_spacer, render_divider
)
from yogrt.core import Component, Context


# ============================================================================
# Tests for Component Factories
# ============================================================================

def test_text_component() -> None:
    """Test Text component factory"""
    comp = Text("Hello, world!")

    assert comp.tag == 'text'
    assert comp.props['content'] == 'Hello, world!'
    assert comp.children == ()


def test_text_component_with_props() -> None:
    """Test Text with additional props"""
    comp = Text("Hello", class_name="my-class")

    assert comp.props['content'] == 'Hello'
    assert comp.props['class_name'] == 'my-class'


def test_header_component() -> None:
    """Test Header component factory"""
    comp = Header("Title", level=2, id="my-title")

    assert comp.tag == 'header'
    assert comp.props['text'] == 'Title'
    assert comp.props['level'] == 2
    assert comp.props['id'] == 'my-title'


def test_image_component() -> None:
    """Test Image component factory"""
    comp = Image("photo.jpg", caption="A photo")

    assert comp.tag == 'image'
    assert comp.props['src'] == 'photo.jpg'
    assert comp.props['caption'] == 'A photo'


def test_code_component() -> None:
    """Test Code component factory"""
    code_str = "print('Hello')"
    comp = Code(code_str, lang="python")

    assert comp.tag == 'code'
    assert comp.props['code'] == code_str
    assert comp.props['lang'] == 'python'


def test_link_component() -> None:
    """Test Link component factory"""
    comp = Link("https://example.com", "Example")

    assert comp.tag == 'link'
    assert comp.props['url'] == 'https://example.com'
    assert comp.props['text'] == 'Example'


def test_page_component() -> None:
    """Test Page component factory"""
    child1 = Text("Child 1")
    child2 = Text("Child 2")

    comp = Page(child1, child2)

    assert comp.tag == 'page'
    assert len(comp.children) == 2
    assert comp.children[0] == child1
    assert comp.children[1] == child2


def test_vstack_component() -> None:
    """Test VStack component factory"""
    child1 = Text("First")
    child2 = Text("Second")

    comp = VStack(child1, child2, gap="2rem")

    assert comp.tag == 'vstack'
    assert comp.props['gap'] == '2rem'
    assert len(comp.children) == 2


def test_hstack_component() -> None:
    """Test HStack component factory"""
    child1 = Text("Left")
    child2 = Text("Right")

    comp = HStack(child1, child2)

    assert comp.tag == 'hstack'
    assert comp.props['gap'] == '1rem'  # default
    assert len(comp.children) == 2


def test_two_column_component() -> None:
    """Test TwoColumn component factory"""
    left = Text("Left content")
    right = Text("Right content")

    comp = TwoColumn(left, right)

    assert comp.tag == 'two-column'
    assert len(comp.children) == 2
    assert comp.children[0] == left
    assert comp.children[1] == right


def test_grid_component() -> None:
    """Test Grid component factory"""
    items = [Text(f"Item {i}") for i in range(4)]

    comp = Grid(*items, columns=2, gap="1rem")

    assert comp.tag == 'grid'
    assert comp.props['columns'] == 2
    assert comp.props['gap'] == '1rem'
    assert len(comp.children) == 4


def test_container_component() -> None:
    """Test Container component factory"""
    child = Text("Content")

    comp = Container(child, class_name="my-container")

    assert comp.tag == 'container'
    assert len(comp.children) == 1
    assert comp.props['class_name'] == 'my-container'


def test_list_component() -> None:
    """Test List component factory"""
    comp = ListComp("Item 1", "Item 2", "Item 3")

    assert comp.tag == 'list'
    assert comp.props['ordered'] is False
    assert len(comp.children) == 3

    # Check that strings were converted to Text components
    assert comp.children[0].tag == 'text'
    assert comp.children[0].props['content'] == 'Item 1'


def test_list_component_ordered() -> None:
    """Test List component with ordered=True"""
    comp = ListComp("First", "Second", ordered=True)

    assert comp.props['ordered'] is True


def test_list_component_with_components() -> None:
    """Test List with Component children"""
    child1 = Header("Title", level=2)
    child2 = Text("Content")

    comp = ListComp(child1, child2)

    assert len(comp.children) == 2
    assert comp.children[0] == child1
    assert comp.children[1] == child2


def test_raw_html_component() -> None:
    """Test RawHtml component factory"""
    html = '<div class="custom">Custom HTML</div>'
    comp = RawHtml(html)

    assert comp.tag == 'raw-html'
    assert comp.props['html'] == html


def test_spacer_component() -> None:
    """Test Spacer component factory"""
    comp = Spacer(height="3rem")

    assert comp.tag == 'spacer'
    assert comp.props['height'] == '3rem'


def test_divider_component() -> None:
    """Test Divider component factory"""
    comp = Divider()

    assert comp.tag == 'divider'


# ============================================================================
# Tests for Renderers
# ============================================================================

def test_render_text() -> None:
    """Test text renderer"""
    comp = Text("Hello")
    ctx = Context()

    result = render_text(comp, ctx)

    assert '<p>Hello</p>' in result


def test_render_text_with_class() -> None:
    """Test text renderer with class"""
    comp = Component(
        tag='text',
        props={'content': 'Hello', 'class': 'my-class'},
        children=()
    )
    ctx = Context()

    result = render_text(comp, ctx)

    assert 'class="my-class"' in result
    assert 'Hello' in result


def test_render_header() -> None:
    """Test header renderer"""
    comp = Header("Title", level=2, id="my-id")
    ctx = Context()

    result = render_header(comp, ctx)

    assert '<h2' in result
    assert 'id="my-id"' in result
    assert 'Title' in result
    assert '</h2>' in result


def test_render_image_with_path() -> None:
    """Test image renderer with file path"""
    comp = Image("photo.jpg", caption="My Photo")
    ctx = Context()

    result = render_image(comp, ctx)

    assert '<img src="photo.jpg"' in result
    assert '<figure>' in result
    assert '<figcaption>My Photo</figcaption>' in result


def test_render_image_without_caption() -> None:
    """Test image renderer without caption"""
    comp = Image("photo.jpg")
    ctx = Context()

    result = render_image(comp, ctx)

    assert '<img src="photo.jpg"' in result
    assert '<figure>' not in result


def test_render_code() -> None:
    """Test code renderer"""
    comp = Code("print('hello')", lang="python")
    ctx = Context()

    result = render_code(comp, ctx)

    assert '<pre><code class="language-python">' in result
    assert "print('hello')" in result
    assert '</code></pre>' in result


def test_render_link() -> None:
    """Test link renderer"""
    comp = Link("https://example.com", "Example Site")
    ctx = Context()

    result = render_link(comp, ctx)

    assert '<a href="https://example.com"' in result
    assert 'target="_blank"' in result
    assert 'Example Site' in result
    assert '</a>' in result


def test_render_page() -> None:
    """Test page renderer"""
    from yogrt.core import render as core_render

    comp = Page(Text("Content"))
    ctx = Context(renderers={'text': render_text})

    result = render_page(comp, ctx)

    assert '<div class="page"' in result
    assert 'id="page-' in result


def test_render_vstack() -> None:
    """Test vstack renderer"""
    from yogrt.core import render as core_render

    comp = VStack(Text("First"), Text("Second"), gap="2rem")
    ctx = Context(renderers={'text': render_text})

    result = render_vstack(comp, ctx)

    assert '<div class="vstack"' in result
    assert 'gap: 2rem' in result
    assert 'flex-direction: column' in result


def test_render_hstack() -> None:
    """Test hstack renderer"""
    comp = HStack(Text("Left"), Text("Right"))
    ctx = Context(renderers={'text': render_text})

    result = render_hstack(comp, ctx)

    assert '<div class="hstack"' in result
    assert 'flex-direction: row' in result


def test_render_two_column() -> None:
    """Test two-column renderer"""
    comp = TwoColumn(Text("Left"), Text("Right"))
    ctx = Context(renderers={'text': render_text})

    result = render_two_column(comp, ctx)

    assert '<div class="two-column"' in result
    assert 'grid-template-columns: 1fr 1fr' in result
    assert '<div class="left">' in result
    assert '<div class="right">' in result


def test_render_grid() -> None:
    """Test grid renderer"""
    comp = Grid(Text("1"), Text("2"), Text("3"), Text("4"), columns=2)
    ctx = Context(renderers={'text': render_text})

    result = render_grid(comp, ctx)

    assert '<div class="grid"' in result
    assert 'grid-template-columns: repeat(2, 1fr)' in result


def test_render_container() -> None:
    """Test container renderer"""
    comp = Container(Text("Content"))
    ctx = Context(renderers={'text': render_text})

    result = render_container(comp, ctx)

    assert '<div>' in result  # No class by default
    assert '</div>' in result


def test_render_list_unordered() -> None:
    """Test list renderer with unordered list"""
    comp = ListComp("Item 1", "Item 2")
    ctx = Context(renderers={'text': render_text})

    result = render_list(comp, ctx)

    assert '<ul>' in result
    assert '</ul>' in result
    assert '<li>' in result
    assert 'Item 1' in result
    assert 'Item 2' in result


def test_render_list_ordered() -> None:
    """Test list renderer with ordered list"""
    comp = ListComp("First", "Second", ordered=True)
    ctx = Context(renderers={'text': render_text})

    result = render_list(comp, ctx)

    assert '<ol>' in result
    assert '</ol>' in result


def test_render_raw_html() -> None:
    """Test raw HTML renderer"""
    html = '<div class="custom">Custom</div>'
    comp = RawHtml(html)
    ctx = Context()

    result = render_raw_html(comp, ctx)

    assert result == html


def test_render_spacer() -> None:
    """Test spacer renderer"""
    comp = Spacer(height="2rem")
    ctx = Context()

    result = render_spacer(comp, ctx)

    assert '<div class="spacer"' in result
    assert 'height: 2rem' in result


def test_render_divider() -> None:
    """Test divider renderer"""
    comp = Divider()
    ctx = Context()

    result = render_divider(comp, ctx)

    assert '<hr class="divider"' in result


# ============================================================================
# Integration Tests
# ============================================================================

def test_components_and_renderers_integration() -> None:
    """Test that all components can be rendered correctly"""
    from yogrt.core import render as core_render
    from yogrt.renderers import DEFAULT_RENDERERS

    # Create a complex page structure
    page = Page(
        Header("My Page", level=1),
        Text("Introduction text"),
        TwoColumn(
            VStack(
                Header("Left Section", level=2),
                Text("Left content"),
                Code("x = 1", lang="python")
            ),
            VStack(
                Header("Right Section", level=2),
                Text("Right content"),
                ListComp("Point 1", "Point 2", "Point 3")
            )
        ),
        Divider(),
        Link("https://example.com", "Learn more")
    )

    # Create context with all default renderers
    ctx = Context(renderers=DEFAULT_RENDERERS)

    # Render
    result = core_render(page, ctx)

    # Verify structure
    assert '<div class="page"' in result
    assert '<h1>My Page</h1>' in result
    assert 'Introduction text' in result
    assert '<div class="two-column"' in result
    assert '<h2>Left Section</h2>' in result
    assert '<h2>Right Section</h2>' in result
    assert '<code class="language-python">x = 1</code>' in result
    assert '<ul>' in result
    assert 'Point 1' in result
    assert '<hr class="divider"' in result
    assert '<a href="https://example.com"' in result


def test_nested_layouts() -> None:
    """Test deeply nested layout components"""
    from yogrt.core import render as core_render
    from yogrt.renderers import DEFAULT_RENDERERS

    # Create nested structure
    page = Page(
        Grid(
            VStack(
                Header("Q1", level=3),
                Text("First quarter")
            ),
            VStack(
                Header("Q2", level=3),
                Text("Second quarter")
            ),
            VStack(
                Header("Q3", level=3),
                Text("Third quarter")
            ),
            VStack(
                Header("Q4", level=3),
                Text("Fourth quarter")
            ),
            columns=2
        )
    )

    ctx = Context(renderers=DEFAULT_RENDERERS)
    result = core_render(page, ctx)

    # Verify nesting works
    assert '<div class="grid"' in result
    assert '<div class="vstack"' in result
    assert '<h3>Q1</h3>' in result
    assert '<h3>Q4</h3>' in result
