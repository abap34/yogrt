"""
Yogrt Standard Components

Defines standard component factory functions with type-safe return types.
"""

from typing import Any
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
)


# ============================================================================
# Basic Components
# ============================================================================

def Text(content: str, **props: Any) -> TextComponent:
    """
    Text component

    Args:
        content: Text to display
        **props: Additional properties

    Returns:
        TextComponent

    Examples:
        >>> text = Text("Hello, world!")
        >>> text.tag
        'text'
        >>> text.props['content']
        'Hello, world!'
        >>> isinstance(text, TextComponent)
        True
    """
    return TextComponent(
        tag='text',
        props={'content': content, **props},
        children=()
    )


def Header(text: str, level: int = 1, **props: Any) -> HeaderComponent:
    """
    Header component

    Args:
        text: Header text
        level: Heading level (1-6)
        **props: Additional properties (id, class, etc.)

    Returns:
        HeaderComponent

    Examples:
        >>> header = Header("Introduction", level=2, id="intro")
        >>> header.tag
        'header'
        >>> header.props['level']
        2
        >>> header.props['id']
        'intro'
        >>> isinstance(header, HeaderComponent)
        True
    """
    return HeaderComponent(
        tag='header',
        props={'text': text, 'level': level, **props},
        children=()
    )


def Image(src: Any, caption: str | None = None, **props: Any) -> ImageComponent:
    """
    Image component

    Args:
        src: Image source (file path, URL, matplotlib Figure, etc.)
        caption: Caption (optional)
        **props: Additional properties

    Returns:
        ImageComponent

    Examples:
        >>> img = Image("photo.jpg", caption="A beautiful sunset")
        >>> img.tag
        'image'
        >>> img.props['caption']
        'A beautiful sunset'
        >>> isinstance(img, ImageComponent)
        True
    """
    return ImageComponent(
        tag='image',
        props={'src': src, 'caption': caption, **props},
        children=()
    )


def Code(code: str, lang: str = "python", **props: Any) -> CodeComponent:
    """
    Code block component

    Args:
        code: Code string
        lang: Programming language
        **props: Additional properties

    Returns:
        CodeComponent

    Examples:
        >>> code = Code("print('Hello')", lang="python")
        >>> code.tag
        'code'
        >>> code.props['lang']
        'python'
        >>> isinstance(code, CodeComponent)
        True
    """
    return CodeComponent(
        tag='code',
        props={'code': code, 'lang': lang, **props},
        children=()
    )


def Link(url: str, text: str, **props: Any) -> LinkComponent:
    """
    Link component

    Args:
        url: Link destination URL
        text: Display text
        **props: Additional properties

    Returns:
        LinkComponent

    Examples:
        >>> link = Link("https://example.com", "Visit Example")
        >>> link.props['url']
        'https://example.com'
        >>> isinstance(link, LinkComponent)
        True
    """
    return LinkComponent(
        tag='link',
        props={'url': url, 'text': text, **props},
        children=()
    )


# ============================================================================
# Container Components
# ============================================================================

def Page(*children: Component, **props: Any) -> PageComponent:
    """
    Page component

    Represents one page of a slide.

    Args:
        *children: Child components
        **props: Additional properties

    Returns:
        PageComponent

    Examples:
        >>> page = Page(
        ...     Header("Title", level=1),
        ...     Text("Content")
        ... )
        >>> page.tag
        'page'
        >>> len(page.children)
        2
        >>> isinstance(page, PageComponent)
        True
    """
    return PageComponent(
        tag='page',
        props=props,
        children=children
    )


def VStack(*children: Component, gap: str = "1rem", **props: Any) -> VStackComponent:
    """
    Vertical stack layout

    Arranges child elements vertically.

    Args:
        *children: Child components
        gap: Spacing between children
        **props: Additional properties

    Returns:
        VStackComponent

    Examples:
        >>> stack = VStack(
        ...     Text("First"),
        ...     Text("Second"),
        ...     gap="2rem"
        ... )
        >>> stack.tag
        'vstack'
        >>> stack.props['gap']
        '2rem'
        >>> isinstance(stack, VStackComponent)
        True
    """
    return VStackComponent(
        tag='vstack',
        props={'gap': gap, **props},
        children=children
    )


def HStack(*children: Component, gap: str = "1rem", **props: Any) -> HStackComponent:
    """
    Horizontal stack layout

    Arranges child elements horizontally.

    Args:
        *children: Child components
        gap: Spacing between children
        **props: Additional properties

    Returns:
        HStackComponent

    Examples:
        >>> stack = HStack(
        ...     Text("Left"),
        ...     Text("Right"),
        ...     gap="1rem"
        ... )
        >>> stack.tag
        'hstack'
        >>> isinstance(stack, HStackComponent)
        True
    """
    return HStackComponent(
        tag='hstack',
        props={'gap': gap, **props},
        children=children
    )


