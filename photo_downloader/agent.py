"""pseudo code"""
import re
import types
import json
import requests
# import base64
# import time
from datetime import datetime
from pathlib import Path

import flickrapi
from tinydb import TinyDB, Query
from tinydb.table import Document
from tinydb.operations import delete

# local libraries
import settings


class _Flickr:
    """
    a helper class to use the flickrapi library
    """
    FLICKR_UID_LOC = "8623220@N02"
    FLICKR_SID_LOC_1910S = "72157603624867509"
    FLICKR_PID_LOC_CAR = '30331622523'

    FLICKR_SID_LOC_1930S = "72157603671370361"
    FLICKR_SID_LOC_CIVIL_WAR_FACES = "72157625520211184"
    FLICKR_SID_LOC_PHOTOCHROM_TRAVEL = "72157612249760312"
    FLICKR_SID_LOC_GOTTLIEB_JAZZ = "72157624588645784"

    FLICKR_UID_COSTICĂ_ACSINTE = '109550159@N08'  # "82497773@N00"
    FLICKR_SID_CA_MILITARI = "72157676896091115"
    FLICKR_PID_CA_TWO_MEN = '30331622523'

    FLICKR_UID_NA = "35740357@N03"
    FLICKR_UID_SMU_LDC = "41131493@N06"

    FLICKR_MAX_PAGE_SIZE = 500

    default_user_id = FLICKR_UID_COSTICĂ_ACSINTE
    default_album_id = FLICKR_SID_CA_MILITARI
    default_photo_id = FLICKR_PID_CA_TWO_MEN

    FLICKR_CDN_URL = 'https://live.staticflickr.com/'
    FLICKR_PHOTO_URL = 'https://www.flickr.com/photos/'
    FLICKR_SIZE_SET = [
        {"suffix": "s", "class": "thumbnail", "label": "Square", "max_edge": 75,
         "notes": "cropped square"},
        {"suffix": "q", "class": "thumbnail", "label": "Large Square", "max_edge": 150,
         "notes": "cropped square"},
        {"suffix": "t", "class": "thumbnail", "label": "Thumbnail", "max_edge": 100,
         "notes": None},
        {"suffix": "m", "class": "small", "label": "Small", "max_edge": 240,
         "notes": None},
        {"suffix": "n", "class": "small", "label": "Small 320", "max_edge": 320,
         "notes": None},
        {"suffix": "w", "class": "small", "label": "Small 400", "max_edge": 400,
         "notes": None},
        {"suffix": "", "class": "medium", "label": "Medium", "max_edge": 500,
         "notes": None},
        {"suffix": "z", "class": "medium", "label": "Medium 640", "max_edge": 640,
         "notes": None},
        {"suffix": "c", "class": "medium", "label": "Medium 800", "max_edge": 800,
         "notes": None},
        {"suffix": "b", "class": "large", "label": "Large", "max_edge": 1024,
         "notes": None},
        {"suffix": "h", "class": "large", "label": "Large 1600", "max_edge": 1600,
         "notes": "has a unique secret; photo owner can restrict"},  # TODO: verify Large 1600
        {"suffix": "k", "class": "large", "label": "Large 2048", "max_edge": 2048,
         "notes": "has a unique secret; photo owner can restrict"},  # TODO: verify Large 2048
        {"suffix": "3k", "class": "extra large", "label": "Extra Large", "max_edge": 3072,
         "notes": "has a unique secret; photo owner can restrict"},  # TODO: verify Extra Large
        {"suffix": "4k", "class": "extra large", "label": "Extra Large 4096", "max_edge": 4096,
         "notes": "has a unique secret; photo owner can restrict"},  # TODO: verify Extra Large 4096
        {"suffix": "f", "class": "extra large", "label": "Extra Large Frame", "max_edge": 4096,
         "notes": "has a unique secret; photo owner can restrict; only exists for 2:1 aspect \
          ratio photos"},  # TODO: verify Extra Large Frame
        {"suffix": "5k", "class": "extra large", "label": "Extra Large 5120", "max_edge": 5120,
         "notes": "has a unique secret; photo owner can restrict"},  # TODO: verify Extra Large 5120
        {"suffix": "6k", "class": "extra large", "label": "Extra Large 6144", "max_edge": 6144,
         "notes": "has a unique secret; photo owner can restrict"},  # TODO: verify Extra Large 6144
        {"suffix": "o", "class": "original", "label": "Original", "max_edge": None,
         "notes": "has a unique secret; photo owner can restrict; files have full EXIF data; \
         files might not be rotate; files can use an arbitrary file extension"},
    ]

    def __init__(self):
        self.cfg = settings.get_config()

        self.flickr_json = flickrapi.FlickrAPI(
            self.cfg.flickr.api_key,
            self.cfg.flickr.api_secret,
            format='json'
        )

        self.flickr_etree = flickrapi.FlickrAPI(
            self.cfg.flickr.api_key,
            self.cfg.flickr.api_secret,
            format='etree'
        )

    def get_user_info(self, user_id: str = None) -> dict:
        """
        fetches a user info object from flicker
        :param user_id:
        :return:
        """
        user_id = user_id or self.default_user_id
        response = self.flickr_json.people.getInfo(user_id=user_id)

        user_info = json.loads(response.decode('utf-8'))

        return user_info

    def get_user_sets(self, user_id: str = None) -> dict:
        """
        fetches a flickr user's photosets / albums
        :param user_id:
        :return:
        """
        user_id = user_id or self.default_user_id
        response = self.flickr_json.photosets.getList(user_id=user_id)

        sets = json.loads(response.decode('utf-8'))

        return sets

    def get_album_info(self, user_id: str = None, album_id: str = None) -> dict:
        """
        fetches a flicker user's photo album/ photoset meta data / info
        :param user_id:
        :param album_id:
        :return:
        """
        user_id = user_id or self.default_user_id
        album_id = album_id or self.default_album_id

        response = self.flickr_json.photosets.getInfo(
            user_id=user_id,
            photoset_id=album_id
        )

        album = json.loads(response.decode('utf-8'))
        return album

    def get_album_photos(self, user_id: str = None, album_id: str = None) -> dict:
        """
        fetches the photo list for a flickr user's photo album / photoset
        :param user_id:
        :param album_id:
        :return:
        """
        user_id = user_id or self.default_user_id
        album_id = album_id or self.default_album_id

        response = self.flickr_json.photosets.getPhotos(
            user_id=user_id,
            photoset_id=album_id
        )

        photos = json.loads(response.decode('utf-8'))

        return photos

    def get_photo_info(self, photo_id: str = None) -> dict:
        """
        fetches a photo's meta data / info
        :param photo_id:
        :return:
        """
        photo_id = photo_id or self.default_photo_id

        response = self.flickr_json.photos.getInfo(photo_id=photo_id)

        photo_info = json.loads(response.decode('utf-8'))

        return photo_info

    def get_photo_sizes(self, photo_id: str = None) -> dict:
        """
        fetches a photo's available sizes, and the corresponding urls
        :param photo_id:
        :return:
        """
        photo_id = photo_id or self.default_photo_id

        response = self.flickr_json.photos.getSizes(photo_id=photo_id)

        photo_size = json.loads(response.decode('utf-8'))

        return photo_size

    def get_photo_exif(self, photo_id: str = None) -> dict:
        """
        fetches a photo's exif meta data
        :param photo_id:
        :return:
        """
        photo_id = photo_id or self.default_photo_id

        response = self.flickr_json.photos.getExif(photo_id=photo_id)

        photo_exif = json.loads(response.decode('utf-8'))

        return photo_exif

    def get_commons_institutions(self) -> dict:
        """
        fetches a list institutions that are participating in creative commons, /
        and returns a minimal user object
        :return:
        """
        response = self.flickr_json.commons.getInstitutions()

        institutions = json.loads(response.decode('utf-8'))

        return institutions

    def get_license_types(self) -> dict:
        """
        fetches a list of license types with their type id, name, and url to the full license text
        :return:
        """
        response = self.flickr_json.photos.licenses.getInfo()

        license_types = json.loads(response.decode('utf-8'))

        return license_types

    def walk_album(self, user_id: str = None, album_id: str = None, func: callable = None):
        """
        a helper function to iterate through all of the photos in a photo album / photoset /
        calls func(photo_id, user_id, album_id, photo) for each photo
        :param user_id:
        :param album_id:
        :param func:
        :return:
        """

        album_info = self.get_album_info(user_id, album_id)
        album_photo_count = album_info['photoset']['count_photos']

        start = datetime.now()

        count = 0

        for _photo in self.flickr_etree.walk_set(album_id, per_page=self.FLICKR_MAX_PAGE_SIZE):

            now = datetime.now()
            deltat = now - start
            percent = count / album_photo_count

            if percent != 0:
                remaining = (deltat / percent)
                eta = remaining + now
                timestr = eta.strftime("%H:%M:%S")
            else:
                timestr = None

            print(count,
                  "{:.1f}".format(percent * 100),
                  timestr,
                  _photo.get('id'),
                  _photo.get('title')
                  )
            count += 1

            # if (func is not None) and callable(func):  # accepts more callable object types
            if (func is not None) and isinstance(func, types.FunctionType):  # strictly functions
                func(_photo.get('id'), user_id, album_id, _photo)

    # TODO: DEPRECATE
    def generate_photo_sizes(self, user_id: str, album_id: str, photo_etree) -> list:
        """
        generates a set of possible sizes and urls for the flickr photo
        :param user_id:
        :param album_id:
        :param photo:
        :return:
        """
        _p = {
            'CDN': self.FLICKR_CDN_URL,
            'WEB': self.FLICKR_PHOTO_URL,
            'user_id': user_id,
            'album_id': album_id,
            'id': photo_etree.get('id'),
            'server_id': photo_etree.get('server'),
            'secret': photo_etree.get('secret')
        }
        _sizes = []
        for s in self.FLICKR_SIZE_SET:
            # default url format
            _source = f"{_p['CDN']}{_p['server_id']}/{_p['id']}_{_p['secret']}_{s['suffix']}.jpg"

            # THIS CODE DOESN'T WORK FOR THE FOLLOWING REASONS
            # All photo image URLs use a secret value that's provided by API methods.
            # All sizes below the H (1600) size use one shared secret.
            # All sizes above and including the H (1600) size each use a unique secret
            # for just themselves.
            # The original size, regardless of dimensions, always uses its own secret.

            if s['label'] == 'Medium':
                _source = f"{_p['CDN']}{_p['server_id']}/{_p['id']}_{_p['secret']}.jpg"
            elif s['label'] == 'Original':
                # TODO figure out a way to get the format without an api call, /
                #  jpg is not guaranteed or likely
                o_format = 'jpg'
                o_secret = None  # can't get this secret without 2nd api call
                _source = (
                    f"{_p['CDN']}{_p['server_id']}/{_p['id']}_{o_secret}_{s['suffix']}."
                    f"{o_format}"
                )
                print(_source)
                x = requests.head(_source)
                print(x)

            _photo_size = {
                'height': None,
                'width': None,
                'label': s['label'],
                'media': 'photo',
                # photo source image url
                'source': _source,
                # photo web page
                'url': f"{_p['WEB']}{_p['user_id']}/{_p['id']}"
            }

            _sizes.append(_photo_size)

        return _sizes


