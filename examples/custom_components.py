"""
Example: Creating Custom Components and Renderers

This example demonstrates how to create custom components
and register their renderers.
"""

from yogrt import create_slide, Page, Header, Text, Component, Context
from typing import Any


# ============================================================================
# Define Custom Components
# ============================================================================

def Alert(message: str, level: str = "info", **props: Any) -> Component:
    """
    Alert component - displays a styled message box

    Args:
        message: Alert message
        level: Alert level (info, warning, error, success)
    """
    return Component(
        tag='alert',
        props={'message': message, 'level': level, **props},
        children=()
    )


def Badge(text: str, color: str = "blue", **props: Any) -> Component:
    """
    Badge component - displays a small label or tag

    Args:
        text: Badge text
        color: Badge color
    """
    return Component(
        tag='badge',
        props={'text': text, 'color': color, **props},
        children=()
    )


def Card(*children: Component, title: str = "", **props: Any) -> Component:
    """
    Card component - a container with optional title

    Args:
        *children: Child components
        title: Card title
    """
    return Component(
        tag='card',
        props={'title': title, **props},
        children=children
    )


# ============================================================================
# Define Custom Renderers
# ============================================================================

def render_alert(component: Component, context: Context) -> str:
    """Render Alert component"""
    message = component.props['message']
    level = component.props['level']

    # Color scheme for different levels
    colors = {
        'info': '#3b82f6',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'success': '#10b981'
    }

    color = colors.get(level, colors['info'])

    return f"""
    <div style="
        background-color: {color}22;
        border-left: 4px solid {color};
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    ">
        <strong style="color: {color};">{level.upper()}</strong>
        <p style="margin: 0.5rem 0 0 0;">{message}</p>
    </div>
    """


def render_badge(component: Component, context: Context) -> str:
    """Render Badge component"""
    text = component.props['text']
    color = component.props['color']

    colors = {
        'blue': '#3b82f6',
        'green': '#10b981',
        'red': '#ef4444',
        'yellow': '#f59e0b',
        'purple': '#8b5cf6'
    }

    bg_color = colors.get(color, colors['blue'])

    return f"""
    <span style="
        display: inline-block;
        background-color: {bg_color};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0 0.25rem;
    ">{text}</span>
    """


def render_card(component: Component, context: Context) -> str:
    """Render Card component"""
    from yogrt import render

    title = component.props.get('title', '')
    children_html = [render(child, context) for child in component.children]

    title_html = f'<h3 style="margin-top: 0; color: #1f2937;">{title}</h3>' if title else ''

    return f"""
    <div style="
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 1rem 0;
    ">
        {title_html}
        {''.join(children_html)}
    </div>
    """


# ============================================================================
# Create Slide with Custom Components
# ============================================================================

def main():
    slide = create_slide()

    # Register custom renderers
    slide.add_renderer('alert', render_alert)
    slide.add_renderer('badge', render_badge)
    slide.add_renderer('card', render_card)

    # Page 1: Title
    slide.add_page(Page(
        Header("Custom Components Demo", level=1),
        Text("Examples of custom components with custom renderers")
    ))

    # Page 2: Alert Examples
    slide.add_page(Page(
        Header("Alert Component", level=2),
        Alert("This is an informational message", level="info"),
        Alert("Warning: Please review this carefully", level="warning"),
        Alert("Error: Something went wrong", level="error"),
        Alert("Success: Operation completed", level="success")
    ))

    # Page 3: Badge Examples
    slide.add_page(Page(
        Header("Badge Component", level=2),
        Text("Technologies used:"),
        Badge("Python", color="blue"),
        Badge("TypeScript", color="blue"),
        Badge("React", color="purple"),
        Text("Status indicators:"),
        Badge("Active", color="green"),
        Badge("Pending", color="yellow"),
        Badge("Failed", color="red")
    ))

    # Page 4: Card Examples
    slide.add_page(Page(
        Header("Card Component", level=2),
        Card(
            Text("This is a card with a title and content."),
            Text("Cards can contain any child components."),
            title="Example Card"
        ),
        Card(
            Alert("You can nest components inside cards!", level="info"),
            Badge("Nested", color="purple"),
            title="Nested Components"
        )
    ))

    # Export
    slide.export("custom_components_example.html")
    print("✓ Generated: custom_components_example.html")


if __name__ == "__main__":
    main()