def TwoColumn(left: Component, right: Component, **props: Any) -> TwoColumnComponent:
    """
    Two-column layout

    Places elements left and right.

    Args:
        left: Left component
        right: Right component
        **props: Additional properties

    Returns:
        TwoColumnComponent

    Examples:
        >>> layout = TwoColumn(
        ...     Text("Left content"),
        ...     Text("Right content")
        ... )
        >>> layout.tag
        'two-column'
        >>> len(layout.children)
        2
        >>> isinstance(layout, TwoColumnComponent)
        True
    """
    return TwoColumnComponent(
        tag='two-column',
        props=props,
        children=(left, right)
    )


def Grid(*children: Component, columns: int = 2, gap: str = "1rem", **props: Any) -> GridComponent:
    """
    Grid layout

    Arranges child elements in a grid.

    Args:
        *children: Child components
        columns: Number of columns
        gap: Grid spacing
        **props: Additional properties

    Returns:
        GridComponent

    Examples:
        >>> grid = Grid(
        ...     Text("1"), Text("2"), Text("3"), Text("4"),
        ...     columns=2
        ... )
        >>> grid.props['columns']
        2
        >>> isinstance(grid, GridComponent)
        True
    """
    return GridComponent(
        tag='grid',
        props={'columns': columns, 'gap': gap, **props},
        children=children
    )


def Container(*children: Component, **props: Any) -> ContainerComponent:
    """
    Generic container

    Groups child elements.

    Args:
        *children: Child components
        **props: Additional properties

    Returns:
        ContainerComponent

    Examples:
        >>> container = Container(
        ...     Text("Item 1"),
        ...     Text("Item 2"),
        ...     class_name="my-container"
        ... )
        >>> container.tag
        'container'
        >>> isinstance(container, ContainerComponent)
        True
    """
    return ContainerComponent(
        tag='container',
        props=props,
        children=children
    )


# ============================================================================
# List Components
# ============================================================================

def List(*items: str | Component, ordered: bool = False, **props: Any) -> ListComponent:
    """
    List component

    Args:
        *items: List items (strings or Components)
        ordered: Whether it's an ordered list
        **props: Additional properties

    Returns:
        ListComponent

    Examples:
        >>> lst = List("Item 1", "Item 2", "Item 3")
        >>> lst.tag
        'list'
        >>> len(lst.children)
        3
        >>> isinstance(lst, ListComponent)
        True

        >>> lst_ordered = List("First", "Second", ordered=True)
        >>> lst_ordered.props['ordered']
        True
    """
    # Convert strings to Text components
    children: list[Component] = []
    for item in items:
        if isinstance(item, str):
            children.append(Text(item))
        else:
            children.append(item)

    return ListComponent(
        tag='list',
        props={'ordered': ordered, **props},
        children=tuple(children)
    )


# ============================================================================
# Special Components
# ============================================================================

def RawHtml(html: str, **props: Any) -> RawHtmlComponent:
    """
    Raw HTML component

    Directly inserts HTML.

    Args:
        html: HTML string
        **props: Additional properties

    Returns:
        RawHtmlComponent

    Examples:
        >>> raw = RawHtml("<div class='custom'>Custom HTML</div>")
        >>> raw.tag
        'raw-html'
        >>> raw.props['html']
        '<div class=\\'custom\\'>Custom HTML</div>'
        >>> isinstance(raw, RawHtmlComponent)
        True
    """
    return RawHtmlComponent(
        tag='raw-html',
        props={'html': html, **props},
        children=()
    )


def Spacer(height: str = "1rem", **props: Any) -> SpacerComponent:
    """
    Spacer component

    Inserts empty space.

    Args:
        height: Height of the space
        **props: Additional properties

    Returns:
        SpacerComponent

    Examples:
        >>> spacer = Spacer(height="2rem")
        >>> spacer.props['height']
        '2rem'
        >>> isinstance(spacer, SpacerComponent)
        True
    """
    return SpacerComponent(
        tag='spacer',
        props={'height': height, **props},
        children=()
    )


def Divider(**props: Any) -> DividerComponent:
    """
    Divider component

    Args:
        **props: Additional properties

    Returns:
        DividerComponent

    Examples:
        >>> divider = Divider()
        >>> divider.tag
        'divider'
        >>> isinstance(divider, DividerComponent)
        True
    """
    return DividerComponent(
        tag='divider',
        props=props,
        children=()
    )
