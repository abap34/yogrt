"""
Yogrt Standard Renderers

Defines renderer functions for standard components.
"""

from .core import Component, Context, render, Renderer


# ============================================================================
# Basic Renderers
# ============================================================================

def render_text(component: Component, context: Context) -> str:
    """Text component renderer"""
    content = component['props']['content']
    class_name = component['props'].get('class', '')
    class_attr = f' class="{class_name}"' if class_name else ''
    return f"<p{class_attr}>{content}</p>"


def render_header(component: Component, context: Context) -> str:
    """Header component renderer"""
    level = component['props']['level']
    text = component['props']['text']
    id_value = component['props'].get('id', '')
    class_name = component['props'].get('class', '')

    id_attr = f' id="{id_value}"' if id_value else ''
    class_attr = f' class="{class_name}"' if class_name else ''

    return f"<h{level}{id_attr}{class_attr}>{text}</h{level}>"


def render_image(component: Component, context: Context) -> str:
    """Image component renderer"""
    src = component['props']['src']
    caption = component['props'].get('caption')
    alt = component['props'].get('alt', '')

    # Handle matplotlib Figure
    if hasattr(src, 'savefig'):
        import io
        import base64

        buf = io.BytesIO()
        src.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode()
        img_tag = f'<img src="data:image/png;base64,{img_data}" alt="{alt}"/>'
    else:
        # File path or URL
        img_tag = f'<img src="{src}" alt="{alt}"/>'

    if caption:
        return f"""
        <figure>
            {img_tag}
            <figcaption>{caption}</figcaption>
        </figure>
        """
    return img_tag


def render_code(component: Component, context: Context) -> str:
    """Code block component renderer"""
    code = component['props']['code']
    lang = component['props'].get('lang', '')
    return f'<pre><code class="language-{lang}">{code}</code></pre>'


def render_link(component: Component, context: Context) -> str:
    """Link component renderer"""
    url = component['props']['url']
    text = component['props']['text']
    target = component['props'].get('target', '_blank')
    return f'<a href="{url}" target="{target}">{text}</a>'


# ============================================================================
# Container Renderers
# ============================================================================

def render_page(component: Component, context: Context) -> str:
    """Page component renderer"""
    children_html = [render(child, context) for child in component['children']]
    page_num = context.current_page
    return f"""
    <div class="page" id="page-{page_num}">
        {"".join(children_html)}
    </div>
    """


def render_vstack(component: Component, context: Context) -> str:
    """Vertical stack renderer"""
    gap = component['props'].get('gap', '1rem')
    children_html = [render(child, context) for child in component['children']]
    return f"""
    <div class="vstack" style="display: flex; flex-direction: column; gap: {gap};">
        {"".join(children_html)}
    </div>
    """


def render_hstack(component: Component, context: Context) -> str:
    """Horizontal stack renderer"""
    gap = component['props'].get('gap', '1rem')
    children_html = [render(child, context) for child in component['children']]
    return f"""
    <div class="hstack" style="display: flex; flex-direction: row; gap: {gap}; align-items: center;">
        {"".join(children_html)}
    </div>
    """


def render_two_column(component: Component, context: Context) -> str:
    """Two-column layout renderer"""
    children = component['children']
    left_html = render(children[0], context) if len(children) > 0 else ''
    right_html = render(children[1], context) if len(children) > 1 else ''

    return f"""
    <div class="two-column" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; height: 100%;">
        <div class="left">{left_html}</div>
        <div class="right">{right_html}</div>
    </div>
    """


def render_grid(component: Component, context: Context) -> str:
    """Grid layout renderer"""
    columns = component['props'].get('columns', 2)
    gap = component['props'].get('gap', '1rem')
    children_html = [render(child, context) for child in component['children']]

    return f"""
    <div class="grid" style="display: grid; grid-template-columns: repeat({columns}, 1fr); gap: {gap};">
        {"".join(children_html)}
    </div>
    """


def render_container(component: Component, context: Context) -> str:
    """Generic container renderer"""
    children_html = [render(child, context) for child in component['children']]
    class_name = component['props'].get('class', '')
    class_attr = f' class="{class_name}"' if class_name else ''

    return f'<div{class_attr}>{"".join(children_html)}</div>'


# ============================================================================
# List Renderers
# ============================================================================

def render_list(component: Component, context: Context) -> str:
    """List component renderer"""
    ordered = component['props'].get('ordered', False)
    tag = 'ol' if ordered else 'ul'

    items_html = []
    for child in component['children']:
        item_html = render(child, context)
        items_html.append(f'<li>{item_html}</li>')

    return f'<{tag}>{"".join(items_html)}</{tag}>'


# ============================================================================
# Special Renderers
# ============================================================================

def render_raw_html(component: Component, context: Context) -> str:
    """Raw HTML component renderer"""
    html = component['props']['html']
    assert isinstance(html, str)
    return html


def render_spacer(component: Component, context: Context) -> str:
    """Spacer component renderer"""
    height = component['props'].get('height', '1rem')
    return f'<div class="spacer" style="height: {height};"></div>'


def render_divider(component: Component, context: Context) -> str:
    """Divider component renderer"""
    return '<hr class="divider" style="border: none; border-top: 1px solid #ccc; margin: 1rem 0;"/>'


# ============================================================================
# Default Renderers Registry
# ============================================================================

DEFAULT_RENDERERS: dict[str, Renderer] = {
    'text': render_text,
    'header': render_header,
    'image': render_image,
    'code': render_code,
    'link': render_link,
    'page': render_page,
    'vstack': render_vstack,
    'hstack': render_hstack,
    'two-column': render_two_column,
    'grid': render_grid,
    'container': render_container,
    'list': render_list,
    'raw-html': render_raw_html,
    'spacer': render_spacer,
    'divider': render_divider,
}
"""Standard renderers registry"""
