"""
Example: Presentation Mode with Navigation and Speaker Notes

This example demonstrates the slide navigation and speaker notes plugins.

Features:
- Full-screen slides with arrow key navigation
- Speaker notes (press 'P' to toggle presenter view)
- Smooth transitions between slides
- Page indicators
"""

from yogrt import (
    create_slide,
    Page,
    Header,
    Text,
    List,
    Code,
    TwoColumn,
    VStack,
    Image,
    slide_navigation_plugin,
    speaker_notes_plugin,
    syntax_highlighting_plugin,
    SpeakerNote,
)


def main():
    # Create slide with all presentation plugins
    slide = create_slide()

    # Enable navigation, speaker notes, and syntax highlighting
    slide.use(slide_navigation_plugin())
    slide.use(speaker_notes_plugin())
    slide.use(syntax_highlighting_plugin('atom-one-dark'))

    # Page 1: Title Slide
    slide.add_page(Page(
        VStack(
            Header("Yogrt Presentation", level=1),
            Text("A Programmable Slide Framework"),
            Text("Press → or ← to navigate"),
            Text("Press 'P' for presenter view"),
            gap="2rem"
        ),
        SpeakerNote("Welcome! This is the title slide. Remember to introduce yourself and the topic.")
    ))

    # Page 2: Features
    slide.add_page(Page(
        Header("Key Features", level=2),
        List(
            "Programmable: Write slides as Python code",
            "Composable: Build complex layouts from simple components",
            "Type-safe: Full mypy type checking",
            "Extensible: Easy to add custom components and plugins"
        ),
        SpeakerNote("Talk about each feature for about 1 minute. Emphasize the programmability aspect.")
    ))

    # Page 3: Code Example
    slide.add_page(Page(
        Header("Simple Example", level=2),
        Text("Creating a slide is as easy as:"),
        Code('''from yogrt import create_slide, Page, Header, Text

slide = create_slide()
slide.add_page(Page(
    Header("My Slide", level=1),
    Text("Hello, World!")
))
slide.export("output.html")''', lang="python"),
        SpeakerNote("Walk through the code line by line. Show how simple the API is.")
    ))

    # Page 4: Two Column Layout
    slide.add_page(Page(
        Header("Flexible Layouts", level=2),
        TwoColumn(
            VStack(
                Header("Built-in Components", level=3),
                List(
                    "Text & Headers",
                    "Images & Code",
                    "Lists & Grids",
                    "Containers"
                )
            ),
            VStack(
                Header("Layout Options", level=3),
                List(
                    "VStack: Vertical",
                    "HStack: Horizontal",
                    "TwoColumn: Side-by-side",
                    "Grid: Flexible grid"
                )
            )
        ),
        SpeakerNote("Demonstrate how layouts can be nested. Maybe show a live demo if time permits.")
    ))

    # Page 5: Advanced Features
    slide.add_page(Page(
        Header("Advanced Features", level=2),
        Text("Yogrt includes powerful features:"),
        List(
            "Footnotes with automatic collection",
            "Bibliography and citations",
            "Auto-generated table of contents",
            "Custom transforms and plugins",
            ordered=True
        ),
        SpeakerNote("These features were added in the latest update. Mention that they work seamlessly with the component system.")
    ))

    # Page 6: Plugin System
    slide.add_page(Page(
        Header("Plugin System", level=2),
        Text("Extend Yogrt with plugins:"),
        Code('''slide.use(slide_navigation_plugin())
slide.use(speaker_notes_plugin())
slide.use(custom_theme_plugin())''', lang="python"),
        Text("Plugins can add:"),
        List(
            "Custom components",
            "Renderers",
            "Transforms",
            "HTML/CSS/JS"
        ),
        SpeakerNote("This is what you're seeing right now! The navigation and notes are both plugins.")
    ))

    # Page 7: Performance
    slide.add_page(Page(
        Header("Production Ready", level=2),
        TwoColumn(
            VStack(
                Header("Type Safety", level=3),
                Text("✓ Full mypy coverage"),
                Text("✓ Dataclass-based components"),
                Text("✓ Runtime validation")
            ),
            VStack(
                Header("Testing", level=3),
                Text("✓ 73 passing tests"),
                Text("✓ 84% code coverage"),
                Text("✓ CI/CD ready")
            )
        ),
        SpeakerNote("Emphasize the production-ready nature. All tests pass, mypy passes, high code coverage.")
    ))

    # Page 8: Thank You
    slide.add_page(Page(
        VStack(
            Header("Thank You!", level=1),
            Text("Questions?"),
            Text(""),
            Text("GitHub: github.com/abap34/yogrt"),
            gap="2rem"
        ),
        SpeakerNote("Open the floor for questions. Be ready to demo creating a custom component if asked.")
    ))

    # Export
    slide.export("presentation_mode.html")
    print("✓ Generated: presentation_mode.html")
    print("")
    print("To view the presentation:")
    print("  1. Open presentation_mode.html in your browser")
    print("  2. Use ← → arrow keys to navigate")
    print("  3. Press 'P' to toggle presenter view")
    print("  4. Speaker notes are only visible in presenter mode")


if __name__ == "__main__":
    main()
