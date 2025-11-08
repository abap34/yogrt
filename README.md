# Yogrt 🥛

**Programmable Slide Framework with Lisp-like Philosophy**

Yogrt is a Python-based slide framework that treats slides as code. Inspired by Lisp's elegant simplicity, Yogrt provides minimal primitives that compose into powerful slide presentations.

## Features

- 🎯 **Programmable**: Write slides as Python code
- 🔧 **Extensible**: Infinite customization through plugins and transforms
- 🪶 **Simple**: Minimal core with 3 primitives
- 🧩 **Composable**: Build complex slides from small parts
- 📊 **Data-Friendly**: Direct matplotlib/pandas integration
- 🎨 **Customizable**: Full control over rendering
- 🔍 **Type-Safe**: Strict mypy type checking
- ✅ **Well-Tested**: 95% test coverage

## Philosophy

Yogrt adopts Lisp's design principles:

1. **Minimal Primitives**: Everything built from `Component`, `render`, and `transform`
2. **Code as Data**: Components are plain Python dicts (like S-expressions)
3. **Functions First**: Everything is a function, no complex OOP
4. **Immutability**: Predictable transformations

## Installation

```bash
# Clone the repository
git clone https://github.com/abap34/yogrt.git
cd yogrt

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

## Quick Start

```python
from yogrt import create_slide, Page, Header, Text

slide = create_slide()

slide.add_page(Page(
    Header("Hello, Yogrt!", level=1),
    Text("A programmable slide framework")
))

slide.export("output.html")
```

## Basic Example

```python
from yogrt import create_slide, Page, Header, Text, TwoColumn, List

slide = create_slide()

# Title page
slide.add_page(Page(
    Header("My Presentation", level=1),
    Text("Author: Your Name")
))

# Content with layout
slide.add_page(Page(
    Header("Key Points", level=1),
    TwoColumn(
        List(
            "First point",
            "Second point",
            "Third point"
        ),
        Text("Details on the right side")
    )
))

slide.export("presentation.html")
```

## Data Visualization

```python
import matplotlib.pyplot as plt
import numpy as np
from yogrt import create_slide, Page, Header, Image

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title("Sine Wave")

# Add to slide - matplotlib figures are automatically converted to base64
slide = create_slide()
slide.add_page(Page(
    Header("Data Visualization", level=1),
    Image(fig, caption="sin(x) from 0 to 10")
))

slide.export("data_viz.html")
```

## Architecture

Yogrt's core consists of three primitives:

### 1. Component (Data)

```python
Component = {
    'tag': str,           # Component type
    'props': dict,        # Properties
    'children': list,     # Child components
}
```

All slide elements are represented as plain Python dictionaries, similar to Lisp's S-expressions.

### 2. Renderer (Component → HTML)

```python
def my_renderer(component: Component, context: Context) -> str:
    content = component['props']['content']
    return f"<div>{content}</div>"
```

Renderers convert components into HTML strings. This is analogous to Lisp's `eval`.

### 3. Transform (Component → Component)

```python
def my_transform(component: Component) -> Component:
    # Modify component tree
    props = component.get('props', {})
    props['class'] = 'styled'
    return {**component, 'props': props}
```

Transforms perform Component → Component conversions. This is analogous to Lisp's macro expansion.

## Creating Custom Components

```python
from yogrt import Component
from typing import Any

def Alert(message: str, level: str = "info", **props: Any) -> Component:
    return {
        'tag': 'alert',
        'props': {'message': message, 'level': level, **props},
        'children': []
    }

# Register renderer
def render_alert(comp: Component, ctx: Context) -> str:
    message = comp['props']['message']
    level = comp['props']['level']
    return f'<div class="alert alert-{level}">{message}</div>'

slide = create_slide()
slide.add_renderer('alert', render_alert)

# Use it
slide.add_page(Page(
    Alert("Important message!", level="warning")
))
```

## Creating Plugins

Plugins are `Slide → Slide` functions that encapsulate reusable functionality:

```python
from yogrt import Slide, Plugin

