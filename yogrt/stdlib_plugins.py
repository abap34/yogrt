"""
Standard Library Plugins for Yogrt

Common, reusable plugins that enhance slide functionality.
"""

from yogrt.core import Component, Context
from yogrt.slide import Slide, Plugin
from dataclasses import dataclass
from typing import Any, Literal


# ============================================================================
# Slide Navigation Plugin
# ============================================================================

@dataclass(frozen=True)
class SpeakerNoteComponent:
    """Speaker note component - shown in presenter view only"""
    content: str
    key: str | None = None

    @property
    def tag(self) -> str:
        return "speaker-note"


def SpeakerNote(content: str, **kwargs: Any) -> SpeakerNoteComponent:
    """Create a speaker note component"""
    return SpeakerNoteComponent(content=content, key=kwargs.get('key'))


def slide_navigation_plugin() -> Plugin:
    """
    Adds full-screen slide navigation with arrow keys

    Features:
    - Each page takes full viewport (100vw x 100vh)
    - Arrow keys (←→) navigate between slides
    - Current slide shown, others hidden
    - Smooth transitions
    - Page indicator showing current/total pages

    Usage:
        slide = create_slide()
        slide.use(slide_navigation_plugin())
    """

    def add_navigation_js(html: str) -> str:
        """Add JavaScript for slide navigation"""
        js_code = """
<style>
body {
    margin: 0;
    padding: 0;
    overflow: hidden !important;
}

.page {
    display: none !important;
}

.slide-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
}

.slide-page {
    display: none;
}

.slide-page.active {
    display: block;
}

.slide-page.active .page {
    display: flex !important;
    flex-direction: column;
    width: 100%;
    height: 100%;
    padding: 2rem;
}

.slide-indicator {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 2rem;
    font-family: monospace;
    font-size: 0.875rem;
    z-index: 1000;
}

.slide-controls {
    position: fixed;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 2rem;
    font-size: 0.875rem;
    z-index: 1000;
    display: flex;
    gap: 1rem;
    align-items: center;
}

.slide-controls button {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 0.5rem;
    cursor: pointer;
    font-size: 1rem;
}

.slide-controls button:hover {
    background: rgba(255, 255, 255, 0.3);
}

.slide-controls button:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}
</style>

<script>
(function() {
    let currentSlide = 0;
    let slides = [];

    function initSlides() {
        const pages = Array.from(document.querySelectorAll('.page'));
        if (pages.length === 0) return;

        const container = document.createElement('div');
        container.className = 'slide-container';
        document.body.insertBefore(container, document.body.firstChild);

        pages.forEach((page, index) => {
            const slideDiv = document.createElement('div');
            slideDiv.className = 'slide-page';
            slideDiv.dataset.slideIndex = index;

            if (page.parentNode) {
                page.parentNode.removeChild(page);
            }

            slideDiv.appendChild(page);
            slides.push(slideDiv);
            container.appendChild(slideDiv);
        });

        const indicator = document.createElement('div');
        indicator.className = 'slide-indicator';
        indicator.id = 'slide-indicator';
        document.body.appendChild(indicator);

        const controls = document.createElement('div');
        controls.className = 'slide-controls';
        controls.innerHTML = `
            <button id="prev-slide">← Prev</button>
            <span id="slide-number"></span>
            <button id="next-slide">Next →</button>
        `;
        document.body.appendChild(controls);

        document.getElementById('prev-slide').addEventListener('click', () => goToSlide(currentSlide - 1));
        document.getElementById('next-slide').addEventListener('click', () => goToSlide(currentSlide + 1));

        goToSlide(0);
    }

    function goToSlide(index) {
        if (index < 0 || index >= slides.length) return;

        slides.forEach(slide => slide.classList.remove('active'));

        currentSlide = index;
        slides[currentSlide].classList.add('active');

        const indicator = document.getElementById('slide-indicator');
        if (indicator) {
            indicator.textContent = `${currentSlide + 1} / ${slides.length}`;
        }

        const slideNumber = document.getElementById('slide-number');
        if (slideNumber) {
            slideNumber.textContent = `${currentSlide + 1} / ${slides.length}`;
        }

        const prevBtn = document.getElementById('prev-slide');
        const nextBtn = document.getElementById('next-slide');
        if (prevBtn) prevBtn.disabled = currentSlide === 0;
        if (nextBtn) nextBtn.disabled = currentSlide === slides.length - 1;
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            e.preventDefault();
            goToSlide(currentSlide - 1);
        } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
            e.preventDefault();
            goToSlide(currentSlide + 1);
        } else if (e.key === 'Home') {
            e.preventDefault();
            goToSlide(0);
        } else if (e.key === 'End') {
            e.preventDefault();
            goToSlide(slides.length - 1);
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSlides);
    } else {
        initSlides();
    }
})();
</script>
"""
        return html.replace('</body>', f'{js_code}</body>')

    def plugin(slide: Slide) -> Slide:
        slide.add_html_transform(add_navigation_js)
        return slide

    return plugin


