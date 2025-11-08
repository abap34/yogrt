"""
方向性B: Composition + Builder パターン
コンポーネントはデータ、ロジックは関数として分離
"""

from dataclasses import dataclass
from typing import Callable, Any, List
from pathlib import Path

# ===== Core Data Types =====

@dataclass
class Component:
    """全てのコンポーネントの基底 - ただのデータ"""
    tag: str
    props: dict[str, Any]
    children: List['Component']

    def __init__(self, tag: str, props: dict = None, children: List['Component'] = None):
        self.tag = tag
        self.props = props or {}
        self.children = children or []

# ===== Rendering Functions =====

RenderFunc = Callable[[Component, 'RenderContext'], str]
TransformFunc = Callable[[Component], Component]
PluginFunc = Callable[['Slide'], 'Slide']

@dataclass
class RenderContext:
    renderers: dict[str, RenderFunc]  # tag -> render function
    data: dict[str, Any]  # プラグインがデータを共有

class Slide:
    def __init__(self):
        self.pages: List[Component] = []
        self.transforms: List[TransformFunc] = []
        self.plugins: List[PluginFunc] = []

    def add_page(self, page: Component):
        self.pages.append(page)
        return self

    def use(self, plugin: PluginFunc):
        """プラグインを登録"""
        self.plugins.append(plugin)
        return self

    def build(self) -> 'Slide':
        """プラグインを適用"""
        result = self
        for plugin in self.plugins:
            result = plugin(result)
        return result

# ===== Component Builders (ファクトリ関数) =====

def Text(content: str) -> Component:
    return Component("text", {"content": content})

def Header(text: str, level: int = 1, **props) -> Component:
    return Component("header", {"text": text, "level": level, **props})

def Image(src: Any, caption: str = None) -> Component:
    return Component("image", {"src": src, "caption": caption})

def Page(*children: Component) -> Component:
    return Component("page", {}, list(children))

# ===== Default Renderers =====

def render_text(comp: Component, ctx: RenderContext) -> str:
    return f"<p>{comp.props['content']}</p>"

def render_header(comp: Component, ctx: RenderContext) -> str:
    level = comp.props['level']
    text = comp.props['text']
    id_attr = f' id="{comp.props["id"]}"' if "id" in comp.props else ""
    return f"<h{level}{id_attr}>{text}</h{level}>"

def render_image(comp: Component, ctx: RenderContext) -> str:
    src = comp.props['src']

    # matplotlib の処理
    if hasattr(src, 'savefig'):
        import io, base64
        buf = io.BytesIO()
        src.savefig(buf, format='png')
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode()
        img_tag = f'<img src="data:image/png;base64,{img_data}"/>'
    else:
        img_tag = f'<img src="{src}"/>'

    caption = comp.props.get('caption')
    if caption:
        return f'<figure>{img_tag}<figcaption>{caption}</figcaption></figure>'
    return img_tag

def render_page(comp: Component, ctx: RenderContext) -> str:
    children_html = [render(child, ctx) for child in comp.children]
    return f'<div class="page">{"".join(children_html)}</div>'

def render(comp: Component, ctx: RenderContext) -> str:
    """汎用レンダラー - タグに応じた関数を呼び出す"""
    renderer = ctx.renderers.get(comp.tag)
    if renderer:
        return renderer(comp, ctx)
    else:
        # デフォルト: 子要素をレンダリング
        children_html = [render(child, ctx) for child in comp.children]
        return f'<div class="{comp.tag}">{"".join(children_html)}</div>'

# ===== ユーザー拡張例 1: カスタムレイアウト =====

def ThreeColumn(left: Component, center: Component, right: Component) -> Component:
    """3カラムレイアウト - 単なる関数"""
    return Component("three-column", {}, [left, center, right])

def render_three_column(comp: Component, ctx: RenderContext) -> str:
    children = [render(child, ctx) for child in comp.children]
    return f'''
    <div class="three-column">
        <div class="col">{children[0]}</div>
        <div class="col">{children[1]}</div>
        <div class="col">{children[2]}</div>
    </div>
    '''

