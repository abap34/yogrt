# ユーザーによるレンダリング拡張の比較

ユーザーが独自のレンダリングロジックを実装する場合、各設計でどう書けるかを比較します。

## 拡張例のリスト

1. **BibTeX統合** - 引用管理とレンダリング
2. **Mermaid図** - テキストから図を生成
3. **LaTeX数式** - MathJax/KaTeXを使った数式レンダリング
4. **インクリメンタル表示** - 箇条書きを1つずつ表示
5. **インタラクティブ要素** - クリックで展開するコンポーネント
6. **D3.js可視化** - カスタムチャート
7. **スライドトランジション** - ページ間のアニメーション効果
8. **発表者ノート** - 表示/非表示を切り替え

---

## 1. BibTeX統合（完全なユーザー実装）

### 方向性A: Protocol

ユーザーはPreprocessPluginとComponentを実装：

```python
from typing import Dict, List
import bibtexparser  # 外部ライブラリを使う

class BibTeXManager:
    """BibTeX処理の中核ロジック - ユーザー実装"""
    def __init__(self, bibfile: str):
        with open(bibfile) as f:
            self.bib_database = bibtexparser.load(f)
        self.citations: List[str] = []

    def cite(self, key: str) -> int:
        """引用を追加し、引用番号を返す"""
        if key not in self.citations:
            self.citations.append(key)
        return self.citations.index(key) + 1

    def format_entry(self, key: str, style: str = "apa") -> str:
        """エントリを指定スタイルでフォーマット"""
        entries = [e for e in self.bib_database.entries if e['ID'] == key]
        if not entries:
            return f"[{key} not found]"

        entry = entries[0]

        if style == "apa":
            author = entry.get('author', 'Unknown')
            year = entry.get('year', 'n.d.')
            title = entry.get('title', 'Untitled')
            journal = entry.get('journal', '')

            if journal:
                return f"{author} ({year}). {title}. <i>{journal}</i>."
            else:
                return f"{author} ({year}). {title}."
        elif style == "ieee":
            # IEEE スタイル
            author = entry.get('author', 'Unknown')
            title = entry.get('title', 'Untitled')
            journal = entry.get('journal', '')
            year = entry.get('year', 'n.d.')
            return f'{author}, "{title}", <i>{journal}</i>, {year}.'
        else:
            # カスタムスタイル
            return str(entry)

# ユーザー定義のプラグイン
class UserBibTeXPlugin:
    """BibTeXプラグイン - 完全にユーザーが実装"""
    def __init__(self, bibfile: str, style: str = "apa"):
        self.manager = BibTeXManager(bibfile)
        self.style = style

    def preprocess(self, slide: Slide) -> None:
        """前処理（必要に応じて）"""
        pass

# ユーザー定義のコンポーネント
@dataclass
class Cite(Component):
    """引用 - ユーザーが完全に実装"""
    key: str

    def analyze(self, ctx: RenderContext) -> None:
        # BibTeX マネージャーを取得
        manager = ctx.plugins.get('bibtex')
        if manager:
            manager.cite(self.key)

    def render(self, ctx: RenderContext) -> str:
        manager = ctx.plugins.get('bibtex')
        if manager:
            num = manager.cite(self.key)
            return f'<sup><a href="#ref-{num}">[{num}]</a></sup>'
        return f'<sup>[?]</sup>'

@dataclass
class Bibliography(Component):
    """参考文献リスト - ユーザーが完全に実装"""

    def analyze(self, ctx: RenderContext) -> None:
        pass

    def render(self, ctx: RenderContext) -> str:
        manager = ctx.plugins.get('bibtex')
        if not manager:
            return '<div>No bibliography</div>'

        html = '<ol class="bibliography">'
        for i, key in enumerate(manager.citations, 1):
            formatted = manager.format_entry(key, manager.style)
            html += f'<li id="ref-{i}">{formatted}</li>'
        html += '</ol>'
        return html

# 使用例
slide = Slide()
bibtex = UserBibTeXPlugin("refs.bib", style="ieee")
slide.register_preprocessor(bibtex)

# ctx に登録する必要があるので、Slide.export() で ctx.plugins['bibtex'] = bibtex する想定
```

**評価:**
- ✅ 型安全性が高い（Component を継承）
- ✅ analyze/render の分離が明確
- ❌ ctx.plugins への登録が煩雑
- ❌ フレームワークの内部構造を理解する必要がある

---

### 方向性B: Composition

ユーザーはファクトリ関数とレンダラー関数を実装：

