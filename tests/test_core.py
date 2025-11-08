"""Tests for yogrt.core module"""

import pytest
from typing import cast
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
)


# Test fixtures
@pytest.fixture
def simple_text_component() -> Component:
    """Simple text component for testing"""
    return cast(Component, {
        'tag': 'text',
        'props': {'content': 'Hello'},
        'children': []
    })


@pytest.fixture
def nested_component() -> Component:
    """Nested component for testing"""
    return cast(Component, {
        'tag': 'page',
        'props': {},
        'children': [
            {
                'tag': 'header',
                'props': {'text': 'Title', 'level': 1},
                'children': []
            },
            {
                'tag': 'text',
                'props': {'content': 'Content'},
                'children': []
            }
        ]
    })


# Test Component type
def test_component_structure(simple_text_component: Component) -> None:
    """Test that Component has correct structure"""
    assert 'tag' in simple_text_component
    assert 'props' in simple_text_component
    assert 'children' in simple_text_component
    assert simple_text_component['tag'] == 'text'
    assert simple_text_component['props']['content'] == 'Hello'
    assert simple_text_component['children'] == []


# Test Context
def test_context_creation() -> None:
    """Test Context initialization"""
    ctx = Context()
    assert ctx.renderers == {}
    assert ctx.store == {}
    assert ctx.current_page == 0
    assert ctx.total_pages == 0


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
        return f"<p>{comp['props']['content']}</p>"

    ctx = Context(renderers={'text': text_renderer})
    result = render(simple_text_component, ctx)

    assert result == "<p>Hello</p>"


def test_render_nested_component(nested_component: Component) -> None:
    """Test render function with nested components"""
    def header_renderer(comp: Component, ctx: Context) -> str:
        level = comp['props']['level']
        text = comp['props']['text']
        return f"<h{level}>{text}</h{level}>"

    def text_renderer(comp: Component, ctx: Context) -> str:
        return f"<p>{comp['props']['content']}</p>"

    def page_renderer(comp: Component, ctx: Context) -> str:
        children_html = [render(child, ctx) for child in comp['children']]
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
    comp = cast(Component, {
        'tag': 'unknown',
        'props': {},
        'children': []
    })

    ctx = Context()
    result = render(comp, ctx)

    assert '<div class="unknown">' in result


# Test transform function
def test_transform_simple() -> None:
    """Test simple component transformation"""
    comp = cast(Component, {
        'tag': 'text',
        'props': {'content': 'Hello'},
        'children': []
    })

    def add_class(c: Component) -> Component:
        props = c.get('props', {})
        props['class'] = 'styled'
        return cast(Component, {**c, 'props': props})

    result = transform(comp, add_class)

    assert result['props']['class'] == 'styled'
    assert result['props']['content'] == 'Hello'  # Original prop preserved


# Test walk function
def test_walk_applies_to_all_nodes(nested_component: Component) -> None:
    """Test that walk applies function to all nodes"""
    def add_class(comp: Component) -> Component:
        props = comp.get('props', {})
        props['visited'] = True
        return cast(Component, {**comp, 'props': props})

    result = walk(nested_component, add_class)

    assert result['props']['visited'] is True
    assert result['children'][0]['props']['visited'] is True
    assert result['children'][1]['props']['visited'] is True


def test_walk_preserves_structure(nested_component: Component) -> None:
    """Test that walk preserves component structure"""
    def identity(comp: Component) -> Component:
        return comp

    result = walk(nested_component, identity)

    assert result['tag'] == nested_component['tag']
    assert len(result['children']) == len(nested_component['children'])
    assert result['children'][0]['tag'] == 'header'
    assert result['children'][1]['tag'] == 'text'


def test_walk_post_order() -> None:
    """Test that walk processes children before parent"""
    order: list[str] = []

    def track_order(comp: Component) -> Component:
        order.append(comp['tag'])
        return comp

    comp = cast(Component, {
        'tag': 'root',
        'props': {},
        'children': [
            {'tag': 'child1', 'props': {}, 'children': []},
            {'tag': 'child2', 'props': {}, 'children': []}
        ]
    })

    walk(comp, track_order)

    # Children should be visited before parent
    assert order == ['child1', 'child2', 'root']


# Test find_components
def test_find_components_with_predicate(nested_component: Component) -> None:
    """Test find_components with custom predicate"""
    # Find all text components
    texts = find_components(
        nested_component,
        lambda c: c['tag'] == 'text'
    )

    assert len(texts) == 1
    assert texts[0]['props']['content'] == 'Content'


def test_find_components_multiple_matches() -> None:
    """Test find_components with multiple matches"""
    comp = cast(Component, {
        'tag': 'page',
        'props': {},
        'children': [
            {'tag': 'text', 'props': {'content': 'A'}, 'children': []},
            {'tag': 'text', 'props': {'content': 'B'}, 'children': []},
            {'tag': 'header', 'props': {}, 'children': []}
        ]
    })

    texts = find_components(comp, lambda c: c['tag'] == 'text')

    assert len(texts) == 2
    assert texts[0]['props']['content'] == 'A'
    assert texts[1]['props']['content'] == 'B'


