"""
Bibliothèque pour la compilation de présentations Markdown
"""

from .config import THEMES, DEFAULT_THEME, CSS_FONTS, ASSETS
from .models import Slide, Presentation
from .parser import parse_presentation, parse_metadata, parse_details_only
from .generator import HTMLGenerator, PageGenerator, format_markdown, format_table_html, format_table_html
__all__ = [
    'Slide',
    'Presentation',
    'parse_presentation',
    'parse_details_only',
    'parse_metadata',
    'CSS_FONTS',
    'HTMLGenerator',
    'PageGenerator',
    'format_markdown',
    'format_table_html',
    'ASSETS',
    'THEMES',
    'DEFAULT_THEME',
]
