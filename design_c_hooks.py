"""
方向性C: Hook + Event システム
レンダリングプロセスをイベントとして扱い、フックで拡張
"""

from dataclasses import dataclass, field
from typing import Callable, Any, List
from enum import Enum

# ===== Event System =====

class EventType(Enum):
    """レンダリングプロセスのイベント"""
    BEFORE_BUILD = "before_build"
    AFTER_BUILD = "after_build"
    BEFORE_ANALYZE = "before_analyze"
    AFTER_ANALYZE = "after_analyze"
    BEFORE_RENDER_PAGE = "before_render_page"
    AFTER_RENDER_PAGE = "after_render_page"
    BEFORE_EXPORT = "before_export"
    AFTER_EXPORT = "after_export"

@dataclass
class Event:
    """イベントデータ"""
    type: EventType
    data: dict[str, Any] = field(default_factory=dict)

HookFunc = Callable[[Event], None]

class HookManager:
    """フック管理"""
    def __init__(self):
        self.hooks: dict[EventType, List[tuple[int, HookFunc]]] = {
            event_type: [] for event_type in EventType
        }

    def register(self, event_type: EventType, func: HookFunc, priority: int = 10):
        """フックを登録（優先度付き）"""
        self.hooks[event_type].append((priority, func))
        # 優先度でソート（小さい方が先）
        self.hooks[event_type].sort(key=lambda x: x[0])

    def trigger(self, event: Event):
        """イベントを発火"""
        for priority, hook in self.hooks[event.type]:
            hook(event)

# ===== Core Components =====

@dataclass
class Component:
    """基底コンポーネント"""
    type: str
    props: dict[str, Any] = field(default_factory=dict)
    children: List['Component'] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)  # フック用メタデータ

@dataclass
class RenderContext:
    """レンダリングコンテキスト"""
    total_pages: int
    current_page: int
    store: dict[str, Any] = field(default_factory=dict)  # プラグイン間でデータ共有

class Slide:
    def __init__(self):
        self.pages: List[Component] = []
        self.hooks = HookManager()
        self.context = RenderContext(total_pages=0, current_page=0)

    def add_page(self, page: Component):
        self.pages.append(page)
        return self

    def use_plugin(self, plugin: 'Plugin'):
        """プラグインを登録"""
        plugin.install(self)
        return self

    def export(self, path: str):
        # BEFORE_BUILD イベント
        self.hooks.trigger(Event(EventType.BEFORE_BUILD, {"slide": self}))

        # ページ数確定
        self.context.total_pages = len(self.pages)

        # BEFORE_ANALYZE イベント
        self.hooks.trigger(Event(EventType.BEFORE_ANALYZE, {
            "slide": self,
            "context": self.context
        }))

        # AFTER_ANALYZE イベント
        self.hooks.trigger(Event(EventType.AFTER_ANALYZE, {
            "slide": self,
            "context": self.context
        }))

        # レンダリング
        html_pages = []
        for i, page in enumerate(self.pages, 1):
            self.context.current_page = i

            # BEFORE_RENDER_PAGE イベント
            self.hooks.trigger(Event(EventType.BEFORE_RENDER_PAGE, {
                "page": page,
                "context": self.context
            }))

            html = self._render_component(page)
            html_pages.append(html)

            # AFTER_RENDER_PAGE イベント
            self.hooks.trigger(Event(EventType.AFTER_RENDER_PAGE, {
                "page": page,
                "html": html,
                "context": self.context
            }))

        # 最終HTML生成
        full_html = self._generate_html(html_pages)

        # BEFORE_EXPORT イベント
        export_event = Event(EventType.BEFORE_EXPORT, {"html": full_html})
        self.hooks.trigger(export_event)
        full_html = export_event.data.get("html", full_html)

        # ファイル書き込み
        with open(path, "w") as f:
            f.write(full_html)

        # AFTER_EXPORT イベント
        self.hooks.trigger(Event(EventType.AFTER_EXPORT, {"path": path}))

    def _render_component(self, comp: Component) -> str:
        """コンポーネントをレンダリング"""
        if comp.type == "text":
            return f"<p>{comp.props['content']}</p>"
        elif comp.type == "header":
            level = comp.props['level']
            text = comp.props['text']
            return f"<h{level}>{text}</h{level}>"
        elif comp.type == "page":
            children_html = [self._render_component(c) for c in comp.children]
            return f'<div class="page">{"".join(children_html)}</div>'
        else:
            # カスタムレンダラーを context.store から取得
            custom_renderer = self.context.store.get(f"renderer:{comp.type}")
            if custom_renderer:
                return custom_renderer(comp, self.context)
            # デフォルト
            children_html = [self._render_component(c) for c in comp.children]
            return f'<div class="{comp.type}">{"".join(children_html)}</div>'

    def _generate_html(self, pages: List[str]) -> str:
        return f'''<!DOCTYPE html>
<html>
<head>
    <style>
        {self.context.store.get('custom_css', '')}
    </style>
</head>
<body>
    {''.join(pages)}
</body>
</html>'''