```python
from typing import Dict, List
import bibtexparser

class BibTeXManager:
    """同じBibTeX処理ロジック"""
    # ... (上と同じ)

# ユーザー定義のプラグイン（高階関数）
def bibtex_plugin(bibfile: str, style: str = "apa"):
    """BibTeXプラグイン - ユーザーが関数として実装"""
    manager = BibTeXManager(bibfile)

    def plugin(slide: Slide) -> Slide:
        # 1. Cite コンポーネントを収集して番号を割り当て
        def collect_and_transform(comp: Component) -> Component:
            if comp.tag == "cite":
                key = comp.props['key']
                num = manager.cite(key)
                # Cite を具体的な HTML に変換
                comp.props['num'] = num

            # 子要素も再帰的に処理
            comp.children = [collect_and_transform(c) for c in comp.children]
            return comp

        # 全ページに適用
        slide.pages = [collect_and_transform(page) for page in slide.pages]

        # 2. カスタムレンダラーを登録（後で使う想定）
        # これは RenderContext に追加する必要があるが、
        # plugin 関数内では slide しか触れないので工夫が必要

        # 解決策: slide にメタデータとして保存
        slide.custom_renderers = getattr(slide, 'custom_renderers', {})
        slide.custom_renderers['cite'] = lambda comp, ctx: render_cite(comp, ctx, manager)
        slide.custom_renderers['bibliography'] = lambda comp, ctx: render_bibliography(comp, ctx, manager)

        return slide

    def render_cite(comp: Component, ctx: RenderContext, mgr: BibTeXManager) -> str:
        num = comp.props.get('num', '?')
        return f'<sup><a href="#ref-{num}">[{num}]</a></sup>'

    def render_bibliography(comp: Component, ctx: RenderContext, mgr: BibTeXManager) -> str:
        html = '<ol class="bibliography">'
        for i, key in enumerate(mgr.citations, 1):
            formatted = mgr.format_entry(key, style)
            html += f'<li id="ref-{i}">{formatted}</li>'
        html += '</ol>'
        return html

    return plugin

# ユーザー定義のコンポーネントファクトリ
def Cite(key: str) -> Component:
    """引用コンポーネント"""
    return Component("cite", {"key": key})

def Bibliography() -> Component:
    """参考文献リスト"""
    return Component("bibliography", {})

# 使用例
slide = Slide()
slide.use(bibtex_plugin("refs.bib", style="ieee"))

slide.add_page(Page(
    Text("According to the paper "),
    Cite("sample2024"),
    Text(" we can see...")
))

slide.add_page(Page(
    Text("References"),
    Bibliography()
))

final = slide.build()
```

**評価:**
- ✅ 非常に柔軟（Transform で何でもできる）
- ✅ 関数を書くだけ
- ❌ レンダラーの登録方法がアドホック（slide.custom_renderers は標準でない）
- ❌ プラグインの実行順序に依存

---

### 方向性C: Hook/Event

ユーザーは Plugin クラスを実装してイベントにフック：

```python
import bibtexparser

class BibTeXManager:
    """同じBibTeX処理ロジック"""
    # ... (上と同じ)

# ユーザー定義のプラグイン
class UserBibTeXPlugin(Plugin):
    """BibTeXプラグイン - ユーザーが完全に実装"""
    def __init__(self, bibfile: str, style: str = "apa"):
        self.manager = BibTeXManager(bibfile)
        self.style = style

    def install(self, slide: Slide):
        # BEFORE_ANALYZE で引用を収集
        def collect_citations(event: Event):
            for page in event.data['slide'].pages:
                self._scan_component(page)

        # カスタムレンダラーを登録
        def register_renderers(event: Event):
            ctx = event.data['context']
            ctx.store['renderer:cite'] = self.render_cite
            ctx.store['renderer:bibliography'] = self.render_bibliography

        slide.hooks.register(EventType.BEFORE_ANALYZE, collect_citations, priority=5)
        slide.hooks.register(EventType.BEFORE_ANALYZE, register_renderers, priority=1)

    def _scan_component(self, comp: Component):
        """再帰的に引用を収集"""
        if comp.type == "cite":
            self.manager.cite(comp.props['key'])
        for child in comp.children:
            self._scan_component(child)

    def render_cite(self, comp: Component, ctx: RenderContext) -> str:
        """引用をレンダリング"""
        key = comp.props['key']
        num = self.manager.cite(key)
        return f'<sup><a href="#ref-{num}">[{num}]</a></sup>'

    def render_bibliography(self, comp: Component, ctx: RenderContext) -> str:
        """参考文献リストをレンダリング"""
        html = '<ol class="bibliography">'
        for i, key in enumerate(self.manager.citations, 1):
            formatted = self.manager.format_entry(key, self.style)
            html += f'<li id="ref-{i}">{formatted}</li>'
        html += '</ol>'
        return html

# コンポーネント定義
def Cite(key: str) -> Component:
    return Component("cite", {"key": key})

def Bibliography() -> Component:
    return Component("bibliography", {})

# 使用例
slide = Slide()
slide.use_plugin(UserBibTeXPlugin("refs.bib", style="ieee"))

slide.add_page(Page(
    Text("According to "),
    Cite("sample2024")
))

slide.add_page(Page(Bibliography()))
```

