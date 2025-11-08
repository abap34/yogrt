"""
Yogrt Core Module - Independent Component Classes

Defines minimal primitives with independent component classes:
- Component Protocol: Interface for all components
- Leaf Components: TextComponent, HeaderComponent, etc. (no children)
- Container Components: PageComponent, VStackComponent, etc. (with children)
- render: Component → HTML
- transform: Component → Component
- walk: Component tree traversal
"""

from typing import Any, Callable, Protocol, Union, runtime_checkable, Mapping
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


# ============================================================================
# Type Aliases
# ============================================================================

# Forward references for type aliases
Renderer = Callable[['Component', 'Context'], str]
"""Renderer function type: (Component, Context) -> HTML string"""

Transform = Callable[['Component'], 'Component']
"""Transform function type: Component -> Component"""

HtmlTransform = Callable[[str], str]
"""HTML transform function type: HTML string -> HTML string"""


# ============================================================================
# Component Protocol
# ============================================================================

@runtime_checkable
class ComponentProtocol(Protocol):
    """
    Protocol that all components must implement

    This allows type checking while keeping components independent.
    """

    @property
    def tag(self) -> str:
        """Component type tag"""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert component to dictionary (homoiconicity)"""
        ...


# ============================================================================
# Leaf Components (No Children)
# ============================================================================

@dataclass(frozen=True)
class TextComponent:
    """Text paragraph component"""
    content: str
    class_name: str = ""
    key: str | None = None

    @property
    def tag(self) -> str:
        return "text"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'text',
            'content': self.content,
            'class': self.class_name,
            'key': self.key
        }


@dataclass(frozen=True)
class HeaderComponent:
    """Header component (h1-h6)"""
    text: str
    level: int = 1
    id: str = ""
    class_name: str = ""
    key: str | None = None

    @property
    def tag(self) -> str:
        return "header"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'header',
            'text': self.text,
            'level': self.level,
            'id': self.id,
            'class': self.class_name,
            'key': self.key
        }


@dataclass(frozen=True)
class ImageComponent:
    """Image component"""
    src: Any  # str path, URL, or matplotlib figure
    alt: str = ""
    caption: str = ""
    width: str = ""
    height: str = ""
    key: str | None = None

    @property
    def tag(self) -> str:
        return "image"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'image',
            'src': self.src if isinstance(self.src, str) else str(self.src),
            'alt': self.alt,
            'caption': self.caption,
            'width': self.width,
            'height': self.height,
            'key': self.key
        }


@dataclass(frozen=True)
class CodeComponent:
    """Code block component"""
    code: str
    lang: str = "python"
    line_numbers: bool = False
    key: str | None = None

    @property
    def tag(self) -> str:
        return "code"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'code',
            'code': self.code,
            'lang': self.lang,
            'line_numbers': self.line_numbers,
            'key': self.key
        }


@dataclass(frozen=True)
class LinkComponent:
    """Hyperlink component"""
    text: str
    href: str
    target: str = "_blank"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "link"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'link',
            'text': self.text,
            'href': self.href,
            'target': self.target,
            'key': self.key
        }


@dataclass(frozen=True)
class SpacerComponent:
    """Vertical spacing component"""
    height: str = "1rem"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "spacer"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'spacer',
            'height': self.height,
            'key': self.key
        }


@dataclass(frozen=True)
class DividerComponent:
    """Horizontal divider component"""
    color: str = "#e5e7eb"
    thickness: str = "1px"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "divider"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'divider',
            'color': self.color,
            'thickness': self.thickness,
            'key': self.key
        }


@dataclass(frozen=True)
class RawHtmlComponent:
    """Raw HTML insertion component"""
    html: str
    key: str | None = None

    @property
    def tag(self) -> str:
        return "raw-html"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'raw-html',
            'html': self.html,
            'key': self.key
        }


@dataclass(frozen=True)
class FootnoteRefComponent:
    """Footnote reference component"""
    note_id: str
    key: str | None = None

    @property
    def tag(self) -> str:
        return "footnote-ref"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'footnote-ref',
            'note_id': self.note_id,
            'key': self.key
        }


@dataclass(frozen=True)
class FootnoteComponent:
    """Footnote content component"""
    note_id: str
    content: str
    key: str | None = None

    @property
    def tag(self) -> str:
        return "footnote"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'footnote',
            'note_id': self.note_id,
            'content': self.content,
            'key': self.key
        }


@dataclass(frozen=True)
class CitationComponent:
    """Citation reference component (for bibtex)"""
    cite_key: str
    key: str | None = None

    @property
    def tag(self) -> str:
        return "citation"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'citation',
            'cite_key': self.cite_key,
            'key': self.key
        }


# ============================================================================
# Container Components (With Children)
# ============================================================================

# Union type for all components
Component = Union[
    TextComponent,
    HeaderComponent,
    ImageComponent,
    CodeComponent,
    LinkComponent,
    SpacerComponent,
    DividerComponent,
    RawHtmlComponent,
    FootnoteRefComponent,
    FootnoteComponent,
    CitationComponent,
    'PageComponent',
    'VStackComponent',
    'HStackComponent',
    'TwoColumnComponent',
    'GridComponent',
    'ContainerComponent',
    'ListComponent',
    'TOCComponent',
    'BibliographyComponent',
]


@dataclass(frozen=True)
class PageComponent:
    """Page container component"""
    children: tuple[Component, ...] = field(default_factory=tuple)
    class_name: str = ""
    key: str | None = None

    @property
    def tag(self) -> str:
        return "page"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'page',
            'children': [child.to_dict() for child in self.children],
            'class': self.class_name,
            'key': self.key
        }


@dataclass(frozen=True)
class VStackComponent:
    """Vertical stack layout component"""
    children: tuple[Component, ...] = field(default_factory=tuple)
    gap: str = "1rem"
    align: str = "left"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "vstack"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'vstack',
            'children': [child.to_dict() for child in self.children],
            'gap': self.gap,
            'align': self.align,
            'key': self.key
        }


@dataclass(frozen=True)
class HStackComponent:
    """Horizontal stack layout component"""
    children: tuple[Component, ...] = field(default_factory=tuple)
    gap: str = "1rem"
    align: str = "center"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "hstack"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'hstack',
            'children': [child.to_dict() for child in self.children],
            'gap': self.gap,
            'align': self.align,
            'key': self.key
        }


@dataclass(frozen=True)
class TwoColumnComponent:
    """Two column layout component"""
    left: Component
    right: Component
    ratio: str = "1:1"
    gap: str = "2rem"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "two-column"

    @property
    def children(self) -> tuple[Component, Component]:
        """Expose children for walk compatibility"""
        return (self.left, self.right)

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'two-column',
            'left': self.left.to_dict(),
            'right': self.right.to_dict(),
            'ratio': self.ratio,
            'gap': self.gap,
            'key': self.key
        }


@dataclass(frozen=True)
class GridComponent:
    """Grid layout component"""
    children: tuple[Component, ...] = field(default_factory=tuple)
    columns: int = 2
    gap: str = "1rem"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "grid"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'grid',
            'children': [child.to_dict() for child in self.children],
            'columns': self.columns,
            'gap': self.gap,
            'key': self.key
        }


@dataclass(frozen=True)
class ContainerComponent:
    """Generic container component"""
    children: tuple[Component, ...] = field(default_factory=tuple)
    class_name: str = ""
    style: str = ""
    key: str | None = None

    @property
    def tag(self) -> str:
        return "container"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'container',
            'children': [child.to_dict() for child in self.children],
            'class': self.class_name,
            'style': self.style,
            'key': self.key
        }


@dataclass(frozen=True)
class ListComponent:
    """List component (ordered/unordered)"""
    children: tuple[Component, ...] = field(default_factory=tuple)
    ordered: bool = False
    key: str | None = None

    @property
    def tag(self) -> str:
        return "list"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'list',
            'children': [child.to_dict() for child in self.children],
            'ordered': self.ordered,
            'key': self.key
        }


@dataclass(frozen=True)
class TOCComponent:
    """Table of Contents component (auto-generated from headers)"""
    max_level: int = 3
    title: str = "Table of Contents"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "toc"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'toc',
            'max_level': self.max_level,
            'title': self.title,
            'key': self.key
        }


@dataclass(frozen=True)
class BibliographyComponent:
    """Bibliography component (renders citations from bibtex)"""
    title: str = "References"
    style: str = "default"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "bibliography"

    def to_dict(self) -> dict[str, Any]:
        return {
            'tag': 'bibliography',
            'title': self.title,
            'style': self.style,
            'key': self.key
        }


# ============================================================================
# Context (Rendering State)
# ============================================================================

@dataclass
class Context:
    """
    Rendering context

    Holds renderers and global state like current page number.
    """
    renderers: dict[str, Callable[[Component, 'Context'], str]] = field(default_factory=dict)
    current_page: int = 1
    total_pages: int = 1
    footnotes: dict[str, str] = field(default_factory=dict)  # id -> content
    citations: dict[str, dict[str, str]] = field(default_factory=dict)  # cite_key -> bibtex data
    headers: list[tuple[int, str, str]] = field(default_factory=list)  # (level, text, id) for TOC

    def get_renderer(self, tag: str) -> Callable[[Component, 'Context'], str]:
        """Get renderer for component tag"""
        return self.renderers.get(tag, default_renderer)


# ============================================================================
# Core Functions
# ============================================================================

def render(component: Component, context: Context) -> str:
    """
    Render component to HTML string

    Args:
        component: Component to render
        context: Rendering context

    Returns:
        HTML string
    """
    renderer = context.get_renderer(component.tag)
    return renderer(component, context)


def transform(component: Component, transformer: Callable[[Component], Component]) -> Component:
    """
    Apply transformation to component

    Args:
        component: Component to transform
        transformer: Transformation function

    Returns:
        Transformed component
    """
    return transformer(component)


def walk(component: Component, f: Callable[[Component], Component]) -> Component:
    """
    Walk component tree and apply function to each node (post-order)

    Recursively processes children before applying function to parent.
    Handles both leaf components (no children) and container components.

    Args:
        component: Root component
        f: Function to apply to each node

    Returns:
        Transformed component tree
    """
    from dataclasses import replace

    # Handle TwoColumnComponent specially (has left/right instead of children)
    if isinstance(component, TwoColumnComponent):
        new_left = walk(component.left, f)
        new_right = walk(component.right, f)
        new_component = replace(component, left=new_left, right=new_right)
        return f(new_component)

    # Check if component has children attribute
    elif hasattr(component, 'children'):
        # Recursively walk children
        new_children = tuple(walk(child, f) for child in component.children)
        new_component = replace(component, children=new_children)  # type: ignore[assignment,arg-type]
        return f(new_component)

    else:
        # Leaf component - just apply function
        return f(component)


def find_components(
    root: Component,
    predicate: Callable[[Component], bool]
) -> list[Component]:
    """
    Find all components matching predicate

    Args:
        root: Root component to search from
        predicate: Function that returns True for matching components

    Returns:
        List of matching components
    """
    results: list[Component] = []

    def collector(comp: Component) -> Component:
        if predicate(comp):
            results.append(comp)
        return comp

    walk(root, collector)
    return results


def filter_by_tag(root: Component, tag: str) -> list[Component]:
    """
    Find all components with given tag

    Args:
        root: Root component
        tag: Tag to search for

    Returns:
        List of matching components
    """
    return find_components(root, lambda c: c.tag == tag)


# Alias for compatibility
map_components = walk


def default_renderer(component: Component, context: Context) -> str:
    """
    Default renderer for unknown components

    Renders children (if any) wrapped in a div.

    Args:
        component: Component to render
        context: Rendering context

    Returns:
        HTML string
    """
    if hasattr(component, 'children'):
        children_html = [render(child, context) for child in component.children]
        return f'<div class="{component.tag}">{"".join(children_html)}</div>'
    else:
        return f'<div class="{component.tag}"></div>'