# ===== Plugin Base Class =====

class Plugin:
    """プラグインの基底クラス"""
    def install(self, slide: Slide):
        """プラグインをインストール"""
        raise NotImplementedError

# ===== Component Builders =====

def Text(content: str) -> Component:
    return Component("text", {"content": content})

def Header(text: str, level: int = 1, **props) -> Component:
    return Component("header", {"text": text, "level": level, **props})

def Page(*children: Component) -> Component:
    return Component("page", {}, list(children))

# ===== ユーザー拡張例 1: TOC自動生成プラグイン =====

class TOCPlugin(Plugin):
    """目次を自動生成するプラグイン"""
    def __init__(self, max_level: int = 2, insert_at: int = 1):
        self.max_level = max_level
        self.insert_at = insert_at
        self.toc_items = []

    def install(self, slide: Slide):
        # BEFORE_ANALYZE で見出しを収集
        def collect_headers(event: Event):
            self.toc_items = []
            for page_num, page in enumerate(event.data['slide'].pages, 1):
                self._scan_headers(page, page_num)

        # AFTER_ANALYZE で TOC ページを挿入
        def insert_toc(event: Event):
            toc_html = '<ul class="toc">'
            for item in self.toc_items:
                indent = '  ' * (item['level'] - 1)
                toc_html += f'{indent}<li>{item["text"]} (p.{item["page"]})</li>'
            toc_html += '</ul>'

            toc_page = Page(
                Header("Table of Contents", level=1),
                Component("raw-html", {"html": toc_html})
            )

            event.data['slide'].pages.insert(self.insert_at, toc_page)
            # ページ数が変わったので更新
            event.data['context'].total_pages = len(event.data['slide'].pages)

        slide.hooks.register(EventType.BEFORE_ANALYZE, collect_headers, priority=5)
        slide.hooks.register(EventType.AFTER_ANALYZE, insert_toc, priority=10)

        # raw-html レンダラーを登録
        slide.context.store['renderer:raw-html'] = lambda c, ctx: c.props['html']

    def _scan_headers(self, comp: Component, page_num: int):
        """再帰的に見出しを収集"""
        if comp.type == "header" and comp.props.get('level', 99) <= self.max_level:
            self.toc_items.append({
                'level': comp.props['level'],
                'text': comp.props['text'],
                'page': page_num
            })
        for child in comp.children:
            self._scan_headers(child, page_num)

# ===== ユーザー拡張例 2: BibTeXプラグイン =====

class BibTeXPlugin(Plugin):
    """BibTeX引用管理プラグイン"""
    def __init__(self, bibfile: str):
        self.bibfile = bibfile
        self.citations = []
        self.entries = {
            'sample2024': {'author': 'Sample A.', 'title': 'Sample Paper', 'year': '2024'}
        }

    def install(self, slide: Slide):
        # BEFORE_ANALYZE で引用を収集
        def collect_citations(event: Event):
            self.citations = []
            for page in event.data['slide'].pages:
                self._scan_citations(page)

        # レンダリング時に引用番号を解決
        def resolve_citation(comp: Component, ctx: RenderContext) -> str:
            key = comp.props['key']
            if key not in self.citations:
                self.citations.append(key)
            num = self.citations.index(key) + 1
            return f'<sup>[{num}]</sup>'

        def render_bibliography(comp: Component, ctx: RenderContext) -> str:
            items = []
            for i, key in enumerate(self.citations, 1):
                entry = self.entries.get(key, {})
                author = entry.get('author', 'Unknown')
                title = entry.get('title', 'Unknown')
                year = entry.get('year', 'Unknown')
                items.append(f'<li>[{i}] {author}, "{title}", {year}</li>')
            return f'<ol class="bibliography">{"".join(items)}</ol>'

        slide.hooks.register(EventType.BEFORE_ANALYZE, collect_citations, priority=5)
        slide.context.store['renderer:cite'] = resolve_citation
        slide.context.store['renderer:bibliography'] = render_bibliography

    def _scan_citations(self, comp: Component):
        """再帰的に引用を収集"""
        if comp.type == "cite":
            key = comp.props['key']
            if key not in self.citations:
                self.citations.append(key)
        for child in comp.children:
            self._scan_citations(child)

def Cite(key: str) -> Component:
    return Component("cite", {"key": key})

def Bibliography() -> Component:
    return Component("bibliography", {})

# ===== ユーザー拡張例 3: 自動フッタープラグイン =====

