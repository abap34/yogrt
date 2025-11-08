# Yogrt 🥛

**Lisp 哲学に基づくプログラマブルスライドフレームワーク**

Yogrt は、スライドをコードとして扱う Python ベースのスライドフレームワークです。Lisp のエレガントなシンプルさにインスパイアされ、最小限のプリミティブから強力なスライドプレゼンテーションを構築します。

## 特徴

- 🎯 **プログラマブル**: Python コードでスライドを記述
- 🔧 **拡張可能**: プラグインとトランスフォームによる無限のカスタマイズ
- 🪶 **シンプル**: 3つのプリミティブのみで構成されたコア
- 🧩 **コンポーザブル**: 小さなパーツから複雑なスライドを構築
- 📊 **データフレンドリー**: matplotlib/pandas との直接統合
- 🎨 **カスタマイズ可能**: レンダリングの完全なコントロール
- 🔍 **型安全**: 厳密な mypy 型チェック
- ✅ **十分なテスト**: 95% のテストカバレッジ

## 哲学

Yogrt は Lisp の設計原則を採用しています:

1. **最小限のプリミティブ**: すべてが `Component`、`render`、`transform` から構築される
2. **コードはデータ**: コンポーネントは単純な Python の辞書（S式のように）
3. **関数優先**: すべてが関数、複雑な OOP は不要
4. **不変性**: 予測可能な変換

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/abap34/yogrt.git
cd yogrt

# uv でインストール（推奨）
uv pip install -e .

# または pip で
pip install -e .
```

## クイックスタート

```python
from yogrt import create_slide, Page, Header, Text

slide = create_slide()

slide.add_page(Page(
    Header("Hello, Yogrt!", level=1),
    Text("プログラマブルスライドフレームワーク")
))

slide.export("output.html")
```

## 基本的な例

```python
from yogrt import create_slide, Page, Header, Text, TwoColumn, List

slide = create_slide()

# タイトルページ
slide.add_page(Page(
    Header("プレゼンテーション", level=1),
    Text("著者: あなたの名前")
))

# レイアウト付きコンテンツ
slide.add_page(Page(
    Header("要点", level=1),
    TwoColumn(
        List(
            "第一のポイント",
            "第二のポイント",
            "第三のポイント"
        ),
        Text("右側に詳細")
    )
))

slide.export("presentation.html")
```

## データビジュアライゼーション

```python
import matplotlib.pyplot as plt
import numpy as np
from yogrt import create_slide, Page, Header, Image

# データ生成
x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title("Sine Wave")

# スライドに追加 - matplotlib の Figure は自動的に base64 に変換される
slide = create_slide()
slide.add_page(Page(
    Header("データビジュアライゼーション", level=1),
    Image(fig, caption="0 から 10 までの sin(x)")
))

slide.export("data_viz.html")
```

## アーキテクチャ

Yogrt のコアは3つのプリミティブから構成されています:

### 1. Component (データ)

```python
Component = {
    'tag': str,           # コンポーネントタイプ
    'props': dict,        # プロパティ
    'children': list,     # 子コンポーネント
}
```

すべてのスライド要素は、Lisp の S 式のように、単純な Python の辞書として表現されます。

### 2. Renderer (Component → HTML)

```python
def my_renderer(component: Component, context: Context) -> str:
    content = component['props']['content']
    return f"<div>{content}</div>"
```

レンダラーはコンポーネントを HTML 文字列に変換します。これは Lisp の `eval` に相当します。

### 3. Transform (Component → Component)

```python
def my_transform(component: Component) -> Component:
    # コンポーネントツリーを変更
    props = component.get('props', {})
    props['class'] = 'styled'
    return {**component, 'props': props}
```

トランスフォームは Component → Component の変換を行います。これは Lisp のマクロ展開に相当します。

## カスタムコンポーネントの作成

```python
from yogrt import Component
from typing import Any

def Alert(message: str, level: str = "info", **props: Any) -> Component:
    return {
        'tag': 'alert',
        'props': {'message': message, 'level': level, **props},
        'children': []
    }

# レンダラーを登録
def render_alert(comp: Component, ctx: Context) -> str:
    message = comp['props']['message']
    level = comp['props']['level']
    return f'<div class="alert alert-{level}">{message}</div>'

slide = create_slide()
slide.add_renderer('alert', render_alert)

# 使用
slide.add_page(Page(
    Alert("重要なメッセージ！", level="warning")
))
```

## プラグインの作成

プラグインは `Slide → Slide` 関数で、再利用可能な機能をカプセル化します:

```python
from yogrt import Slide, Plugin

def my_plugin(option: str) -> Plugin:
    def plugin(slide: Slide) -> Slide:
        # カスタムレンダラーを追加
        slide.add_renderer('my-tag', my_renderer)

        # トランスフォームを追加
        slide.add_transform(my_transform)

        # HTML トランスフォームを追加
        slide.add_html_transform(lambda html: html + "<!-- custom -->")

        return slide
    return plugin

