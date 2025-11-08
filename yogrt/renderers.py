"""
Yogrt Standard Renderers

Defines renderer functions for all standard components.
"""

from .core import Component, Context, render


# ============================================================================
# Leaf Component Renderers
# ============================================================================

def render_text(component: Component, context: 'Context') -> str:
    """Text component renderer"""
    from .core import TextComponent
    assert isinstance(component, TextComponent)

    class_attr = f' class="{component.class_name}"' if component.class_name else ''
    return f"<p{class_attr}>{component.content}</p>"


def render_header(component: Component, context: 'Context') -> str:
    """Header component renderer"""
    from .core import HeaderComponent
    assert isinstance(component, HeaderComponent)

    # Track headers for TOC generation
    if component.id and component.id not in [h[2] for h in context.headers]:
        context.headers.append((component.level, component.text, component.id))

    id_attr = f' id="{component.id}"' if component.id else ''
    class_attr = f' class="{component.class_name}"' if component.class_name else ''

    return f"<h{component.level}{id_attr}{class_attr}>{component.text}</h{component.level}>"


def render_image(component: Component, context: 'Context') -> str:
    """Image component renderer"""
    from .core import ImageComponent
    assert isinstance(component, ImageComponent)

    src = component.src

    # Handle matplotlib Figure
    if hasattr(src, 'savefig'):
        import io
        import base64

        buf = io.BytesIO()
        src.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode()
        img_tag = f'<img src="data:image/png;base64,{img_data}" alt="{component.alt}"/>'
    else:
        # Regular image path or URL
        img_tag = f'<img src="{src}" alt="{component.alt}"/>'

    # Add width/height if specified
    if component.width:
        img_tag = img_tag.replace('/>', f' width="{component.width}"/>')
    if component.height:
        img_tag = img_tag.replace('/>', f' height="{component.height}"/>')

    # Wrap in figure with caption
    if component.caption:
        return f'''
        <figure>
            {img_tag}
            <figcaption>{component.caption}</figcaption>
        </figure>
        '''

    return img_tag


def render_code(component: Component, context: 'Context') -> str:
    """Code component renderer"""
    from .core import CodeComponent
    assert isinstance(component, CodeComponent)

    # Escape HTML in code
    code_escaped = component.code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    return f'''
    <pre><code class="language-{component.lang}">{code_escaped}</code></pre>
    '''


def render_link(component: Component, context: 'Context') -> str:
    """Link component renderer"""
    from .core import LinkComponent
    assert isinstance(component, LinkComponent)

    target_attr = f' target="{component.target}"' if component.target else ''
    return f'<a href="{component.href}"{target_attr}>{component.text}</a>'


def render_spacer(component: Component, context: 'Context') -> str:
    """Spacer component renderer"""
    from .core import SpacerComponent
    assert isinstance(component, SpacerComponent)

    return f'<div class="spacer" style="height: {component.height};"></div>'


def render_divider(component: Component, context: 'Context') -> str:
    """Divider component renderer"""
    from .core import DividerComponent
    assert isinstance(component, DividerComponent)

    return f'<hr class="divider" style="border-color: {component.color}; border-width: {component.thickness};"/>'


def render_raw_html(component: Component, context: 'Context') -> str:
    """Raw HTML component renderer"""
    from .core import RawHtmlComponent
    assert isinstance(component, RawHtmlComponent)

    return component.html


def render_footnote_ref(component: Component, context: 'Context') -> str:
    """Footnote reference renderer"""
    from .core import FootnoteRefComponent
    assert isinstance(component, FootnoteRefComponent)

    # Return superscript link to footnote
    return f'<sup><a href="#fn-{component.note_id}" id="fnref-{component.note_id}">[{component.note_id}]</a></sup>'


def render_footnote(component: Component, context: 'Context') -> str:
    """Footnote content renderer"""
    from .core import FootnoteComponent
    assert isinstance(component, FootnoteComponent)

    # Store footnote in context for later rendering
    context.footnotes[component.note_id] = component.content

    # Return empty string (footnotes are rendered at the end)
    return ''


def render_citation(component: Component, context: 'Context') -> str:
    """Citation renderer"""
    from .core import CitationComponent
    assert isinstance(component, CitationComponent)

    # Return citation reference
    return f'<cite><a href="#ref-{component.cite_key}">[{component.cite_key}]</a></cite>'


# ============================================================================
# Container Component Renderers
# ============================================================================

def render_page(component: Component, context: 'Context') -> str:
    """Page component renderer"""
    from .core import PageComponent
    assert isinstance(component, PageComponent)

    children_html = [render(child, context) for child in component.children]
    page_num = context.current_page

    class_attr = f' class="{component.class_name}"' if component.class_name else ''

    # Render footnotes at the end of page if any
    footnotes_html = ''
    if context.footnotes:
        footnote_items = [
            f'<li id="fn-{note_id}">{content} <a href="#fnref-{note_id}">↩</a></li>'
            for note_id, content in context.footnotes.items()
        ]
        footnotes_html = f'''
        <div class="footnotes">
            <hr/>
            <ol>
                {"".join(footnote_items)}
            </ol>
        </div>
        '''
        # Clear footnotes for next page
        context.footnotes.clear()

    return f'''
    <div class="page" id="page-{page_num}"{class_attr}>
        {"".join(children_html)}
        {footnotes_html}
    </div>
    '''


