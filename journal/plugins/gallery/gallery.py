# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import codecs
import logging
import multiprocessing as mp
from functools import partial
from datetime import datetime

from pelican import signals
from pelican.contents import Content
from pelican.generators import CachingGenerator
from pelican.settings import DEFAULT_CONFIG

_logger = logging.getLogger(__name__)

# try:
from PIL import Image
from PIL import ImageOps
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL import ImageFont
# except ImportError:
#     _logger.error('PIL/Pillow not found')

# try:
import piexif
# except ImportError:
#     _logger.error('Piexif not found!')


class Photo(Content):
    mandatory_properties = ()
    default_template = 'photo'


def initialized(pelican):
    _logger.debug("Initialized!!")

    DEFAULT_CONFIG['GALLERY_PHOTO_TEMPLATE'] = 'photo'

    DEFAULT_CONFIG['GALLERY_THUMBNAIL_NAME_FORMAT'] = 'THUMB_{}'
    DEFAULT_CONFIG['GALLERY_ARTICLE_NAME_FORMAT'] = 'ARTICLE_{}'

    DEFAULT_CONFIG['GALLERY_THUMBNAIL_SIZE'] = ((512, 512), 80)
    DEFAULT_CONFIG['GALLERY_ARTICLE_SIZE'] = ((1024, 1024), 80)

    DEFAULT_CONFIG['GALLERY_IMAGE_OUTPUTS'] = {
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

    DEFAULT_CONFIG['GALLERY_COPY_ORIGINAL'] = True
    DEFAULT_CONFIG['GALLERY_AUTO_ROTATE'] = True
    DEFAULT_CONFIG['GALLERY_PATHS'] = ['photos']
    DEFAULT_CONFIG['GALLERY_PATHS_EXCLUDE'] = []
    DEFAULT_CONFIG['GALLERY_MAX_JOBS'] = 4

    DEFAULT_CONFIG['PHOTO_SAVE_AS'] = 'photo/{slug}.html'
    DEFAULT_CONFIG['PHOTO_URL'] = 'photo/{slug}.html'

    DEFAULT_CONFIG['GALLERY_EXIF'] = {
        'Make': ('0th', piexif.ImageIFD.Make),
        'Model': ('0th', piexif.ImageIFD.Model),
        'Timestamp': ('0th', piexif.ImageIFD.DateTime),
        'Timezone': ('0th', piexif.ImageIFD.TimeZoneOffset),
        'Location': {
            'LatitudeRef': ('GPS', piexif.GPSIFD.GPSLatitudeRef),
            'LongitudeRef': ('GPS', piexif.GPSIFD.GPSLongitudeRef),
            'Latitude': ('GPS', piexif.GPSIFD.GPSLongitudeRef),
            'Longitude': ('GPS', piexif.GPSIFD.GPSLongitudeRef),
        }
    }

def rotate(img, exif):
    if "exif" in img.info and piexif.ImageIFD.Orientation in exif["0th"]:
        orientation = exif["0th"].pop(piexif.ImageIFD.Orientation)
        if orientation == 2:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            img = img.rotate(180)
        elif orientation == 4:
            img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 5:
            img = img.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            img = img.rotate(-90)
        elif orientation == 7:
            img = img.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            img = img.rotate(90)
        return (img, exif)

def process_image(abs_path, photo, settings):
    input_filename = os.path.split(photo.original_path)[1]
    output_path = os.path.join(settings['OUTPUT_PATH'], photo.original_path)
    output_directory = os.path.split(output_path)[0]
    output_directory_relative = os.path.split(photo.original_path)[0]
    _logger.debug("Process: {}".format(abs_path))

    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory)
        except Exception:
            _logger.exception('Could not create {}'.format(output_directory))

    orig_img = Image.open(abs_path)
    exif = piexif.load(orig_img.info['exif'])

    if settings['GALLERY_AUTO_ROTATE']:
        orig_img, exif = rotate(orig_img, exif)

    for name, output_type in settings['GALLERY_IMAGE_OUTPUTS'].items():
        img = ImageOps.fit(orig_img.copy(), output_type['size'], Image.ANTIALIAS)
        output_filename = output_type['filename'].format(input_filename)
        path = os.path.join(output_directory, output_filename)
        _logger.debug("Save: {}".format(path))
        img.save(path, quality=output_type['quality'], exif=piexif.dump(exif))

        # photo[name] = os.path.join(output_directory_relative, output_filename)

    return photo