def test_find_components_no_matches() -> None:
    """Test find_components with no matches"""
    comp = cast(Component, {
        'tag': 'page',
        'props': {},
        'children': []
    })

    result = find_components(comp, lambda c: c['tag'] == 'nonexistent')

    assert result == []


# Test filter_by_tag
def test_filter_by_tag(nested_component: Component) -> None:
    """Test filter_by_tag function"""
    headers = filter_by_tag(nested_component, 'header')

    assert len(headers) == 1
    assert headers[0]['props']['text'] == 'Title'


def test_filter_by_tag_multiple() -> None:
    """Test filter_by_tag with multiple matches"""
    comp = cast(Component, {
        'tag': 'page',
        'props': {},
        'children': [
            {'tag': 'item', 'props': {'id': 1}, 'children': []},
            {'tag': 'item', 'props': {'id': 2}, 'children': []},
            {'tag': 'other', 'props': {}, 'children': []}
        ]
    })

    items = filter_by_tag(comp, 'item')

    assert len(items) == 2
    assert items[0]['props']['id'] == 1
    assert items[1]['props']['id'] == 2


# Test map_components
def test_map_components_is_walk_alias() -> None:
    """Test that map_components is an alias for walk"""
    comp = cast(Component, {
        'tag': 'test',
        'props': {},
        'children': []
    })

    def add_prop(c: Component) -> Component:
        props = c.get('props', {})
        props['mapped'] = True
        return cast(Component, {**c, 'props': props})

    result1 = walk(comp, add_prop)

    # Reset component
    comp = cast(Component, {
        'tag': 'test',
        'props': {},
        'children': []
    })

    result2 = map_components(comp, add_prop)

    assert result1['props']['mapped'] == result2['props']['mapped']


# Test default_renderer
def test_default_renderer() -> None:
    """Test default_renderer function"""
    comp = cast(Component, {
        'tag': 'custom',
        'props': {},
        'children': []
    })

    ctx = Context()
    result = default_renderer(comp, ctx)

    assert '<div class="custom">' in result


def test_default_renderer_with_children() -> None:
    """Test default_renderer with children"""
    def text_renderer(comp: Component, ctx: Context) -> str:
        return f"<p>{comp['props']['content']}</p>"

    comp = cast(Component, {
        'tag': 'container',
        'props': {},
        'children': [
            {'tag': 'text', 'props': {'content': 'Child'}, 'children': []}
        ]
    })

    ctx = Context(renderers={'text': text_renderer})
    result = default_renderer(comp, ctx)

    assert '<div class="container">' in result
    assert '<p>Child</p>' in result


# Integration tests
def test_full_rendering_pipeline() -> None:
    """Test complete rendering pipeline"""
    # Create a slide structure
    slide_comp = cast(Component, {
        'tag': 'slide',
        'props': {},
        'children': [
            {
                'tag': 'page',
                'props': {},
                'children': [
                    {'tag': 'header', 'props': {'text': 'Page 1', 'level': 1}, 'children': []},
                    {'tag': 'text', 'props': {'content': 'Content 1'}, 'children': []}
                ]
            },
            {
                'tag': 'page',
                'props': {},
                'children': [
                    {'tag': 'header', 'props': {'text': 'Page 2', 'level': 1}, 'children': []},
                    {'tag': 'text', 'props': {'content': 'Content 2'}, 'children': []}
                ]
            }
        ]
    })

    # Transform: add IDs to headers
    def add_header_ids(comp: Component) -> Component:
        if comp['tag'] == 'header':
            text = comp['props']['text']
            id_value = text.lower().replace(' ', '-')
            props = {**comp['props'], 'id': id_value}
            return cast(Component, {**comp, 'props': props})
        return comp

    transformed = walk(slide_comp, add_header_ids)

    # Verify transformation
    headers = filter_by_tag(transformed, 'header')
    assert len(headers) == 2
    assert headers[0]['props']['id'] == 'page-1'
    assert headers[1]['props']['id'] == 'page-2'

    # Render
    def header_renderer(comp: Component, ctx: Context) -> str:
        level = comp['props']['level']
        text = comp['props']['text']
        id_value = comp['props'].get('id', '')
        id_attr = f' id="{id_value}"' if id_value else ''
        return f"<h{level}{id_attr}>{text}</h{level}>"

    def text_renderer(comp: Component, ctx: Context) -> str:
        return f"<p>{comp['props']['content']}</p>"

    def page_renderer(comp: Component, ctx: Context) -> str:
        children_html = [render(child, ctx) for child in comp['children']]
        return f'<div class="page">{"".join(children_html)}</div>'

    def slide_renderer(comp: Component, ctx: Context) -> str:
        children_html = [render(child, ctx) for child in comp['children']]
        return f'<div class="slide">{"".join(children_html)}</div>'

    ctx = Context(renderers={
        'slide': slide_renderer,
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
