"""
Yogrt Core Module

最小限のプリミティブを定義:
- Component: データ構造
- render: Component → HTML
- transform: Component → Component
- walk: Component 木の走査
"""

from typing import TypedDict, Any, Callable, cast
from dataclasses import dataclass, field


# ============================================================================
# Type Definitions
# ============================================================================

class Component(TypedDict, total=False):
    """
    コンポーネントの型定義

    Lisp の S式に相当する木構造。
    すべてのスライド要素はこの型で表現される。

    Attributes:
        tag: コンポーネントタイプを識別する文字列
        props: コンポーネント固有のプロパティ
        children: 子コンポーネントのリスト
        key: コンポーネントの一意識別子（オプション）

    Examples:
        >>> text_comp: Component = {
        ...     'tag': 'text',
        ...     'props': {'content': 'Hello'},
        ...     'children': []
        ... }

        >>> page_comp: Component = {
        ...     'tag': 'page',
        ...     'props': {},
        ...     'children': [text_comp]
        ... }
    """
    tag: str
    props: dict[str, Any]
    children: list['Component']
    key: str | None


# Type aliases
Renderer = Callable[[Component, 'Context'], str]
"""Component → HTML の変換関数（レンダラー）"""

Transform = Callable[[Component], Component]
"""Component → Component の変換関数"""

HtmlTransform = Callable[[str], str]
"""HTML → HTML の変換関数"""


# ============================================================================
# Context
# ============================================================================

@dataclass
class Context:
    """
    レンダリングコンテキスト

    レンダリング時の状態とレンダラーを保持する。
    プラグイン間でデータを共有するための store も提供。

    Attributes:
        renderers: タグ名 → レンダラー関数のマッピング
        store: プラグイン間で共有するデータストア
        current_page: 現在のページ番号（1始まり）
        total_pages: 総ページ数
    """
    renderers: dict[str, Renderer] = field(default_factory=dict)
    store: dict[str, Any] = field(default_factory=dict)
    current_page: int = 0
    total_pages: int = 0

    def get_renderer(self, tag: str) -> Renderer:
        """
        タグに対応するレンダラーを取得

        Args:
            tag: コンポーネントのタグ名

        Returns:
            レンダラー関数（見つからない場合はデフォルトレンダラー）
        """
        return self.renderers.get(tag, default_renderer)


# ============================================================================
# Core Functions
# ============================================================================

def render(component: Component, context: Context) -> str:
    """
    Component を HTML 文字列にレンダリング

    これは Lisp の eval に相当する関数。
    Component（データ）を実行して HTML（結果）を得る。

    Args:
        component: レンダリング対象のコンポーネント
        context: レンダリングコンテキスト

    Returns:
        HTML文字列

    Examples:
        >>> comp: Component = {'tag': 'text', 'props': {'content': 'Hello'}, 'children': []}
        >>> ctx = Context(renderers={'text': lambda c, ctx: f"<p>{c['props']['content']}</p>"})
        >>> render(comp, ctx)
        '<p>Hello</p>'
    """
    tag = component['tag']
    renderer = context.get_renderer(tag)
    return renderer(component, context)


def transform(component: Component, transformer: Transform) -> Component:
    """
    Component を別の Component に変換

    これは Lisp のマクロ展開に相当する。
    Component → Component の変換を行う。

    Args:
        component: 変換対象のコンポーネント
        transformer: 変換関数

    Returns:
        変換後のコンポーネント

    Examples:
        >>> def make_bold(comp: Component) -> Component:
        ...     return {'tag': 'bold', 'props': {}, 'children': [comp]}
        >>> comp: Component = {'tag': 'text', 'props': {'content': 'Hi'}, 'children': []}
        >>> transform(comp, make_bold)
        {'tag': 'bold', 'props': {}, 'children': [{'tag': 'text', 'props': {'content': 'Hi'}, 'children': []}]}
    """
    return transformer(component)