class PhotoGenerator(CachingGenerator):
    def __init__(self, *args, **kwargs):
        self.photos = []
        self.dates = {}
        super(PhotoGenerator, self).__init__(*args, **kwargs)

    def _convert_to_degress(self, v):
        d = float(v[0][0]) / float(v[0][1])
        m = float(v[1][0]) / float(v[1][1])
        s = float(v[2][0]) / float(v[2][1])
        return d + (m / 60.0) + (s / 3600.0)

    def _convert_datetime(self, v):
        dt = datetime.strptime(v.decode("utf-8"), '%Y:%m:%d %H:%M:%S')
        return dt.isoformat(' ')

    def _get(self, d, k):
        if k in d:
            # HACK: Convert gps latitude and longitude to degrees
            if k == piexif.GPSIFD.GPSLatitude or k == piexif.GPSIFD.GPSLongitude:
                return self._convert_to_degress(d[k])
            # HACK: Parse datetime
            elif k == piexif.ImageIFD.DateTime:
                return self._convert_datetime(d[k])
            else:
                return d[k]
        return ''

    def _unmap(self, exif, mapping):
        if isinstance(mapping, dict):
            res = {}
            for key, value in mapping.items():
                res[key] = self._unmap(exif, value)
        elif isinstance(mapping, tuple):
            res = exif
            for key in mapping:
                r = self._get(res, key)
                if isinstance(r, bytes):
                    res = r.decode("utf-8")
                elif r:
                    res = r
                else:
                    return r
        return res


    def get_exif(self, img):
        mapping = self.settings['GALLERY_EXIF']
        try:
            exif = piexif.load(img.info['exif'])
            return self._unmap(exif, mapping)
        except Exception:
            _logger.debug('EXIF information not found')
            return {}

    def get_photo_content(self, path):
        abs_path = os.path.join(self.path, path)
        # _logger.debug('img path: {}'.format(abs_path))

        image = Image.open(abs_path)

        exif = self.get_exif(image)

        res = {
            'info': exif
        }

        if True: # self.settings['GALLERY_COPY_ORIGINAL']:
            res['original_path'] = path

        filename = os.path.split(path)[1]
        directory = os.path.split(path)[0]

        for name, output_type in self.settings['GALLERY_IMAGE_OUTPUTS'].items():
            res[name] = os.path.join(directory, output_type['filename'].format(filename))

        res['title'] = os.path.splitext(os.path.split(path)[1])[0]

        photo = Photo(content=image, metadata=res, source_path=path)
        # _logger.debug("Photo {}".format(photo))

        return photo

    def generate_context(self):
        _logger.debug('Generate context')

        files = self.get_files(
            self.settings['GALLERY_PATHS'],
            self.settings['GALLERY_PATHS_EXCLUDE'],
            ['jpg'],
        )

        for f in files:
            photo = self.get_cached_data(f, None)
            if photo is None:
                photo = self.get_photo_content(f)

            self.photos.append(photo)
            self.cache_data(f, photo)

        self.save_cache()

    def _need_processing(self, info):
        output_path = os.path.join(self.settings['OUTPUT_PATH'], info.original_path)
        output_directory = os.path.split(output_path)[0]
        input_filename = os.path.split(info.original_path)[1]

        for name, output_type in self.settings['GALLERY_IMAGE_OUTPUTS'].items():
            output_filename = output_type['filename'].format(input_filename)
            path = os.path.join(output_directory, output_filename)
            if not os.path.exists(path):
                return True
        return False

    def generate_output(self, writer):
        debug = False
        _logger.debug('Generate Output: {}'.format(self.settings['OUTPUT_PATH']))

        pool = mp.Pool(self.settings['GALLERY_MAX_JOBS'])
        params = []

        for photo in self.photos:
            if self._need_processing(photo):
                abs_path = os.path.join(self.path, photo.original_path)
                params.append((abs_path, photo, self.settings))

        res = pool.starmap(process_image, params)
        self.generate_pages(writer)

    def generate_pages(self, writer):
        """Generate the pages on the disk"""
        write = partial(writer.write_file,
                                relative_urls=self.settings['RELATIVE_URLS'])
        self.generate_photo_pages(write)
        self.generate_gallery_templates(write)

    def generate_photo_pages(self, write):
        _logger.debug("Generate photo pages")
        template = self.settings['GALLERY_PHOTO_TEMPLATE']
        for photo in self.photos:
            write(photo.save_as, self.get_template(photo.template),
                  self.context, photo=photo, blog=True)

    def generate_gallery_templates(self, write):
        _logger.debug("Generate gallery pages")

        PAGINATED_TEMPLATES = ['gallery']
        TEMPLATES = ['gallery']

        for template in TEMPLATES:
            paginated = {}
            if template in PAGINATED_TEMPLATES:
                paginated = {'photos': self.photos}

            save_as = self.settings.get("{}_SAVE_AS".format(template.upper()),
                                        '{}.html'.format(template))
            if not save_as:
                continue

            _logger.debug("Write. saveas: {}".format(save_as))

            write(save_as, self.get_template(template),
                  self.context, blog=True, paginated=paginated,
                  page_name=os.path.splitext(save_as)[0])

def photo_generator(generators):
    return PhotoGenerator

def register():
    signals.initialized.connect(initialized)

    try:
        signals.get_generators.connect(photo_generator)
    except Exception as e:
        _logger.exception('Plugin failed to execute: {}'.format(pprint.pformat(e)))
