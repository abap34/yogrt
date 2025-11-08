"""
Yogrt Standard Components

Defines standard component factory functions.
"""

from typing import Any
from .core import Component


# ============================================================================
# Basic Components
# ============================================================================

def Text(content: str, **props: Any) -> Component:
    """
    Text component

    Args:
        content: Text to display
        **props: Additional properties

    Returns:
        Text component

    Examples:
        >>> text = Text("Hello, world!")
        >>> text['tag']
        'text'
        >>> text['props']['content']
        'Hello, world!'
    """
    return {
        'tag': 'text',
        'props': {'content': content, **props},
        'children': []
    }


def Header(text: str, level: int = 1, **props: Any) -> Component:
    """
    Header component

    Args:
        text: Header text
        level: Heading level (1-6)
        **props: Additional properties (id, class, etc.)

    Returns:
        Header component

    Examples:
        >>> header = Header("Introduction", level=2, id="intro")
        >>> header['tag']
        'header'
        >>> header['props']['level']
        2
        >>> header['props']['id']
        'intro'
    """
    return {
        'tag': 'header',
        'props': {'text': text, 'level': level, **props},
        'children': []
    }


def Image(src: Any, caption: str | None = None, **props: Any) -> Component:
    """
    Image component

    Args:
        src: Image source (file path, URL, matplotlib Figure, etc.)
        caption: Caption (optional)
        **props: Additional properties

    Returns:
        Image component

    Examples:
        >>> img = Image("photo.jpg", caption="A beautiful sunset")
        >>> img['tag']
        'image'
        >>> img['props']['caption']
        'A beautiful sunset'
    """
    return {
        'tag': 'image',
        'props': {'src': src, 'caption': caption, **props},
        'children': []
    }


def Code(code: str, lang: str = "python", **props: Any) -> Component:
    """
    Code block component

    Args:
        code: Code string
        lang: Programming language
        **props: Additional properties

    Returns:
        Code component

    Examples:
        >>> code = Code("print('Hello')", lang="python")
        >>> code['tag']
        'code'
        >>> code['props']['lang']
        'python'
    """
    return {
        'tag': 'code',
        'props': {'code': code, 'lang': lang, **props},
        'children': []
    }


def Link(url: str, text: str, **props: Any) -> Component:
    """
    Link component

    Args:
        url: Link destination URL
        text: Display text
        **props: Additional properties

    Returns:
        Link component

    Examples:
        >>> link = Link("https://example.com", "Visit Example")
        >>> link['props']['url']
        'https://example.com'
    """
    return {
        'tag': 'link',
        'props': {'url': url, 'text': text, **props},
        'children': []
    }


# ============================================================================
# Container Components
# ============================================================================

def Page(*children: Component, **props: Any) -> Component:
    """
    Page component

    Represents one page of a slide.

    Args:
        *children: Child components
        **props: Additional properties

    Returns:
        Page component

    Examples:
        >>> page = Page(
        ...     Header("Title", level=1),
        ...     Text("Content")
        ... )
        >>> page['tag']
        'page'
        >>> len(page['children'])
        2
    """
    return {
        'tag': 'page',
        'props': props,
        'children': list(children)
    }


def VStack(*children: Component, gap: str = "1rem", **props: Any) -> Component:
    """
    Vertical stack layout

    Arranges child elements vertically.

    Args:
        *children: Child components
        gap: Spacing between children
        **props: Additional properties

    Returns:
        VStack component

    Examples:
        >>> stack = VStack(
        ...     Text("First"),
        ...     Text("Second"),
        ...     gap="2rem"
        ... )
        >>> stack['tag']
        'vstack'
        >>> stack['props']['gap']
        '2rem'
    """
    return {
        'tag': 'vstack',
        'props': {'gap': gap, **props},
        'children': list(children)
    }


def HStack(*children: Component, gap: str = "1rem", **props: Any) -> Component:
    """
    Horizontal stack layout

    Arranges child elements horizontally.

    Args:
        *children: Child components
        gap: Spacing between children
        **props: Additional properties

    Returns:
        HStack component

    Examples:
        >>> stack = HStack(
        ...     Text("Left"),
        ...     Text("Right"),
        ...     gap="1rem"
        ... )
        >>> stack['tag']
        'hstack'
    """
    return {
        'tag': 'hstack',
        'props': {'gap': gap, **props},
        'children': list(children)
    }


