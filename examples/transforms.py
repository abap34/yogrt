"""
Example: Using Transforms to Modify Component Trees

This example demonstrates how transforms can modify the component tree
before rendering, enabling powerful preprocessing capabilities.
"""

from yogrt import create_slide, Page, Header, Text, List, Component, walk
from typing import Any


# ============================================================================
# Transform 1: Auto-generate IDs for Headers
# ============================================================================

def auto_id_transform(component: Component) -> Component:
    """
    Automatically generates IDs for headers based on their text

    This allows easy linking within the presentation.
    """
    if component.get('tag') != 'header':
        return component

    # Get header text and generate ID
    text = component['props'].get('text', '')
    # Convert to lowercase, replace spaces with hyphens
    auto_id = text.lower().replace(' ', '-').replace('?', '').replace('!', '')

    # Add ID to props
    props = component.get('props', {})
    if 'id' not in props:  # Don't override existing IDs
        props['id'] = auto_id

    return {**component, 'props': props}


# ============================================================================
# Transform 2: Add CSS Classes Based on Content
# ============================================================================

def style_by_content_transform(component: Component) -> Component:
    """
    Adds CSS classes to components based on their content

    For example, text containing "important" gets a special class.
    """
    if component.get('tag') != 'text':
        return component

    content = component['props'].get('content', '')
    props = component.get('props', {})

    # Check for special keywords
    if 'important' in content.lower():
        props['class'] = props.get('class', '') + ' important-text'
    elif 'note' in content.lower():
        props['class'] = props.get('class', '') + ' note-text'

    return {**component, 'props': props}


# ============================================================================
# Transform 3: Uppercase All Headers
# ============================================================================

def uppercase_headers_transform(component: Component) -> Component:
    """
    Converts all header text to uppercase

    Demonstrates simple text transformation.
    """
    if component.get('tag') != 'header':
        return component

    props = component.get('props', {})
    text = props.get('text', '')
    props['text'] = text.upper()

    return {**component, 'props': props}


# ============================================================================
# Transform 4: Add Numbering to List Items
# ============================================================================

counter = {'value': 0}

def numbered_list_transform(component: Component) -> Component:
    """
    Adds automatic numbering to list items

    Note: This is a stateful transform for demonstration.
    In production, use Context for state management.
    """
    if component.get('tag') == 'list':
        counter['value'] = 0

    if component.get('tag') == 'text' and component in []:
        # This is simplified - in practice you'd check parent
        counter['value'] += 1
        props = component.get('props', {})
        content = props.get('content', '')
        props['content'] = f"{counter['value']}. {content}"
        return {**component, 'props': props}

    return component


# ============================================================================
# Transform 5: Wrap Code Blocks with Labels
# ============================================================================

def label_code_transform(component: Component) -> Component:
    """
    Adds language labels to code blocks

    Wraps code components in a container with a language label.
    """
    if component.get('tag') != 'code':
        return component

    lang = component['props'].get('lang', 'text')

    # Create a container with label
    label: Component = {
        'tag': 'raw-html',
        'props': {'html': f'<div style="background:#374151;color:#fff;padding:0.25rem 0.5rem;font-size:0.75rem;border-radius:4px 4px 0 0;display:inline-block;">{lang.upper()}</div>'},
        'children': []
    }

    # Wrap in container
    return {
        'tag': 'container',
        'props': {'class': 'code-with-label'},
        'children': [label, component]
    }


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
    if component.get('tag') != 'text':
        return component

    content = component['props'].get('content', '')

    for abbr, full in ABBREVIATIONS.items():
        if abbr in content:
            # Replace with HTML abbr tag
            content = content.replace(
                abbr,
                f'<abbr title="{full}" style="cursor:help;text-decoration:underline dotted;">{abbr}</abbr>'
            )

    props = component.get('props', {})
    props['content'] = content

    return {**component, 'props': props}


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

    # Add custom CSS for styled classes
    slide2.context.store['custom_css'] = """
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
    """

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

    slide6.context.store['custom_css'] = """
        .important-text {
            background-color: #fef08a;
            padding: 0.5rem;
            border-left: 4px solid #f59e0b;
            display: block;
            margin: 0.5rem 0;
        }
    """

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
