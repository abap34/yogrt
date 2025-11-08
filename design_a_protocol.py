"""
方向性A: Protocol ベースの拡張システム
明確な拡張ポイントを定義し、ユーザーはそれに従って実装
"""

from typing import Protocol, List, Any, runtime_checkable
from dataclasses import dataclass
from abc import ABC, abstractmethod

# ===== Core Extension Points =====

@runtime_checkable
class Component(Protocol):
    """全てのコンポーネントが実装すべきインターフェース"""
    def render(self, ctx: 'RenderContext') -> str:
        ...

@runtime_checkable
class AnalyzableComponent(Protocol):
    """解析フェーズに参加するコンポーネント（TOC生成など）"""
    def analyze(self, ctx: 'RenderContext') -> None:
        ...

    def render(self, ctx: 'RenderContext') -> str:
        ...

@runtime_checkable
class PreprocessPlugin(Protocol):
    """レンダリング前の前処理"""
    def preprocess(self, slide: 'Slide') -> None:
        ...

@runtime_checkable
class PostprocessPlugin(Protocol):
    """レンダリング後の後処理"""
    def postprocess(self, html: str) -> str:
        ...

@runtime_checkable
class ResourceProvider(Protocol):
    """外部リソースの取得（画像、アイコンなど）"""
    def fetch(self, identifier: str) -> bytes:
        ...

# ===== Framework Core =====

@dataclass
class RenderContext:
    slide_title: str
    total_pages: int
    current_page: int
    theme: 'Theme'
    references: dict[str, Any]
    plugins: dict[str, Any]  # プラグイン用のストレージ

class Page:
    def __init__(self, *components: Component):
        self.components = list(components)

class Slide:
    def __init__(self):
        self.pages: List[Page] = []
        self.preprocessors: List[PreprocessPlugin] = []
        self.postprocessors: List[PostprocessPlugin] = []
        self.resource_providers: dict[str, ResourceProvider] = {}

    def register_preprocessor(self, plugin: PreprocessPlugin):
        self.preprocessors.append(plugin)

    def register_postprocessor(self, plugin: PostprocessPlugin):
        self.postprocessors.append(plugin)

    def register_resource_provider(self, name: str, provider: ResourceProvider):
        self.resource_providers[name] = provider

    def __lshift__(self, page: Page):
        self.pages.append(page)
        return self

# ===== ユーザー拡張例 1: カスタムレイアウト =====

@dataclass
class ThreeColumn:
    """3カラムレイアウト - ユーザー定義"""
    left: Component
    center: Component
    right: Component

    def render(self, ctx: RenderContext) -> str:
        return f'''
        <div class="three-column">
            <div class="col">{self.left.render(ctx)}</div>
            <div class="col">{self.center.render(ctx)}</div>
            <div class="col">{self.right.render(ctx)}</div>
        </div>
        '''

@dataclass
class CodeWithOutput:
    """コードとその実行結果を並べて表示 - ユーザー定義"""
    code: str
    lang: str = "python"
    auto_execute: bool = True

    def render(self, ctx: RenderContext) -> str:
        code_html = f'<pre><code class="language-{self.lang}">{self.code}</code></pre>'

        if self.auto_execute and self.lang == "python":
            import io
            import sys
            from contextlib import redirect_stdout

            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                try:
                    exec(self.code)
                    output = output_buffer.getvalue()
                except Exception as e:
                    output = f"Error: {e}"

            output_html = f'<pre class="output">{output}</pre>'
        else:
            output_html = '<pre class="output">No output</pre>'

        return f'''
        <div class="code-with-output">
            <div class="code-section">{code_html}</div>
            <div class="output-section">{output_html}</div>
        </div>
        '''

# ===== ユーザー拡張例 2: 外部リソース統合 =====

class GitHubIconProvider:
    """GitHubからユーザーアイコンを取得 - ユーザー定義プラグイン"""
    def fetch(self, username: str) -> bytes:
        import urllib.request
        url = f"https://github.com/{username}.png"
        with urllib.request.urlopen(url) as response:
            return response.read()

@dataclass
class GitHubIcon:
    """GitHubアイコンコンポーネント - ユーザー定義"""
    username: str
    size: int = 100

    def render(self, ctx: RenderContext) -> str:
        provider = ctx.plugins.get('github_icon_provider')
        if provider:
            import base64
            img_data = provider.fetch(self.username)
            img_b64 = base64.b64encode(img_data).decode()
            return f'<img src="data:image/png;base64,{img_b64}" width="{self.size}"/>'
        return f'<div>Icon for {self.username}</div>'

# セットアップ
# slide.register_resource_provider('github_icon_provider', GitHubIconProvider())

# ===== ユーザー拡張例 3: BibTeX統合 =====

class BibTeXPlugin:
    """BibTeX引用管理 - ユーザー定義プラグイン"""
    def __init__(self, bibfile: str):
        self.bibfile = bibfile
        self.citations: List[str] = []
        self.entries: dict = {}

    def cite(self, key: str) -> str:
        """引用を追加し、引用番号を返す"""
        if key not in self.citations:
            self.citations.append(key)
        return f"[{self.citations.index(key) + 1}]"

    def preprocess(self, slide: Slide):
        """BibTeXファイルをパース"""
        # 簡易実装（実際は bibtexparser などを使う）
        self.entries = {
            'sample2024': {
                'author': 'Sample A.',
                'title': 'Sample Paper',
                'year': '2024'
            }
        }

    def generate_bibliography(self) -> str:
        """参考文献リストを生成"""
        items = []
        for i, key in enumerate(self.citations, 1):
            entry = self.entries.get(key, {})
            author = entry.get('author', 'Unknown')
            title = entry.get('title', 'Unknown')
            year = entry.get('year', 'Unknown')
            items.append(f'<li>[{i}] {author}, "{title}", {year}</li>')
        return f'<ol class="bibliography">{"".join(items)}</ol>'

