"""
Example: Using Transforms to Modify Component Trees

This example demonstrates how transforms can modify the component tree
before rendering, enabling powerful preprocessing capabilities.
"""

from yogrt import create_slide, Page, Header, Text, List, Component, walk
from yogrt.core import (
    HeaderComponent, TextComponent, ListComponent, CodeComponent, PageComponent
)
from typing import Any
from dataclasses import replace
# ============================================================================
# Transform 1: Auto-generate IDs for Headers
# ============================================================================

def auto_id_transform(component: Component) -> Component:
    """
    Automatically generates IDs for headers based on their text

    This allows easy linking within the presentation.
    """
    if not isinstance(component, HeaderComponent):
        return component

    # Get header text and generate ID
    text = component.text
    # Convert to lowercase, replace spaces with hyphens
    auto_id = text.lower().replace(' ', '-').replace('?', '').replace('!', '')

    # Add ID only if not already set
    if not component.id:  # Don't override existing IDs
        return replace(component, id=auto_id)

    return component
# ============================================================================
# Transform 2: Add CSS Classes Based on Content
# ============================================================================

def style_by_content_transform(component: Component) -> Component:
    """
    Adds CSS classes to components based on their content

    For example, text containing "important" gets a special class.
    """
    if not isinstance(component, TextComponent):
        return component

    content = component.content

    # Check for special keywords
    if 'important' in content.lower():
        class_value = component.class_name + ' important-text' if component.class_name else 'important-text'
        return replace(component, class_name=class_value.strip())
    elif 'note' in content.lower():
        class_value = component.class_name + ' note-text' if component.class_name else 'note-text'
        return replace(component, class_name=class_value.strip())

    return component
# ============================================================================
# Transform 3: Uppercase All Headers
# ============================================================================

def uppercase_headers_transform(component: Component) -> Component:
    """
    Converts all header text to uppercase

    Demonstrates simple text transformation.
    """
    if not isinstance(component, HeaderComponent):
        return component

    text = component.text
    return replace(component, text=text.upper())
# ============================================================================
# Transform 4: Add Numbering to List Items
# ============================================================================

counter = {'value': 0}

def numbered_list_transform(component: Component) -> Component:
    """
    Adds automatic numbering to list items

    Note: This is simplified - ListComponent already has ordered=True support.
    This is mainly for demonstration purposes.
    """
    if isinstance(component, ListComponent):
        counter['value'] = 0
        return component

    # Simplified - in practice you'd track parent context
    if isinstance(component, TextComponent):
        counter['value'] += 1
        content = component.content
        new_content = f"{counter['value']}. {content}"
        return replace(component, content=new_content)

    return component
# ============================================================================
# Transform 5: Wrap Code Blocks with Labels
# ============================================================================

def label_code_transform(component: Component) -> Component:
    """
    Adds language labels to code blocks

    Note: This would wrap code components in a container with a language label.
    Simplified for the new API - code blocks already show language in renderer.
    """
    if not isinstance(component, CodeComponent):
        return component

    # CodeComponent already has lang attribute shown by default renderer
    # This transform is kept simple for demonstration
    return component
# ============================================================================
# Transform 6: Expand Abbreviations
# ============================================================================

ABBREVIATIONS = {
    'API': 'Application Programming Interface',
    'HTML': 'HyperText Markup Language',
    'CSS': 'Cascading Style Sheets',
    'JS': 'JavaScript'
}

def expand_abbreviations_transform(component: Component) -> Component:
    """
    Expands common abbreviations with tooltips

    Replaces abbreviations with HTML that shows full text on hover.
    """
    if not isinstance(component, TextComponent):
        return component

    content = component.content

    for abbr, full in ABBREVIATIONS.items():
        if abbr in content:
            # Replace with HTML abbr tag
            content = content.replace(
                abbr,
                f'<abbr title="{full}" style="cursor:help;text-decoration:underline dotted;">{abbr}</abbr>'
            )

    return replace(component, content=content)
# ============================================================================
# Create Slides with Different Transforms
# ============================================================================

