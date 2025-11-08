"""
Yogrt Standard Components

標準コンポーネントのファクトリ関数を定義。
"""

from typing import Any
from .core import Component


# ============================================================================
# Basic Components
# ============================================================================

def Text(content: str, **props) -> Component:
    """
    テキストコンポーネント

    Args:
        content: 表示するテキスト
        **props: 追加プロパティ

    Returns:
        テキストコンポーネント

    Examples:
        >>> text = Text("Hello, world!")
        >>> text['tag']
        'text'
        >>> text['props']['content']
        'Hello, world!'
    """
    return {
        'tag': 'text',
        'props': {'content': content, **props},
        'children': []
    }


def Header(text: str, level: int = 1, **props) -> Component:
    """
    ヘッダーコンポーネント

    Args:
        text: ヘッダーテキスト
        level: 見出しレベル (1-6)
        **props: 追加プロパティ（id, class など）

    Returns:
        ヘッダーコンポーネント

    Examples:
        >>> header = Header("Introduction", level=2, id="intro")
        >>> header['tag']
        'header'
        >>> header['props']['level']
        2
        >>> header['props']['id']
        'intro'
    """
    return {
        'tag': 'header',
        'props': {'text': text, 'level': level, **props},
        'children': []
    }


def Image(src: Any, caption: str | None = None, **props) -> Component:
    """
    画像コンポーネント

    Args:
        src: 画像ソース（ファイルパス、URL、matplotlib Figure など）
        caption: キャプション（オプション）
        **props: 追加プロパティ

    Returns:
        画像コンポーネント

    Examples:
        >>> img = Image("photo.jpg", caption="A beautiful sunset")
        >>> img['tag']
        'image'
        >>> img['props']['caption']
        'A beautiful sunset'
    """
    return {
        'tag': 'image',
        'props': {'src': src, 'caption': caption, **props},
        'children': []
    }


def Code(code: str, lang: str = "python", **props) -> Component:
    """
    コードブロックコンポーネント

    Args:
        code: コード文字列
        lang: プログラミング言語
        **props: 追加プロパティ

    Returns:
        コードコンポーネント

    Examples:
        >>> code = Code("print('Hello')", lang="python")
        >>> code['tag']
        'code'
        >>> code['props']['lang']
        'python'
    """
    return {
        'tag': 'code',
        'props': {'code': code, 'lang': lang, **props},
        'children': []
    }


def Link(url: str, text: str, **props) -> Component:
    """
    リンクコンポーネント

    Args:
        url: リンク先URL
        text: 表示テキスト
        **props: 追加プロパティ

    Returns:
        リンクコンポーネント

    Examples:
        >>> link = Link("https://example.com", "Visit Example")
        >>> link['props']['url']
        'https://example.com'
    """
    return {
        'tag': 'link',
        'props': {'url': url, 'text': text, **props},
        'children': []
    }


# ============================================================================
# Container Components
# ============================================================================

def Page(*children: Component, **props) -> Component:
    """
    ページコンポーネント

    スライドの1ページを表す。

    Args:
        *children: 子コンポーネント
        **props: 追加プロパティ

    Returns:
        ページコンポーネント

    Examples:
        >>> page = Page(
        ...     Header("Title", level=1),
        ...     Text("Content")
        ... )
        >>> page['tag']
        'page'
        >>> len(page['children'])
        2
    """
    return {
        'tag': 'page',
        'props': props,
        'children': list(children)
    }


def VStack(*children: Component, gap: str = "1rem", **props) -> Component:
    """
    垂直スタックレイアウト

    子要素を縦に並べる。

    Args:
        *children: 子コンポーネント
        gap: 子要素間の間隔
        **props: 追加プロパティ

    Returns:
        VStack コンポーネント

    Examples:
        >>> stack = VStack(
        ...     Text("First"),
        ...     Text("Second"),
        ...     gap="2rem"
        ... )
        >>> stack['tag']
        'vstack'
        >>> stack['props']['gap']
        '2rem'
    """
    return {
        'tag': 'vstack',
        'props': {'gap': gap, **props},
        'children': list(children)
    }


def HStack(*children: Component, gap: str = "1rem", **props) -> Component:
    """
    水平スタックレイアウト

    子要素を横に並べる。

    Args:
        *children: 子コンポーネント
        gap: 子要素間の間隔
        **props: 追加プロパティ

    Returns:
        HStack コンポーネント

    Examples:
        >>> stack = HStack(
        ...     Text("Left"),
        ...     Text("Right"),
        ...     gap="1rem"
        ... )
        >>> stack['tag']
        'hstack'
    """
    return {
        'tag': 'hstack',
        'props': {'gap': gap, **props},
        'children': list(children)
    }


