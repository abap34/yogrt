"""
Yogrt - Programmable Slide Framework

Lisp的な哲学に基づいた、簡潔で無限に拡張可能なスライドフレームワーク。

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
    デフォルト設定でスライドを作成

    標準レンダラーがすべて登録された Slide インスタンスを返す。

    Returns:
        Slide インスタンス

    Examples:
        >>> slide = create_slide()
        >>> slide.add_page(Page(Text("Hello")))
        <yogrt.slide.Slide object at ...>
    """
    slide = Slide()

    # 標準レンダラーを登録
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
    # Components - Basic
    'Text',
    'Header',
    'Image',
    'Code',
    'Link',
    # Components - Containers
    'Page',
    'VStack',
    'HStack',
    'TwoColumn',
    'Grid',
    'Container',
    # Components - Lists
    'List',
    # Components - Special
    'RawHtml',
    'Spacer',
    'Divider',
    # Renderers
    'DEFAULT_RENDERERS',
]
