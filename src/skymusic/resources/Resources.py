# -*- coding: utf-8 -*-
import io, os, importlib, re
try:
    from importlib import resources as importlib_resources
except ImportError:
    import importlib_resources
from skymusic.resources import fonts, png, css, js, svg, gamepads
#from skymusic import modes

def get_default_theme():
    global THEMES
    return list(THEMES)[0]

def detect_themes():
    '''
    Detects available themes by listing directories inside ./css/    
    '''
    css_dir = os.path.dirname(css.__file__)
    contents = os.listdir(css_dir)
    themes = [content for content in contents if os.path.isdir(os.path.join(css_dir, content))]
    return themes

def load_theme(theme, platform='mobile'):
    '''
    Loads CSS and PNG files as string and bytes buffers respectively, for a theme whose name 'theme' must be defined in the THEMES list
    '''
    global PNGS, CSS, SVG, THEMES, PLATFORMS, PNG_SETTINGS
    
    if theme not in THEMES:
        load_theme(get_default_theme(), platform)
    elif (THEMES[theme] is False) or (PLATFORMS[platform] is False):
        
        png_module = importlib.import_module('.'+theme+'.'+platform, png.__name__)       
        png_files = importlib_resources.contents(png_module)        
        
        if not png_files:
            print(f"\n*** ERROR: could not find any PNG file to embed from {png_module}. ***\n")   
        
        png_files = [file for file in png_files if os.path.splitext(file)[1].lower() == '.png']
        
        for png_file in png_files: #Populates the PNG dictionary using extension stripped filenames as keys
            PNGS[platform][os.path.splitext(png_file)[0]] = io.BytesIO(importlib_resources.read_binary(png_module, png_file))

        if platform == 'mobile':
            PNG_SETTINGS['png_max_quavers'] = len([PNGS[platform][name] for name in PNGS[platform] if re.match(r'root\-highlighted\-[\d]+', name)])
            
        css_module = importlib.import_module('.'+theme, css.__name__)        
        
        css_files = importlib_resources.contents(css_module)
        if not css_files:
            print(f"\n*** ERROR: could not find any CSS file to embed from {css_module}. ***\n")     
        
        css_files = [file for file in css_files if os.path.splitext(file)[1].lower() == '.css']
        
        for css_file in css_files:
            CSS[os.path.splitext(css_file)[0]] = io.StringIO(importlib_resources.read_text(css_module, css_file))
        
        svg_module = importlib.import_module('.'+theme, svg.__name__)        
        
        svg_files = importlib_resources.contents(svg_module)
        if not svg_files:
            print(f"\n*** ERROR: could not find any SVG file to embed from {svg_module}. ***\n")     
        
        svg_files = [file for file in svg_files if os.path.splitext(file)[1].lower() == '.svg']
        
        for svg_file in svg_files:
            SVG[os.path.splitext(svg_file)[0]] = io.StringIO(importlib_resources.read_text(svg_module, svg_file))
              
        PNG_SETTINGS['font_color'] = COLORS[theme]['font_color']
        PNG_SETTINGS['dimmed_font_color'] = COLORS[theme]['dimmed_font_color']  
        PNG_SETTINGS['harp_color'] = COLORS[theme]['harp_color']
        PNG_SETTINGS['text_bkg'] = COLORS[theme]['text_bkg']  
        PNG_SETTINGS['song_bkg'] = COLORS[theme]['song_bkg']  
        PNG_SETTINGS['hr_color'] = COLORS[theme]['hr_color']
        
        THEMES[theme] = True
        PLATFORMS[platform] = True


# %% Parameters
THEMES = {'light': False, 'dark': False}
PLATFORMS = {'mobile': False, 'playstation': False, 'switch': False}
# THEMES = detect_themes()
# Must be initialized with the theme names, which must correspond to directories in tue css and png folders

CSS = {'svg': io.StringIO(), 'html_base': io.StringIO(), 'html_mobile': io.StringIO(),  'html_gamepad': io.StringIO()}
"""
CSS Must be initialized with the base names of the CSS files inside each theme directory in ./css/{theme}/
At the moment the svg renderer needs svg.css
The html renderer needs html_base.css, html_gamepad.css, html_base.css
The svg to png converter needs svg2png.css
"""

SVG = {'mobile': io.StringIO(), 'playstation': io.StringIO(), 'switch': io.StringIO()} # Names of the SVG templates to load
PNGS = {'mobile': dict(), 'playstation': dict(), 'switch': dict()}

'''A dictionary of gamepad images, to be shown when user asks for help. Only the first image found is used in practice'''
GAMEPAD_IMAGES = {'mobile': [], 'playstation': [], 'switch': []}
for platform in GAMEPAD_IMAGES:
    try:
        platform_module = importlib.import_module('.'+platform, gamepads.__name__)
        platform_images = importlib_resources.contents(platform_module)        
        platform_images = [file for file in platform_images if os.path.splitext(file)[1].lower() in ('.jpg', '.png', '.webp', '.gif', '.tif', '.jpeg', '.tiff')]
        for image in platform_images:
            with importlib_resources.path(platform_module, image) as fp:
                GAMEPAD_IMAGES[platform].append(str(fp))
    except ModuleNotFoundError:
        pass


#Will be populated by load_theme()
COLORS = {
        'light': {'font_color': (0, 0, 0),
                  'dimmed_font_color': (128, 128, 128),
                  'harp_color': (255, 255, 255),
                  'text_bkg': (255, 255, 255, 0), #Transparent white
                  'song_bkg': (255, 255, 255),
                  'hr_color': (0, 0, 0)},
        'dark': {'font_color': (255, 255, 255),
                  'dimmed_font_color': (128, 128, 128),
                  'harp_color': (40, 40, 40),
                  'text_bkg': (40, 40, 40, 0), #Transparent dark
                  'song_bkg': (40, 40, 40),
                  'hr_color': (255, 255, 255)}, 
}                  
    