def TwoColumn(left: Component, right: Component, **props) -> Component:
    """
    2カラムレイアウト

    左右に要素を配置。

    Args:
        left: 左側のコンポーネント
        right: 右側のコンポーネント
        **props: 追加プロパティ

    Returns:
        TwoColumn コンポーネント

    Examples:
        >>> layout = TwoColumn(
        ...     Text("Left content"),
        ...     Text("Right content")
        ... )
        >>> layout['tag']
        'two-column'
        >>> len(layout['children'])
        2
    """
    return {
        'tag': 'two-column',
        'props': props,
        'children': [left, right]
    }


def Grid(*children: Component, columns: int = 2, gap: str = "1rem", **props) -> Component:
    """
    グリッドレイアウト

    子要素をグリッド状に配置。

    Args:
        *children: 子コンポーネント
        columns: カラム数
        gap: グリッドの間隔
        **props: 追加プロパティ

    Returns:
        Grid コンポーネント

    Examples:
        >>> grid = Grid(
        ...     Text("1"), Text("2"), Text("3"), Text("4"),
        ...     columns=2
        ... )
        >>> grid['props']['columns']
        2
    """
    return {
        'tag': 'grid',
        'props': {'columns': columns, 'gap': gap, **props},
        'children': list(children)
    }


def Container(*children: Component, **props) -> Component:
    """
    汎用コンテナ

    子要素をグループ化する。

    Args:
        *children: 子コンポーネント
        **props: 追加プロパティ

    Returns:
        Container コンポーネント

    Examples:
        >>> container = Container(
        ...     Text("Item 1"),
        ...     Text("Item 2"),
        ...     class_name="my-container"
        ... )
        >>> container['tag']
        'container'
    """
    return {
        'tag': 'container',
        'props': props,
        'children': list(children)
    }


# ============================================================================
# List Components
# ============================================================================

def List(*items: str | Component, ordered: bool = False, **props) -> Component:
    """
    リストコンポーネント

    Args:
        *items: リストアイテム（文字列または Component）
        ordered: 順序付きリストかどうか
        **props: 追加プロパティ

    Returns:
        List コンポーネント

    Examples:
        >>> lst = List("Item 1", "Item 2", "Item 3")
        >>> lst['tag']
        'list'
        >>> len(lst['children'])
        3

        >>> lst_ordered = List("First", "Second", ordered=True)
        >>> lst_ordered['props']['ordered']
        True
    """
    # 文字列を Text コンポーネントに変換
    children = []
    for item in items:
        if isinstance(item, str):
            children.append(Text(item))
        else:
            children.append(item)

    return {
        'tag': 'list',
        'props': {'ordered': ordered, **props},
        'children': children
    }


# ============================================================================
# Special Components
# ============================================================================

def RawHtml(html: str, **props) -> Component:
    """
    生HTMLコンポーネント

    直接HTMLを挿入する。

    Args:
        html: HTML文字列
        **props: 追加プロパティ

    Returns:
        RawHtml コンポーネント

    Examples:
        >>> raw = RawHtml("<div class='custom'>Custom HTML</div>")
        >>> raw['tag']
        'raw-html'
        >>> raw['props']['html']
        '<div class=\'custom\'>Custom HTML</div>'
    """
    return {
        'tag': 'raw-html',
        'props': {'html': html, **props},
        'children': []
    }


def Spacer(height: str = "1rem", **props) -> Component:
    """
    スペーサーコンポーネント

    空白スペースを挿入。

    Args:
        height: スペースの高さ
        **props: 追加プロパティ

    Returns:
        Spacer コンポーネント

    Examples:
        >>> spacer = Spacer(height="2rem")
        >>> spacer['props']['height']
        '2rem'
    """
    return {
        'tag': 'spacer',
        'props': {'height': height, **props},
        'children': []
    }


def Divider(**props) -> Component:
    """
    区切り線コンポーネント

    Args:
        **props: 追加プロパティ

    Returns:
        Divider コンポーネント

    Examples:
        >>> divider = Divider()
        >>> divider['tag']
        'divider'
    """
    return {
        'tag': 'divider',
        'props': props,
        'children': []
    }