# ============================================================================
# Speaker Notes Plugin
# ============================================================================

def speaker_notes_plugin() -> Plugin:
    """
    Adds speaker notes functionality

    Features:
    - Add notes to slides that only appear in presenter view
    - Toggle presenter view with 'P' key
    - Presenter view shows current slide + notes + next slide preview
    - Regular view hides notes

    Usage:
        slide = create_slide()
        slide.use(speaker_notes_plugin())

        slide.add_page(Page(
            Header("My Slide"),
            Text("Visible content"),
            SpeakerNote("This is a note only I can see")
        ))
    """

    def render_speaker_note(component: Component, context: Context) -> str:
        """Render speaker note (hidden by default)"""
        assert isinstance(component, SpeakerNoteComponent)

        return f'''
        <div class="speaker-note" style="display: none;">
            <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 1rem; margin: 1rem 0;">
                <strong style="color: #f59e0b;">📝 Speaker Note:</strong>
                <p style="margin: 0.5rem 0 0 0;">{component.content}</p>
            </div>
        </div>
        '''

    def add_presenter_mode_js(html: str) -> str:
        """Add JavaScript for presenter mode"""
        js_code = """
<style>
.presenter-mode {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: #1f2937;
    color: white;
    z-index: 10000;
    overflow: auto;
}

.presenter-mode.active {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 1rem;
    padding: 1rem;
}

.presenter-current {
    background: white;
    border-radius: 8px;
    overflow: auto;
}

.presenter-notes {
    background: #374151;
    border-radius: 8px;
    padding: 1rem;
    overflow: auto;
}

.presenter-notes h3 {
    margin-top: 0;
    color: #f59e0b;
}

.presenter-next {
    background: #4b5563;
    border-radius: 8px;
    overflow: auto;
    opacity: 0.7;
}

.presenter-next h3 {
    padding: 0.5rem;
    margin: 0;
    background: #374151;
    color: #9ca3af;
}

.presenter-toggle {
    position: fixed;
    top: 1rem;
    right: 1rem;
    background: rgba(59, 130, 246, 0.9);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    cursor: pointer;
    font-size: 0.875rem;
    z-index: 10001;
}

.presenter-toggle:hover {
    background: rgba(37, 99, 235, 0.9);
}
</style>

<button class="presenter-toggle" id="presenter-toggle">
    Press 'P' for Presenter View
</button>

<div class="presenter-mode" id="presenter-mode">
    <div class="presenter-current">
        <div id="presenter-current-slide"></div>
    </div>
    <div class="presenter-notes">
        <h3>📝 Speaker Notes</h3>
        <div id="presenter-notes-content"></div>
    </div>
    <div class="presenter-next">
        <h3>Next Slide</h3>
        <div id="presenter-next-slide"></div>
    </div>
</div>

<script>
(function() {
    let presenterMode = false;

    function togglePresenterMode() {
        presenterMode = !presenterMode;
        const presenterDiv = document.getElementById('presenter-mode');

        if (!presenterDiv) return;

        if (presenterMode) {
            presenterDiv.classList.add('active');
            updatePresenterView();
        } else {
            presenterDiv.classList.remove('active');
        }
    }

    function updatePresenterView() {
        if (!presenterMode) return;

        const activeSlide = document.querySelector('.slide-page.active');
        if (!activeSlide) return;

        const currentIndex = parseInt(activeSlide.dataset.slideIndex);
        const allSlides = document.querySelectorAll('.slide-page');

        const currentContent = activeSlide.cloneNode(true);
        document.getElementById('presenter-current-slide').innerHTML = '';
        document.getElementById('presenter-current-slide').appendChild(currentContent);

        const notes = activeSlide.querySelectorAll('.speaker-note');
        const notesContent = document.getElementById('presenter-notes-content');
        notesContent.innerHTML = '';

        if (notes.length > 0) {
            notes.forEach(note => {
                const noteClone = note.cloneNode(true);
                noteClone.style.display = 'block';
                notesContent.appendChild(noteClone);
            });
        } else {
            notesContent.innerHTML = '<p style="color: #9ca3af;">No notes for this slide.</p>';
        }

        const nextSlide = allSlides[currentIndex + 1];
        const nextContent = document.getElementById('presenter-next-slide');
        nextContent.innerHTML = '';

        if (nextSlide) {
            const nextClone = nextSlide.cloneNode(true);
            nextContent.appendChild(nextClone);
        } else {
            nextContent.innerHTML = '<p style="color: #9ca3af; padding: 1rem;">End of presentation</p>';
        }
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'p' || e.key === 'P') {
            e.preventDefault();
            togglePresenterMode();
        }
    });

    const presenterToggleBtn = document.getElementById('presenter-toggle');
    if (presenterToggleBtn) {
        presenterToggleBtn.addEventListener('click', togglePresenterMode);
    }

    document.addEventListener('keydown', (e) => {
        if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' '].includes(e.key)) {
            setTimeout(updatePresenterView, 100);
        }
    });
})();
</script>
"""
        return html.replace('</body>', f'{js_code}</body>')

    def plugin(slide: Slide) -> Slide:
        slide.add_renderer('speaker-note', render_speaker_note)
        slide.add_html_transform(add_presenter_mode_js)
        return slide

    return plugin