**評価:**
- ✅ イベント駆動で処理の流れが明確
- ✅ レンダラー登録が統一的（ctx.store）
- ✅ プラグインの実行順序を制御可能（priority）
- ❌ Plugin クラスと install() を理解する必要がある

---

## 2. Mermaid図のレンダリング

Mermaid記法から図を生成する拡張。

### 方向性A: Protocol

```python
@dataclass
class Mermaid(Component):
    """Mermaidコンポーネント - ユーザー実装"""
    code: str

    def analyze(self, ctx: RenderContext) -> None:
        pass

    def render(self, ctx: RenderContext) -> str:
        # 方法1: mermaid.js を使う（クライアント側レンダリング）
        return f'''
        <div class="mermaid">
        {self.code}
        </div>
        '''

        # 方法2: mermaid-cli でサーバー側レンダリング
        # import subprocess
        # svg = subprocess.run(['mmdc', '-i', '-'], input=self.code.encode(),
        #                      capture_output=True).stdout.decode()
        # return f'<div>{svg}</div>'

# 使用時にスクリプトタグを追加する必要がある
class MermaidPlugin:
    def postprocess(self, html: str) -> str:
        # mermaid.js を追加
        script = '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'
        return html.replace('</body>', f'{script}</body>')

slide.register_postprocessor(MermaidPlugin())
```

### 方向性B: Composition

```python
def mermaid_plugin():
    """Mermaidプラグイン"""
    def plugin(slide: Slide) -> Slide:
        # レンダラー登録
        def render_mermaid(comp: Component, ctx: RenderContext) -> str:
            code = comp.props['code']
            return f'<div class="mermaid">{code}</div>'

        slide.custom_renderers = getattr(slide, 'custom_renderers', {})
        slide.custom_renderers['mermaid'] = render_mermaid

        # 後処理でスクリプト追加（どう実装する？）
        slide.post_html_transforms = getattr(slide, 'post_html_transforms', [])
        slide.post_html_transforms.append(lambda html:
            html.replace('</body>',
                '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script></body>')
        )

        return slide

    return plugin

def Mermaid(code: str) -> Component:
    return Component("mermaid", {"code": code})

# 使用
slide.use(mermaid_plugin())
```

### 方向性C: Hook/Event

```python
class MermaidPlugin(Plugin):
    def install(self, slide: Slide):
        # レンダラー登録
        def register_renderer(event: Event):
            ctx = event.data['context']
            ctx.store['renderer:mermaid'] = self.render_mermaid

        # HTML後処理でスクリプト追加
        def add_mermaid_script(event: Event):
            html = event.data['html']
            script = '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'
            event.data['html'] = html.replace('</body>', f'{script}</body>')

        slide.hooks.register(EventType.BEFORE_ANALYZE, register_renderer, priority=1)
        slide.hooks.register(EventType.BEFORE_EXPORT, add_mermaid_script, priority=10)

    def render_mermaid(self, comp: Component, ctx: RenderContext) -> str:
        code = comp.props['code']
        return f'<div class="mermaid">{code}</div>'

def Mermaid(code: str) -> Component:
    return Component("mermaid", {"code": code})
```

---

## 3. LaTeX数式レンダリング

### 方向性A: Protocol

```python
@dataclass
class Math(Component):
    """数式コンポーネント - ユーザー実装"""
    latex: str
    display: bool = False  # True なら display math, False なら inline

    def render(self, ctx: RenderContext) -> str:
        if self.display:
            return f'$$\n{self.latex}\n$$'
        else:
            return f'${self.latex}$'

class MathJaxPlugin:
    """MathJax を埋め込むプラグイン"""
    def postprocess(self, html: str) -> str:
        mathjax_config = '''
        <script>
        MathJax = {
          tex: {inlineMath: [['$', '$']], displayMath: [['$$', '$$']]}
        };
        </script>
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        '''
        return html.replace('</head>', f'{mathjax_config}</head>')

slide.register_postprocessor(MathJaxPlugin())
```

