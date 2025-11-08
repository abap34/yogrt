"""Tests for yogrt.core module"""

import pytest
from dataclasses import replace
from yogrt.core import (
    Component,
    Context,
    render,
    transform,
    walk,
    find_components,
    filter_by_tag,
    map_components,
    default_renderer,
    TextComponent,
    HeaderComponent,
    PageComponent,
)


# Test fixtures
@pytest.fixture
def simple_text_component() -> Component:
    """Simple text component for testing"""
    return TextComponent(content='Hello')


@pytest.fixture
def nested_component() -> Component:
    """Nested component for testing"""
    header = HeaderComponent(text='Title', level=1)
    text = TextComponent(content='Content')
    return PageComponent(children=(header, text))


# Test Component type
def test_component_structure(simple_text_component: Component) -> None:
    """Test that Component has correct structure"""
    assert hasattr(simple_text_component, 'tag')
    assert simple_text_component.tag == 'text'
    assert isinstance(simple_text_component, TextComponent)
    assert simple_text_component.content == 'Hello'


# Test Context
def test_context_creation() -> None:
    """Test Context initialization"""
    ctx = Context()
    assert ctx.renderers == {}
    assert ctx.current_page == 1
    assert ctx.total_pages == 1
    assert ctx.footnotes == {}
    assert ctx.citations == {}
    assert ctx.headers == []


def test_context_get_renderer() -> None:
    """Test Context.get_renderer"""
    ctx = Context()

    # Test with custom renderer
    def custom_renderer(comp: Component, ctx: Context) -> str:
        return "<custom />"

    ctx.renderers['custom'] = custom_renderer
    assert ctx.get_renderer('custom') == custom_renderer

    # Test with default renderer
    assert ctx.get_renderer('unknown') == default_renderer


# Test render function
def test_render_with_custom_renderer(simple_text_component: Component) -> None:
    """Test render function with custom renderer"""
    def text_renderer(comp: Component, ctx: Context) -> str:
        assert isinstance(comp, TextComponent)
        return f"<p>{comp.content}</p>"

    ctx = Context(renderers={'text': text_renderer})
    result = render(simple_text_component, ctx)

    assert result == "<p>Hello</p>"


def test_render_nested_component(nested_component: Component) -> None:
    """Test render function with nested components"""
    def header_renderer(comp: Component, ctx: Context) -> str:
        assert isinstance(comp, HeaderComponent)
        return f"<h{comp.level}>{comp.text}</h{comp.level}>"

    def text_renderer(comp: Component, ctx: Context) -> str:
        assert isinstance(comp, TextComponent)
        return f"<p>{comp.content}</p>"

    def page_renderer(comp: Component, ctx: Context) -> str:
        assert isinstance(comp, PageComponent)
        children_html = [render(child, ctx) for child in comp.children]
        return f'<div class="page">{"".join(children_html)}</div>'

    ctx = Context(renderers={
        'page': page_renderer,
        'header': header_renderer,
        'text': text_renderer
    })

    result = render(nested_component, ctx)
    assert '<h1>Title</h1>' in result
    assert '<p>Content</p>' in result
    assert '<div class="page">' in result


def test_render_with_default_renderer() -> None:
    """Test render with default renderer for unknown tag"""
    from yogrt.core import ContainerComponent
    comp = ContainerComponent(children=())

    ctx = Context()
    result = render(comp, ctx)

    assert '<div' in result


# Test transform function
def test_transform_simple() -> None:
    """Test simple component transformation"""
    comp = TextComponent(content='Hello')

    def add_class(c: Component) -> Component:
        if isinstance(c, TextComponent):
            return replace(c, class_name='styled')
        return c

    result = transform(comp, add_class)

    assert isinstance(result, TextComponent)
    assert result.class_name == 'styled'
    assert result.content == 'Hello'  # Original prop preserved


# Test walk function
def test_walk_applies_to_all_nodes(nested_component: Component) -> None:
    """Test that walk applies function to all nodes"""
    visited = []

    def track_visit(comp: Component) -> Component:
        visited.append(comp.tag)
        return comp

    result = walk(nested_component, track_visit)

    # All nodes should be visited
    assert 'page' in visited
    assert 'header' in visited
    assert 'text' in visited
    assert len(visited) == 3


def test_walk_preserves_structure(nested_component: Component) -> None:
    """Test that walk preserves component structure"""
    def identity(comp: Component) -> Component:
        return comp

    result = walk(nested_component, identity)

    assert result.tag == nested_component.tag
    assert isinstance(result, PageComponent)
    assert len(result.children) == len(nested_component.children)  # type: ignore[union-attr]
    assert result.children[0].tag == 'header'
    assert result.children[1].tag == 'text'


def test_walk_post_order() -> None:
    """Test that walk processes children before parent"""
    order: list[str] = []

    def track_order(comp: Component) -> Component:
        order.append(comp.tag)
        return comp

    child1 = TextComponent(content='child1')
    child2 = TextComponent(content='child2')
    comp = PageComponent(children=(child1, child2))

    walk(comp, track_order)

    # Children should be visited before parent
    assert order == ['text', 'text', 'page']


# Test find_components
def test_find_components_with_predicate(nested_component: Component) -> None:
    """Test find_components with custom predicate"""
    # Find all text components
    texts = find_components(
        nested_component,
        lambda c: c.tag == 'text'
    )

    assert len(texts) == 1
    assert isinstance(texts[0], TextComponent)
    assert texts[0].content == 'Content'


