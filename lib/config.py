"""
Configuration centralisée du compilateur de présentation
"""

# Marqueurs Markdown (syntaxe Pandoc)
MARKERS = {
    'details': ':::details',
    'questions': ':::questions',
    'no_annexes': ':::no-annexes',
}

# Types de slides
SLIDE_TYPES = {
    'title': 'title',
    'content': 'content',
    'image': 'image',
}

# Préfixes Markdown
MD_PREFIXES = {
    'h1': '# ',
    'h2': '## ',
    'image': '### Image: ',
    'subtitle': '> ',
    'caption': 'Caption: ',
    'list_item': ('- ', '* '),
}

# CSS et JS par défaut (chemins relatifs au script principal)
ASSETS = {
    'css': 'css/style.css',
    'js': 'js/presentation.js',
}

# Fonts Google
GOOGLE_FONTS_URL = "https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Work+Sans:wght@300;500;700&display=swap"
