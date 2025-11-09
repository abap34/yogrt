"""Tests for advanced features (footnotes, citations, TOC)"""

import pytest
from pathlib import Path

from yogrt import (
    create_slide,
    Page,
    Header,
    Text,
    Context,
    FootnoteRef,
    Footnote,
    Citation,
    TOC,
    Bibliography,
)
from yogrt.renderers import (
    render_footnote_ref,
    render_footnote,
    render_citation,
    render_toc,
    render_bibliography,
)


def test_footnote_ref_component() -> None:
    """Test FootnoteRef component"""
    ref = FootnoteRef("1")

    assert ref.note_id == "1"
    assert ref.tag == "footnote-ref"


def test_footnote_component() -> None:
    """Test Footnote component"""
    note = Footnote("1", "This is a footnote")

    assert note.note_id == "1"
    assert note.content == "This is a footnote"
    assert note.tag == "footnote"


def test_citation_component() -> None:
    """Test Citation component"""
    cite = Citation("smith2020")

    assert cite.cite_key == "smith2020"
    assert cite.tag == "citation"


def test_toc_component() -> None:
    """Test TOC component"""
    toc = TOC(max_level=2, title="Contents")

    assert toc.max_level == 2
    assert toc.title == "Contents"
    assert toc.tag == "toc"


def test_bibliography_component() -> None:
    """Test Bibliography component"""
    bib = Bibliography(title="References")

    assert bib.title == "References"
    assert bib.tag == "bibliography"


def test_render_footnote_ref() -> None:
    """Test footnote reference rendering"""
    ref = FootnoteRef("1")
    ctx = Context()

    html = render_footnote_ref(ref, ctx)

    assert 'href="#fn-1"' in html
    assert 'id="fnref-1"' in html
    assert '[1]' in html


def test_render_footnote() -> None:
    """Test footnote rendering"""
    note = Footnote("1", "This is a footnote")
    ctx = Context()

    # Render should store in context
    html = render_footnote(note, ctx)

    # Returns empty string (rendered at page end)
    assert html == ''

    # Should be stored in context
    assert '1' in ctx.footnotes
    assert ctx.footnotes['1'] == 'This is a footnote'


def test_render_citation() -> None:
    """Test citation rendering"""
    cite = Citation("smith2020")
    ctx = Context()

    html = render_citation(cite, ctx)

    assert 'href="#ref-smith2020"' in html
    assert '[smith2020]' in html


def test_render_toc_empty() -> None:
    """Test TOC rendering with no headers"""
    toc = TOC()
    ctx = Context()

    html = render_toc(toc, ctx)

    # Should return empty string if no headers
    assert html == ''


def test_render_toc_with_headers() -> None:
    """Test TOC rendering with headers"""
    toc = TOC(max_level=2, title="Table of Contents")
    ctx = Context()

    # Add headers to context
    ctx.headers.append((1, "Introduction", "introduction"))
    ctx.headers.append((2, "Background", "background"))
    ctx.headers.append((3, "Details", "details"))  # Should be filtered (level 3)

    html = render_toc(toc, ctx)

    assert 'Table of Contents' in html
    assert 'href="#introduction"' in html
    assert 'Introduction' in html
    assert 'href="#background"' in html
    assert 'Background' in html
    # Level 3 should not appear (max_level=2)
    assert 'Details' not in html


def test_render_bibliography_empty() -> None:
    """Test bibliography rendering with no citations"""
    bib = Bibliography()
    ctx = Context()

    html = render_bibliography(bib, ctx)

    # Should return empty string if no citations
    assert html == ''


def test_render_bibliography_with_citations() -> None:
    """Test bibliography rendering with citations"""
    bib = Bibliography(title="References")
    ctx = Context()

    # Add citations to context
    ctx.citations['smith2020'] = {
        'author': 'John Smith',
        'title': 'A Great Paper',
        'year': '2020'
    }
    ctx.citations['doe2021'] = {
        'author': 'Jane Doe',
        'title': 'Another Paper',
        'year': '2021'
    }

    html = render_bibliography(bib, ctx)

    assert 'References' in html
    assert 'id="ref-smith2020"' in html
    assert 'John Smith' in html
    assert 'A Great Paper' in html
    assert '2020' in html
    assert 'id="ref-doe2021"' in html
    assert 'Jane Doe' in html
    assert 'Another Paper' in html
    assert '2021' in html