def _string_to_abv_title(title: str = ''):
    """
    :param title:
    :return abv:
    """
    # TODO: make names path safe, exclude (<>:"/\|?*)
    _title = title
    abv = _title.title().replace(' ', '').replace('The', '')

    # was getting problematic with international names, and with multiple albums
    # if len(_title.split(' ')) <= 2 or len(_title <= 16):
    #     abv = _title.title().replace(' ', '_').lower()
    # else:
    #     abv = re.sub(
    #        '([Tt]he\\s*)|([a-z]{4,}\\b)|(\\s)',
    #        '',
    #        _title.title().replace('Of', 'O')
    #    ).lower()

    return abv


class Agent:
    """
    Album download agent
    """
    flickr = _Flickr()
    cfg = settings.get_config()

    # TODO: what file formats should we support?
    photo_extensions = {'.jpg', '.jpeg', '.tiff', '.tif', '.png', '.bmp', '.webp'}

    user_id = None
    album_id = None
    album = {}
    photos_dir = []

    def __init__(self, user_id: str, album_id: str):
        self.user_id = user_id
        self.album_id = album_id

        self.file_path = self.cfg.get('photos.path')
        self.db_path = self.cfg.get('tinydb.path')

        self.db = TinyDB(
            settings.fix_path(self.db_path),
            sort_keys=False,
            indent=2,
            separators=(',', ': ')
        )

        self.licenses = self.db.table('licenses')
        self.users = self.db.table('users')
        self.albums = self.db.table('albums')
        self.photos = self.db.table('photos')
        self.files = self.db.table('files')

        print("### loaded tables ###", self.db.tables())
        self.scan_files()
        self.scan_photos()

        pass

    def sync_licenses(self, service: str = 'flickr') -> dict:
        """
        fetches the license mapping from flickr and updates
        :param service:
        :return license:
        """
        license_info = {}
        flickr_license_map = {}
        flickr_license_list = self.flickr.get_license_types()['licenses']['license']

        # remap according to the license id
        for item in flickr_license_list:
            flickr_license_map[item['id']] = item

        license_info['map'] = flickr_license_map
        license_info['_source_api'] = service
        license_info['_type'] = 'license'
        license_info['_uuid'] = '.'.join([
            license_info['_source_api'],
            license_info['_type']
        ])

        license_info['id'] = license_info['_uuid']

        print(json.dumps(license_info, indent=2))

        license_q = Query()
        self.licenses.upsert(
            license_info,
            license_q.id == license_info['id']
        )

        return license_info

    def get_flickr_license(self, license_id: str) -> dict:
        """
        gets an individual license object based on the flickr id
        :param license_id:
        :return:
        """
        license_q = Query()
        flickr_license_info = self.licenses.get(license_q.id == 'flickr.license')
        license_info = flickr_license_info.get('map', {}).get(license_id)
        # TODO: check album _update_date, if out of date, get sync album before returning

        return license_info

    def sync_album(self):
        """
        synchronize album data from flickr, and update db
        :return:
        """
        album_info = self.flickr.get_album_info(self.user_id, self.album_id)['photoset']

        # TODO: add _update_date - flickr want's 24hr caching only
        album_info['_source_api'] = "flickr"
        album_info['_type'] = 'album'
        album_info['_uuid'] = '.'.join([
            album_info['_source_api'],
            album_info['_type'],
            album_info['id']
        ])
        album_info['_path'] = '/'.join([
            _string_to_abv_title(album_info.get('username')),
            _string_to_abv_title(album_info.get('title', {}).get('_content'))
        ])

        print(json.dumps(album_info, indent=2))
        album_q = Query()
        self.albums.upsert(
            album_info,
            album_q.id == album_info['id']
        )

        return album_info

    def get_album(self):
        """
        gets the current album object from the db
        :return album:
        """
        album = Query()
        album_info = self.albums.get(album.id == self.album_id)
        # TODO: check album _update_date, if out of date, get sync album before returning

        return album_info

    def get_album_path(self):
        """
        returns the album path from the current album
        :return:
        """
        return self.get_album()['_path']

    def get_album_photos(self) -> list:
        """
        queries the DB and returns the set of photos for an album
        :return:
        """
        _q = Query()
        _photos = self.photos.search(
            (_q['_user_id'] == self.user_id) &
            (_q['_album_id'] == self.album_id)
        )
        return _photos

    def sync_user(self):
        """
        synchronize user data from flickr
        :return:
        """
        user_info = self.flickr.get_user_info(self.user_id)['person']

        # TODO: add _update_date - flickr want's 24hr caching only
        user_info['_source_api'] = 'flickr'
        user_info['_type'] = 'user'
        user_info['_uuid'] = '.'.join([
            user_info['_source_api'],
            user_info['_type'],
            user_info['id']
        ])
        user_info['_path'] = '/'.join([
            _string_to_abv_title(user_info.get('username', {}).get('_content'))
        ])

        print(json.dumps(user_info, indent=2))
        user_q = Query()
        self.users.upsert(
            user_info,
            user_q.id == user_info['id']
        )

        return user_info

    def get_user(self):
        """
        get's the current user object from the db
        :return album:
        """
        user_q = Query()
        user_info = self.albums.get(user_q.id == self.user_id)
        # TODO: check album _update_date, if out of date, get sync album before returning

        return user_info

    def get_user_path(self):
        """
        returns the album path from the current album
        :return:
        """
        return self.get_user()['_path']

    def sync_photo(self, photo_id: str):
        """
        synchronize photo data from flickr
        :return:
        """
        photo_info = self.flickr.get_photo_info(photo_id)['photo']
        photo_exif = self.flickr.get_photo_exif(photo_id)['photo']['exif']
        photo_sizes = self.flickr.get_photo_sizes(photo_id)['sizes']

        photo_info['sizes'] = photo_sizes
        photo_info['exif'] = photo_exif

        # TODO: add _update_date - flickr want's 24hr caching only
        photo_info['_source_api'] = 'flickr'
        photo_info['_type'] = 'photo'
        photo_info['_uuid'] = '.'.join([
            photo_info['_source_api'],
            photo_info['_type'],
            photo_info['id']
        ])

        # TODO: technically a photo can belong to two albums,
        #  so when upserting, we should first check what albums the photos
        #  is already a part of, and then add this photo to that list
        photo_info['_album_id'] = self.album_id
        photo_info['_user_id'] = self.user_id

        # TODO: is this the best photo to get?
        _source = self.get_photo_largest(photo_id, photo_info)['source']
        _path = _source.split('/')
        _ext = _path[-1].split('.')[-1]

        photo_info['_path'] = '/'.join([
            _string_to_abv_title(photo_info.get('owner', {}).get('username')),
            _string_to_abv_title(self.get_album().get('title', {}).get('_content')),
            '.'.join([photo_info['id'], _ext])
        ])

        print(json.dumps(photo_info, indent=2))
        # print(json.dumps(photo_exif, indent=2))
        # print(json.dumps(photo_sizes, indent=2))

        photo_q = Query()
        self.photos.upsert(
            photo_info,
            photo_q.id == photo_info['id']
        )

        return photo_info

    def get_photo(self, photo_id: str):
        """
        get's the current user object from the db
        :return album:
        """
        photo_q = Query()
        photo_info = self.photos.get(photo_q.id == photo_id)
        # TODO: check album _update_date, if out of date, get sync album before returning

        return photo_info

    def get_photo_size(self, photo_id: str, size_label: str) -> dict:
        """
        returns a size obj to the specified photo and size, includes "source" url, and web "url"
        common labels
         'Square', 'Large Square', 'Thumbnail',
         'Small', 'Small 320', 'Small 400',
         'Medium', 'Medium 640', 'Medium 800',
         'Large',
         'Original'

        :param photo_id:
        :param size_label:
        :return:
        """
        _photo = self.get_photo(photo_id)
        size_list = _photo.get('sizes', {}).get('size', [])
        _photo_size_info = None

        for size in size_list:
            if size['label'] == size_label:
                _photo_size_info = size

        return _photo_size_info

    def get_photo_largest(self, photo_id: str, photo_info=None) -> dict:
        """
        gets the photo, and finds the largest image available
        # TODO is this always the 'Original'?
        :param photo_id:
        :param photo_info:
        :return:
        """
        _photo = self.get_photo(photo_id)
        if photo_info and photo_info['sizes']['size']:
            size_list = photo_info.get('sizes', {}).get('size', [])
        else:
            size_list = _photo.get('sizes', {}).get('size', [])

        _photo_size_info = None
        _largest_area = 0
        _largest_size = None

        for size in size_list:
            area = int(size['width']) * int(size['height'])
            if area >= _largest_area:
                _largest_size = size

        _photo_size_info = _largest_size
        return _photo_size_info

    def get_photo_path(self, photo_id: str):
        """
        returns the photo path from the current album
        :return:
        """
        return self.get_photo(photo_id)['_path']

    def validate_photo_dir(self):
        """
        check for missing photo info, or photo files
        :return:
        """

    def scan_files(self, sub_path: str = None):
        """
        scan photo directory for files
        :return:
        """
        _p = self.file_path
        if sub_path:
            _p += "/" + sub_path

        p = Path(_p)
        path_glob = p.rglob('*.*')
        file_list = list(path_glob)

        print(file_list)
        return file_list

    def scan_photos(self, sub_path: str = None):
        """
        scan photo directory for photos
        :return:
        """
        _p = self.file_path
        if sub_path:
            _p += "/" + sub_path

        p = Path(self.file_path)
        path_glob = p.rglob('*.*')
        file_list = []

        for file in path_glob:
            if file.suffix in self.photo_extensions:
                file_list.append(file)

        print(file_list)
        return file_list

    def sync_photos(self):
        """
        synchronize photo data from flickr
        :return:
        """
        dir_path = '\\'.join([self.file_path,
                              self.get_album_path()])
        p3 = Path(dir_path)
        if not p3.exists():
            p3.mkdir(parents=True)

        photo_list = self.get_album_photos()
        for _photo in photo_list:
            p = Path(self.file_path + '\\' + _photo['_path'])
            if p.exists():
                pass
            else:
                _url = self.get_photo_largest(_photo['id'])['source']
                r = requests.get(_url, allow_redirects=True)

                # TODO: temporary until i fix _path on the photos, wanted photos to have the 'suffix' on them.
                file_name = re.sub('(_[A-Za-z0-9]*_)', '_', _url).split('/')[-1]
                file_path = '\\'.join([
                    self.file_path,
                    self.get_album_path(),
                    file_name
                ])
                p2 = Path(file_path)
                p2.write_bytes(r.content)
                # open(p2, 'wb').write(r.content)
                pass