def test_find_components_multiple_matches() -> None:
    """Test find_components with multiple matches"""
    text_a = TextComponent(content='A')
    text_b = TextComponent(content='B')
    header = HeaderComponent(text='Title', level=1)
    comp = PageComponent(children=(text_a, text_b, header))

    texts = find_components(comp, lambda c: c.tag == 'text')

    assert len(texts) == 2
    assert isinstance(texts[0], TextComponent)
    assert isinstance(texts[1], TextComponent)
    assert texts[0].content == 'A'
    assert texts[1].content == 'B'


def test_find_components_no_matches() -> None:
    """Test find_components with no matches"""
    comp = PageComponent(children=())

    result = find_components(comp, lambda c: c.tag == 'nonexistent')

    assert result == []


# Test filter_by_tag
def test_filter_by_tag(nested_component: Component) -> None:
    """Test filter_by_tag function"""
    headers = filter_by_tag(nested_component, 'header')

    assert len(headers) == 1
    assert isinstance(headers[0], HeaderComponent)
    assert headers[0].text == 'Title'


def test_filter_by_tag_multiple() -> None:
    """Test filter_by_tag with multiple matches"""
    text1 = TextComponent(content='A')
    text2 = TextComponent(content='B')
    header = HeaderComponent(text='Title', level=1)
    comp = PageComponent(children=(text1, text2, header))

    texts = filter_by_tag(comp, 'text')

    assert len(texts) == 2
    assert isinstance(texts[0], TextComponent)
    assert isinstance(texts[1], TextComponent)


# Test map_components
def test_map_components_is_walk_alias() -> None:
    """Test that map_components is an alias for walk"""
    comp = TextComponent(content='test')

    def add_key(c: Component) -> Component:
        if isinstance(c, TextComponent):
            return replace(c, key='mapped')
        return c

    result1 = walk(comp, add_key)
    result2 = map_components(comp, add_key)

    assert result1.key == result2.key
    assert result1.key == 'mapped'


# Test default_renderer
def test_default_renderer() -> None:
    """Test default_renderer function"""
    from yogrt.core import ContainerComponent
    comp = ContainerComponent(children=())

    ctx = Context()
    result = default_renderer(comp, ctx)

    assert '<div class="container">' in result


def test_default_renderer_with_children() -> None:
    """Test default_renderer with children"""
    def text_renderer(comp: Component, ctx: Context) -> str:
        assert isinstance(comp, TextComponent)
        return f"<p>{comp.content}</p>"

    child = TextComponent(content='Child')
    from yogrt.core import ContainerComponent
    comp = ContainerComponent(children=(child,))

    ctx = Context(renderers={'text': text_renderer})
    result = default_renderer(comp, ctx)

    assert '<div class="container">' in result
    assert '<p>Child</p>' in result


# Integration tests
def test_full_rendering_pipeline() -> None:
    """Test complete rendering pipeline"""
    from yogrt.core import ContainerComponent

    # Create a slide structure
    header1 = HeaderComponent(text='Page 1', level=1)
    text1 = TextComponent(content='Content 1')
    page1 = PageComponent(children=(header1, text1))

    header2 = HeaderComponent(text='Page 2', level=1)
    text2 = TextComponent(content='Content 2')
    page2 = PageComponent(children=(header2, text2))

    slide_comp = ContainerComponent(children=(page1, page2))

    # Transform: add IDs to headers
    def add_header_ids(comp: Component) -> Component:
        if isinstance(comp, HeaderComponent):
            id_value = comp.text.lower().replace(' ', '-')
            return replace(comp, id=id_value)
        return comp

    transformed = walk(slide_comp, add_header_ids)

    # Verify transformation
    headers = filter_by_tag(transformed, 'header')
    assert len(headers) == 2
    assert isinstance(headers[0], HeaderComponent)
    assert isinstance(headers[1], HeaderComponent)
    assert headers[0].id == 'page-1'
    assert headers[1].id == 'page-2'

    # Render
    def header_renderer(comp: Component, ctx: Context) -> str:
        assert isinstance(comp, HeaderComponent)
        id_attr = f' id="{comp.id}"' if comp.id else ''
        return f"<h{comp.level}{id_attr}>{comp.text}</h{comp.level}>"

    def text_renderer(comp: Component, ctx: Context) -> str:
        assert isinstance(comp, TextComponent)
        return f"<p>{comp.content}</p>"

    def page_renderer(comp: Component, ctx: Context) -> str:
        assert isinstance(comp, PageComponent)
        children_html = [render(child, ctx) for child in comp.children]
        return f'<div class="page">{"".join(children_html)}</div>'

    def slide_renderer(comp: Component, ctx: Context) -> str:
        from yogrt.core import ContainerComponent
        assert isinstance(comp, ContainerComponent)
        children_html = [render(child, ctx) for child in comp.children]
        return f'<div class="slide">{"".join(children_html)}</div>'

    ctx = Context(renderers={
        'container': slide_renderer,
        'page': page_renderer,
        'header': header_renderer,
        'text': text_renderer
    })

    result = render(transformed, ctx)

    # Verify rendered HTML
    assert '<div class="slide">' in result
    assert '<h1 id="page-1">Page 1</h1>' in result
    assert '<h1 id="page-2">Page 2</h1>' in result
    assert '<p>Content 1</p>' in result
    assert '<p>Content 2</p>' in result