def test_footnotes_in_page() -> None:
    """Test footnotes appear at end of page"""
    slide = create_slide()

    slide.add_page(Page(
        Header("Test Page", level=1),
        Text("This has a footnote"),
        FootnoteRef("1"),
        Footnote("1", "This is the footnote content")
    ))

    output = Path("test_footnotes.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Check footnote reference
        assert 'href="#fn-1"' in html

        # Check footnote appears in footnotes section
        assert 'class="footnotes"' in html
        assert 'This is the footnote content' in html
    finally:
        if output.exists():
            output.unlink()


def test_toc_in_slide() -> None:
    """Test TOC auto-generation"""
    slide = create_slide()

    # First page with headers
    slide.add_page(Page(
        Header("Introduction", level=1, id="intro"),
        Text("Some content"),
        Header("Chapter 1", level=2, id="chapter1"),
        Text("More content")
    ))

    # Second page with TOC (headers already tracked from first page)
    slide.add_page(Page(
        Header("Table of Contents", level=1),
        TOC(max_level=2, title="Contents")
    ))

    output = Path("test_toc.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Check TOC rendered
        assert 'Contents' in html
        assert 'href="#intro"' in html
        assert 'Introduction' in html
        assert 'href="#chapter1"' in html
        assert 'Chapter 1' in html
    finally:
        if output.exists():
            output.unlink()


def test_bibliography_in_slide() -> None:
    """Test bibliography rendering"""
    slide = create_slide()

    # Add citation data to context
    slide.context.citations['smith2020'] = {
        'author': 'John Smith',
        'title': 'Research Paper',
        'year': '2020'
    }

    slide.add_page(Page(
        Header("References", level=1),
        Text("See citation"),
        Citation("smith2020"),
        Bibliography(title="Bibliography")
    ))

    output = Path("test_bibliography.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        # Check citation
        assert 'href="#ref-smith2020"' in html
        assert '[smith2020]' in html

        # Check bibliography
        assert 'Bibliography' in html
        assert 'John Smith' in html
        assert 'Research Paper' in html
        assert '2020' in html
    finally:
        if output.exists():
            output.unlink()


def test_multiple_footnotes() -> None:
    """Test multiple footnotes on one page"""
    slide = create_slide()

    slide.add_page(Page(
        Text("First footnote"),
        FootnoteRef("1"),
        Text("Second footnote"),
        FootnoteRef("2"),
        Footnote("1", "First note"),
        Footnote("2", "Second note")
    ))

    output = Path("test_multiple_footnotes.html")
    try:
        slide.export(str(output))
        html = output.read_text()

        assert 'href="#fn-1"' in html
        assert 'href="#fn-2"' in html
        assert 'First note' in html
        assert 'Second note' in html
    finally:
        if output.exists():
            output.unlink()


def test_header_tracking_for_toc() -> None:
    """Test headers are tracked in context for TOC"""
    from yogrt.renderers import render_header
    from yogrt.core import HeaderComponent

    ctx = Context()

    # Render header with ID
    header = HeaderComponent(text="Test Header", level=1, id="test")
    render_header(header, ctx)

    # Should be tracked
    assert len(ctx.headers) == 1
    assert ctx.headers[0] == (1, "Test Header", "test")


def test_header_not_duplicated_in_toc() -> None:
    """Test headers aren't duplicated if rendered multiple times"""
    from yogrt.renderers import render_header
    from yogrt.core import HeaderComponent

    ctx = Context()

    header = HeaderComponent(text="Test", level=1, id="test")

    # Render twice
    render_header(header, ctx)
    render_header(header, ctx)

    # Should only appear once
    assert len(ctx.headers) == 1
