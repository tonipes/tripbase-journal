#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import piexif
import os

AUTHOR = 'Toni'
SITENAME = "Entries"
SITESUBTITLE = 'This is a test site'
SITEURL = ''

THEME = 'theme'

PATH = os.environ['TRIPBASE_JOURNAL_CONTENT_PATH'] #'content'

TIMEZONE = 'Europe/Helsinki'

DEFAULT_LANG = 'en'
DEFAULT_DATE_FORMAT = '%a %Y-%m-%d'

PLUGIN_PATHS = ['plugins']
PLUGINS = ['assets', 'gallery']

FILENAME_METADATA = "(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>.*)"

AUTHOR_SAVE_AS = ''
AUTHORS_SAVE_AS = ''
CATEGORY_SAVE_AS = ''
CATEGORIES_SAVE_AS = ''
TAGS_SAVE_AS = ''

GOOGLE_MAPS_API_KEY = os.environ['TRIPBASE_GOOGLE_MAPS_API_KEY']

GALLERY_PATHS = ['photos']
GALLERY_PATHS_EXCLUDE = []
# GALLERY_PHOTO_TEMPLATE = 'photo'

GALLERY_EXIF = {
    'make': ('0th', piexif.ImageIFD.Make),
    'model': ('0th', piexif.ImageIFD.Model),
    'date': ('0th', piexif.ImageIFD.DateTime),
    'timezone': ('0th', piexif.ImageIFD.TimeZoneOffset),
    'location': {
        'latitude_ref': ('GPS', piexif.GPSIFD.GPSLatitudeRef),
        'longitude_ref': ('GPS', piexif.GPSIFD.GPSLongitudeRef),
        'latitude': ('GPS', piexif.GPSIFD.GPSLatitude),
        'longitude': ('GPS', piexif.GPSIFD.GPSLongitude),
    }
}

GALLERY_IMAGE_OUTPUTS = {
    'article_image': {
        'size': (1024, 1024),
        'quality': 80,
        'filename': 'ARTICLE_{}',
    },
    'thumbnail_image': {
        'size': (512, 512),
        'quality': 80,
        'filename': 'THUMB_{}',
    },
}

MENU_LINKS = [
    {
        'title': 'Entries',
        'icon': 'fa-pencil-square',
        'link': 'index'
    },
    {
        'title': 'Gallery',
        'icon': 'fa-camera-retro',
        'link': 'gallery'
    },
    {
        'title': 'Info',
        'icon': 'fa-info-circle',
        'link': 'info'
    },
]

MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {},
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
    },
    'output_format': 'html5',
}

DIRECT_TEMPLATES = ['index']
PAGINATED_DIRECT_TEMPLATES = ['index']
# CACHE_CONTENT = True
# CHECK_MODIFIED_METHOD = 'mtime'
# CONTENT_CACHING_LAYER = 'generator'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = []

# Social widget
SOCIAL = []

DEFAULT_PAGINATION = 9

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
