"""
Advanced Usage Example

データ可視化とプログラム実行の例。
"""

from yogrt import create_slide, Page, Header, Text, Image, TwoColumn, Code
import matplotlib.pyplot as plt
import numpy as np

# スライド作成
slide = create_slide()

# タイトル
slide.add_page(Page(
    Header("Data Analysis Example", level=1),
    Text("Demonstrating matplotlib integration")
))

# データ生成とプロット
np.random.seed(42)
data = np.random.randn(1000)

fig1, ax1 = plt.subplots(figsize=(8, 6))
ax1.hist(data, bins=30, alpha=0.7, color='blue')
ax1.set_title("Normal Distribution")
ax1.set_xlabel("Value")
ax1.set_ylabel("Frequency")

slide.add_page(Page(
    Header("Distribution Analysis", level=1),
    TwoColumn(
        Text(f"""
Statistical Summary:
• Mean: {data.mean():.2f}
• Std Dev: {data.std():.2f}
• Min: {data.min():.2f}
• Max: {data.max():.2f}
        """),
        Image(fig1, caption="Histogram of random data")
    )
))

plt.close(fig1)

# 時系列データ
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

fig2, ax2 = plt.subplots(figsize=(8, 6))
ax2.plot(x, y1, label='sin(x)', linewidth=2)
ax2.plot(x, y2, label='cos(x)', linewidth=2)
ax2.legend()
ax2.set_title("Trigonometric Functions")
ax2.set_xlabel("x")
ax2.set_ylabel("y")
ax2.grid(True, alpha=0.3)

slide.add_page(Page(
    Header("Time Series", level=1),
    Image(fig2, caption="sin(x) and cos(x)"),
    Code("""
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
plt.plot(x, y1, label='sin(x)')
plt.plot(x, y2, label='cos(x)')
    """, lang="python")
))

plt.close(fig2)

# Export
slide.export("advanced_example.html")
print("✓ Slide exported to advanced_example.html")
