"""
Yogrt Standard Components

Factory functions for creating standard components with type-safe return types.
"""

from typing import Any
from .core import (
    Component,
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
    PageComponent,
    VStackComponent,
    HStackComponent,
    TwoColumnComponent,
    GridComponent,
    ContainerComponent,
    ListComponent,
    TOCComponent,
    BibliographyComponent,
)


# ============================================================================
# Leaf Components
# ============================================================================

def Text(content: str, class_name: str = "", **kwargs: Any) -> TextComponent:
    """
    Text component

    Args:
        content: Text to display
        class_name: CSS class name
        **kwargs: Additional keyword arguments (key)

    Returns:
        TextComponent
    """
    return TextComponent(
        content=content,
        class_name=class_name,
        key=kwargs.get('key')
    )


def Header(text: str, level: int = 1, id: str = "", class_name: str = "", **kwargs: Any) -> HeaderComponent:
    """
    Header component

    Args:
        text: Header text
        level: Heading level (1-6)
        id: Element ID for linking
        class_name: CSS class name
        **kwargs: Additional keyword arguments (key)

    Returns:
        HeaderComponent
    """
    return HeaderComponent(
        text=text,
        level=level,
        id=id,
        class_name=class_name,
        key=kwargs.get('key')
    )


def Image(src: Any, alt: str = "", caption: str = "", width: str = "", height: str = "", **kwargs: Any) -> ImageComponent:
    """
    Image component

    Args:
        src: Image source (file path, URL, matplotlib Figure)
        alt: Alt text
        caption: Image caption
        width: Image width
        height: Image height
        **kwargs: Additional keyword arguments (key)

    Returns:
        ImageComponent
    """
    return ImageComponent(
        src=src,
        alt=alt,
        caption=caption,
        width=width,
        height=height,
        key=kwargs.get('key')
    )


def Code(code: str, lang: str = "python", line_numbers: bool = False, **kwargs: Any) -> CodeComponent:
    """
    Code block component

    Args:
        code: Code string
        lang: Programming language
        line_numbers: Show line numbers
        **kwargs: Additional keyword arguments (key)

    Returns:
        CodeComponent
    """
    return CodeComponent(
        code=code,
        lang=lang,
        line_numbers=line_numbers,
        key=kwargs.get('key')
    )


def Link(href: str, text: str, target: str = "_blank", **kwargs: Any) -> LinkComponent:
    """
    Link component

    Args:
        href: URL destination
        text: Link text
        target: Link target
        **kwargs: Additional keyword arguments (key)

    Returns:
        LinkComponent
    """
    return LinkComponent(
        text=text,
        href=href,
        target=target,
        key=kwargs.get('key')
    )


def Spacer(height: str = "1rem", **kwargs: Any) -> SpacerComponent:
    """
    Spacer component

    Args:
        height: Height of spacer
        **kwargs: Additional keyword arguments (key)

    Returns:
        SpacerComponent
    """
    return SpacerComponent(
        height=height,
        key=kwargs.get('key')
    )


def Divider(color: str = "#e5e7eb", thickness: str = "1px", **kwargs: Any) -> DividerComponent:
    """
    Divider component

    Args:
        color: Divider color
        thickness: Divider thickness
        **kwargs: Additional keyword arguments (key)

    Returns:
        DividerComponent
    """
    return DividerComponent(
        color=color,
        thickness=thickness,
        key=kwargs.get('key')
    )


def RawHtml(html: str, **kwargs: Any) -> RawHtmlComponent:
    """
    Raw HTML component

    Args:
        html: Raw HTML string
        **kwargs: Additional keyword arguments (key)

    Returns:
        RawHtmlComponent
    """
    return RawHtmlComponent(
        html=html,
        key=kwargs.get('key')
    )


def FootnoteRef(note_id: str, **kwargs: Any) -> FootnoteRefComponent:
    """
    Footnote reference component

    Args:
        note_id: Footnote identifier
        **kwargs: Additional keyword arguments (key)

    Returns:
        FootnoteRefComponent
    """
    return FootnoteRefComponent(
        note_id=note_id,
        key=kwargs.get('key')
    )


def Footnote(note_id: str, content: str, **kwargs: Any) -> FootnoteComponent:
    """
    Footnote content component

    Args:
        note_id: Footnote identifier
        content: Footnote text
        **kwargs: Additional keyword arguments (key)

    Returns:
        FootnoteComponent
    """
    return FootnoteComponent(
        note_id=note_id,
        content=content,
        key=kwargs.get('key')
    )


