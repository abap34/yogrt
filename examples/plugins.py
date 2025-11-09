"""
Example: Creating and Using Plugins

This example demonstrates how to create plugins that encapsulate
reusable functionality (renderers, transforms, HTML transforms).
"""

from yogrt import create_slide, Page, Header, Text, Component, Context, Slide, Plugin
from typing import Any
from dataclasses import dataclass


# ============================================================================
# Define Custom Component Classes for Plugins
# ============================================================================

@dataclass(frozen=True)
class HighlightComponent:
    """Highlight text with background color"""
    text: str
    color: str = "yellow"
    key: str | None = None

    @property
    def tag(self) -> str:
        return "highlight"


@dataclass(frozen=True)
class QuoteComponent:
    """Blockquote with optional author attribution"""
    text: str
    author: str = ""
    key: str | None = None

    @property
    def tag(self) -> str:
        return "quote"


@dataclass(frozen=True)
class PageNumberComponent:
    """Page number placeholder (will be filled by transform)"""
    key: str | None = None

    @property
    def tag(self) -> str:
        return "page-number"


# ============================================================================
# Factory Functions
# ============================================================================

def Highlight(text: str, color: str = "yellow", **kwargs: Any) -> HighlightComponent:
    """Create a Highlight component"""
    return HighlightComponent(text=text, color=color, key=kwargs.get('key'))


def Quote(text: str, author: str = "", **kwargs: Any) -> QuoteComponent:
    """Create a Quote component"""
    return QuoteComponent(text=text, author=author, key=kwargs.get('key'))


def PageNumber(**kwargs: Any) -> PageNumberComponent:
    """Create a PageNumber component"""
    return PageNumberComponent(key=kwargs.get('key'))


# ============================================================================
# Plugin 1: Highlight Plugin
# ============================================================================

def highlight_plugin() -> Plugin:
    """
    Plugin that adds support for highlighted text

    Returns:
        Plugin function
    """
    def render_highlight(component: Component, context: Context) -> str:
        assert isinstance(component, HighlightComponent)

        text = component.text
        color = component.color

        colors = {
            'yellow': '#fef08a',
            'green': '#bbf7d0',
            'blue': '#bfdbfe',
            'pink': '#fbcfe8'
        }

        bg_color = colors.get(color, colors['yellow'])

        return f'<mark style="background-color: {bg_color}; padding: 0.125rem 0.25rem;">{text}</mark>'

    def plugin(slide: Slide) -> Slide:
        slide.add_renderer('highlight', render_highlight)
        return slide

    return plugin


# ============================================================================
# Plugin 2: Quote Plugin
# ============================================================================

def quote_plugin() -> Plugin:
    """
    Plugin that adds support for styled blockquotes

    Returns:
        Plugin function
    """
    def render_quote(component: Component, context: Context) -> str:
        assert isinstance(component, QuoteComponent)

        text = component.text
        author = component.author

        author_html = f'<footer style="margin-top: 0.5rem; color: #6b7280;">— {author}</footer>' if author else ''

        return f"""
        <blockquote style="
            border-left: 4px solid #3b82f6;
            padding-left: 1rem;
            margin: 1.5rem 0;
            font-style: italic;
            color: #374151;
        ">
            <p style="margin: 0;">{text}</p>
            {author_html}
        </blockquote>
        """

    def plugin(slide: Slide) -> Slide:
        slide.add_renderer('quote', render_quote)
        return slide

    return plugin


# ============================================================================
# Plugin 3: Page Number Plugin (with Transform)
# ============================================================================

def page_number_plugin(position: str = "bottom-right") -> Plugin:
    """
    Plugin that adds page numbers to slides

    Args:
        position: Position of page numbers (bottom-right, bottom-center, top-right)

    Returns:
        Plugin function
    """
    def render_page_number(component: Component, context: Context) -> str:
        assert isinstance(component, PageNumberComponent)

        current = context.current_page
        total = context.total_pages

        positions = {
            'bottom-right': 'position: fixed; bottom: 1rem; right: 2rem;',
            'bottom-center': 'position: fixed; bottom: 1rem; left: 50%; transform: translateX(-50%);',
            'top-right': 'position: fixed; top: 1rem; right: 2rem;'
        }

        style = positions.get(position, positions['bottom-right'])

        return f"""
        <div style="{style} color: #6b7280; font-size: 0.875rem;">
            {current} / {total}
        </div>
        """

    def add_page_number(component: Component) -> Component:
        """Transform that adds page number to each page"""
        from dataclasses import replace
        from yogrt.core import PageComponent

        if not isinstance(component, PageComponent):
            return component

        # Add page number component to page
        page_number = PageNumber()
        new_children = component.children + (page_number,)  # type: ignore[arg-type]

        return replace(component, children=new_children)

    def plugin(slide: Slide) -> Slide:
        slide.add_renderer('page-number', render_page_number)
        slide.add_transform(add_page_number)
        return slide

    return plugin


# ============================================================================
# Plugin 4: Custom CSS Plugin (HTML Transform)
# ============================================================================

def custom_css_plugin(css: str) -> Plugin:
    """
    Plugin that adds custom CSS to the output HTML

    Args:
        css: CSS string to inject

    Returns:
        Plugin function
    """
    def inject_css(html: str) -> str:
        """HTML transform that injects CSS"""
        css_tag = f'<style>{css}</style>'
        return html.replace('</head>', f'{css_tag}</head>')

    def plugin(slide: Slide) -> Slide:
        slide.add_html_transform(inject_css)
        return slide

    return plugin


# ============================================================================
# Create Slide with Plugins
# ============================================================================

def main():
    slide = create_slide()

    # Use plugins
    slide.use(highlight_plugin())
    slide.use(quote_plugin())
    slide.use(page_number_plugin(position="bottom-right"))

    # Add custom CSS for better styling
    custom_css = """
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .page {
            background: white;
        }
    """
    slide.use(custom_css_plugin(custom_css))

    # Page 1: Title
    slide.add_page(Page(
        Header("Plugins Demo", level=1),
        Text("Examples of using plugins to extend Yogrt")
    ))

    # Page 2: Highlight Plugin
    slide.add_page(Page(
        Header("Highlight Plugin", level=2),
        Text("You can highlight important text:"),
        Highlight("This is highlighted in yellow", color="yellow"),
        Text("Different colors are supported:"),
        Highlight("Green highlight", color="green"),
        Highlight("Blue highlight", color="blue"),
        Highlight("Pink highlight", color="pink")
    ))

    # Page 3: Quote Plugin
    slide.add_page(Page(
        Header("Quote Plugin", level=2),
        Quote(
            "The best way to predict the future is to invent it.",
            author="Alan Kay"
        ),
        Quote(
            "Programs must be written for people to read, and only incidentally for machines to execute.",
            author="Harold Abelson"
        ),
        Quote(
            "Simplicity is prerequisite for reliability."
        )
    ))

    # Page 4: Multiple Plugins
    slide.add_page(Page(
        Header("Combining Plugins", level=2),
        Text("All plugins work together seamlessly:"),
        Quote(
            "Lisp has jokingly been called 'the most intelligent way to misuse a computer'. "
            "I think that description is a great compliment because it transmits the full "
            "flavor of liberation.",
            author="John McCarthy"
        ),
        Text("Notice the page numbers at the bottom-right corner!")
    ))

    # Export
    slide.export("plugins_example.html")
    print("✓ Generated: plugins_example.html")


if __name__ == "__main__":
    main()
