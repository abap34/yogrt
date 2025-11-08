"""
Yogrt Core Module

Defines minimal primitives:
- Component: Data structure
- render: Component → HTML
- transform: Component → Component  
- walk: Component tree traversal
"""

from typing import Any, Callable
from dataclasses import dataclass, field, asdict


# ============================================================================
# Type Definitions
# ============================================================================

@dataclass(frozen=True)
class Component:
    """
    Base Component type definition

    A tree structure equivalent to Lisp's S-expressions.
    All slide elements are subclasses of this type.

    Immutable by design (frozen=True) to ensure predictable transformations.

    Attributes:
        tag: String identifying the component type
        props: Component-specific properties
        children: Tuple of child components (immutable)
        key: Unique component identifier (optional)

    Examples:
        >>> text_comp = Component(
        ...     tag='text',
        ...     props={'content': 'Hello'},
        ...     children=()
        ... )

        >>> page_comp = Component(
        ...     tag='page',
        ...     props={},
        ...     children=(text_comp,)
        ... )
    """
    tag: str
    props: dict[str, Any] = field(default_factory=dict)
    children: tuple['Component', ...] = field(default_factory=tuple)
    key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert Component to dictionary (homoiconicity)

        Enables treating components as data, like Lisp S-expressions.

        Returns:
            Dictionary representation
        """
        return {
            'tag': self.tag,
            'props': self.props.copy(),
            'children': [child.to_dict() for child in self.children],
            'key': self.key
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> 'Component':
        """
        Create Component from dictionary (homoiconicity)

        Enables treating data as components, like Lisp S-expressions.

        Args:
            data: Dictionary representation

        Returns:
            Component instance
        """
        children_data = data.get('children', [])
        children = tuple(Component.from_dict(child) for child in children_data)

        return Component(
            tag=data['tag'],
            props=data.get('props', {}),
            children=children,
            key=data.get('key')
        )


# ============================================================================
# Component Subclasses (Type Markers)
# ============================================================================

class TextComponent(Component):
    """Text component type marker"""
    pass


class HeaderComponent(Component):
    """Header component type marker"""
    pass


class ImageComponent(Component):
    """Image component type marker"""
    pass


class CodeComponent(Component):
    """Code component type marker"""
    pass


class LinkComponent(Component):
    """Link component type marker"""
    pass


class PageComponent(Component):
    """Page component type marker"""
    pass


class VStackComponent(Component):
    """VStack component type marker"""
    pass


class HStackComponent(Component):
    """HStack component type marker"""
    pass


class TwoColumnComponent(Component):
    """TwoColumn component type marker"""
    pass


class GridComponent(Component):
    """Grid component type marker"""
    pass


class ContainerComponent(Component):
    """Container component type marker"""
    pass


class ListComponent(Component):
    """List component type marker"""
    pass


class RawHtmlComponent(Component):
    """RawHtml component type marker"""
    pass


class SpacerComponent(Component):
    """Spacer component type marker"""
    pass


class DividerComponent(Component):
    """Divider component type marker"""
    pass


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
        >>> comp = Component(tag='text', props={'content': 'Hello'}, children=())
        >>> ctx = Context(renderers={'text': lambda c, ctx: f"<p>{c.props['content']}</p>"})
        >>> render(comp, ctx)
        '<p>Hello</p>'
    """
    renderer = context.get_renderer(component.tag)
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
        ...     return Component(tag='bold', props={}, children=(comp,))
        >>> comp = Component(tag='text', props={'content': 'Hi'}, children=())
        >>> result = transform(comp, make_bold)
        >>> result.tag
        'bold'
        >>> result.children[0].tag
        'text'
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
        >>> from dataclasses import replace
        >>> def add_class(comp: Component) -> Component:
        ...     new_props = {**comp.props, 'class': 'styled'}
        ...     return replace(comp, props=new_props)
        >>> root = Component(
        ...     tag='page',
        ...     props={},
        ...     children=(
        ...         Component(tag='text', props={}, children=()),
        ...     )
        ... )
        >>> result = walk(root, add_class)
        >>> result.props['class']
        'styled'
        >>> result.children[0].props['class']
        'styled'
    """
    # First process children recursively
    new_children = tuple(walk(child, f) for child in component.children)

    # Create component with updated children using dataclass replace
    from dataclasses import replace
    new_component = replace(component, children=new_children)

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
    children_html = [render(child, context) for child in component.children]
    return f'<div class="{component.tag}">{"".join(children_html)}</div>'


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
        >>> root = Component(
        ...     tag='page',
        ...     props={},
        ...     children=(
        ...         Component(tag='header', props={'level': 1}, children=()),
        ...         Component(tag='text', props={}, children=()),
        ...     )
        ... )
        >>> headers = find_components(root, lambda c: c.tag == 'header')
        >>> len(headers)
        1
    """
    result: list[Component] = []

    def visit(comp: Component) -> None:
        if predicate(comp):
            result.append(comp)
        for child in comp.children:
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
        >>> root = Component(
        ...     tag='page',
        ...     props={},
        ...     children=(
        ...         Component(tag='text', props={'content': 'A'}, children=()),
        ...         Component(tag='text', props={'content': 'B'}, children=()),
        ...     )
        ... )
        >>> texts = filter_by_tag(root, 'text')
        >>> len(texts)
        2
    """
    return find_components(root, lambda c: c.tag == tag)


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