### 方向性B: Composition

```python
def mathjax_plugin():
    def plugin(slide: Slide) -> Slide:
        # レンダラー
        def render_math(comp: Component, ctx: RenderContext) -> str:
            latex = comp.props['latex']
            display = comp.props.get('display', False)
            if display:
                return f'$$\n{latex}\n$$'
            else:
                return f'${latex}$'

        slide.custom_renderers = getattr(slide, 'custom_renderers', {})
        slide.custom_renderers['math'] = render_math

        # MathJax スクリプト追加
        slide.post_html_transforms = getattr(slide, 'post_html_transforms', [])
        slide.post_html_transforms.append(lambda html:
            html.replace('</head>', '''
            <script>
            MathJax = {tex: {inlineMath: [['$', '$']], displayMath: [['$$', '$$']]}};
            </script>
            <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            </head>''')
        )

        return slide

    return plugin

def Math(latex: str, display: bool = False) -> Component:
    return Component("math", {"latex": latex, "display": display})
```

### 方向性C: Hook/Event

```python
class MathJaxPlugin(Plugin):
    def install(self, slide: Slide):
        def register_renderer(event: Event):
            ctx = event.data['context']
            ctx.store['renderer:math'] = self.render_math

        def add_mathjax(event: Event):
            html = event.data['html']
            mathjax_config = '''
            <script>
            MathJax = {tex: {inlineMath: [['$', '$']], displayMath: [['$$', '$$']]}};
            </script>
            <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            '''
            event.data['html'] = html.replace('</head>', f'{mathjax_config}</head>')

        slide.hooks.register(EventType.BEFORE_ANALYZE, register_renderer, priority=1)
        slide.hooks.register(EventType.BEFORE_EXPORT, add_mathjax, priority=10)

    def render_math(self, comp: Component, ctx: RenderContext) -> str:
        latex = comp.props['latex']
        display = comp.props.get('display', False)
        if display:
            return f'$$\n{latex}\n$$'
        else:
            return f'${latex}$'

def Math(latex: str, display: bool = False) -> Component:
    return Component("math", {"latex": latex, "display": display})
```

---

## 4. インクリメンタル表示（アニメーション）

箇条書きを1つずつ表示する機能。reveal.js の fragment 的なもの。

### 方向性A: Protocol

```python
@dataclass
class IncrementalList(Component):
    """インクリメンタル表示リスト - ユーザー実装"""
    items: List[Component]

    def render(self, ctx: RenderContext) -> str:
        html = '<ul>'
        for i, item in enumerate(self.items):
            # fragment クラスで1つずつ表示
            html += f'<li class="fragment" data-fragment-index="{i}">{item.render(ctx)}</li>'
        html += '</ul>'
        return html

class RevealJSPlugin:
    """reveal.js 統合"""
    def postprocess(self, html: str) -> str:
        # reveal.js を読み込み
        reveal_setup = '''
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.css">
        <script src="https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.js"></script>
        <script>Reveal.initialize();</script>
        '''
        return html.replace('</body>', f'{reveal_setup}</body>')

slide.register_postprocessor(RevealJSPlugin())
```

### 方向性B: Composition

```python
def incremental_plugin():
    """インクリメンタル表示プラグイン"""
    def plugin(slide: Slide) -> Slide:
        def render_incremental_list(comp: Component, ctx: RenderContext) -> str:
            items = comp.children  # 子要素をアイテムとして扱う
            html = '<ul>'
            for i, item in enumerate(items):
                item_html = render(item, ctx)  # 各アイテムをレンダリング
                html += f'<li class="fragment" data-fragment-index="{i}">{item_html}</li>'
            html += '</ul>'
            return html

        slide.custom_renderers = getattr(slide, 'custom_renderers', {})
        slide.custom_renderers['incremental-list'] = render_incremental_list

        # reveal.js セットアップ
        slide.post_html_transforms = getattr(slide, 'post_html_transforms', [])
        slide.post_html_transforms.append(lambda html:
            html.replace('</body>', '''
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.css">
            <script src="https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.js"></script>
            <script>Reveal.initialize();</script>
            </body>''')
        )

        return slide

    return plugin

def IncrementalList(*items: Component) -> Component:
    return Component("incremental-list", {}, list(items))

# 使用
slide.use(incremental_plugin())
slide.add_page(Page(
    Header("Key Points", level=2),
    IncrementalList(
        Text("Point 1"),
        Text("Point 2"),
        Text("Point 3")
    )
))
```