# ============================================================================
# Syntax Highlighting Plugin
# ============================================================================

def syntax_highlighting_plugin(
    theme: Literal['default', 'monokai', 'github', 'atom-one-dark', 'vs'] = 'atom-one-dark'
) -> Plugin:
    """
    Adds syntax highlighting to code blocks using highlight.js

    Features:
    - Automatic language detection
    - Multiple themes available
    - Line numbers
    - Copy button

    Args:
        theme: Color theme for syntax highlighting
            - 'default': highlight.js default
            - 'monokai': Monokai theme
            - 'github': GitHub theme
            - 'atom-one-dark': Atom One Dark theme
            - 'vs': Visual Studio theme

    Usage:
        slide = create_slide()
        slide.use(syntax_highlighting_plugin('atom-one-dark'))
    """

    def add_syntax_highlighting(html: str) -> str:
        """Add highlight.js for syntax highlighting"""

        theme_urls = {
            'default': 'default',
            'monokai': 'monokai',
            'github': 'github',
            'atom-one-dark': 'atom-one-dark',
            'vs': 'vs',
        }

        theme_name = theme_urls.get(theme, 'atom-one-dark')

        highlighting_code = f"""
<!-- Syntax Highlighting with highlight.js -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/{theme_name}.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

<style>
.code-container {{
    position: relative;
    margin: 1rem 0;
}}

.code-header {{
    background: #2d3748;
    color: #cbd5e0;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem 0.5rem 0 0;
    font-size: 0.875rem;
    font-family: monospace;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.code-lang {{
    text-transform: uppercase;
    font-weight: 600;
}}

.code-copy-btn {{
    background: rgba(255, 255, 255, 0.1);
    border: none;
    color: #cbd5e0;
    padding: 0.25rem 0.75rem;
    border-radius: 0.25rem;
    cursor: pointer;
    font-size: 0.75rem;
    transition: background 0.2s;
}}

.code-copy-btn:hover {{
    background: rgba(255, 255, 255, 0.2);
}}

.code-copy-btn:active {{
    background: rgba(255, 255, 255, 0.3);
}}

.code-copy-btn.copied {{
    background: #48bb78;
}}

pre code.hljs {{
    border-radius: 0 0 0.5rem 0.5rem !important;
    margin: 0 !important;
}}
</style>

<script>
document.addEventListener('DOMContentLoaded', (event) => {{
    document.querySelectorAll('pre code').forEach((block) => {{
        hljs.highlightElement(block);
    }});

    document.querySelectorAll('.code-copy-btn').forEach((btn) => {{
        btn.addEventListener('click', function() {{
            const codeBlock = this.closest('.code-container').querySelector('code');
            const text = codeBlock.textContent;

            navigator.clipboard.writeText(text).then(() => {{
                this.textContent = '✓ Copied!';
                this.classList.add('copied');

                setTimeout(() => {{
                    this.textContent = 'Copy';
                    this.classList.remove('copied');
                }}, 2000);
            }});
        }});
    }});
}});
</script>
"""
        return html.replace('</head>', f'{highlighting_code}</head>')

    def plugin(slide: Slide) -> Slide:
        slide.add_html_transform(add_syntax_highlighting)
        return slide

    return plugin
