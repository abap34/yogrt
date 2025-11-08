# 設計方向性の比較

## 概要

| 方向性 | 核となる思想 | ファイル |
|--------|------------|---------|
| A: Protocol ベース | 明確な拡張ポイントを Protocol で定義 | `design_a_protocol.py` |
| B: Composition | Component はデータ、ロジックは関数として分離 | `design_b_composition.py` |
| C: Hook/Event | レンダリングをイベントとして扱い、フックで拡張 | `design_c_hooks.py` |

## 詳細比較

### 1. ユーザー拡張の容易さ

| 拡張内容 | A: Protocol | B: Composition | C: Hook |
|----------|------------|----------------|---------|
| カスタムレイアウト | ★★★★☆<br/>dataclass + render() | ★★★★★<br/>関数を書くだけ | ★★★☆☆<br/>カスタムレンダラー登録 |
| 外部リソース統合 | ★★★★☆<br/>ResourceProvider 実装 | ★★★★★<br/>高階関数でプラグイン | ★★★★☆<br/>Plugin クラス実装 |
| グローバル機能追加 | ★★★☆☆<br/>Preprocessor 実装 | ★★★★★<br/>Transform 関数 | ★★★★★<br/>Hook で介入 |
| 条件付きレンダリング | ★★★★★<br/>Python の if/for | ★★★★★<br/>Python の if/for | ★★★★★<br/>Python の if/for |

### 2. 実装例の比較

#### カスタムレイアウト (ThreeColumn)

**A: Protocol**
```python
@dataclass
class ThreeColumn:
    left: Component
    center: Component
    right: Component

    def render(self, ctx: RenderContext) -> str:
        return f'<div class="three-column">...'
```

**B: Composition**
```python
def ThreeColumn(left, center, right):
    return Component("three-column", {}, [left, center, right])

# 別途レンダラーを定義
def render_three_column(comp, ctx):
    return f'<div class="three-column">...'
```

**C: Hook**
```python
def ThreeColumn(left, center, right):
    return Component("three-column", {}, [left, center, right])

# Plugin 内でレンダラーを登録
slide.context.store['renderer:three-column'] = render_three_column
```

#### BibTeX 引用

**A: Protocol**
```python
class BibTeXPlugin:
    def preprocess(self, slide): ...
    def cite(self, key): ...

@dataclass
class Cite:
    key: str
    def render(self, ctx):
        return ctx.plugins['bibtex'].cite(self.key)
```

**B: Composition**
```python
def bibtex_plugin(bibfile):
    def plugin(slide):
        # Transform: Cite を Text に変換
        ...
    return plugin

slide.use(bibtex_plugin("refs.bib"))
```

**C: Hook**
```python
class BibTeXPlugin(Plugin):
    def install(self, slide):
        slide.hooks.register(EventType.BEFORE_ANALYZE, collect_citations)
        slide.context.store['renderer:cite'] = resolve_citation
```

#### TOC 自動生成

**A: Protocol**
```python
def TableOfContents(max_level=2):
    @dataclass
    class TOC(Component):
        def render(self, ctx):
            # ctx.references から見出しを取得
            ...
    return TOC(max_level)
```

**B: Composition**
```python
def toc_plugin(max_level=2):
    def plugin(slide):
        # スライド全体をスキャンして TOC 生成
        ...
        slide.pages.insert(1, toc_page)
    return plugin
```

**C: Hook**
```python
class TOCPlugin(Plugin):
    def install(self, slide):
        slide.hooks.register(BEFORE_ANALYZE, collect_headers)
        slide.hooks.register(AFTER_ANALYZE, insert_toc)
```

### 3. 型安全性

| 方向性 | 型安全性 | 理由 |
|--------|---------|------|
| A | ★★★★☆ | Protocol で型が明示される。ただし ctx.plugins は dict |
| B | ★★☆☆☆ | Component.props は dict[str, Any] で何でも入る |
| C | ★★★☆☆ | イベントデータは dict だが、イベント型は Enum で明確 |