def main():
    # Example 1: Auto-ID Transform
    slide1 = create_slide()
    slide1.add_transform(auto_id_transform)

    slide1.add_page(Page(
        Header("Transforms Demo", level=1),
        Text("Demonstrating auto-generated header IDs")
    ))

    slide1.add_page(Page(
        Header("What are Transforms?", level=2),
        Text("Transforms modify the component tree before rendering."),
        Text("This enables powerful preprocessing capabilities.")
    ))

    slide1.export("transforms_auto_id.html")
    print("✓ Generated: transforms_auto_id.html")
    # Example 2: Multiple Transforms
    slide2 = create_slide()

    # Add custom CSS via HTML transform
    def add_style_css(html: str) -> str:
        custom_css = """
        <style>
        .important-text {
            background-color: #fef08a;
            padding: 0.5rem;
            border-left: 4px solid #f59e0b;
            display: block;
            margin: 0.5rem 0;
        }
        .note-text {
            background-color: #dbeafe;
            padding: 0.5rem;
            border-left: 4px solid #3b82f6;
            display: block;
            margin: 0.5rem 0;
        }
        </style>
        """
        return html.replace('</head>', f'{custom_css}</head>')

    slide2.add_html_transform(add_style_css)
    slide2.add_transform(style_by_content_transform)
    slide2.add_transform(auto_id_transform)

    slide2.add_page(Page(
        Header("Styled Content", level=1),
        Text("This is regular text."),
        Text("Important: This text contains the word 'important' and gets styled!"),
        Text("Note: This is a note and gets different styling.")
    ))

    slide2.export("transforms_styled.html")
    print("✓ Generated: transforms_styled.html")
    # Example 3: Uppercase Transform
    slide3 = create_slide()
    slide3.add_transform(uppercase_headers_transform)

    slide3.add_page(Page(
        Header("This header will be uppercase", level=1),
        Text("But this text remains lowercase.")
    ))

    slide3.add_page(Page(
        Header("Another uppercase header", level=2),
        Text("Transforms are applied to all pages uniformly.")
    ))

    slide3.export("transforms_uppercase.html")
    print("✓ Generated: transforms_uppercase.html")
    # Example 4: Abbreviation Expansion
    slide4 = create_slide()
    slide4.add_transform(expand_abbreviations_transform)

    slide4.add_page(Page(
        Header("Abbreviation Expansion", level=1),
        Text("Modern web development uses HTML, CSS, and JS."),
        Text("API design is important for backend systems."),
        Text("Hover over abbreviations to see their full meaning!")
    ))

    slide4.export("transforms_abbreviations.html")
    print("✓ Generated: transforms_abbreviations.html")
    # Example 5: Code Label Transform
    slide5 = create_slide()
    slide5.add_transform(label_code_transform)

    from yogrt import Code

    slide5.add_page(Page(
        Header("Labeled Code Blocks", level=1),
        Text("Code blocks now have language labels:"),
        Code("def hello():\n    print('Hello, world!')", lang="python"),
        Code("const x = 42;", lang="javascript")
    ))

    slide5.export("transforms_code_labels.html")
    print("✓ Generated: transforms_code_labels.html")
    # Example 6: Combining Multiple Transforms
    slide6 = create_slide()

    # Apply multiple transforms in order
    slide6.add_transform(auto_id_transform)
    slide6.add_transform(expand_abbreviations_transform)
    slide6.add_transform(style_by_content_transform)

    # Add custom CSS via HTML transform
    def add_combined_css(html: str) -> str:
        custom_css = """
        <style>
        .important-text {
            background-color: #fef08a;
            padding: 0.5rem;
            border-left: 4px solid #f59e0b;
            display: block;
            margin: 0.5rem 0;
        }
        </style>
        """
        return html.replace('</head>', f'{custom_css}</head>')

    slide6.add_html_transform(add_combined_css)

    slide6.add_page(Page(
        Header("Combined Transforms", level=1),
        Text("This demonstrates multiple transforms working together.")
    ))

    slide6.add_page(Page(
        Header("Web Technologies", level=2),
        Text("Important: Understanding HTML, CSS, and API design is crucial."),
        Text("These are the building blocks of modern web development.")
    ))

    slide6.export("transforms_combined.html")
    print("✓ Generated: transforms_combined.html")
if __name__ == "__main__":
    main()
