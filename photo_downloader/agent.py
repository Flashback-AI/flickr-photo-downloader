"""pseudo code"""
import types
import json
# import time
from datetime import datetime

import flickrapi
import tinydb

# local libraries
import settings


class Agent:
    def __init__(self):
        pass


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

        for photo in self.flickr_etree.walk_set(album_id, per_page=self.FLICKR_MAX_PAGE_SIZE):

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
                  photo.get('id'),
                  photo.get('title')
                  )
            count += 1

            # if (func is not None) and callable(func):  # accepts more callable object types
            if (func is not None) and isinstance(func, types.FunctionType):  # strictly functions
                func(photo.get('id'), user_id, album_id, photo)


# print("### Photo Info ###", json.dumps(get_photo_info('2163445674'), indent=2))
# print("### Photo Exif ###", json.dumps(get_photo_exif('2163445674'), indent=2))
# print("### Photo Sizes ###", json.dumps(get_photo_sizes('2163445674'), indent=2))

# print("### LICENSES ###", json.dumps(get_license_types(), indent=2))

# print("### COMMONS INSTITUTIONS ###", json.dumps(get_commons_institutions(), indent=2))

F = _Flickr()

print("### License Info ###", json.dumps(
    F.get_license_types(), indent=2))

print("### Album Info ###", json.dumps(
    F.get_album_info(
        F.default_user_id,
        F.default_album_id
    ), indent=2))

# F.walk_album()