def TwoColumn(left: Component, right: Component, **props: Any) -> Component:
    """
    Two-column layout

    Places elements left and right.

    Args:
        left: Left component
        right: Right component
        **props: Additional properties

    Returns:
        TwoColumn component

    Examples:
        >>> layout = TwoColumn(
        ...     Text("Left content"),
        ...     Text("Right content")
        ... )
        >>> layout['tag']
        'two-column'
        >>> len(layout['children'])
        2
    """
    return {
        'tag': 'two-column',
        'props': props,
        'children': [left, right]
    }


def Grid(*children: Component, columns: int = 2, gap: str = "1rem", **props: Any) -> Component:
    """
    Grid layout

    Arranges child elements in a grid.

    Args:
        *children: Child components
        columns: Number of columns
        gap: Grid spacing
        **props: Additional properties

    Returns:
        Grid component

    Examples:
        >>> grid = Grid(
        ...     Text("1"), Text("2"), Text("3"), Text("4"),
        ...     columns=2
        ... )
        >>> grid['props']['columns']
        2
    """
    return {
        'tag': 'grid',
        'props': {'columns': columns, 'gap': gap, **props},
        'children': list(children)
    }


def Container(*children: Component, **props: Any) -> Component:
    """
    Generic container

    Groups child elements.

    Args:
        *children: Child components
        **props: Additional properties

    Returns:
        Container component

    Examples:
        >>> container = Container(
        ...     Text("Item 1"),
        ...     Text("Item 2"),
        ...     class_name="my-container"
        ... )
        >>> container['tag']
        'container'
    """
    return {
        'tag': 'container',
        'props': props,
        'children': list(children)
    }


# ============================================================================
# List Components
# ============================================================================

def List(*items: str | Component, ordered: bool = False, **props: Any) -> Component:
    """
    List component

    Args:
        *items: List items (strings or Components)
        ordered: Whether it's an ordered list
        **props: Additional properties

    Returns:
        List component

    Examples:
        >>> lst = List("Item 1", "Item 2", "Item 3")
        >>> lst['tag']
        'list'
        >>> len(lst['children'])
        3

        >>> lst_ordered = List("First", "Second", ordered=True)
        >>> lst_ordered['props']['ordered']
        True
    """
    # Convert strings to Text components
    children = []
    for item in items:
        if isinstance(item, str):
            children.append(Text(item))
        else:
            children.append(item)

    return {
        'tag': 'list',
        'props': {'ordered': ordered, **props},
        'children': children
    }


# ============================================================================
# Special Components
# ============================================================================

def RawHtml(html: str, **props: Any) -> Component:
    """
    Raw HTML component

    Directly inserts HTML.

    Args:
        html: HTML string
        **props: Additional properties

    Returns:
        RawHtml component

    Examples:
        >>> raw = RawHtml("<div class='custom'>Custom HTML</div>")
        >>> raw['tag']
        'raw-html'
        >>> raw['props']['html']
        '<div class=\'custom\'>Custom HTML</div>'
    """
    return {
        'tag': 'raw-html',
        'props': {'html': html, **props},
        'children': []
    }


def Spacer(height: str = "1rem", **props: Any) -> Component:
    """
    Spacer component

    Inserts empty space.

    Args:
        height: Height of the space
        **props: Additional properties

    Returns:
        Spacer component

    Examples:
        >>> spacer = Spacer(height="2rem")
        >>> spacer['props']['height']
        '2rem'
    """
    return {
        'tag': 'spacer',
        'props': {'height': height, **props},
        'children': []
    }


def Divider(**props: Any) -> Component:
    """
    Divider component

    Args:
        **props: Additional properties

    Returns:
        Divider component

    Examples:
        >>> divider = Divider()
        >>> divider['tag']
        'divider'
    """
    return {
        'tag': 'divider',
        'props': props,
        'children': []
    }