def render_vstack(component: Component, context: 'Context') -> str:
    """VStack component renderer"""
    from .core import VStackComponent
    assert isinstance(component, VStackComponent)

    children_html = [render(child, context) for child in component.children]

    return f'''
    <div class="vstack" style="display: flex; flex-direction: column; gap: {component.gap}; align-items: {component.align};">
        {"".join(children_html)}
    </div>
    '''


def render_hstack(component: Component, context: 'Context') -> str:
    """HStack component renderer"""
    from .core import HStackComponent
    assert isinstance(component, HStackComponent)

    children_html = [render(child, context) for child in component.children]

    return f'''
    <div class="hstack" style="display: flex; flex-direction: row; gap: {component.gap}; align-items: {component.align};">
        {"".join(children_html)}
    </div>
    '''


def render_two_column(component: Component, context: 'Context') -> str:
    """Two-column component renderer"""
    from .core import TwoColumnComponent
    assert isinstance(component, TwoColumnComponent)

    left_html = render(component.left, context)
    right_html = render(component.right, context)

    # Parse ratio (e.g., "1:1", "2:1")
    parts = component.ratio.split(':')
    left_ratio = parts[0] if len(parts) > 0 else '1'
    right_ratio = parts[1] if len(parts) > 1 else '1'

    return f'''
    <div class="two-column" style="display: grid; grid-template-columns: {left_ratio}fr {right_ratio}fr; gap: {component.gap};">
        <div class="left">{left_html}</div>
        <div class="right">{right_html}</div>
    </div>
    '''


def render_grid(component: Component, context: 'Context') -> str:
    """Grid component renderer"""
    from .core import GridComponent
    assert isinstance(component, GridComponent)

    children_html = [render(child, context) for child in component.children]

    return f'''
    <div class="grid" style="display: grid; grid-template-columns: repeat({component.columns}, 1fr); gap: {component.gap};">
        {"".join(children_html)}
    </div>
    '''


def render_container(component: Component, context: 'Context') -> str:
    """Container component renderer"""
    from .core import ContainerComponent
    assert isinstance(component, ContainerComponent)

    children_html = [render(child, context) for child in component.children]

    class_attr = f' class="{component.class_name}"' if component.class_name else ''
    style_attr = f' style="{component.style}"' if component.style else ''

    return f'''
    <div{class_attr}{style_attr}>
        {"".join(children_html)}
    </div>
    '''


def render_list(component: Component, context: 'Context') -> str:
    """List component renderer"""
    from .core import ListComponent
    assert isinstance(component, ListComponent)

    items_html = [f'<li>{render(child, context)}</li>' for child in component.children]

    tag = 'ol' if component.ordered else 'ul'

    return f'''
    <{tag}>
        {"".join(items_html)}
    </{tag}>
    '''


def render_toc(component: Component, context: 'Context') -> str:
    """Table of Contents renderer"""
    from .core import TOCComponent
    assert isinstance(component, TOCComponent)

    # Filter headers by max_level
    filtered_headers = [
        (level, text, id_val)
        for level, text, id_val in context.headers
        if level <= component.max_level
    ]

    if not filtered_headers:
        return ''

    # Build nested list
    toc_items = []
    for level, text, id_val in filtered_headers:
        indent = '  ' * (level - 1)
        toc_items.append(f'{indent}<li><a href="#{id_val}">{text}</a></li>')

    return f'''
    <div class="toc">
        <h2>{component.title}</h2>
        <ul>
            {"".join(toc_items)}
        </ul>
    </div>
    '''


def render_bibliography(component: Component, context: 'Context') -> str:
    """Bibliography renderer"""
    from .core import BibliographyComponent
    assert isinstance(component, BibliographyComponent)

    if not context.citations:
        return ''

    # Render citations
    citation_items = []
    for cite_key, bib_data in context.citations.items():
        # Simple default style
        author = bib_data.get('author', 'Unknown')
        title = bib_data.get('title', 'Untitled')
        year = bib_data.get('year', '')

        citation_items.append(
            f'<li id="ref-{cite_key}">[{cite_key}] {author}. "{title}". {year}.</li>'
        )

    return f'''
    <div class="bibliography">
        <h2>{component.title}</h2>
        <ol>
            {"".join(citation_items)}
        </ol>
    </div>
    '''


# ============================================================================
# Default Renderers Registry
# ============================================================================

DEFAULT_RENDERERS = {
    'text': render_text,
    'header': render_header,
    'image': render_image,
    'code': render_code,
    'link': render_link,
    'spacer': render_spacer,
    'divider': render_divider,
    'raw-html': render_raw_html,
    'footnote-ref': render_footnote_ref,
    'footnote': render_footnote,
    'citation': render_citation,
    'page': render_page,
    'vstack': render_vstack,
    'hstack': render_hstack,
    'two-column': render_two_column,
    'grid': render_grid,
    'container': render_container,
    'list': render_list,
    'toc': render_toc,
    'bibliography': render_bibliography,
}
