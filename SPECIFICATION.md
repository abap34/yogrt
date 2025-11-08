# Yogrt: Programmable Slide Framework - Complete Specification

**Version:** 1.0.0
**Date:** 2025-11-08
**Status:** Draft

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Design Philosophy](#design-philosophy)
3. [Core Specification](#core-specification)
4. [Extension Mechanisms](#extension-mechanisms)
5. [Standard Library](#standard-library)
6. [Type System](#type-system)
7. [Rendering Pipeline](#rendering-pipeline)
8. [Implementation Guide](#implementation-guide)
9. [API Reference](#api-reference)
10. [Extension Examples](#extension-examples)
11. [Appendix](#appendix)

---

## 1. Executive Summary

**Yogrt** は、Pythonによるプログラマブルなスライド作成フレームワークです。

### 1.1 設計目標

1. **Programmability**: スライドをPythonプログラムとして記述
2. **Extensibility**: ユーザーが無限に拡張可能
3. **Simplicity**: 最小限のプリミティブで構成
4. **Composability**: 小さな部品を組み合わせて複雑な機能を実現

### 1.2 核となる原理

- **Code as Data**: Component は単なるデータ構造
- **Functions as Primitives**: すべての操作は関数
- **Immutability**: Component は不変
- **Homoiconicity**: Component 自体がPythonのデータ構造

### 1.3 3つのプリミティブ

```python
# 1. Component: データ構造
Component = dict[str, Any]

# 2. Renderer: Component → HTML
Renderer = Callable[[Component, Context], str]

# 3. Transform: Component → Component
Transform = Callable[[Component], Component]
```

これら3つのプリミティブから、すべての機能を構築します。

---

## 2. Design Philosophy

### 2.1 Lisp的な設計原理

本フレームワークは、Lisp言語の以下の哲学を採用します:

#### 2.1.1 最小限のプリミティブ

Lispは `cons`, `car`, `cdr` という3つの基本操作からリスト処理を構築します。
Yogrtは `Component`, `render`, `transform` という3つのプリミティブからスライド作成を構築します。

#### 2.1.2 Homoiconicity（コードとデータの同一性）

LispのS式のように、Component はPythonの標準データ構造（dict）です。
これにより、Component を検査・操作・生成するコードが自然に書けます。

#### 2.1.3 マクロによる拡張

Lispのマクロは `(code) → (code)` の変換を行います。
Yogrtの Transform は `Component → Component` の変換を行い、同じ役割を果たします。

#### 2.1.4 First-class Functions

すべての操作は関数です。レンダラー、トランスフォーム、プラグインはすべて関数として表現されます。

### 2.2 設計上の選択

以下の設計選択を行いました:

| 選択肢 | 採用 | 理由 |
|--------|------|------|
| OOP vs FP | **FP** | 関数合成が自然、副作用を最小化 |
| Mutable vs Immutable | **Immutable** | 予測可能性、並列化、デバッグ容易性 |
| 静的型 vs 動的型 | **動的型（型ヒント付き）** | 柔軟性と型安全性のバランス |
| DSL vs ホスト言語 | **ホスト言語（Python）** | エディタサポート、エコシステム |
| 宣言的 vs 手続き型 | **両方** | Python の if/for が使える |

### 2.3 Non-Goals（意図的に含めないもの）

- ❌ **WYSIWYG エディタ**: テキストベースのみ
- ❌ **リアルタイムプレビュー**: ビルドベース
- ❌ **GUI**: CLI/API のみ
- ❌ **完全な型安全性**: Python の限界内で型ヒント
- ❌ **後方互換性（当面）**: 1.0までは破壊的変更あり

---

## 3. Core Specification

### 3.1 Component（コアデータ構造）

Component は以下の構造を持つ不変なdict型です:

```python
Component = TypedDict('Component', {
    'tag': str,           # コンポーネントの種類
    'props': dict,        # プロパティ（任意のデータ）
    'children': list,     # 子コンポーネント（Component のリスト）
    'key': str | None,    # 一意識別子（オプション）
})
```

#### 3.1.1 正式な定義

```python
from typing import TypedDict, Any

class Component(TypedDict, total=False):
    """
    コンポーネントの型定義

    Attributes:
        tag: コンポーネントタイプを識別する文字列
        props: コンポーネント固有のプロパティ
        children: 子コンポーネントのリスト
        key: コンポーネントの一意識別子（オプション）
    """
    tag: str
    props: dict[str, Any]
    children: list['Component']
    key: str | None
```

#### 3.1.2 不変性

Component は **常に不変** です。変更が必要な場合は、新しい Component を作成します:

```python
# ❌ Bad: Component を変更
component['props']['title'] = "New Title"

# ✅ Good: 新しい Component を作成
new_component = {
    **component,
    'props': {**component['props'], 'title': "New Title"}
}
```

#### 3.1.3 木構造

Component は木構造を形成します:

```
Component
├── tag: "page"
├── props: {}
└── children:
    ├── Component (tag: "header")
    │   └── children: [...]
    └── Component (tag: "text")
        └── children: []
```

### 3.2 Context（レンダリングコンテキスト）

Context は、レンダリング時の状態とレンダラーを保持します:

```python
from dataclasses import dataclass, field

@dataclass
class Context:
    """
    レンダリングコンテキスト

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
        """タグに対応するレンダラーを取得"""
        return self.renderers.get(tag, default_renderer)
```

### 3.3 核となる関数

#### 3.3.1 render: Component → HTML

```python
def render(component: Component, context: Context) -> str:
    """
    Component を HTML 文字列にレンダリング

    Args:
        component: レンダリング対象のコンポーネント
        context: レンダリングコンテキスト

    Returns:
        HTML文字列

    Examples:
        >>> comp = {'tag': 'text', 'props': {'content': 'Hello'}, 'children': []}
        >>> ctx = Context(renderers={'text': render_text})
        >>> render(comp, ctx)
        '<p>Hello</p>'
    """
    tag = component['tag']
    renderer = context.get_renderer(tag)
    return renderer(component, context)
```

#### 3.3.2 transform: Component → Component

```python
def transform(component: Component, transformer: Transform) -> Component:
    """
    Component を別の Component に変換

    Args:
        component: 変換対象のコンポーネント
        transformer: 変換関数

    Returns:
        変換後のコンポーネント

    Examples:
        >>> def make_bold(comp):
        ...     return {'tag': 'bold', 'props': {}, 'children': [comp]}
        >>> comp = {'tag': 'text', 'props': {'content': 'Hi'}, 'children': []}
        >>> transform(comp, make_bold)
        {'tag': 'bold', 'props': {}, 'children': [{'tag': 'text', ...}]}
    """
    return transformer(component)
```

#### 3.3.3 walk: 木の走査

```python
def walk(component: Component, f: Callable[[Component], Component]) -> Component:
    """
    Component 木を再帰的に走査し、各ノードに関数を適用

    Args:
        component: 走査対象のコンポーネント
        f: 各ノードに適用する関数

    Returns:
        変換後のコンポーネント木

    Examples:
        >>> def add_class(comp):
        ...     props = comp.get('props', {})
        ...     props['class'] = 'styled'
        ...     return {**comp, 'props': props}
        >>> walk(root_component, add_class)
    """
    # まず子要素を再帰的に処理
    children = component.get('children', [])
    new_children = [walk(child, f) for child in children]

    # 子要素を更新したコンポーネントを作成
    new_component = {**component, 'children': new_children}

    # 関数を適用
    return f(new_component)
```

### 3.4 Slide（スライドコンテナ）

Slide は、ページのリストとレンダリング設定を保持します:

```python
from typing import List

class Slide:
    """
    スライド全体を表すコンテナ

    Attributes:
        pages: ページのリスト（各ページは Component）
        context: レンダリングコンテキスト
        transforms: 適用する変換関数のリスト
        html_transforms: HTML変換関数のリスト
    """

    def __init__(self):
        self.pages: List[Component] = []
        self.context = Context()
        self.transforms: List[Transform] = []
        self.html_transforms: List[Callable[[str], str]] = []

    def add_page(self, page: Component) -> 'Slide':
        """ページを追加"""
        self.pages.append(page)
        return self

    def add_renderer(self, tag: str, renderer: Renderer) -> 'Slide':
        """カスタムレンダラーを登録"""
        self.context.renderers[tag] = renderer
        return self

    def add_transform(self, transformer: Transform) -> 'Slide':
        """変換関数を追加"""
        self.transforms.append(transformer)
        return self

    def add_html_transform(self, transformer: Callable[[str], str]) -> 'Slide':
        """HTML変換関数を追加"""
        self.html_transforms.append(transformer)
        return self

    def use(self, plugin: 'Plugin') -> 'Slide':
        """プラグインを適用"""
        return plugin(self)

    def build(self) -> 'Slide':
        """
        すべての変換を適用して新しい Slide を返す

        Returns:
            変換適用後の新しい Slide インスタンス
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

        Args:
            path: 出力ファイルパス
        """
        # ビルド（変換適用）
        built = self.build()

        # コンテキスト設定
        built.context.total_pages = len(built.pages)

        # 各ページをレンダリング
        html_pages = []
        for i, page in enumerate(built.pages, 1):
            built.context.current_page = i
            html_pages.append(render(page, built.context))

        # HTML生成
        html = self._generate_html(html_pages)

        # HTML変換を適用
        for html_transformer in built.html_transforms:
            html = html_transformer(html)

        # ファイル書き込み
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)

    def _generate_html(self, pages: List[str]) -> str:
        """HTMLテンプレート生成"""
        css = self.context.store.get('custom_css', '')

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: sans-serif; }}
        .page {{
            width: 100vw;
            height: 100vh;
            padding: 2rem;
            page-break-after: always;
        }}
        {css}
    </style>
</head>
<body>
    {''.join(pages)}
</body>
</html>"""
```

---

## 4. Extension Mechanisms

### 4.1 カスタムレンダラー

最も基本的な拡張は、新しいタグのレンダラーを定義することです。

#### 4.1.1 レンダラーの型

```python
from typing import Protocol

class Renderer(Protocol):
    """レンダラー関数の型"""
    def __call__(self, component: Component, context: Context) -> str:
        """
        Component を HTML にレンダリング

        Args:
            component: レンダリング対象
            context: レンダリングコンテキスト

        Returns:
            HTML文字列
        """
        ...
```

#### 4.1.2 レンダラーの実装例

```python
def render_text(component: Component, context: Context) -> str:
    """テキストコンポーネントのレンダラー"""
    content = component['props']['content']
    return f"<p>{content}</p>"

def render_header(component: Component, context: Context) -> str:
    """ヘッダーコンポーネントのレンダラー"""
    level = component['props']['level']
    text = component['props']['text']
    return f"<h{level}>{text}</h{level}>"

# 登録
slide.add_renderer('text', render_text)
slide.add_renderer('header', render_header)
```

#### 4.1.3 子要素のレンダリング

レンダラー内で子要素をレンダリングする場合:

```python
def render_container(component: Component, context: Context) -> str:
    """コンテナコンポーネント"""
    children_html = [render(child, context) for child in component['children']]
    return f'<div class="container">{"".join(children_html)}</div>'
```

### 4.2 Transform（Component変換）

Transform は `Component → Component` の変換を行います。

#### 4.2.1 Transform の型

```python
Transform = Callable[[Component], Component]
```

#### 4.2.2 Transform の実装例

```python
def add_ids(component: Component) -> Component:
    """すべての header に ID を追加"""
    if component['tag'] == 'header':
        text = component['props']['text']
        id_value = text.lower().replace(' ', '-')
        new_props = {**component['props'], 'id': id_value}
        return {**component, 'props': new_props}
    return component

# 使用
slide.add_transform(add_ids)
```

#### 4.2.3 高度な Transform

複数の Component を1つに統合する Transform:

```python
def merge_consecutive_text(component: Component) -> Component:
    """連続するテキストコンポーネントを統合"""
    if component['tag'] != 'page':
        return component

    children = component['children']
    merged = []
    text_buffer = []

    for child in children:
        if child['tag'] == 'text':
            text_buffer.append(child['props']['content'])
        else:
            if text_buffer:
                merged_text = ' '.join(text_buffer)
                merged.append({
                    'tag': 'text',
                    'props': {'content': merged_text},
                    'children': []
                })
                text_buffer = []
            merged.append(child)

    if text_buffer:
        merged_text = ' '.join(text_buffer)
        merged.append({
            'tag': 'text',
            'props': {'content': merged_text},
            'children': []
        })

    return {**component, 'children': merged}
```

### 4.3 Plugin（高階関数による拡張）

Plugin は `Slide → Slide` の関数です。

#### 4.3.1 Plugin の型

```python
Plugin = Callable[[Slide], Slide]
```

#### 4.3.2 Plugin の実装パターン

```python
def my_plugin(option1: str, option2: int) -> Plugin:
    """
    プラグインファクトリ

    Args:
        option1: プラグインのオプション
        option2: 別のオプション

    Returns:
        Plugin 関数
    """
    def plugin(slide: Slide) -> Slide:
        # 1. レンダラー追加
        slide.add_renderer('my-tag', my_renderer)

        # 2. Transform 追加
        slide.add_transform(my_transform)

        # 3. HTML Transform 追加
        slide.add_html_transform(my_html_transform)

        # 4. Context にデータを保存
        slide.context.store['my_plugin_data'] = {'option1': option1}

        return slide

    return plugin

# 使用
slide.use(my_plugin(option1="value", option2=42))
```

### 4.4 HTML Transform

レンダリング後のHTML全体を変換します。

#### 4.4.1 HTML Transform の型

```python
HtmlTransform = Callable[[str], str]
```

#### 4.4.2 実装例

```python
def add_script(script_url: str) -> HtmlTransform:
    """スクリプトタグを追加"""
    def transformer(html: str) -> str:
        script_tag = f'<script src="{script_url}"></script>'
        return html.replace('</body>', f'{script_tag}</body>')
    return transformer

# 使用
slide.add_html_transform(add_script("https://cdn.example.com/lib.js"))
```

---

## 5. Standard Library

フレームワークが提供する標準コンポーネントとユーティリティ。

### 5.1 コンポーネントファクトリ

#### 5.1.1 基本コンポーネント

```python
def Text(content: str, **props) -> Component:
    """テキストコンポーネント"""
    return {
        'tag': 'text',
        'props': {'content': content, **props},
        'children': []
    }

def Header(text: str, level: int = 1, **props) -> Component:
    """ヘッダーコンポーネント"""
    return {
        'tag': 'header',
        'props': {'text': text, 'level': level, **props},
        'children': []
    }

def Image(src: Any, caption: str | None = None, **props) -> Component:
    """画像コンポーネント"""
    return {
        'tag': 'image',
        'props': {'src': src, 'caption': caption, **props},
        'children': []
    }

def Page(*children: Component, **props) -> Component:
    """ページコンポーネント"""
    return {
        'tag': 'page',
        'props': props,
        'children': list(children)
    }
```

#### 5.1.2 レイアウトコンポーネント

```python
def VStack(*children: Component, gap: str = "1rem", **props) -> Component:
    """垂直スタック"""
    return {
        'tag': 'vstack',
        'props': {'gap': gap, **props},
        'children': list(children)
    }

def HStack(*children: Component, gap: str = "1rem", **props) -> Component:
    """水平スタック"""
    return {
        'tag': 'hstack',
        'props': {'gap': gap, **props},
        'children': list(children)
    }

def TwoColumn(left: Component, right: Component, **props) -> Component:
    """2カラムレイアウト"""
    return {
        'tag': 'two-column',
        'props': props,
        'children': [left, right]
    }
```

### 5.2 標準レンダラー

```python
def default_renderer(component: Component, context: Context) -> str:
    """デフォルトレンダラー（未知のタグ用）"""
    tag = component['tag']
    children_html = [render(child, context) for child in component['children']]
    return f'<div class="{tag}">{"".join(children_html)}</div>'

def render_text(component: Component, context: Context) -> str:
    content = component['props']['content']
    return f"<p>{content}</p>"

def render_header(component: Component, context: Context) -> str:
    level = component['props']['level']
    text = component['props']['text']
    id_attr = f' id="{component["props"]["id"]}"' if 'id' in component['props'] else ''
    return f"<h{level}{id_attr}>{text}</h{level}>"

def render_image(component: Component, context: Context) -> str:
    src = component['props']['src']
    caption = component['props'].get('caption')

    # matplotlib Figure の場合
    if hasattr(src, 'savefig'):
        import io, base64
        buf = io.BytesIO()
        src.savefig(buf, format='png')
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode()
        img_tag = f'<img src="data:image/png;base64,{img_data}"/>'
    else:
        img_tag = f'<img src="{src}"/>'

    if caption:
        return f'<figure>{img_tag}<figcaption>{caption}</figcaption></figure>'
    return img_tag

def render_page(component: Component, context: Context) -> str:
    children_html = [render(child, context) for child in component['children']]
    return f'<div class="page">{"".join(children_html)}</div>'

def render_vstack(component: Component, context: Context) -> str:
    gap = component['props'].get('gap', '1rem')
    children_html = [render(child, context) for child in component['children']]
    return f'<div class="vstack" style="display: flex; flex-direction: column; gap: {gap};">{"".join(children_html)}</div>'

def render_hstack(component: Component, context: Context) -> str:
    gap = component['props'].get('gap', '1rem')
    children_html = [render(child, context) for child in component['children']]
    return f'<div class="hstack" style="display: flex; flex-direction: row; gap: {gap};">{"".join(children_html)}</div>'

def render_two_column(component: Component, context: Context) -> str:
    children = component['children']
    left_html = render(children[0], context) if len(children) > 0 else ''
    right_html = render(children[1], context) if len(children) > 1 else ''
    return f'''
    <div class="two-column" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
        <div class="left">{left_html}</div>
        <div class="right">{right_html}</div>
    </div>
    '''

# 標準レンダラー登録
DEFAULT_RENDERERS = {
    'text': render_text,
    'header': render_header,
    'image': render_image,
    'page': render_page,
    'vstack': render_vstack,
    'hstack': render_hstack,
    'two-column': render_two_column,
}
```

### 5.3 ユーティリティ関数

```python
def find_components(root: Component, predicate: Callable[[Component], bool]) -> List[Component]:
    """
    条件を満たすコンポーネントを検索

    Args:
        root: 検索開始ノード
        predicate: 判定関数

    Returns:
        条件を満たすコンポーネントのリスト
    """
    result = []

    def visit(comp: Component):
        if predicate(comp):
            result.append(comp)
        for child in comp.get('children', []):
            visit(child)

    visit(root)
    return result

def filter_by_tag(root: Component, tag: str) -> List[Component]:
    """特定のタグを持つコンポーネントを検索"""
    return find_components(root, lambda c: c['tag'] == tag)

def map_components(root: Component, f: Callable[[Component], Component]) -> Component:
    """すべてのコンポーネントに関数を適用（walk のエイリアス）"""
    return walk(root, f)
```

---

## 6. Type System

### 6.1 型定義

```python
from typing import TypedDict, Any, Callable, List, Protocol

# Core types
class Component(TypedDict, total=False):
    tag: str
    props: dict[str, Any]
    children: list['Component']
    key: str | None

class Renderer(Protocol):
    def __call__(self, component: Component, context: 'Context') -> str: ...

Transform = Callable[[Component], Component]
HtmlTransform = Callable[[str], str]
Plugin = Callable[['Slide'], 'Slide']

# Context
from dataclasses import dataclass, field

@dataclass
class Context:
    renderers: dict[str, Renderer] = field(default_factory=dict)
    store: dict[str, Any] = field(default_factory=dict)
    current_page: int = 0
    total_pages: int = 0

    def get_renderer(self, tag: str) -> Renderer:
        from .renderers import default_renderer
        return self.renderers.get(tag, default_renderer)
```

### 6.2 型チェック

型ヒントを活用することで、IDEのサポートを受けられます:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import reveal_type

    comp: Component = Text("Hello")
    reveal_type(comp)  # TypedDict

    renderer: Renderer = render_text
    reveal_type(renderer)  # (Component, Context) -> str
```

---

## 7. Rendering Pipeline

### 7.1 パイプライン全体図

```
[ユーザーコード]
    ↓
[Component 構築]
    ↓
[Plugin 適用] (slide.use(...))
    ↓
[Build] (Transform 適用)
    ↓
[Render] (各ページを HTML に)
    ↓
[HTML Transform]
    ↓
[Export] (ファイル書き込み)
```

### 7.2 各フェーズの詳細

#### 7.2.1 Component 構築フェーズ

ユーザーがコンポーネントを作成:

```python
slide = Slide()
slide.add_page(Page(
    Header("Title", level=1),
    Text("Content")
))
```

#### 7.2.2 Plugin 適用フェーズ

プラグインが Slide を変換:

```python
slide.use(my_plugin())
# → slide に renderer/transform/html_transform が追加される
```

#### 7.2.3 Build フェーズ

`slide.build()` または `slide.export()` 内で実行:

```python
built = slide.build()
# → すべての Transform が各ページの Component 木に適用される
```

#### 7.2.4 Render フェーズ

各ページを HTML に変換:

```python
html_pages = []
for page in built.pages:
    html_pages.append(render(page, built.context))
```

#### 7.2.5 HTML Transform フェーズ

HTML 全体を変換:

```python
html = generate_html(html_pages)
for transformer in built.html_transforms:
    html = transformer(html)
```

#### 7.2.6 Export フェーズ

ファイルに書き込み:

```python
with open(path, 'w') as f:
    f.write(html)
```

### 7.3 不変性の保証

各フェーズで新しいオブジェクトを生成することで、不変性を保証します:

```python
# ❌ Bad: 元の slide を変更
def bad_plugin(slide: Slide) -> Slide:
    slide.pages.append(new_page)  # mutation!
    return slide

# ✅ Good: 新しいページリストを作成
def good_plugin(slide: Slide) -> Slide:
    slide.pages = slide.pages + [new_page]  # 新しいリスト
    return slide
```

---

## 8. Implementation Guide

### 8.1 ディレクトリ構造

```
yogrt/
├── yogrt/
│   ├── __init__.py
│   ├── core.py              # Component, Context, render, transform, walk
│   ├── slide.py             # Slide クラス
│   ├── components.py        # Text, Header, Image, Page など
│   ├── renderers.py         # 標準レンダラー
│   ├── utils.py             # find_components, filter_by_tag など
│   └── plugins/
│       ├── __init__.py
│       ├── toc.py           # TOC プラグイン
│       ├── bibtex.py        # BibTeX プラグイン
│       └── mathjax.py       # MathJax プラグイン
├── tests/
│   ├── test_core.py
│   ├── test_slide.py
│   ├── test_components.py
│   └── test_plugins/
├── examples/
│   ├── basic.py
│   ├── bibtex_example.py
│   └── custom_plugin.py
├── docs/
│   ├── index.md
│   ├── tutorial.md
│   └── api.md
├── pyproject.toml
├── README.md
└── SPECIFICATION.md (this file)
```

### 8.2 モジュール分割

#### 8.2.1 `core.py`

最小限のプリミティブのみ:

```python
# yogrt/core.py
from typing import TypedDict, Any, Callable, List

# 型定義
class Component(TypedDict, total=False):
    tag: str
    props: dict[str, Any]
    children: list['Component']
    key: str | None

# 核となる関数
def render(component: Component, context: 'Context') -> str:
    """Component を HTML にレンダリング"""
    ...

def transform(component: Component, transformer: Callable) -> Component:
    """Component を変換"""
    ...

def walk(component: Component, f: Callable) -> Component:
    """Component 木を走査"""
    ...
```

#### 8.2.2 `slide.py`

Slide クラスとパイプライン:

```python
# yogrt/slide.py
from .core import Component, Context, render, walk

class Slide:
    def __init__(self): ...
    def add_page(self, page: Component) -> 'Slide': ...
    def use(self, plugin) -> 'Slide': ...
    def build(self) -> 'Slide': ...
    def export(self, path: str) -> None: ...
```

#### 8.2.3 `components.py`

コンポーネントファクトリ:

```python
# yogrt/components.py
from .core import Component

def Text(content: str, **props) -> Component: ...
def Header(text: str, level: int = 1, **props) -> Component: ...
# ...
```

#### 8.2.4 `renderers.py`

標準レンダラー:

```python
# yogrt/renderers.py
from .core import Component, Context

def render_text(component: Component, context: Context) -> str: ...
def render_header(component: Component, context: Context) -> str: ...
# ...

DEFAULT_RENDERERS = {
    'text': render_text,
    'header': render_header,
    # ...
}
```

### 8.3 初期化

```python
# yogrt/__init__.py
from .core import Component, render, transform, walk
from .slide import Slide, Context
from .components import Text, Header, Image, Page, VStack, HStack, TwoColumn
from .renderers import DEFAULT_RENDERERS

# Slide のデフォルトレンダラーを設定
def create_slide() -> Slide:
    slide = Slide()
    for tag, renderer in DEFAULT_RENDERERS.items():
        slide.add_renderer(tag, renderer)
    return slide

__all__ = [
    'Component', 'render', 'transform', 'walk',
    'Slide', 'Context', 'create_slide',
    'Text', 'Header', 'Image', 'Page',
    'VStack', 'HStack', 'TwoColumn',
]
```

### 8.4 テスト戦略

#### 8.4.1 ユニットテスト

各関数を独立してテスト:

```python
# tests/test_core.py
from yogrt.core import Component, render, walk, Context
from yogrt.renderers import render_text

def test_render_text():
    comp = {'tag': 'text', 'props': {'content': 'Hello'}, 'children': []}
    ctx = Context(renderers={'text': render_text})
    result = render(comp, ctx)
    assert result == '<p>Hello</p>'

def test_walk():
    comp = {
        'tag': 'page',
        'props': {},
        'children': [
            {'tag': 'text', 'props': {'content': 'Hi'}, 'children': []}
        ]
    }

    def add_class(c):
        props = c.get('props', {})
        props['class'] = 'styled'
        return {**c, 'props': props}

    result = walk(comp, add_class)
    assert result['props']['class'] == 'styled'
    assert result['children'][0]['props']['class'] == 'styled'
```

#### 8.4.2 統合テスト

パイプライン全体をテスト:

```python
# tests/test_slide.py
from yogrt import create_slide, Text, Header, Page

def test_slide_export(tmp_path):
    slide = create_slide()
    slide.add_page(Page(
        Header("Title", level=1),
        Text("Content")
    ))

    output = tmp_path / "test.html"
    slide.export(str(output))

    html = output.read_text()
    assert '<h1>Title</h1>' in html
    assert '<p>Content</p>' in html
```

#### 8.4.3 プラグインテスト

```python
# tests/test_plugins/test_toc.py
from yogrt import create_slide, Page, Header
from yogrt.plugins.toc import toc_plugin

def test_toc_plugin():
    slide = create_slide()
    slide.add_page(Page(Header("Intro", level=1)))
    slide.add_page(Page(Header("Methods", level=1)))

    slide.use(toc_plugin())
    built = slide.build()

    # TOC ページが挿入されている
    assert len(built.pages) == 3  # 元の2ページ + TOC
```

### 8.5 パッケージング

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "yogrt"
version = "0.1.0"
description = "Programmable slide framework with Lisp-like philosophy"
authors = [{name = "Your Name", email = "your.email@example.com"}]
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "mypy>=1.0",
    "black>=23.0",
    "ruff>=0.1.0",
]

plugins = [
    "bibtexparser>=1.4.0",  # for bibtex plugin
    "matplotlib>=3.0",       # for image support
]

[tool.setuptools.packages.find]
where = ["."]
include = ["yogrt*"]

[tool.mypy]
python_version = "3.10"
strict = true

[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
```

---

## 9. API Reference

### 9.1 Core API

#### `Component`

```python
Component = TypedDict('Component', {
    'tag': str,
    'props': dict[str, Any],
    'children': list['Component'],
    'key': str | None,
})
```

#### `render(component, context) -> str`

Component を HTML にレンダリング。

**Parameters:**
- `component: Component` - レンダリング対象
- `context: Context` - レンダリングコンテキスト

**Returns:**
- `str` - HTML文字列

#### `transform(component, transformer) -> Component`

Component を変換。

**Parameters:**
- `component: Component` - 変換対象
- `transformer: Callable[[Component], Component]` - 変換関数

**Returns:**
- `Component` - 変換後のコンポーネント

#### `walk(component, f) -> Component`

Component 木を再帰的に走査し、各ノードに関数を適用。

**Parameters:**
- `component: Component` - 走査対象
- `f: Callable[[Component], Component]` - 各ノードに適用する関数

**Returns:**
- `Component` - 変換後のコンポーネント木

### 9.2 Slide API

#### `class Slide`

スライド全体を表すコンテナ。

**Methods:**

##### `add_page(page: Component) -> Slide`

ページを追加。

##### `add_renderer(tag: str, renderer: Renderer) -> Slide`

カスタムレンダラーを登録。

##### `add_transform(transformer: Transform) -> Slide`

変換関数を追加。

##### `add_html_transform(transformer: HtmlTransform) -> Slide`

HTML変換関数を追加。

##### `use(plugin: Plugin) -> Slide`

プラグインを適用。

##### `build() -> Slide`

すべての変換を適用して新しい Slide を返す。

##### `export(path: str) -> None`

スライドをHTMLファイルとしてエクスポート。

### 9.3 Component Factories

#### `Text(content: str, **props) -> Component`

テキストコンポーネントを作成。

#### `Header(text: str, level: int = 1, **props) -> Component`

ヘッダーコンポーネントを作成。

#### `Image(src: Any, caption: str | None = None, **props) -> Component`

画像コンポーネントを作成。

#### `Page(*children: Component, **props) -> Component`

ページコンポーネントを作成。

#### `VStack(*children: Component, gap: str = "1rem", **props) -> Component`

垂直スタックコンポーネントを作成。

#### `HStack(*children: Component, gap: str = "1rem", **props) -> Component`

水平スタックコンポーネントを作成。

#### `TwoColumn(left: Component, right: Component, **props) -> Component`

2カラムレイアウトコンポーネントを作成。

### 9.4 Utilities

#### `find_components(root: Component, predicate: Callable) -> List[Component]`

条件を満たすコンポーネントを検索。

#### `filter_by_tag(root: Component, tag: str) -> List[Component]`

特定のタグを持つコンポーネントを検索。

---

## 10. Extension Examples

### 10.1 BibTeX Plugin

完全なBibTeX統合プラグイン。

```python
# yogrt/plugins/bibtex.py
from typing import List
import bibtexparser
from ..core import Component, Context, walk
from ..slide import Slide, Plugin

class BibTeXManager:
    """BibTeX処理マネージャー"""
    def __init__(self, bibfile: str):
        with open(bibfile) as f:
            self.bib_database = bibtexparser.load(f)
        self.citations: List[str] = []

    def cite(self, key: str) -> int:
        if key not in self.citations:
            self.citations.append(key)
        return self.citations.index(key) + 1

    def format_entry(self, key: str, style: str = "apa") -> str:
        entries = [e for e in self.bib_database.entries if e['ID'] == key]
        if not entries:
            return f"[{key} not found]"

        entry = entries[0]
        author = entry.get('author', 'Unknown')
        year = entry.get('year', 'n.d.')
        title = entry.get('title', 'Untitled')
        journal = entry.get('journal', '')

        if style == "apa":
            if journal:
                return f"{author} ({year}). {title}. <i>{journal}</i>."
            else:
                return f"{author} ({year}). {title}."
        else:
            return str(entry)

def bibtex_plugin(bibfile: str, style: str = "apa") -> Plugin:
    """
    BibTeX引用管理プラグイン

    Args:
        bibfile: .bib ファイルのパス
        style: 引用スタイル ("apa", "ieee" など)

    Returns:
        Plugin 関数

    Usage:
        slide.use(bibtex_plugin("refs.bib", style="apa"))

        slide.add_page(Page(
            Text("According to "),
            Cite("key2024"),
            Text(" we can see...")
        ))

        slide.add_page(Page(Bibliography()))
    """
    manager = BibTeXManager(bibfile)

    def plugin(slide: Slide) -> Slide:
        # 1. 引用収集 Transform
        def collect_citations(comp: Component) -> Component:
            if comp['tag'] == 'cite':
                manager.cite(comp['props']['key'])
            return comp

        slide.add_transform(collect_citations)

        # 2. Cite レンダラー
        def render_cite(comp: Component, ctx: Context) -> str:
            key = comp['props']['key']
            num = manager.cite(key)
            return f'<sup><a href="#ref-{num}">[{num}]</a></sup>'

        slide.add_renderer('cite', render_cite)

        # 3. Bibliography レンダラー
        def render_bibliography(comp: Component, ctx: Context) -> str:
            html = '<ol class="bibliography">'
            for i, key in enumerate(manager.citations, 1):
                formatted = manager.format_entry(key, style)
                html += f'<li id="ref-{i}">{formatted}</li>'
            html += '</ol>'
            return html

        slide.add_renderer('bibliography', render_bibliography)

        return slide

    return plugin

# Component factories
def Cite(key: str) -> Component:
    """引用コンポーネント"""
    return {'tag': 'cite', 'props': {'key': key}, 'children': []}

def Bibliography() -> Component:
    """参考文献リスト"""
    return {'tag': 'bibliography', 'props': {}, 'children': []}
```

### 10.2 TOC (Table of Contents) Plugin

目次自動生成プラグイン。

```python
# yogrt/plugins/toc.py
from ..core import Component, Context, walk
from ..slide import Slide, Plugin
from ..components import Page, Header

def toc_plugin(max_level: int = 2, insert_at: int = 1) -> Plugin:
    """
    目次自動生成プラグイン

    Args:
        max_level: 目次に含める見出しの最大レベル
        insert_at: 目次ページを挿入する位置（0始まり）

    Returns:
        Plugin 関数
    """
    def plugin(slide: Slide) -> Slide:
        # 見出しを収集
        toc_items = []

        for page_num, page in enumerate(slide.pages, 1):
            def collect_headers(comp: Component) -> Component:
                if comp['tag'] == 'header':
                    level = comp['props'].get('level', 1)
                    if level <= max_level:
                        toc_items.append({
                            'level': level,
                            'text': comp['props']['text'],
                            'page': page_num,
                            'id': comp['props'].get('id', '')
                        })
                return comp

            walk(page, collect_headers)

        # TOC ページ作成
        toc_html = '<ul class="toc">'
        for item in toc_items:
            indent = '  ' * (item['level'] - 1)
            link = f'#page-{item["page"]}'
            toc_html += f'{indent}<li><a href="{link}">{item["text"]}</a></li>'
        toc_html += '</ul>'

        toc_page = Page(
            Header("Table of Contents", level=1),
            {'tag': 'raw-html', 'props': {'html': toc_html}, 'children': []}
        )

        # ページ挿入
        slide.pages.insert(insert_at, toc_page)

        # raw-html レンダラー登録
        slide.add_renderer('raw-html', lambda c, ctx: c['props']['html'])

        return slide

    return plugin
```

### 10.3 MathJax Plugin

LaTeX数式レンダリングプラグイン。

```python
# yogrt/plugins/mathjax.py
from ..core import Component, Context
from ..slide import Slide, Plugin

def mathjax_plugin(config: dict = None) -> Plugin:
    """
    MathJax数式レンダリングプラグイン

    Args:
        config: MathJax設定（省略可）

    Returns:
        Plugin 関数

    Usage:
        slide.use(mathjax_plugin())

        slide.add_page(Page(
            Math(r"E = mc^2", display=True)
        ))
    """
    default_config = {
        'tex': {
            'inlineMath': [['$', '$']],
            'displayMath': [['$$', '$$']]
        }
    }
    config = config or default_config

    def plugin(slide: Slide) -> Slide:
        # Math レンダラー
        def render_math(comp: Component, ctx: Context) -> str:
            latex = comp['props']['latex']
            display = comp['props'].get('display', False)

            if display:
                return f'$$\n{latex}\n$$'
            else:
                return f'${latex}$'

        slide.add_renderer('math', render_math)

        # MathJax スクリプト追加
        import json
        config_json = json.dumps(config)

        def add_mathjax(html: str) -> str:
            mathjax_setup = f'''
            <script>
            MathJax = {config_json};
            </script>
            <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            '''
            return html.replace('</head>', f'{mathjax_setup}</head>')

        slide.add_html_transform(add_mathjax)

        return slide

    return plugin

def Math(latex: str, display: bool = False) -> Component:
    """数式コンポーネント"""
    return {'tag': 'math', 'props': {'latex': latex, 'display': display}, 'children': []}
```

### 10.4 Code Execution Plugin

コード実行プラグイン。

```python
# yogrt/plugins/code_exec.py
from ..core import Component, Context
from ..slide import Slide, Plugin

def code_execution_plugin() -> Plugin:
    """
    コード実行プラグイン

    Usage:
        slide.use(code_execution_plugin())

        slide.add_page(Page(
            CodeWithOutput('''
print("Hello!")
result = 1 + 1
print(f"Result: {result}")
            ''', lang="python", auto_execute=True)
        ))
    """
    def plugin(slide: Slide) -> Slide:
        def render_code_with_output(comp: Component, ctx: Context) -> str:
            code = comp['props']['code']
            lang = comp['props'].get('lang', 'python')
            auto_execute = comp['props'].get('auto_execute', True)

            # コード部分
            code_html = f'<pre><code class="language-{lang}">{code}</code></pre>'

            # 実行結果
            output = ""
            if auto_execute and lang == "python":
                import io
                import sys
                from contextlib import redirect_stdout

                output_buffer = io.StringIO()
                with redirect_stdout(output_buffer):
                    try:
                        exec(code)
                        output = output_buffer.getvalue()
                    except Exception as e:
                        output = f"Error: {e}"

            output_html = f'<pre class="output">{output}</pre>' if output else ''

            return f'''
            <div class="code-with-output" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="code-section">{code_html}</div>
                <div class="output-section">{output_html}</div>
            </div>
            '''

        slide.add_renderer('code-with-output', render_code_with_output)

        return slide

    return plugin

def CodeWithOutput(code: str, lang: str = "python", auto_execute: bool = True) -> Component:
    """コード実行コンポーネント"""
    return {
        'tag': 'code-with-output',
        'props': {'code': code, 'lang': lang, 'auto_execute': auto_execute},
        'children': []
    }
```

---

## 11. Appendix

### 11.1 完全な使用例

```python
from yogrt import create_slide, Page, Header, Text, Image, TwoColumn
from yogrt.plugins.bibtex import bibtex_plugin, Cite, Bibliography
from yogrt.plugins.mathjax import mathjax_plugin, Math
from yogrt.plugins.toc import toc_plugin
from yogrt.plugins.code_exec import code_execution_plugin, CodeWithOutput

from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# スライド作成
slide = create_slide()

# プラグイン適用
slide.use(bibtex_plugin("refs.bib", style="apa"))
slide.use(mathjax_plugin())
slide.use(toc_plugin(max_level=2))
slide.use(code_execution_plugin())

# タイトルページ
slide.add_page(Page(
    Header("Programmable Slides with Yogrt", level=1),
    Text(f"Date: {datetime.now().strftime('%Y-%m-%d')}"),
    Text("Author: Your Name")
))

# (TOC はここに自動挿入される)

# イントロ
slide.add_page(Page(
    Header("Introduction", level=1),
    Text("This is a programmable slide framework."),
    Math(r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}", display=True)
))

# コード例
slide.add_page(Page(
    Header("Code Example", level=1),
    CodeWithOutput("""
import numpy as np
data = np.random.randn(100)
print(f"Mean: {data.mean():.2f}")
print(f"Std: {data.std():.2f}")
""", auto_execute=True)
))

# データ可視化
slide.add_page(Page(
    Header("Data Visualization", level=1),
    TwoColumn(
        Text("We analyze the data and plot the results."),
        Image(create_plot(), caption="Sample plot")
    )
))

# 引用
slide.add_page(Page(
    Header("Related Work", level=1),
    Text("According to Smith et al. "),
    Cite("smith2024"),
    Text(" the approach is effective.")
))

# 参考文献
slide.add_page(Page(
    Header("References", level=1),
    Bibliography()
))

# エクスポート
slide.export("presentation.html")

def create_plot():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    ax.set_title("Sample Plot")
    return fig
```

### 11.2 カスタムコンポーネントの作成例

```python
# ユーザー定義コンポーネント
def Alert(message: str, level: str = "info") -> Component:
    """アラートコンポーネント"""
    return {
        'tag': 'alert',
        'props': {'message': message, 'level': level},
        'children': []
    }

# レンダラー
def render_alert(comp: Component, ctx: Context) -> str:
    message = comp['props']['message']
    level = comp['props']['level']

    colors = {
        'info': '#3498db',
        'warning': '#f39c12',
        'error': '#e74c3c',
        'success': '#2ecc71'
    }
    color = colors.get(level, '#95a5a6')

    return f'''
    <div class="alert alert-{level}" style="
        background: {color};
        color: white;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    ">
        {message}
    </div>
    '''

# 登録
slide.add_renderer('alert', render_alert)

# 使用
slide.add_page(Page(
    Alert("This is important!", level="warning")
))
```

### 11.3 Transform の高度な例

```python
# すべての画像を最適化する Transform
def optimize_images(component: Component) -> Component:
    """画像を最適化（リサイズ、圧縮など）"""
    if component['tag'] == 'image':
        src = component['props']['src']

        # PIL で最適化
        if isinstance(src, str):  # ファイルパス
            from PIL import Image
            img = Image.open(src)

            # リサイズ
            max_size = (1920, 1080)
            img.thumbnail(max_size, Image.LANCZOS)

            # 最適化して保存
            optimized_path = f"optimized_{src}"
            img.save(optimized_path, optimize=True, quality=85)

            # 新しいコンポーネント返す
            return {
                **component,
                'props': {**component['props'], 'src': optimized_path}
            }

    return component

slide.add_transform(optimize_images)
```

### 11.4 設計の形式的性質

#### 11.4.1 Component の代数的性質

Component は以下の性質を持ちます:

**木構造（Tree）:**
```
Component ::= Node(tag, props, [Component])
```

**Functor則:**
```python
# Identity
walk(comp, lambda x: x) == comp

# Composition
walk(walk(comp, f), g) == walk(comp, lambda x: g(f(x)))
```

#### 11.4.2 レンダリングの合成性

理想的には、レンダリングは合成的であるべきです:

```
render(Node(tag, props, [c1, c2, ...]), ctx) =
    combine(render(c1, ctx), render(c2, ctx), ...)
```

ただし、Context 依存のため、完全には合成的ではありません。

#### 11.4.3 Transform の性質

Transform は Component → Component の関数です:

```python
type Transform = Component → Component
```

Transform の合成:
```python
compose(f, g) = lambda x: f(g(x))
```

恒等Transform:
```python
identity = lambda x: x
```

---

## 12. Migration from Marp

Marpからの移行ガイド。

### 12.1 基本的な対応

| Marp | Yogrt |
|------|-------|
| `# Title` | `Header("Title", level=1)` |
| `Regular text` | `Text("Regular text")` |
| `![](image.png)` | `Image("image.png")` |
| `---` (new slide) | `slide.add_page(Page(...))` |

### 12.2 移行例

**Marp:**
```markdown
---
marp: true
---

# My Presentation

---

## Introduction

This is the introduction.

---

## Methods

- Step 1
- Step 2
```

**Yogrt:**
```python
from yogrt import create_slide, Page, Header, Text

slide = create_slide()

slide.add_page(Page(
    Header("My Presentation", level=1)
))

slide.add_page(Page(
    Header("Introduction", level=2),
    Text("This is the introduction.")
))

slide.add_page(Page(
    Header("Methods", level=2),
    Text("• Step 1"),
    Text("• Step 2")
))

slide.export("presentation.html")
```

---

## 13. FAQ

### Q1: なぜ dict を使うのか？dataclass ではダメなのか？

**A:** dict は Python の組み込み型で、最も基本的なデータ構造です。これにより:
- JSON へのシリアライズが容易
- パターンマッチングが使いやすい
- 動的な属性追加が可能
- Lisp の S式に近い

dataclass も選択肢ですが、柔軟性とシンプルさを優先しました。

### Q2: 型安全性が低いのでは？

**A:** TypedDict と型ヒントにより、ある程度の型安全性は確保されます。
完全な型安全性が必要な場合は、別のアプローチ（Rust, Haskell等）を検討してください。

### Q3: パフォーマンスは？

**A:** 現状ではパフォーマンスよりも、シンプルさと拡張性を優先しています。
最適化が必要な場合は、レンダラーをCythonで書く、キャッシュを追加するなどの方法があります。

### Q4: React/Vue のような仮想DOMは使わないのか？

**A:** 現在は静的サイト生成のみをサポートしています。
将来的にインタラクティブなスライドをサポートする場合、検討する可能性があります。

---

## 14. Versioning and Stability

- **v0.x**: 実験的、破壊的変更あり
- **v1.0**: API安定化、セマンティックバージョニング採用
- **v2.0+**: メジャーバージョンアップ時のみ破壊的変更

---

## 15. License

MIT License

---

**End of Specification v1.0.0**