def Citation(cite_key: str, **kwargs: Any) -> CitationComponent:
    """
    Citation component (bibtex reference)

    Args:
        cite_key: Bibtex citation key
        **kwargs: Additional keyword arguments (key)

    Returns:
        CitationComponent
    """
    return CitationComponent(
        cite_key=cite_key,
        key=kwargs.get('key')
    )


# ============================================================================
# Container Components
# ============================================================================

def Page(*children: Component, class_name: str = "", **kwargs: Any) -> PageComponent:
    """
    Page component

    Args:
        *children: Child components
        class_name: CSS class name
        **kwargs: Additional keyword arguments (key)

    Returns:
        PageComponent
    """
    return PageComponent(
        children=children,
        class_name=class_name,
        key=kwargs.get('key')
    )


def VStack(*children: Component, gap: str = "1rem", align: str = "left", **kwargs: Any) -> VStackComponent:
    """
    Vertical stack layout

    Args:
        *children: Child components
        gap: Gap between children
        align: Alignment (left, center, right)
        **kwargs: Additional keyword arguments (key)

    Returns:
        VStackComponent
    """
    return VStackComponent(
        children=children,
        gap=gap,
        align=align,
        key=kwargs.get('key')
    )


def HStack(*children: Component, gap: str = "1rem", align: str = "center", **kwargs: Any) -> HStackComponent:
    """
    Horizontal stack layout

    Args:
        *children: Child components
        gap: Gap between children
        align: Alignment (top, center, bottom)
        **kwargs: Additional keyword arguments (key)

    Returns:
        HStackComponent
    """
    return HStackComponent(
        children=children,
        gap=gap,
        align=align,
        key=kwargs.get('key')
    )


def TwoColumn(left: Component, right: Component, ratio: str = "1:1", gap: str = "2rem", **kwargs: Any) -> TwoColumnComponent:
    """
    Two-column layout

    Args:
        left: Left column component
        right: Right column component
        ratio: Column width ratio
        gap: Gap between columns
        **kwargs: Additional keyword arguments (key)

    Returns:
        TwoColumnComponent
    """
    return TwoColumnComponent(
        left=left,
        right=right,
        ratio=ratio,
        gap=gap,
        key=kwargs.get('key')
    )


def Grid(*children: Component, columns: int = 2, gap: str = "1rem", **kwargs: Any) -> GridComponent:
    """
    Grid layout

    Args:
        *children: Child components
        columns: Number of columns
        gap: Gap between items
        **kwargs: Additional keyword arguments (key)

    Returns:
        GridComponent
    """
    return GridComponent(
        children=children,
        columns=columns,
        gap=gap,
        key=kwargs.get('key')
    )


def Container(*children: Component, class_name: str = "", style: str = "", **kwargs: Any) -> ContainerComponent:
    """
    Generic container

    Args:
        *children: Child components
        class_name: CSS class name
        style: Inline CSS style
        **kwargs: Additional keyword arguments (key)

    Returns:
        ContainerComponent
    """
    return ContainerComponent(
        children=children,
        class_name=class_name,
        style=style,
        key=kwargs.get('key')
    )


def List(*items: str | Component, ordered: bool = False, **kwargs: Any) -> ListComponent:
    """
    List component

    Args:
        *items: List items (strings or components)
        ordered: Use ordered list (ol) vs unordered (ul)
        **kwargs: Additional keyword arguments (key)

    Returns:
        ListComponent
    """
    # Convert string items to Text components
    children = tuple(
        Text(item) if isinstance(item, str) else item
        for item in items
    )

    return ListComponent(
        children=children,
        ordered=ordered,
        key=kwargs.get('key')
    )


# Alias for backwards compatibility
ListComp = List


def TOC(max_level: int = 3, title: str = "Table of Contents", **kwargs: Any) -> TOCComponent:
    """
    Table of Contents component (auto-generated)

    Args:
        max_level: Maximum header level to include
        title: TOC title
        **kwargs: Additional keyword arguments (key)

    Returns:
        TOCComponent
    """
    return TOCComponent(
        max_level=max_level,
        title=title,
        key=kwargs.get('key')
    )


def Bibliography(title: str = "References", style: str = "default", **kwargs: Any) -> BibliographyComponent:
    """
    Bibliography component (renders citations)

    Args:
        title: Bibliography title
        style: Citation style
        **kwargs: Additional keyword arguments (key)

    Returns:
        BibliographyComponent
    """
    return BibliographyComponent(
        title=title,
        style=style,
        key=kwargs.get('key')
    )