rel_css_path = '../css/main.css' # For IMPORT and HREF methods of embedding css files
offline_scripts_urls = [] #Embedded in HTML files
#online_scripts_urls = ['/js/navigationTableScript.js', '/js/sheetDarkModeScript.js', '/js/sheetDownloaderScript.js'] # linked in HTML files, stored on sky-music.github.io
online_scripts_urls = ['/js/navigationTableScript.js', '/js/sheetDownloaderScript.js'] # linked in HTML files, stored on sky-music.github.io

script_buffers = []
for script in offline_scripts_urls:
    try:
        script_buffers.append(io.StringIO(importlib_resources.read_text(js, script)))
    except FileNotFoundError:
        print(f"\n***WARNING: could not find javascript {script} file to embed it in HTML.\n")
        script_buffers.append(io.StringIO())

# To generate a link by sky-musiv.herokuapp.com
skyjson_api_url = "https://sky-music.herokuapp.com/api/generateTempSong"
skyjson_api_key = ""    


PNG_SETTINGS = {'harp_color': None,  # theme dependent
                'font_color': None, # theme dependent
                'text_bkg': None,   # theme dependent
                'song_bkg': None,   # theme dependent
                'hr_color': None,   # theme dependent
                'harp_font_size':38,
                'voice_font_size':36,
                'h1_font_size':48,
                'h2_font_size':42,
                'font_size':36,
                'font_path': None,
                'png_compress':6,
                'png_dpi': (2*96, 2*96),
                'max_quavers':6, #Default value is 6 for gamepad, will be calculated according to number of png files for mobile
                'max_chord_size':6, #maximum number of notes in a chord
                'max_harps_line': 10,
                'max_gp_notes_line':20,#the more, the smaller the buttons
                'row_names': ['A', 'B', 'C'],
                'typical_notes': {'mobile': 'A-root', 'playstation': 'X', 'switch': 'X'},
                'harp_aspect_ratio': 1.4553,
                'harp_rel_spacings': (0.13, 0.1), #H and V padding relative to harp width and height
                }

SVG_SETTINGS = {'font_size': 12, #pt
                'gp_note_size':(100,110),# viewport of SVG symbols
                'harp_aspect_ratio': 1.4553,
                'harp_rel_spacings': (0.13, 0.1),
                'max_harps_line':10,
                'max_gp_notes_line':20,
                }

FONTS = {
'asian': 'NotoSansCJKjp-Bold.otf',
'ja': 'NotoSansCJKjp-Bold.otf',
'zh': 'NotoSansCJKjp-Bold.otf',
'ko': 'NotoSansCJKjp-Bold.otf',
'latin': 'NotoSans-Full-Bold.ttf',
'pl': 'NotoSans-Bold.ttf',
'el': 'NotoSans-Bold.ttf',
'ar': 'NotoSansArabic-Bold.ttf',
'he': 'NotoSansHebrew-Bold.ttf',
'th': 'NotoSansThai-Bold.ttf',
'cyrillic': 'NotoSans-Bold.ttf',
'ru': 'NotoSans-Bold.ttf',
'uk': 'NotoSans-Bold.ttf',
'vi': 'NotoSans-Full-Bold.ttf',
'hy': 'NotoSansArmenian-Bold.ttf',
'ka': 'NotoSansGeorgian-Bold.ttf',
}

def load_font(locale='ja'):

    # Keep only locale prefix
    matchobj = re.match(r'([^_-]*)[_|-]*([^_-]*)', locale.strip())
    if matchobj: locale = matchobj.group(1).lower()
    if locale not in FONTS: locale = list(FONTS)[0]

    try:
        with importlib_resources.path(fonts, FONTS[locale]) as fp:
            PNG_SETTINGS['font_path'] = str(fp)
    except FileNotFoundError:
        PNG_SETTINGS['font_path'] = os.path.join(os.path.dirname(fonts.__file__), FONTS[locale])
        print(f"***ERROR: Could not find: 'fonts/{os.path.relpath(PNG_SETTINGS['font_path'], start=os.path.dirname(fonts.__file__))}'")
        
    return PNG_SETTINGS['font_path']

MAX_FILENAME_LENGTH = 127
MAX_NUM_FILES = 15

BINARY_EXT = ('.mid', '.midi') # Files that must be opened in binary mode

MARKDOWN_CODES = {'rulers': ['--', '__']} # Supported Markdown characters

DELIMITERS = {'icon': ' ',
              'pause': '.',
              'quaver': "-",
              'jianpu_pause': '0',
              'jianpu_quaver': '^',
              'lyric': '#',
              'metadata': '#$',
              'repeat': '*',
              'broken_harp': 'X',
              'layer': '==',
            }

SKYJSON_CHORD_DELAY = 50 #Delay in ms below which 2 notes are considered a chord
DEFAULT_BPM = 220
PARSING_START_OCTAVE = 1
RENDERING_START_OCTAVE = 4

DEFAULT_KEY = 'C' # The default proposed song key, to parse notes when the song key cannot be retrieved, not to be confused with the 0 index of the English/Jianpu/doremi chromatic scales, which is C by convention 

DEFAULT_INSTRUMENT = 'harp'

MIDI_PITCHES = {'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63, 'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68, 'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71}
MIDI_SEMITONES = [0, 2, 4, 5, 7, 9, 11]  # May no longer be used when Western_scales is merged
