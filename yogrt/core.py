"""
Yogrt Core Module

Defines minimal primitives:
- Component: Data structure
- render: Component → HTML
- transform: Component → Component  
- walk: Component tree traversal
"""

from typing import TypedDict, Any, Callable, cast
from dataclasses import dataclass, field


# ============================================================================
# Type Definitions
# ============================================================================

class Component(TypedDict, total=False):
    """
    Component type definition

    A tree structure equivalent to Lisp's S-expressions.
    All slide elements are represented by this type.

    Attributes:
        tag: String identifying the component type
        props: Component-specific properties
        children: List of child components
        key: Unique component identifier (optional)

    Examples:
        >>> text_comp: Component = {
        ...     'tag': 'text',
        ...     'props': {'content': 'Hello'},
        ...     'children': []
        ... }

        >>> page_comp: Component = {
        ...     'tag': 'page',
        ...     'props': {},
        ...     'children': [text_comp]
        ... }
    """
    tag: str
    props: dict[str, Any]
    children: list['Component']
    key: str | None


# Type aliases
Renderer = Callable[[Component, 'Context'], str]
"""Component → HTML conversion function (renderer)"""

Transform = Callable[[Component], Component]
"""Component → Component transformation function"""

HtmlTransform = Callable[[str], str]
"""HTML → HTML transformation function"""


# ============================================================================
# Context
# ============================================================================

@dataclass
class Context:
    """
    Rendering context

    Holds rendering state and renderers.
    Also provides a store for data sharing between plugins.

    Attributes:
        renderers: Mapping from tag name to renderer function
        store: Data store shared between plugins
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
    """
    renderers: dict[str, Renderer] = field(default_factory=dict)
    store: dict[str, Any] = field(default_factory=dict)
    current_page: int = 0
    total_pages: int = 0

    def get_renderer(self, tag: str) -> Renderer:
        """
        Get renderer corresponding to a tag

        Args:
            tag: Component tag name

        Returns:
            Renderer function (default renderer if not found)
        """
        return self.renderers.get(tag, default_renderer)


# ============================================================================
# Core Functions
# ============================================================================

def render(component: Component, context: Context) -> str:
    """
    Render a Component to an HTML string

    This is equivalent to Lisp's eval function.
    Executes a Component (data) to produce HTML (result).

    Args:
        component: Component to render
        context: Rendering context

    Returns:
        HTML string

    Examples:
        >>> comp: Component = {'tag': 'text', 'props': {'content': 'Hello'}, 'children': []}
        >>> ctx = Context(renderers={'text': lambda c, ctx: f"<p>{c['props']['content']}</p>"})
        >>> render(comp, ctx)
        '<p>Hello</p>'
    """
    tag = component['tag']
    renderer = context.get_renderer(tag)
    return renderer(component, context)


def transform(component: Component, transformer: Transform) -> Component:
    """
    Transform a Component into another Component

    This is equivalent to Lisp's macro expansion.
    Performs Component → Component transformation.

    Args:
        component: Component to transform
        transformer: Transformation function

    Returns:
        Transformed component

    Examples:
        >>> def make_bold(comp: Component) -> Component:
        ...     return {'tag': 'bold', 'props': {}, 'children': [comp]}
        >>> comp: Component = {'tag': 'text', 'props': {'content': 'Hi'}, 'children': []}
        >>> transform(comp, make_bold)
        {'tag': 'bold', 'props': {}, 'children': [{'tag': 'text', 'props': {'content': 'Hi'}, 'children': []}]}
    """
    return transformer(component)


def walk(component: Component, f: Callable[[Component], Component]) -> Component:
    """
    Recursively traverse a Component tree and apply a function to each node

    Traverses the tree depth-first and processes children before parents (post-order traversal).

    Args:
        component: Component to traverse
        f: Function to apply to each node

    Returns:
        Transformed component tree

    Examples:
        >>> def add_class(comp: Component) -> Component:
        ...     props = comp.get('props', {})
        ...     props['class'] = 'styled'
        ...     return {**comp, 'props': props}
        >>> root: Component = {
        ...     'tag': 'page',
        ...     'props': {},
        ...     'children': [
        ...         {'tag': 'text', 'props': {}, 'children': []}
        ...     ]
        ... }
        >>> result = walk(root, add_class)
        >>> result['props']['class']
        'styled'
        >>> result['children'][0]['props']['class']
        'styled'
    """
    # First process children recursively
    children = component.get('children', [])
    new_children = [walk(child, f) for child in children]

    # Create component with updated children
    new_component = cast(Component, {**component, 'children': new_children})

    # Apply function
    return f(new_component)


# ============================================================================
# Default Renderer
# ============================================================================

def default_renderer(component: Component, context: Context) -> str:
    """
    Default renderer

    Used for unknown tags.
    Renders children and wraps them in a div tag.

    Args:
        component: Component to render
        context: Rendering context

    Returns:
        HTML string
    """
    tag = component['tag']
    children = component.get('children', [])
    children_html = [render(child, context) for child in children]
    return f'<div class="{tag}">{"".join(children_html)}</div>'


# ============================================================================
# Utility Functions
# ============================================================================

def find_components(
    root: Component,
    predicate: Callable[[Component], bool]
) -> list[Component]:
    """
    Search for components that satisfy a condition

    Traverses the Component tree and returns all components that satisfy the predicate.

    Args:
        root: Starting node for search
        predicate: Predicate function

    Returns:
        List of components satisfying the condition

    Examples:
        >>> root: Component = {
        ...     'tag': 'page',
        ...     'props': {},
        ...     'children': [
        ...         {'tag': 'header', 'props': {'level': 1}, 'children': []},
        ...         {'tag': 'text', 'props': {}, 'children': []}
        ...     ]
        ... }
        >>> headers = find_components(root, lambda c: c['tag'] == 'header')
        >>> len(headers)
        1
    """
    result: list[Component] = []

    def visit(comp: Component) -> None:
        if predicate(comp):
            result.append(comp)
        for child in comp.get('children', []):
            visit(child)

    visit(root)
    return result


def filter_by_tag(root: Component, tag: str) -> list[Component]:
    """
    Search for components with a specific tag

    Args:
        root: Starting node for search
        tag: Tag name to search for

    Returns:
        List of components with the specified tag

    Examples:
        >>> from typing import cast
        >>> root = cast(Component, {
        ...     'tag': 'page',
        ...     'props': {},
        ...     'children': [
        ...         {'tag': 'text', 'props': {'content': 'A'}, 'children': []},
        ...         {'tag': 'text', 'props': {'content': 'B'}, 'children': []}
        ...     ]
        ... })
        >>> texts = filter_by_tag(root, 'text')
        >>> len(texts)
        2
    """
    return find_components(root, lambda c: c['tag'] == tag)


def map_components(
    root: Component,
    f: Callable[[Component], Component]
) -> Component:
    """
    Apply a function to all components

    Alias for walk. More functional programming style name.

    Args:
        root: Root component to transform
        f: Function to apply to each component

    Returns:
        Transformed component tree
    """
    return walk(root, f)
