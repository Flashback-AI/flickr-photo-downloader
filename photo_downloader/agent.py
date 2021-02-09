"""pseudo code"""
import re
import types
import json
# import base64
# import time
from datetime import datetime
from pathlib import Path

import flickrapi
from tinydb import TinyDB, Query
from tinydb.table import Document

# local libraries
import settings


class _Flickr:
    """
    a helper class to use the flickrapi library
    """
    FLICKR_UID_LOC = "8623220@N02"
    FLICKR_SID_LOC_1910S = "72157603624867509"
    FLICKR_SID_LOC_1930S = "72157603671370361"
    FLICKR_SID_LOC_CIVIL_WAR_FACES = "72157625520211184"
    FLICKR_SID_LOC_PHOTOCHROM_TRAVEL = "72157612249760312"
    FLICKR_SID_LOC_GOTTLIEB_JAZZ = "72157624588645784"

    FLICKR_UID_NA = "35740357@N03"
    FLICKR_UID_SMU_LDC = "41131493@N06"
    FLICKR_MAX_PAGE_SIZE = 500

    default_user_id = FLICKR_UID_LOC
    default_album_id = FLICKR_SID_LOC_1910S
    default_photo_id = '2163445674'

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
        user_id = user_id or self.default_user_id
        album_id = album_id or self.default_album_id

        set_info = self.get_album_info(user_id, album_id)
        set_photo_count = set_info['photoset']['count_photos']

        start = datetime.now()

        count = 0

        for _photo in self.flickr_etree.walk_set(album_id, per_page=self.FLICKR_MAX_PAGE_SIZE):

            now = datetime.now()
            deltat = now - start
            percent = count / set_photo_count

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
                func(photo.get('id'), user_id, album_id, photo)


def _string_to_abv_title(title: str = ''):
    """
    shortens a string to an abbreviated title
    ex. 'The Library of Congress -> loc
    :param title:
    :return abv:
    """
    abv = re.sub(
        '([Tt]he\\s*)|([a-z]{4,}\\b)|(\\s)',
        '',
        title.title().replace('Of', 'O')
    ).lower()

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
            sort_keys=True,
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
        self.licenses.upsert(license_info, license_q.id == license_info['id'])

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
        self.albums.upsert(album_info, album_q.id == album_info['id'])

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
        self.users.upsert(user_info, user_q.id == user_info['id'])

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

        # TODO: add _update_date - flickr want's 24hr caching only
        photo_info['_source_api'] = 'flickr'
        photo_info['_type'] = 'photo'
        photo_info['_uuid'] = '.'.join([
            photo_info['_source_api'],
            photo_info['_type'],
            photo_info['id']
        ])

        photo_info['_path'] = '/'.join([
            _string_to_abv_title(photo_info.get('owner', {}).get('username')),
            _string_to_abv_title(self.get_album().get('title', {}).get('_content'))
            # TODO: Add actual file name to path
        ])

        photo_info['sizes'] = photo_sizes
        photo_info['exif'] = photo_exif

        print(json.dumps(photo_info, indent=2))
        # print(json.dumps(photo_exif, indent=2))
        # print(json.dumps(photo_sizes, indent=2))

        photo_q = Query()
        self.photos.upsert(photo_info, photo_q.id == photo_info['id'])

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

    def get_photo_largest(self, photo_id: str) -> dict:
        """
        gets the photo, and finds the largest image available
        # TODO is this always the 'Original'?
        :param photo_id:
        :return:
        """
        _photo = self.get_photo(photo_id)
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

    def scan_files(self):
        """
        scan photo directory for files
        :return:
        """
        p = Path(self.file_path)
        path_glob = p.rglob('*.*')
        file_list = list(path_glob)

        print(file_list)
        return file_list

    def scan_photos(self):
        """
        scan photo directory for photos
        :return:
        """
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
photo = A.sync_photo(_Flickr.default_photo_id)
print(A.get_photo_size(_Flickr.default_photo_id, 'Original')['source'])
print(A.get_photo_largest(_Flickr.default_photo_id)['source'])

# print("### License Info ###", json.dumps(
#     F.get_license_types(), indent=2))

# print("### Album Info ###", json.dumps(
#     F.get_album_info(
#         F.default_user_id,
#         F.default_album_id
#     ), indent=2))

# F.walk_album()