def CodeWithOutput(code: str, lang: str = "python", auto_execute: bool = True) -> Component:
    """コードと出力 - 実行結果をpropsに格納"""
    output = ""
    if auto_execute and lang == "python":
        import io, sys
        from contextlib import redirect_stdout

        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            try:
                exec(code)
                output = output_buffer.getvalue()
            except Exception as e:
                output = f"Error: {e}"

    return Component("code-with-output", {
        "code": code,
        "lang": lang,
        "output": output
    })

def render_code_with_output(comp: Component, ctx: RenderContext) -> str:
    code = comp.props['code']
    lang = comp.props['lang']
    output = comp.props['output']

    code_html = f'<pre><code class="language-{lang}">{code}</code></pre>'
    output_html = f'<pre class="output">{output}</pre>'

    return f'''
    <div class="code-with-output">
        <div class="code-section">{code_html}</div>
        <div class="output-section">{output_html}</div>
    </div>
    '''

# ===== ユーザー拡張例 2: プラグインによる機能追加 =====

def github_icon_plugin(username: str, size: int = 100) -> PluginFunc:
    """GitHubアイコン取得プラグイン - 高階関数で実装"""

    def fetch_icon(username: str) -> bytes:
        import urllib.request
        url = f"https://github.com/{username}.png"
        with urllib.request.urlopen(url) as response:
            return response.read()

    def plugin(slide: Slide) -> Slide:
        # カスタムレンダラーを登録
        import base64

        def render_github_icon(comp: Component, ctx: RenderContext) -> str:
            username = comp.props['username']
            size = comp.props.get('size', 100)
            img_data = fetch_icon(username)
            img_b64 = base64.b64encode(img_data).decode()
            return f'<img src="data:image/png;base64,{img_b64}" width="{size}"/>'

        # Slide を変更せず、レンダラーだけ追加する想定
        # （実際は RenderContext に追加する）
        return slide

    return plugin

def GitHubIcon(username: str, size: int = 100) -> Component:
    """GitHubアイコン - プラグインと組み合わせて使う"""
    return Component("github-icon", {"username": username, "size": size})

# ===== ユーザー拡張例 3: BibTeX統合（関数型スタイル）=====

def bibtex_plugin(bibfile: str) -> PluginFunc:
    """BibTeX引用管理プラグイン"""

    citations = []
    entries = {
        'sample2024': {
            'author': 'Sample A.',
            'title': 'Sample Paper',
            'year': '2024'
        }
    }

    def cite_key(key: str) -> str:
        if key not in citations:
            citations.append(key)
        return f"[{citations.index(key) + 1}]"

    def plugin(slide: Slide) -> Slide:
        # Transform: Cite コンポーネントを Text に変換
        def transform_cite(comp: Component) -> Component:
            if comp.tag == "cite":
                key = comp.props['key']
                citation = cite_key(key)
                return Text(citation)
            else:
                # 子要素も再帰的に変換
                comp.children = [transform_cite(child) for child in comp.children]
                return comp

        # Transform: Bibliography を実際の HTML に変換
        def transform_bibliography(comp: Component) -> Component:
            if comp.tag == "bibliography":
                items = []
                for i, key in enumerate(citations, 1):
                    entry = entries.get(key, {})
                    author = entry.get('author', 'Unknown')
                    title = entry.get('title', 'Unknown')
                    year = entry.get('year', 'Unknown')
                    items.append(f'<li>[{i}] {author}, "{title}", {year}</li>')
                bib_html = f'<ol class="bibliography">{"".join(items)}</ol>'
                return Component("raw-html", {"html": bib_html})
            else:
                comp.children = [transform_bibliography(child) for child in comp.children]
                return comp

        # 全ページを変換
        slide.pages = [transform_bibliography(transform_cite(page)) for page in slide.pages]
        return slide

    return plugin

def Cite(key: str) -> Component:
    return Component("cite", {"key": key})

def Bibliography() -> Component:
    return Component("bibliography", {})

# ===== ユーザー拡張例 4: 自動フッター追加 =====

def auto_footer_plugin(footer_text: str) -> PluginFunc:
    """全ページにフッターを追加"""
    def plugin(slide: Slide) -> Slide:
        footer = Component("footer", {"text": footer_text})

        for page in slide.pages:
            page.children.append(footer)

        return slide

    return plugin

