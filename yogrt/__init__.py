"""
Yogrt - Programmable Slide Framework

A Lisp-inspired slide framework with concise design and infinite extensibility.

Examples:
    >>> from yogrt import create_slide, Page, Header, Text
    >>> slide = create_slide()
    >>> slide.add_page(Page(
    ...     Header("Hello, Yogrt!", level=1),
    ...     Text("A programmable slide framework")
    ... ))
    >>> slide.export("output.html")  # doctest: +SKIP
"""

__version__ = "0.1.0"

# Core exports
from .core import (
    Component,
    TextComponent,
    HeaderComponent,
    ImageComponent,
    CodeComponent,
    LinkComponent,
    PageComponent,
    VStackComponent,
    HStackComponent,
    TwoColumnComponent,
    GridComponent,
    ContainerComponent,
    ListComponent,
    RawHtmlComponent,
    SpacerComponent,
    DividerComponent,
    Context,
    Renderer,
    Transform,
    HtmlTransform,
    render,
    transform,
    walk,
    find_components,
    filter_by_tag,
    map_components,
)

# Slide exports
from .slide import Slide, Plugin

# Component exports
from .components import (
    # Basic
    Text,
    Header,
    Image,
    Code,
    Link,
    # Containers
    Page,
    VStack,
    HStack,
    TwoColumn,
    Grid,
    Container,
    # Lists
    List,
    # Special
    RawHtml,
    Spacer,
    Divider,
)

# Renderer exports
from .renderers import DEFAULT_RENDERERS


# ============================================================================
# Factory Function
# ============================================================================

def create_slide() -> Slide:
    """
    Create a slide with default configuration

    Returns a Slide instance with all standard renderers registered.

    Returns:
        Slide instance

    Examples:
        >>> slide = create_slide()
        >>> slide.add_page(Page(Text("Hello")))
        <yogrt.slide.Slide object at ...>
    """
    slide = Slide()

    # Register standard renderers
    for tag, renderer in DEFAULT_RENDERERS.items():
        slide.add_renderer(tag, renderer)

    return slide


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # Version
    '__version__',
    # Core
    'Component',
    # Component Types
    'TextComponent',
    'HeaderComponent',
    'ImageComponent',
    'CodeComponent',
    'LinkComponent',
    'PageComponent',
    'VStackComponent',
    'HStackComponent',
    'TwoColumnComponent',
    'GridComponent',
    'ContainerComponent',
    'ListComponent',
    'RawHtmlComponent',
    'SpacerComponent',
    'DividerComponent',
    # Core types and functions
    'Context',
    'Renderer',
    'Transform',
    'HtmlTransform',
    'render',
    'transform',
    'walk',
    'find_components',
    'filter_by_tag',
    'map_components',
    # Slide
    'Slide',
    'Plugin',
    'create_slide',
    # Component Factory Functions - Basic
    'Text',
    'Header',
    'Image',
    'Code',
    'Link',
    # Component Factory Functions - Containers
    'Page',
    'VStack',
    'HStack',
    'TwoColumn',
    'Grid',
    'Container',
    # Component Factory Functions - Lists
    'List',
    # Component Factory Functions - Special
    'RawHtml',
    'Spacer',
    'Divider',
    # Renderers
    'DEFAULT_RENDERERS',
]