class AutoFooterPlugin(Plugin):
    """全ページにフッターを自動追加"""
    def __init__(self, text: str):
        self.text = text

    def install(self, slide: Slide):
        def add_footer(event: Event):
            """各ページレンダリング前にフッターを追加"""
            page = event.data['page']
            ctx = event.data['context']

            footer = Component("footer", {
                "text": self.text,
                "page_num": ctx.current_page,
                "total": ctx.total_pages
            })
            page.children.append(footer)

        def render_footer(comp: Component, ctx: RenderContext) -> str:
            text = comp.props['text']
            page_num = comp.props['page_num']
            total = comp.props['total']
            return f'<div class="footer">{text} | Page {page_num}/{total}</div>'

        slide.hooks.register(EventType.BEFORE_RENDER_PAGE, add_footer, priority=100)
        slide.context.store['renderer:footer'] = render_footer

# ===== ユーザー拡張例 4: コード実行プラグイン =====

class CodeExecutionPlugin(Plugin):
    """コードを実行して結果を埋め込む"""
    def install(self, slide: Slide):
        def render_code_with_output(comp: Component, ctx: RenderContext) -> str:
            code = comp.props['code']
            lang = comp.props.get('lang', 'python')
            auto_execute = comp.props.get('auto_execute', True)

            code_html = f'<pre><code class="language-{lang}">{code}</code></pre>'

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

            output_html = f'<pre class="output">{output}</pre>'

            return f'''
            <div class="code-with-output">
                <div class="code-section">{code_html}</div>
                <div class="output-section">{output_html}</div>
            </div>
            '''

        slide.context.store['renderer:code-with-output'] = render_code_with_output

def CodeWithOutput(code: str, lang: str = "python", auto_execute: bool = True) -> Component:
    return Component("code-with-output", {
        "code": code,
        "lang": lang,
        "auto_execute": auto_execute
    })

# ===== ユーザー拡張例 5: デバッグプラグイン =====

class DebugPlugin(Plugin):
    """レンダリングプロセスをログ出力"""
    def install(self, slide: Slide):
        def log_event(event_name: str):
            def logger(event: Event):
                print(f"[DEBUG] {event_name}: {event.data.keys()}")
            return logger

        for event_type in EventType:
            slide.hooks.register(event_type, log_event(event_type.value), priority=0)

# ===== ユーザー拡張例 6: CSSテーマプラグイン =====

class ThemePlugin(Plugin):
    """CSSテーマを適用"""
    def __init__(self, primary_color: str = "#3498db"):
        self.primary_color = primary_color

    def install(self, slide: Slide):
        css = f'''
        body {{ font-family: Arial, sans-serif; }}
        .page {{ border-top: 3px solid {self.primary_color}; padding: 20px; }}
        .footer {{ margin-top: 20px; color: gray; font-size: 0.8em; }}
        .code-with-output {{ display: flex; gap: 20px; }}
        .code-section, .output-section {{ flex: 1; }}
        '''
        slide.context.store['custom_css'] = css

# ===== 使用例 =====

def example_usage():
    slide = Slide()

    # プラグインをインストール
    slide.use_plugin(ThemePlugin(primary_color="#e74c3c"))
    slide.use_plugin(BibTeXPlugin("refs.bib"))
    slide.use_plugin(AutoFooterPlugin("My Presentation"))
    slide.use_plugin(CodeExecutionPlugin())
    slide.use_plugin(TOCPlugin(max_level=2, insert_at=1))
    slide.use_plugin(DebugPlugin())  # デバッグ用

    # ページ追加
    slide.add_page(Page(
        Header("Introduction", level=1),
        Text("Welcome to my presentation")
    ))

    slide.add_page(Page(
        Header("Code Example", level=1),
        CodeWithOutput("""
print("Hello from slide!")
for i in range(3):
    print(f"  Item {i}")
""", auto_execute=True)
    ))

    slide.add_page(Page(
        Header("Related Work", level=1),
        Text("According to Sample et al. "),
        Cite("sample2024"),
        Text(" we can see...")
    ))

    slide.add_page(Page(
        Header("References", level=1),
        Bibliography()
    ))

    # エクスポート
    slide.export("output.html")

# ===== この方向性の評価 =====

"""
【長所】
1. プラグイン間の依存関係が明確（優先度で制御）
2. イベントドリブンで理解しやすい
3. プラグインの実行順序を制御可能
4. デバッグしやすい（イベントログを取れる）
5. プラグインの追加・削除が容易

【短所】
1. イベントの種類を適切に設計する必要がある
2. フック内でスライドを変更すると副作用がわかりづらい
3. イベントが多すぎると煩雑になる
4. パフォーマンスオーバーヘッド（イベント発火コスト）

【ユーザー拡張の容易さ】★★★★☆
- Plugin クラスを継承して install() を実装するだけ
- イベントの概念を理解する必要がある

【柔軟性】★★★★☆
- イベントドリブンなので拡張ポイントは限定的
- ただしフック内で何でもできる
"""