def my_plugin(option: str) -> Plugin:
    def plugin(slide: Slide) -> Slide:
        # Add custom renderer
        slide.add_renderer('my-tag', my_renderer)

        # Add transform
        slide.add_transform(my_transform)

        # Add HTML transform
        slide.add_html_transform(lambda html: html + "<!-- custom -->")

        return slide
    return plugin

# Use plugin
slide = create_slide()
slide.use(my_plugin(option="value"))
```

## Available Components

### Basic Components
- **Text**: Paragraph text
- **Header**: Headings (h1-h6)
- **Image**: Images (supports file paths, URLs, matplotlib figures)
- **Code**: Code blocks with syntax highlighting
- **Link**: Hyperlinks

### Layout Components
- **Page**: Slide page container
- **VStack**: Vertical stack layout
- **HStack**: Horizontal stack layout
- **TwoColumn**: Two-column layout
- **Grid**: Grid layout
- **Container**: Generic container

### List Components
- **List**: Unordered/ordered lists

### Special Components
- **RawHtml**: Direct HTML insertion
- **Spacer**: Vertical spacing
- **Divider**: Horizontal divider

## Project Structure

```
yogrt/
├── yogrt/
│   ├── core.py          # Core primitives (Component, render, transform, walk)
│   ├── slide.py         # Slide container and export
│   ├── components.py    # Standard components (15 components)
│   ├── renderers.py     # Standard renderers
│   └── __init__.py      # Public API
├── examples/
│   ├── basic.py         # Basic usage example
│   └── advanced.py      # Data visualization example
├── tests/
│   ├── test_core.py                      # Core tests (19 tests, 100% coverage)
│   ├── test_slide.py                     # Slide tests (16 tests, 100% coverage)
│   └── test_components_and_renderers.py  # Component tests (38 tests)
├── SPECIFICATION.md     # Complete specification
├── pyproject.toml       # Project configuration (uv, mypy, pytest)
└── README.md           # This file
```

## Development

```bash
# Install with dev dependencies using uv
uv pip install -e .

# Run tests
pytest

# Run tests with coverage
pytest --cov=yogrt --cov-report=term-missing

# Type checking (strict mode)
mypy yogrt

# All tests must pass, all types must check
```

### Development Requirements

- Python 3.10+
- uv (recommended) or pip
- pytest for testing
- mypy for type checking
- matplotlib (optional, for data visualization)

## Why "Yogrt"?

The name comes from "Yogurt" (ヨーグルト), representing something:
- **Simple and pure** (like Lisp)
- **Healthy and natural** (minimal dependencies)
- **Customizable** (add your own toppings/plugins)

The unconventional spelling makes it unique and easy to search.

## Comparison with Other Tools

| Feature | Yogrt | Marp | reveal.js | PowerPoint |
|---------|-------|------|-----------|------------|
| Programmable | ✅ | Partial | Partial | ❌ |
| Python Integration | ✅ | ❌ | ❌ | ❌ |
| Git-friendly | ✅ | ✅ | ✅ | ❌ |
| Extensible | ✅ | Limited | Limited | ❌ |
| Data Visualization | ✅ | ❌ | Partial | Partial |
| Type-Safe | ✅ | ❌ | ❌ | ❌ |
| Functional | ✅ | ❌ | ❌ | ❌ |

## Examples

See the `examples/` directory for complete working examples:

- **basic.py**: Basic slide creation with text, headers, and layouts
- **advanced.py**: Data visualization with matplotlib integration

Run examples:
```bash
cd examples
python basic.py      # Generates basic_example.html
python advanced.py   # Generates advanced_example.html
```

## Design Philosophy

For a deep dive into the design philosophy and technical specification, see:

- 📖 [Complete Specification](SPECIFICATION.md) - 6000+ lines of detailed documentation
- 📊 [Design Alternatives](user_rendering_extensions.md) - Comparison of design approaches

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass (`pytest`)
5. Ensure type checking passes (`mypy yogrt`)
6. Submit a pull request

## Links

- 🐛 [Issue Tracker](https://github.com/abap34/yogrt/issues)
- 💬 [Discussions](https://github.com/abap34/yogrt/discussions)

---

Made with ❤️ and functional programming
