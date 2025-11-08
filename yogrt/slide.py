"""
Yogrt Slide Module

Slide クラスとレンダリングパイプラインを定義。
"""

from typing import Callable
from .core import Component, Context, render, walk, Transform, HtmlTransform


# ============================================================================
# Plugin Type
# ============================================================================

Plugin = Callable[['Slide'], 'Slide']
"""Plugin の型定義: Slide → Slide の関数"""


# ============================================================================
# Slide Class
# ============================================================================

class Slide:
    """
    スライド全体を表すコンテナ

    ページのリストとレンダリング設定を保持する。
    Plugin による拡張をサポート。

    Attributes:
        pages: ページのリスト（各ページは Component）
        context: レンダリングコンテキスト
        transforms: 適用する変換関数のリスト
        html_transforms: HTML変換関数のリスト

    Examples:
        >>> from yogrt import create_slide, Page, Header, Text
        >>> slide = create_slide()
        >>> slide.add_page(Page(Header("Title", level=1), Text("Content")))
        >>> slide.export("output.html")
    """

    def __init__(self):
        """Slide を初期化"""
        self.pages: list[Component] = []
        self.context = Context()
        self.transforms: list[Transform] = []
        self.html_transforms: list[HtmlTransform] = []

    def add_page(self, page: Component) -> 'Slide':
        """
        ページを追加

        Args:
            page: 追加するページコンポーネント

        Returns:
            self（メソッドチェーン用）

        Examples:
            >>> slide = Slide()
            >>> slide.add_page({'tag': 'page', 'props': {}, 'children': []})
            <yogrt.slide.Slide object at ...>
        """
        self.pages.append(page)
        return self

    def add_renderer(self, tag: str, renderer: Callable) -> 'Slide':
        """
        カスタムレンダラーを登録

        Args:
            tag: コンポーネントのタグ名
            renderer: レンダラー関数

        Returns:
            self（メソッドチェーン用）

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
        変換関数を追加

        Transform は Component → Component の変換を行う。
        build() 時にすべてのページに適用される。

        Args:
            transformer: 変換関数

        Returns:
            self（メソッドチェーン用）

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
        HTML変換関数を追加

        HTML Transform は HTML → HTML の変換を行う。
        レンダリング後、エクスポート前に適用される。

        Args:
            transformer: HTML変換関数

        Returns:
            self（メソッドチェーン用）

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
        プラグインを適用

        Plugin は Slide → Slide の関数。
        レンダラー、Transform、HTML Transform などを登録する。

        Args:
            plugin: プラグイン関数

        Returns:
            プラグイン適用後の Slide

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
        すべての変換を適用して新しい Slide を返す

        Transform をすべてのページの Component 木に適用し、
        新しい Slide インスタンスを返す（元の Slide は変更しない）。

        Returns:
            変換適用後の新しい Slide インスタンス

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
        # 新しい Slide を作成（immutable パターン）
        new_slide = Slide()
        new_slide.context = self.context
        new_slide.html_transforms = self.html_transforms

        # すべての変換を各ページに適用
        for page in self.pages:
            transformed_page = page
            for transformer in self.transforms:
                transformed_page = walk(transformed_page, transformer)
            new_slide.pages.append(transformed_page)

        return new_slide

    def export(self, path: str) -> None:
        """
        スライドをHTMLファイルとしてエクスポート

        パイプライン:
        1. Build (Transform 適用)
        2. Render (各ページを HTML に変換)
        3. HTML Transform 適用
        4. ファイル書き込み

        Args:
            path: 出力ファイルパス

        Examples:
            >>> slide = Slide()
            >>> slide.add_page({'tag': 'page', 'props': {}, 'children': []})
            <yogrt.slide.Slide object at ...>
            >>> slide.export("output.html")  # doctest: +SKIP
        """
        # 1. ビルド（変換適用）
        built = self.build()

        # 2. コンテキスト設定
        built.context.total_pages = len(built.pages)

        # 3. 各ページをレンダリング
        html_pages = []
        for i, page in enumerate(built.pages, 1):
            built.context.current_page = i
            html_pages.append(render(page, built.context))

        # 4. HTML生成
        html = built._generate_html(html_pages)

        # 5. HTML変換を適用
        for html_transformer in built.html_transforms:
            html = html_transformer(html)

        # 6. ファイル書き込み
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)

    def _generate_html(self, pages: list[str]) -> str:
        """
        HTMLテンプレート生成

        Args:
            pages: レンダリング済みのページHTML

        Returns:
            完全なHTML文書
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