# print("### Photo Info ###", json.dumps(get_photo_info('2163445674'), indent=2))
# print("### Photo Exif ###", json.dumps(get_photo_exif('2163445674'), indent=2))
# print("### Photo Sizes ###", json.dumps(get_photo_sizes('2163445674'), indent=2))

# print("### LICENSES ###", json.dumps(get_license_types(), indent=2))

# print("### COMMONS INSTITUTIONS ###", json.dumps(get_commons_institutions(), indent=2))

F = _Flickr()

A = Agent(F.default_user_id, F.default_album_id)
# A.sync_album()
# A.sync_user()
# A.sync_licenses()
# photo = A.sync_photo(_Flickr.default_photo_id)

album_path = A.get_album_path()
A.scan_files(album_path)
A.scan_photos(album_path)
A.sync_photos()


# print("### License Info ###", json.dumps(
#     F.get_license_types(), indent=2))

# print("### Album Info ###", json.dumps(
#     F.get_album_info(
#         F.default_user_id,
#         F.default_album_id
#     ), indent=2))

# hack to update photos
# q = Query()
# A.photos.upsert({'_album_id': A.album_id}, q.owner.nsid == A.user_id)
# A.photos.update(delete('_album'), (q.owner.nsid == A.user_id) & (q['_album'].exists()))
# A.photos.upsert({'_user_id': A.user_id}, q.owner.nsid == A.user_id)


def test_func(photo_id, user_id, album_id, photo_etree):
    F.generate_photo_sizes(user_id, album_id, photo_etree)


def _sync_photo(photo_id, user_id, album_id, photo_etree):
    A.sync_photo(photo_id)

# F.walk_album(
#     F.default_user_id,
#     F.default_album_id,
#     _sync_photo
# )
