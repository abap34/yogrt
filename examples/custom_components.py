"""
Example: Creating Custom Components and Renderers

This example demonstrates how to create custom components
and register their renderers.
"""

from yogrt import create_slide, Page, Header, Text, Component, Context
from typing import Any
from dataclasses import dataclass


# ============================================================================
# Define Custom Component Classes
# ============================================================================

@dataclass(frozen=True)
class AlertComponent:
    """Alert component - displays a styled message box"""
    message: str
    level: str = "info"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "alert"


@dataclass(frozen=True)
class BadgeComponent:
    """Badge component - displays a small label or tag"""
    text: str
    color: str = "blue"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "badge"


@dataclass(frozen=True)
class CardComponent:
    """Card component - a container with optional title"""
    children: tuple[Component | Any, ...] = ()
    title: str = ""
    key: str | None = None

    @property
    def tag(self) -> str:
        return "card"


# ============================================================================
# Factory Functions
# ============================================================================

def Alert(message: str, level: str = "info", **kwargs: Any) -> AlertComponent:
    """Create an Alert component"""
    return AlertComponent(message=message, level=level, key=kwargs.get('key'))


def Badge(text: str, color: str = "blue", **kwargs: Any) -> BadgeComponent:
    """Create a Badge component"""
    return BadgeComponent(text=text, color=color, key=kwargs.get('key'))


def Card(*children: Component | Any, title: str = "", **kwargs: Any) -> CardComponent:
    """Create a Card component"""
    return CardComponent(children=children, title=title, key=kwargs.get('key'))


# ============================================================================
# Define Custom Renderers
# ============================================================================

def render_alert(component: Component, context: Context) -> str:
    """Render Alert component"""
    # Cast to our custom component type for attribute access
    assert isinstance(component, AlertComponent)

    message = component.message
    level = component.level

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
    assert isinstance(component, BadgeComponent)

    text = component.text
    color = component.color

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

    assert isinstance(component, CardComponent)

    title = component.title
    children_html = [render(child, context) for child in component.children]  # type: ignore[arg-type]

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