# プラグインを使用
slide = create_slide()
slide.use(my_plugin(option="value"))
```

## 利用可能なコンポーネント

### 基本コンポーネント
- **Text**: 段落テキスト
- **Header**: 見出し (h1-h6)
- **Image**: 画像（ファイルパス、URL、matplotlib の Figure をサポート）
- **Code**: シンタックスハイライト付きコードブロック
- **Link**: ハイパーリンク

### レイアウトコンポーネント
- **Page**: スライドページコンテナ
- **VStack**: 垂直スタックレイアウト
- **HStack**: 水平スタックレイアウト
- **TwoColumn**: 2カラムレイアウト
- **Grid**: グリッドレイアウト
- **Container**: 汎用コンテナ

### リストコンポーネント
- **List**: 順序なし/順序付きリスト

### 特殊コンポーネント
- **RawHtml**: 直接 HTML 挿入
- **Spacer**: 垂直スペース
- **Divider**: 水平区切り線

## プロジェクト構造

```
yogrt/
├── yogrt/
│   ├── core.py          # コアプリミティブ (Component, render, transform, walk)
│   ├── slide.py         # Slide コンテナとエクスポート
│   ├── components.py    # 標準コンポーネント (15個のコンポーネント)
│   ├── renderers.py     # 標準レンダラー
│   └── __init__.py      # 公開 API
├── examples/
│   ├── basic.py         # 基本的な使用例
│   └── advanced.py      # データビジュアライゼーション例
├── tests/
│   ├── test_core.py                      # コアテスト (19テスト、100%カバレッジ)
│   ├── test_slide.py                     # Slide テスト (16テスト、100%カバレッジ)
│   └── test_components_and_renderers.py  # コンポーネントテスト (38テスト)
├── SPECIFICATION.md     # 完全な仕様書
├── pyproject.toml       # プロジェクト設定 (uv, mypy, pytest)
└── README.md           # このファイル
```

## 開発

```bash
# uv で開発依存関係を含めてインストール
uv pip install -e .

# テストを実行
pytest

# カバレッジ付きでテストを実行
pytest --cov=yogrt --cov-report=term-missing

# 型チェック（厳密モード）
mypy yogrt

# すべてのテストが通過し、すべての型がチェックされる必要があります
```

### 開発要件

- Python 3.10+
- uv（推奨）または pip
- pytest（テスト用）
- mypy（型チェック用）
- matplotlib（オプション、データビジュアライゼーション用）

## なぜ "Yogrt"?

名前は「ヨーグルト」に由来し、以下を表しています:
- **シンプルで純粋**（Lisp のように）
- **健康的で自然**（最小限の依存関係）
- **カスタマイズ可能**（自分のトッピング/プラグインを追加）

慣習的でないスペルにより、ユニークで検索しやすくなっています。

## 他のツールとの比較

| 機能 | Yogrt | Marp | reveal.js | PowerPoint |
|---------|-------|------|-----------|------------|
| プログラマブル | ✅ | 部分的 | 部分的 | ❌ |
| Python 統合 | ✅ | ❌ | ❌ | ❌ |
| Git フレンドリー | ✅ | ✅ | ✅ | ❌ |
| 拡張可能 | ✅ | 限定的 | 限定的 | ❌ |
| データビジュアライゼーション | ✅ | ❌ | 部分的 | 部分的 |
| 型安全 | ✅ | ❌ | ❌ | ❌ |
| 関数型 | ✅ | ❌ | ❌ | ❌ |

## サンプル

完全に動作するサンプルについては `examples/` ディレクトリを参照してください:

- **basic.py**: テキスト、見出し、レイアウトを使った基本的なスライド作成
- **advanced.py**: matplotlib 統合によるデータビジュアライゼーション

サンプルの実行:
```bash
cd examples
python basic.py      # basic_example.html を生成
python advanced.py   # advanced_example.html を生成
```

## 設計哲学

設計哲学と技術仕様の詳細については、以下を参照してください:

- 📖 [完全な仕様書](SPECIFICATION.md) - 6000行以上の詳細なドキュメント
- 📊 [設計代替案](user_rendering_extensions.md) - 設計アプローチの比較

## ライセンス

MIT License - LICENSE ファイルを参照

## 貢献

貢献を歓迎します！以下の手順に従ってください:

1. リポジトリをフォーク
2. 機能ブランチを作成
3. 新機能のテストを記述
4. すべてのテストが通過することを確認（`pytest`）
5. 型チェックが通過することを確認（`mypy yogrt`）
6. プルリクエストを送信

## リンク

- 🐛 [Issue Tracker](https://github.com/abap34/yogrt/issues)
- 💬 [Discussions](https://github.com/abap34/yogrt/discussions)

---

❤️ と関数型プログラミングで作成
