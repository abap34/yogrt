"""
Yogrt Standard Renderers

標準コンポーネントのレンダラー関数を定義。
"""

from .core import Component, Context, render


# ============================================================================
# Basic Renderers
# ============================================================================

def render_text(component: Component, context: Context) -> str:
    """テキストコンポーネントのレンダラー"""
    content = component['props']['content']
    class_name = component['props'].get('class', '')
    class_attr = f' class="{class_name}"' if class_name else ''
    return f"<p{class_attr}>{content}</p>"


def render_header(component: Component, context: Context) -> str:
    """ヘッダーコンポーネントのレンダラー"""
    level = component['props']['level']
    text = component['props']['text']
    id_value = component['props'].get('id', '')
    class_name = component['props'].get('class', '')

    id_attr = f' id="{id_value}"' if id_value else ''
    class_attr = f' class="{class_name}"' if class_name else ''

    return f"<h{level}{id_attr}{class_attr}>{text}</h{level}>"


def render_image(component: Component, context: Context) -> str:
    """画像コンポーネントのレンダラー"""
    src = component['props']['src']
    caption = component['props'].get('caption')
    alt = component['props'].get('alt', '')

    # matplotlib Figure の場合
    if hasattr(src, 'savefig'):
        import io
        import base64

        buf = io.BytesIO()
        src.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode()
        img_tag = f'<img src="data:image/png;base64,{img_data}" alt="{alt}"/>'
    else:
        # ファイルパスまたはURL
        img_tag = f'<img src="{src}" alt="{alt}"/>'

    if caption:
        return f'''
        <figure>
            {img_tag}
            <figcaption>{caption}</figcaption>
        </figure>
        '''
    return img_tag


def render_code(component: Component, context: Context) -> str:
    """コードブロックコンポーネントのレンダラー"""
    code = component['props']['code']
    lang = component['props'].get('lang', '')
    return f'<pre><code class="language-{lang}">{code}</code></pre>'


def render_link(component: Component, context: Context) -> str:
    """リンクコンポーネントのレンダラー"""
    url = component['props']['url']
    text = component['props']['text']
    target = component['props'].get('target', '_blank')
    return f'<a href="{url}" target="{target}">{text}</a>'


# ============================================================================
# Container Renderers
# ============================================================================

def render_page(component: Component, context: Context) -> str:
    """ページコンポーネントのレンダラー"""
    children_html = [render(child, context) for child in component['children']]
    page_num = context.current_page
    return f'''
    <div class="page" id="page-{page_num}">
        {"".join(children_html)}
    </div>
    '''


def render_vstack(component: Component, context: Context) -> str:
    """垂直スタックのレンダラー"""
    gap = component['props'].get('gap', '1rem')
    children_html = [render(child, context) for child in component['children']]
    return f'''
    <div class="vstack" style="display: flex; flex-direction: column; gap: {gap};">
        {"".join(children_html)}
    </div>
    '''


def render_hstack(component: Component, context: Context) -> str:
    """水平スタックのレンダラー"""
    gap = component['props'].get('gap', '1rem')
    children_html = [render(child, context) for child in component['children']]
    return f'''
    <div class="hstack" style="display: flex; flex-direction: row; gap: {gap}; align-items: center;">
        {"".join(children_html)}
    </div>
    '''


def render_two_column(component: Component, context: Context) -> str:
    """2カラムレイアウトのレンダラー"""
    children = component['children']
    left_html = render(children[0], context) if len(children) > 0 else ''
    right_html = render(children[1], context) if len(children) > 1 else ''

    return f'''
    <div class="two-column" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; height: 100%;">
        <div class="left">{left_html}</div>
        <div class="right">{right_html}</div>
    </div>
    '''


def render_grid(component: Component, context: Context) -> str:
    """グリッドレイアウトのレンダラー"""
    columns = component['props'].get('columns', 2)
    gap = component['props'].get('gap', '1rem')
    children_html = [render(child, context) for child in component['children']]

    return f'''
    <div class="grid" style="display: grid; grid-template-columns: repeat({columns}, 1fr); gap: {gap};">
        {"".join(children_html)}
    </div>
    '''


def render_container(component: Component, context: Context) -> str:
    """汎用コンテナのレンダラー"""
    children_html = [render(child, context) for child in component['children']]
    class_name = component['props'].get('class', '')
    class_attr = f' class="{class_name}"' if class_name else ''

    return f'<div{class_attr}>{"".join(children_html)}</div>'


# ============================================================================
# List Renderers
# ============================================================================

def render_list(component: Component, context: Context) -> str:
    """リストコンポーネントのレンダラー"""
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
    """生HTMLコンポーネントのレンダラー"""
    return component['props']['html']


def render_spacer(component: Component, context: Context) -> str:
    """スペーサーコンポーネントのレンダラー"""
    height = component['props'].get('height', '1rem')
    return f'<div class="spacer" style="height: {height};"></div>'


def render_divider(component: Component, context: Context) -> str:
    """区切り線コンポーネントのレンダラー"""
    return '<hr class="divider" style="border: none; border-top: 1px solid #ccc; margin: 1rem 0;"/>'


# ============================================================================
# Default Renderers Registry
# ============================================================================

DEFAULT_RENDERERS = {
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
"""標準レンダラーのレジストリ"""