@dataclass
class Cite:
    """引用コンポーネント - ユーザー定義"""
    key: str

    def render(self, ctx: RenderContext) -> str:
        bibtex = ctx.plugins.get('bibtex')
        if bibtex:
            citation = bibtex.cite(self.key)
            return f'<sup>{citation}</sup>'
        return f'<sup>[?]</sup>'

@dataclass
class Bibliography:
    """参考文献リスト - ユーザー定義"""
    def render(self, ctx: RenderContext) -> str:
        bibtex = ctx.plugins.get('bibtex')
        if bibtex:
            return bibtex.generate_bibliography()
        return '<div>No references</div>'

# ===== ユーザー拡張例 4: 静的解析統合 =====

class CodeLintPlugin:
    """コードのlintを実行 - ユーザー定義プラグイン"""
    def __init__(self, strict: bool = True):
        self.strict = strict
        self.errors: List[str] = []

    def lint_python(self, code: str, filename: str = "<slide>"):
        """Pythonコードをlint"""
        import ast
        try:
            ast.parse(code)
        except SyntaxError as e:
            error_msg = f"Syntax error in {filename}: {e}"
            self.errors.append(error_msg)
            if self.strict:
                raise ValueError(error_msg)

    def postprocess(self, html: str) -> str:
        """lint結果をレポート"""
        if self.errors:
            print("=== Lint Errors ===")
            for error in self.errors:
                print(f"  {error}")
        return html

def py_static_lint(code: str):
    """ユーザー向けヘルパー関数"""
    import ast
    try:
        ast.parse(code)
        print(f"✓ Code is valid Python")
    except SyntaxError as e:
        raise ValueError(f"Invalid Python code: {e}")

# ===== ユーザー拡張例 5: グローバル機能（フッター自動挿入）=====

class AutoFooterPlugin:
    """全ページに自動でフッターを追加 - ユーザー定義プラグイン"""
    def __init__(self, footer_text: str):
        self.footer_text = footer_text

    def preprocess(self, slide: Slide):
        """全ページにフッターコンポーネントを追加"""
        for page in slide.pages:
            page.components.append(Footer(self.footer_text))

@dataclass
class Footer:
    """フッターコンポーネント"""
    text: str

    def render(self, ctx: RenderContext) -> str:
        return f'<div class="footer">{self.text} | Page {ctx.current_page}/{ctx.total_pages}</div>'

# ===== 使用例 =====

def example_usage():
    from pathlib import Path

    slide = Slide()

    # プラグイン登録
    bibtex = BibTeXPlugin("refs.bib")
    slide.preprocessors.append(bibtex)
    slide.preprocessors.append(AutoFooterPlugin("My Presentation"))
    slide.postprocessors.append(CodeLintPlugin(strict=False))

    # RenderContext にプラグインを渡す必要があるので、
    # Slide.export() 内で ctx.plugins に登録される想定

    # 1. GitHubアイコンを使ったタイトル
    github_provider = GitHubIconProvider()
    slide.register_resource_provider('github_icon_provider', github_provider)

    @dataclass
    class Text:
        content: str
        def render(self, ctx): return f"<p>{self.content}</p>"

    slide << Page(
        Text("My Presentation"),
        GitHubIcon("abap34", size=150)
    )

    # 2. カスタムレイアウト
    slide << Page(
        ThreeColumn(
            Text("Left column"),
            Text("Center column"),
            Text("Right column")
        )
    )

    # 3. コード実行
    slide << Page(
        CodeWithOutput("""
print("Hello from slide!")
for i in range(3):
    print(f"  Item {i}")
""", auto_execute=True)
    )

    # 4. BibTeX引用
    slide << Page(
        Text("According to Sample et al."),
        Cite("sample2024"),
        Text("we can conclude that...")
    )

    slide << Page(
        Text("References"),
        Bibliography()
    )

    # 5. 外部コードの検証
    alg1_src = Path("alg1.py").read_text() if Path("alg1.py").exists() else "print('example')"
    py_static_lint(alg1_src)

    slide << Page(
        Text("Algorithm 1"),
        CodeWithOutput(alg1_src, auto_execute=False)
    )

# ===== この方向性の評価 =====

"""
【長所】
1. 拡張ポイントが明確（Protocol で定義）
2. 型チェックの恩恵を受けられる（Protocol は型ヒントとして機能）
3. プラグインの登録が統一的
4. ユーザーは dataclass を書くだけで簡単に拡張可能

【短所】
1. 新しい拡張ポイントが必要になるたびにフレームワーク側の変更が必要
2. Plugin の依存関係管理が難しい（どの順序で実行するか）
3. RenderContext にプラグインを渡す方法がやや煩雑
4. ユーザーが「どの Protocol を実装すべきか」を理解する必要がある

【ユーザー拡張の容易さ】★★★★☆
- 明確な契約があるので実装しやすい
- ただし、フレームワークの理解が必要

【柔軟性】★★★☆☆
- 定義された拡張ポイント内でのみ拡張可能
- 予期しない拡張には対応しづらい
"""
