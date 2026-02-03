"""
Bibliothèque pour la compilation de présentations Markdown
"""

from .models import Slide, Section, Presentation
from .parser import parse_presentation, parse_details_only
from .generator import HTMLGenerator, format_bold, format_markdown
from .config import MARKERS, SLIDE_TYPES, ASSETS, THEMES, DEFAULT_THEME

__all__ = [
    'Slide',
    'Section', 
    'Presentation',
    'parse_presentation',
    'parse_details_only',
    'HTMLGenerator',
    'format_bold',
    'format_markdown',
    'MARKERS',
    'SLIDE_TYPES',
    'ASSETS',
    'THEMES',
    'DEFAULT_THEME',
]