### 4. 拡張の柔軟性

| 拡張内容 | A: Protocol | B: Composition | C: Hook |
|----------|------------|----------------|---------|
| 予期しない用途 | △<br/>Protocol に縛られる | ◎<br/>Transform で何でもできる | ○<br/>Hook で介入可能 |
| レンダリングパイプライン変更 | △<br/>フレームワーク側の変更が必要 | ◎<br/>カスタムレンダラーを登録 | ○<br/>イベントで介入 |
| プラグイン間の連携 | ○<br/>ctx.plugins 経由 | △<br/>slide.plugins の順序に依存 | ◎<br/>イベント優先度で制御 |
| デバッグのしやすさ | ○<br/>各フェーズが明確 | △<br/>どの Transform が何をしたか追いづらい | ◎<br/>イベントログを取れる |

### 5. パフォーマンス

| 方向性 | レンダリング速度 | メモリ使用量 | 理由 |
|--------|---------------|------------|------|
| A | ★★★★☆ | ★★★★☆ | 最小限の処理 |
| B | ★★★☆☆ | ★★★☆☆ | Transform で木を複製する可能性 |
| C | ★★☆☆☆ | ★★★★☆ | イベント発火のオーバーヘッド |

### 6. ユーザーが書くコード量

典型的なプラグインの実装を比較：

**A: Protocol - 約20行**
```python
class MyPlugin:
    def preprocess(self, slide): ...

@dataclass
class MyComponent:
    def render(self, ctx): ...
```

**B: Composition - 約15行**
```python
def my_plugin():
    def plugin(slide):
        ...
    return plugin
```

**C: Hook - 約25行**
```python
class MyPlugin(Plugin):
    def install(self, slide):
        def hook(event): ...
        slide.hooks.register(EventType.X, hook)
```

### 7. 学習曲線

| 方向性 | 初学者 | 理解すべき概念 |
|--------|--------|-------------|
| A | ★★★☆☆ | Protocol, analyze/render フェーズ |
| B | ★★★★☆ | 関数合成, Transform の概念 |
| C | ★★☆☆☆ | イベント駆動, フックの概念, 優先度 |

## ハイブリッド案の可能性

3つの方向性の良いところを組み合わせることも可能：

### 案D: 階層型ハイブリッド

```python
# レイヤー1: コアは Composition（柔軟性重視）
Component = データクラス
Transform = 関数

# レイヤー2: プラグインは Hook（制御性重視）
Plugin クラス + イベントシステム

# レイヤー3: ユーザー向けは Protocol（使いやすさ重視）
明確な拡張ポイント定義
```

この場合：
- ユーザーは Protocol に従って簡単に拡張
- 高度なユーザーは Hook や Transform を直接使う
- コアは Composition でシンプルに保つ

## 議論ポイント

1. **ユーザー層をどう想定するか**
   - 初学者向け？ → Protocol ベースが良い
   - 上級者向け？ → Composition が柔軟
   - 両方？ → ハイブリッド

2. **拡張の予測可能性 vs 柔軟性**
   - 予測可能性重視（Protocol/Hook）
   - 柔軟性重視（Composition）

3. **デバッグのしやすさ**
   - Hook システムはデバッグプラグインが作りやすい
   - Composition は純粋関数でテストしやすい

4. **エコシステムの育てやすさ**
   - Protocol: 明確な規約があるのでプラグイン共有しやすい
   - Composition: 自由度が高いが規約が曖昧
   - Hook: イベント体系が明確なので標準化しやすい

5. **実装の簡潔さ vs 表現力**
   - シンプルに保つ → Protocol
   - 表現力重視 → Composition
   - バランス → Hook

どの方向性が良いか、あるいはハイブリッドにするか、
具体的なユースケースを想定しながら議論したいです。
