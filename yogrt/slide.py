"""
Yogrt Slide Module

Defines Slide class and rendering pipeline.
"""

from typing import Callable
from .core import Component, Context, render, walk, Transform, HtmlTransform, Renderer


# ============================================================================
# Plugin Type
# ============================================================================

Plugin = Callable[['Slide'], 'Slide']
"""Plugin type definition: Slide → Slide function"""


# ============================================================================
# Slide Class
# ============================================================================

class Slide:
    """
    Container representing an entire slide deck

    Holds a list of pages and rendering configuration.
    Supports extension through plugins.

    Attributes:
        pages: List of pages (each page is a Component)
        context: Rendering context
        transforms: List of transformation functions to apply
        html_transforms: List of HTML transformation functions

    Examples:
        >>> from yogrt import create_slide, Page, Header, Text
        >>> slide = create_slide()
        >>> slide.add_page(Page(Header("Title", level=1), Text("Content")))
        >>> slide.export("output.html")
    """

    def __init__(self) -> None:
        """Initialize Slide"""
        self.pages: list[Component] = []
        self.context = Context()
        self.transforms: list[Transform] = []
        self.html_transforms: list[HtmlTransform] = []

    def add_page(self, page: Component) -> 'Slide':
        """
        Add a page to the slide

        Args:
            page: Page component to add

        Returns:
            self (for method chaining)

        Examples:
            >>> slide = Slide()
            >>> slide.add_page({'tag': 'page', 'props': {}, 'children': []})
            <yogrt.slide.Slide object at ...>
        """
        self.pages.append(page)
        return self

    def add_renderer(self, tag: str, renderer: Renderer) -> 'Slide':
        """
        Register a custom renderer

        Args:
            tag: Component tag name
            renderer: Renderer function

        Returns:
            self (for method chaining)

        Examples:
            >>> def my_renderer(comp, ctx):
            ...     return f"<div>{comp['props']}</div>"
            >>> slide = Slide()
            >>> slide.add_renderer('my-tag', my_renderer)
            <yogrt.slide.Slide object at ...>
        """
        self.context.renderers[tag] = renderer
        return self

    def add_transform(self, transformer: Transform) -> 'Slide':
        """
        Add a transformation function

        Transform performs Component → Component transformations.
        Applied to all pages during build().

        Args:
            transformer: Transformation function

        Returns:
            self (for method chaining)

        Examples:
            >>> def add_id(comp):
            ...     if comp['tag'] == 'header':
            ...         props = comp.get('props', {})
            ...         props['id'] = 'auto-id'
            ...         return {**comp, 'props': props}
            ...     return comp
            >>> slide = Slide()
            >>> slide.add_transform(add_id)
            <yogrt.slide.Slide object at ...>
        """
        self.transforms.append(transformer)
        return self

    def add_html_transform(self, transformer: HtmlTransform) -> 'Slide':
        """
        Add an HTML transformation function

        HTML Transform performs HTML → HTML transformations.
        Applied after rendering, before export.

        Args:
            transformer: HTML transformation function

        Returns:
            self (for method chaining)

        Examples:
            >>> def add_script(html):
            ...     return html.replace('</body>', '<script>...</script></body>')
            >>> slide = Slide()
            >>> slide.add_html_transform(add_script)
            <yogrt.slide.Slide object at ...>
        """
        self.html_transforms.append(transformer)
        return self

    def use(self, plugin: Plugin) -> 'Slide':
        """
        Apply a plugin

        Plugin is a Slide → Slide function.
        Registers renderers, transforms, HTML transforms, etc.

        Args:
            plugin: Plugin function

        Returns:
            Slide after applying the plugin

        Examples:
            >>> def my_plugin(slide):
            ...     slide.add_renderer('my-tag', lambda c, ctx: '<div>...</div>')
            ...     return slide
            >>> slide = Slide()
            >>> slide.use(my_plugin)
            <yogrt.slide.Slide object at ...>
        """
        return plugin(self)

    def build(self) -> 'Slide':
        """
        Apply all transformations and return a new Slide

        Applies all transforms to each page's Component tree and
        returns a new Slide instance (does not modify the original Slide).

        Returns:
            New Slide instance after applying transformations

        Examples:
            >>> slide = Slide()
            >>> slide.add_page({'tag': 'page', 'props': {}, 'children': []})
            <yogrt.slide.Slide object at ...>
            >>> def add_class(comp):
            ...     props = comp.get('props', {})
            ...     props['class'] = 'styled'
            ...     return {**comp, 'props': props}
            >>> slide.add_transform(add_class)
            <yogrt.slide.Slide object at ...>
            >>> built = slide.build()
            >>> built.pages[0]['props']['class']
            'styled'
        """
        # Create new Slide (immutable pattern)
        new_slide = Slide()
        new_slide.context = self.context
        new_slide.html_transforms = self.html_transforms

        # Apply all transforms to each page
        for page in self.pages:
            transformed_page = page
            for transformer in self.transforms:
                transformed_page = walk(transformed_page, transformer)
            new_slide.pages.append(transformed_page)

        return new_slide

    def export(self, path: str) -> None:
        """
        Export the slide as an HTML file

        Pipeline:
        1. Build (apply transforms)
        2. Render (convert each page to HTML)
        3. Apply HTML transforms
        4. Write to file

        Args:
            path: Output file path

        Examples:
            >>> slide = Slide()
            >>> slide.add_page({'tag': 'page', 'props': {}, 'children': []})
            <yogrt.slide.Slide object at ...>
            >>> slide.export("output.html")  # doctest: +SKIP
        """
        # 1. Build (apply transforms)
        built = self.build()

        # 2. Set context
        built.context.total_pages = len(built.pages)

        # 3. Render each page
        html_pages = []
        for i, page in enumerate(built.pages, 1):
            built.context.current_page = i
            html_pages.append(render(page, built.context))

        # 4. Generate HTML
        html = built._generate_html(html_pages)

        # 5. Apply HTML transforms
        for html_transformer in built.html_transforms:
            html = html_transformer(html)

        # 6. Write to file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)

    def _generate_html(self, pages: list[str]) -> str:
        """
        Generate HTML template

        Args:
            pages: Rendered page HTML

        Returns:
            Complete HTML document
        """
        css = self.context.store.get('custom_css', '')

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .page {{
            width: 100vw;
            height: 100vh;
            padding: 2rem;
            page-break-after: always;
            display: flex;
            flex-direction: column;
        }}
        @media print {{
            .page {{ page-break-after: always; }}
        }}
        {css}
    </style>
</head>
<body>
    {''.join(pages)}
</body>
</html>"""