def render_footer(comp: Component, ctx: RenderContext) -> str:
    text = comp.props['text']
    page_num = ctx.data.get('current_page', '?')
    total = ctx.data.get('total_pages', '?')
    return f'<div class="footer">{text} | Page {page_num}/{total}</div>'

# ===== ユーザー拡張例 5: TOC自動生成 =====

def toc_plugin(max_level: int = 2) -> PluginFunc:
    """目次を自動生成して2ページ目に挿入"""
    def plugin(slide: Slide) -> Slide:
        toc_items = []

        # 全ページをスキャン
        for page_num, page in enumerate(slide.pages, 1):
            for comp in page.children:
                if comp.tag == "header" and comp.props.get('level', 99) <= max_level:
                    toc_items.append({
                        'level': comp.props['level'],
                        'text': comp.props['text'],
                        'page': page_num
                    })

        # TOC ページを生成
        toc_html = '<ul class="toc">'
        for item in toc_items:
            indent = '  ' * (item['level'] - 1)
            toc_html += f'{indent}<li><a href="#page-{item["page"]}">{item["text"]}</a></li>'
        toc_html += '</ul>'

        toc_page = Page(
            Header("Table of Contents", level=1),
            Component("raw-html", {"html": toc_html})
        )

        # 2番目に挿入
        slide.pages.insert(1, toc_page)
        return slide

    return plugin

# ===== 使用例 =====

def example_usage():
    slide = Slide()

    # プラグイン登録
    slide.use(bibtex_plugin("refs.bib"))
    slide.use(auto_footer_plugin("My Presentation"))
    slide.use(toc_plugin(max_level=2))

    # ページ追加
    slide.add_page(Page(
        Header("Introduction", level=1, id="intro"),
        Text("Welcome to my presentation")
    ))

    slide.add_page(Page(
        Header("Methods", level=1, id="methods"),
        ThreeColumn(
            Text("Step 1"),
            Text("Step 2"),
            Text("Step 3")
        )
    ))

    slide.add_page(Page(
        Header("Code Example", level=1),
        CodeWithOutput("""
print("Hello!")
result = sum(range(10))
print(f"Sum: {result}")
""")
    ))

    slide.add_page(Page(
        Header("References", level=1),
        Text("See paper "),
        Cite("sample2024")
    ))

    slide.add_page(Page(
        Bibliography()
    ))

    # ビルド（プラグイン適用）
    final_slide = slide.build()

    # レンダリング
    ctx = RenderContext(
        renderers={
            "text": render_text,
            "header": render_header,
            "image": render_image,
            "page": render_page,
            "three-column": render_three_column,
            "code-with-output": render_code_with_output,
            "footer": render_footer,
            "raw-html": lambda c, ctx: c.props['html']
        },
        data={"current_page": 1, "total_pages": len(final_slide.pages)}
    )

    html_pages = []
    for i, page in enumerate(final_slide.pages, 1):
        ctx.data['current_page'] = i
        html_pages.append(render(page, ctx))

    html = f'''<!DOCTYPE html>
<html>
<head>
    <style>
        .three-column {{ display: flex; }}
        .three-column .col {{ flex: 1; padding: 10px; }}
        .code-with-output {{ display: flex; }}
        .code-section, .output-section {{ flex: 1; }}
    </style>
</head>
<body>
    {''.join(html_pages)}
</body>
</html>'''

    with open("output.html", "w") as f:
        f.write(html)

# ===== この方向性の評価 =====

"""
【長所】
1. 非常に柔軟 - コンポーネントはただのデータなので何でも可能
2. 関数合成が自然 - プラグインを組み合わせやすい
3. テストしやすい - レンダリング関数は純粋関数
4. レンダラーを動的に追加可能 - ctx.renderers に登録するだけ
5. Transform による前処理が強力

【短所】
1. 型安全性が低い - Component.props は dict[str, Any]
2. レンダラーの登録が煩雑 - どこで誰が登録するか管理が必要
3. プラグインの実行順序が重要 - 依存関係の管理が難しい
4. デバッグが難しい - どのプラグインがどう変換したか追いづらい

【ユーザー拡張の容易さ】★★★★★
- 関数を書くだけで拡張可能
- フレームワークの内部を理解しなくても使える

【柔軟性】★★★★★
- 何でもできる（Transform, カスタムレンダラー等）
- 予期しない用途にも対応可能
"""
