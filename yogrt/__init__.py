"""
Yogrt - Programmable Slide Framework

A Lisp-inspired slide framework with independent component classes.

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
    # Type aliases
    Renderer,
    Transform,
    HtmlTransform,
    # Core types
    Component,
    ComponentProtocol,
    Context,
    # Leaf Components
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
    # Container Components
    PageComponent,
    VStackComponent,
    HStackComponent,
    TwoColumnComponent,
    GridComponent,
    ContainerComponent,
    ListComponent,
    TOCComponent,
    BibliographyComponent,
    # Core functions
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
    # Leaf components
    Text,
    Header,
    Image,
    Code,
    Link,
    Spacer,
    Divider,
    RawHtml,
    FootnoteRef,
    Footnote,
    Citation,
    # Container components
    Page,
    VStack,
    HStack,
    TwoColumn,
    Grid,
    Container,
    List,
    ListComp,  # Alias
    TOC,
    Bibliography,
)

# Renderer exports
from .renderers import DEFAULT_RENDERERS

# Standard library plugins
from .stdlib_plugins import (
    SpeakerNote,
    SpeakerNoteComponent,
    slide_navigation_plugin,
    speaker_notes_plugin,
    syntax_highlighting_plugin,
)


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
    # Type aliases
    'Renderer',
    'Transform',
    'HtmlTransform',
    # Core types
    'Component',
    'ComponentProtocol',
    'Context',
    # Leaf Component Types
    'TextComponent',
    'HeaderComponent',
    'ImageComponent',
    'CodeComponent',
    'LinkComponent',
    'SpacerComponent',
    'DividerComponent',
    'RawHtmlComponent',
    'FootnoteRefComponent',
    'FootnoteComponent',
    'CitationComponent',
    # Container Component Types
    'PageComponent',
    'VStackComponent',
    'HStackComponent',
    'TwoColumnComponent',
    'GridComponent',
    'ContainerComponent',
    'ListComponent',
    'TOCComponent',
    'BibliographyComponent',
    # Core functions
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
    # Component Factory Functions - Leaf
    'Text',
    'Header',
    'Image',
    'Code',
    'Link',
    'Spacer',
    'Divider',
    'RawHtml',
    'FootnoteRef',
    'Footnote',
    'Citation',
    # Component Factory Functions - Container
    'Page',
    'VStack',
    'HStack',
    'TwoColumn',
    'Grid',
    'Container',
    'List',
    'ListComp',
    'TOC',
    'Bibliography',
    # Renderers
    'DEFAULT_RENDERERS',
    # Standard library plugins
    'SpeakerNote',
    'SpeakerNoteComponent',
    'slide_navigation_plugin',
    'speaker_notes_plugin',
    'syntax_highlighting_plugin',
]
