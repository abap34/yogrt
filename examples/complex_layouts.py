"""
Example: Complex Layouts and Compositions

This example demonstrates advanced layout techniques by combining
multiple layout components (VStack, HStack, Grid, TwoColumn).
"""

from yogrt import (
    create_slide, Page, Header, Text, List, Image, Code,
    VStack, HStack, Grid, TwoColumn, Container, Divider, Spacer
)


def main():
    slide = create_slide()

    # Add custom CSS via HTML transform
    def add_custom_css(html: str) -> str:
        custom_css = """
        <style>
        .feature-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card {
            background: #f9fafb;
            border: 2px solid #e5e7eb;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        .code-box {
            background: #1f2937;
            padding: 1rem;
            border-radius: 8px;
            color: #f3f4f6;
        }
        </style>
        """
        return html.replace('</head>', f'{custom_css}</head>')

    slide.add_html_transform(add_custom_css)

    # ========================================================================
    # Page 1: Title with Centered Layout
    # ========================================================================
    slide.add_page(Page(
        Container(
            VStack(
                Spacer(height="25vh"),
                Header("Complex Layouts", level=1),
                Text("Demonstrating advanced layout compositions in Yogrt"),
                Spacer(height="2rem"),
                Text("Press → to continue"),
                gap="1rem"
            ),
            **{'class': 'center'}
        )
    ))

    # ========================================================================
    # Page 2: Two-Column Layout with Lists
    # ========================================================================
    slide.add_page(Page(
        Header("Two-Column Layout", level=2),
        TwoColumn(
            VStack(
                Header("Features", level=3),
                List(
                    "Programmable",
                    "Extensible",
                    "Type-safe",
                    "Well-tested"
                ),
                gap="0.5rem"
            ),
            VStack(
                Header("Benefits", level=3),
                List(
                    "Faster development",
                    "Better maintainability",
                    "Data integration",
                    "Version control friendly"
                ),
                gap="0.5rem"
            )
        )
    ))

    # ========================================================================
    # Page 3: Grid Layout with Feature Boxes
    # ========================================================================
    slide.add_page(Page(
        Header("Grid Layout", level=2),
        Grid(
            Container(
                Header("🎯 Simple", level=3),
                Text("Minimal core, easy to learn"),
                **{'class': 'feature-box'}
            ),
            Container(
                Header("🔧 Flexible", level=3),
                Text("Customize everything"),
                **{'class': 'feature-box'}
            ),
            Container(
                Header("📊 Data-First", level=3),
                Text("Built for data science"),
                **{'class': 'feature-box'}
            ),
            Container(
                Header("⚡ Fast", level=3),
                Text("Quick development cycle"),
                **{'class': 'feature-box'}
            ),
            columns=2,
            gap="1.5rem"
        )
    ))

    # ========================================================================
    # Page 4: Nested Layouts (VStack + HStack)
    # ========================================================================
    slide.add_page(Page(
        Header("Nested Layouts", level=2),
        VStack(
            Text("You can nest layouts to create complex structures:"),
            Container(
                VStack(
                    HStack(
                        Container(
                            Header("Left", level=4),
                            Text("First row, left column"),
                            **{'class': 'stat-card'}
                        ),
                        Container(
                            Header("Right", level=4),
                            Text("First row, right column"),
                            **{'class': 'stat-card'}
                        ),
                        gap="1rem"
                    ),
                    Divider(),
                    HStack(
                        Container(
                            Header("Left", level=4),
                            Text("Second row, left column"),
                            **{'class': 'stat-card'}
                        ),
                        Container(
                            Header("Right", level=4),
                            Text("Second row, right column"),
                            **{'class': 'stat-card'}
                        ),
                        gap="1rem"
                    ),
                    gap="1rem"
                )
            ),
            gap="1rem"
        )
    ))

    # ========================================================================
    # Page 5: Code + Explanation Layout
    # ========================================================================
    slide.add_page(Page(
        Header("Code + Explanation", level=2),
        TwoColumn(
            VStack(
                Text("Python code example:"),
                Container(
                    Code(
                        """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

print(factorial(5))""",
                        lang="python"
                    ),
                    **{'class': 'code-box'}
                ),
                gap="0.5rem"
            ),
            VStack(
                Header("Explanation", level=3),
                List(
                    "Recursive function",
                    "Base case: n ≤ 1",
                    "Recursive case: n × factorial(n-1)",
                    "Example: factorial(5) = 120"
                ),
                Text("This pattern is fundamental in functional programming."),
                gap="0.5rem"
            )
        )
    ))

    # ========================================================================
    # Page 6: Statistics Dashboard Layout
    # ========================================================================
    slide.add_page(Page(
        Header("Dashboard Layout", level=2),
        VStack(
            # Top row: 3 stat cards
            HStack(
                Container(
                    Header("1,234", level=3),
                    Text("Total Users"),
                    **{'class': 'stat-card'}
                ),
                Container(
                    Header("98%", level=3),
                    Text("Uptime"),
                    **{'class': 'stat-card'}
                ),
                Container(
                    Header("42ms", level=3),
                    Text("Avg Response"),
                    **{'class': 'stat-card'}
                ),
                gap="1rem"
            ),
            # Bottom row: Full-width content
            Container(
                Header("Recent Activity", level=3),
                List(
                    "User John Doe signed up",
                    "Payment processed: $99.00",
                    "New feature deployed",
                    "Database backup completed"
                ),
                **{'class': 'stat-card'}
            ),
            gap="1.5rem"
        )
    ))

    # ========================================================================
    # Page 7: Complex Multi-Section Layout
    # ========================================================================
    slide.add_page(Page(
        Header("Multi-Section Layout", level=2),
        VStack(
            # Section 1: Header with description
            Container(
                Text("This page combines multiple layout patterns into one slide."),
                **{'class': 'stat-card'}
            ),

            # Section 2: Two columns with different content
            TwoColumn(
                Grid(
                    Text("Item 1"),
                    Text("Item 2"),
                    Text("Item 3"),
                    Text("Item 4"),
                    columns=2,
                    gap="0.5rem"
                ),
                VStack(
                    Text("Vertical stack on the right:"),
                    List("Point A", "Point B", "Point C"),
                    gap="0.5rem"
                )
            ),

            # Section 3: Full-width footer
            Divider(),
            HStack(
                Text("Left footer text"),
                Text("Right footer text"),
                gap="2rem"
            ),

            gap="1rem"
        )
    ))

    # ========================================================================
    # Page 8: Responsive Grid (3 columns)
    # ========================================================================
    slide.add_page(Page(
        Header("3-Column Grid", level=2),
        Grid(
            VStack(
                Header("Column 1", level=3),
                Text("Content for the first column goes here."),
                Divider(),
                Text("Additional information."),
                gap="0.5rem"
            ),
            VStack(
                Header("Column 2", level=3),
                Text("Content for the second column goes here."),
                Divider(),
                Text("Additional information."),
                gap="0.5rem"
            ),
            VStack(
                Header("Column 3", level=3),
                Text("Content for the third column goes here."),
                Divider(),
                Text("Additional information."),
                gap="0.5rem"
            ),
            columns=3,
            gap="1.5rem"
        )
    ))

    # ========================================================================
    # Page 9: Mixed Content Layout
    # ========================================================================
    slide.add_page(Page(
        VStack(
            Header("Mixed Content Layout", level=2),

            TwoColumn(
                Container(
                    Header("Text Section", level=3),
                    Text("This demonstrates mixing different content types in a structured layout."),
                    Spacer(height="1rem"),
                    Text("Each section can have its own styling and structure."),
                    **{'class': 'stat-card'}
                ),
                Container(
                    Header("List Section", level=3),
                    List(
                        "First item",
                        "Second item",
                        "Third item",
                        "Fourth item"
                    ),
                    **{'class': 'stat-card'}
                )
            ),

            Divider(),

            Grid(
                Container(Text("Box 1"), **{'class': 'feature-box'}),
                Container(Text("Box 2"), **{'class': 'feature-box'}),
                Container(Text("Box 3"), **{'class': 'feature-box'}),
                columns=3,
                gap="1rem"
            ),

            gap="1.5rem"
        )
    ))

    # ========================================================================
    # Page 10: Final Summary
    # ========================================================================
    slide.add_page(Page(
        Container(
            VStack(
                Spacer(height="20vh"),
                Header("Layout Possibilities", level=1),
                Spacer(height="2rem"),
                Grid(
                    Text("✓ Two-Column"),
                    Text("✓ Grid"),
                    Text("✓ VStack"),
                    Text("✓ HStack"),
                    Text("✓ Nested"),
                    Text("✓ Mixed"),
                    columns=3,
                    gap="1rem"
                ),
                Spacer(height="2rem"),
                Text("Combine layouts to create any design you can imagine!"),
                gap="1rem"
            )
        )
    ))

    # Export
    slide.export("complex_layouts_example.html")
    print("✓ Generated: complex_layouts_example.html")


if __name__ == "__main__":
    main()