def walk(component: Component, f: Callable[[Component], Component]) -> Component:
    """
    Component 木を再帰的に走査し、各ノードに関数を適用

    深さ優先探索で木を走査し、各ノードに変換関数を適用する。
    子要素から先に処理される（post-order traversal）。

    Args:
        component: 走査対象のコンポーネント
        f: 各ノードに適用する関数

    Returns:
        変換後のコンポーネント木

    Examples:
        >>> def add_class(comp: Component) -> Component:
        ...     props = comp.get('props', {})
        ...     props['class'] = 'styled'
        ...     return {**comp, 'props': props}
        >>> root: Component = {
        ...     'tag': 'page',
        ...     'props': {},
        ...     'children': [
        ...         {'tag': 'text', 'props': {}, 'children': []}
        ...     ]
        ... }
        >>> result = walk(root, add_class)
        >>> result['props']['class']
        'styled'
        >>> result['children'][0]['props']['class']
        'styled'
    """
    # まず子要素を再帰的に処理
    children = component.get('children', [])
    new_children = [walk(child, f) for child in children]

    # 子要素を更新したコンポーネントを作成
    new_component = cast(Component, {**component, 'children': new_children})

    # 関数を適用
    return f(new_component)


# ============================================================================
# Default Renderer
# ============================================================================

def default_renderer(component: Component, context: Context) -> str:
    """
    デフォルトレンダラー

    未知のタグに対して使用される。
    子要素をレンダリングし、div タグで囲む。

    Args:
        component: レンダリング対象
        context: レンダリングコンテキスト

    Returns:
        HTML文字列
    """
    tag = component['tag']
    children = component.get('children', [])
    children_html = [render(child, context) for child in children]
    return f'<div class="{tag}">{"".join(children_html)}</div>'


# ============================================================================
# Utility Functions
# ============================================================================

def find_components(
    root: Component,
    predicate: Callable[[Component], bool]
) -> list[Component]:
    """
    条件を満たすコンポーネントを検索

    Component 木を走査し、述語を満たすすべてのコンポーネントを返す。

    Args:
        root: 検索開始ノード
        predicate: 判定関数

    Returns:
        条件を満たすコンポーネントのリスト

    Examples:
        >>> root: Component = {
        ...     'tag': 'page',
        ...     'props': {},
        ...     'children': [
        ...         {'tag': 'header', 'props': {'level': 1}, 'children': []},
        ...         {'tag': 'text', 'props': {}, 'children': []}
        ...     ]
        ... }
        >>> headers = find_components(root, lambda c: c['tag'] == 'header')
        >>> len(headers)
        1
    """
    result: list[Component] = []

    def visit(comp: Component) -> None:
        if predicate(comp):
            result.append(comp)
        for child in comp.get('children', []):
            visit(child)

    visit(root)
    return result


def filter_by_tag(root: Component, tag: str) -> list[Component]:
    """
    特定のタグを持つコンポーネントを検索

    Args:
        root: 検索開始ノード
        tag: 検索するタグ名

    Returns:
        指定されたタグを持つコンポーネントのリスト

    Examples:
        >>> from typing import cast
        >>> root = cast(Component, {
        ...     'tag': 'page',
        ...     'props': {},
        ...     'children': [
        ...         {'tag': 'text', 'props': {'content': 'A'}, 'children': []},
        ...         {'tag': 'text', 'props': {'content': 'B'}, 'children': []}
        ...     ]
        ... })
        >>> texts = filter_by_tag(root, 'text')
        >>> len(texts)
        2
    """
    return find_components(root, lambda c: c['tag'] == tag)


def map_components(
    root: Component,
    f: Callable[[Component], Component]
) -> Component:
    """
    すべてのコンポーネントに関数を適用

    walk のエイリアス。より関数型プログラミング的な名前。

    Args:
        root: 変換対象のルートコンポーネント
        f: 各コンポーネントに適用する関数

    Returns:
        変換後のコンポーネント木
    """
    return walk(root, f)
