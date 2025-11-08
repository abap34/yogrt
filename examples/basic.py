"""
Basic Usage Example

Yogrt の基本的な使い方を示す例。
"""

from yogrt import create_slide, Page, Header, Text, Image, TwoColumn, List

# スライド作成
slide = create_slide()

# タイトルページ
slide.add_page(Page(
    Header("Yogrt: Programmable Slides", level=1),
    Text("A Lisp-inspired slide framework"),
    Text("Built with Python")
))

# Introduction
slide.add_page(Page(
    Header("Why Yogrt?", level=1),
    List(
        "Programmable: Write slides as Python code",
        "Extensible: Infinite customization through plugins",
        "Simple: Minimal core with powerful primitives",
        "Composable: Build complex slides from small parts"
    )
))

# Two Column Layout
slide.add_page(Page(
    Header("Two Column Layout", level=1),
    TwoColumn(
        Text("Left column content"),
        Text("Right column content")
    )
))

# Export
slide.export("basic_example.html")
print("✓ Slide exported to basic_example.html")