### 方向性C: Hook/Event

```python
class IncrementalPlugin(Plugin):
    def install(self, slide: Slide):
        def register_renderer(event: Event):
            ctx = event.data['context']
            ctx.store['renderer:incremental-list'] = self.render_incremental_list

        def add_reveal_js(event: Event):
            html = event.data['html']
            reveal_setup = '''
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.css">
            <script src="https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.js"></script>
            <script>Reveal.initialize();</script>
            '''
            event.data['html'] = html.replace('</body>', f'{reveal_setup}</body>')

        slide.hooks.register(EventType.BEFORE_ANALYZE, register_renderer, priority=1)
        slide.hooks.register(EventType.BEFORE_EXPORT, add_reveal_js, priority=10)

    def render_incremental_list(self, comp: Component, ctx: RenderContext) -> str:
        # Slide の _render_component を使って子要素をレンダリング
        # （ここは設計上の問題: ctx から Slide インスタンスにアクセスできない）
        # 解決策: ctx.store['slide'] = slide を設定しておく
        slide_instance = ctx.store.get('slide')

        html = '<ul>'
        for i, item in enumerate(comp.children):
            item_html = slide_instance._render_component(item) if slide_instance else str(item)
            html += f'<li class="fragment" data-fragment-index="{i}">{item_html}</li>'
        html += '</ul>'
        return html

def IncrementalList(*items: Component) -> Component:
    return Component("incremental-list", {}, list(items))
```

---

## まとめ：ユーザーによるレンダリング拡張の比較

| 拡張内容 | A: Protocol | B: Composition | C: Hook |
|----------|------------|----------------|---------|
| **BibTeX** | Component継承<br/>analyze/render実装 | ファクトリ関数 + Transform | Plugin + レンダラー登録 |
| **Mermaid** | Component継承<br/>postprocessor | ファクトリ + post_html_transforms | Plugin + BEFORE_EXPORT |
| **LaTeX** | 同上 | 同上 | 同上 |
| **アニメーション** | Component継承 | ファクトリ + custom_renderer | Plugin + レンダラー |

### コード量の比較

典型的な拡張（例：BibTeX）を実装する場合：

**A: Protocol - 約50行**
- クラス定義が必要
- analyze/render を両方実装
- ctx.plugins への登録が必要

**B: Composition - 約40行**
- 関数だけでOK
- ただし slide.custom_renderers などアドホックな仕組みが必要

**C: Hook - 約60行**
- Plugin クラス + install()
- イベント登録が明示的
- やや冗長だが構造は明確

### 拡張のしやすさ

| 観点 | A | B | C |
|------|---|---|---|
| 学習コスト | 中 | 低 | 中〜高 |
| 柔軟性 | 中 | 高 | 高 |
| デバッグ | 中 | 難 | 易 |
| 型安全性 | 高 | 低 | 中 |

### 重大な設計上の問題点

各方向性で見つかった問題：

**A: Protocol**
- `ctx.plugins` への登録タイミングが不明確
- フレームワークが `ctx.plugins['bibtex'] = bibtex` を自動でやる必要がある

**B: Composition**
- `slide.custom_renderers` は標準機能でない（アドホック）
- `post_html_transforms` も同様
- フレームワークがこれらをサポートする必要がある

**C: Hook**
- `ctx.store['slide']` にSlideインスタンスを保存する必要がある
- レンダラー内で `slide._render_component()` を呼ぶのは循環参照的

## 提案：どの設計を選ぶか

ユーザーが自由にレンダリングを拡張することを重視するなら：

### 推奨: **B (Composition) + 標準化された拡張メカニズム**

理由：
1. 最も柔軟（Transform で何でもできる）
2. ユーザーは関数を書くだけ
3. ただし、フレームワークが以下を標準サポートすべき：
   - `slide.add_renderer(tag, func)` - カスタムレンダラー登録
   - `slide.add_html_transform(func)` - HTML後処理
   - `slide.add_component_transform(func)` - Component木の変換

### 次点: **C (Hook) + より多くのイベント**

理由：
1. 拡張ポイントが明確
2. プラグイン間の依存関係を制御可能
3. ただし、より細かいイベントが必要：
   - `BEFORE_RENDER_COMPONENT` - 個別コンポーネントのレンダリング前
   - `AFTER_RENDER_COMPONENT` - 個別コンポーネントのレンダリング後
   - `HTML_TRANSFORM` - HTML変換用

どちらにしても、**フレームワークが提供すべき最小限の機能**を明確にする必要があります。
