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
    'section': 'section'
}

# Préfixes Markdown
MD_PREFIXES = {
    'h1': '# ',
    'h2': '## ',
    'h3': '### ',
    'image': '## Image: ',
    'subtitle': '> ',
    'caption': 'Caption: ',
    'list_item': ('- ', '* '),
}

# Thèmes de couleurs
THEMES = {
    'ocean': {
        'primary': '#0a4d68',
        'secondary': '#088395',
        'accent': '#05bfdb',
        'warning': '#ff6b35',
    },
    'glacier': {
        'primary': '#1a365d',
        'secondary': '#2c5282',
        'accent': '#63b3ed',
        'warning': '#ed8936',
    },
    'bordeaux': {
        'primary': '#742a2a',
        'secondary': '#9b2c2c',
        'accent': '#fc8181',
        'warning': '#d69e2e',
    },
}

DEFAULT_THEME = 'ocean'

# CSS et JS par défaut (chemins relatifs au script principal)
ASSETS = {
    'css': 'css/style.css',
    'js': 'js/presentation.js',
    'fonts': "fonts",
}


CSS_FONTS = '''
/* crimson-pro-regular - latin */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Crimson Pro';
  font-style: normal;
  font-weight: 400;
  src: url('/fonts/crimson-pro-v28-latin-regular.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}

/* crimson-pro-700 - latin */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Crimson Pro';
  font-style: normal;
  font-weight: 700;
  src: url('/fonts/crimson-pro-v28-latin-700.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}


/* work-sans-300 - latin */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Work Sans';
  font-style: normal;
  font-weight: 300;
  src: url('/fonts/work-sans-v24-latin-300.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}

/* work-sans-regular - latin */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Work Sans';
  font-style: normal;
  font-weight: 400;
  src: url('/fonts/work-sans-v24-latin-regular.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}

/* work-sans-500 - latin */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Work Sans';
  font-style: normal;
  font-weight: 500;
  src: url('/fonts/work-sans-v24-latin-500.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}

/* work-sans-700 - latin */
@font-face {
  font-display: swap;
  /* Check https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display for other options. */
  font-family: 'Work Sans';
  font-style: normal;
  font-weight: 700;
  src: url('/fonts/work-sans-v24-latin-700.woff2') format('woff2');
  /* Chrome 36+, Opera 23+, Firefox 39+, Safari 12+, iOS 10+ */
}
'''
