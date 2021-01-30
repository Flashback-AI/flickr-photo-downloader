"""pseudo code"""
import json

import flickrapi
# import tinydb

# local libraries
import settings

FLICKR_UID_LOC = "8623220@N02"
FLICKR_SID_LOC_1910S = "72157603624867509"
FLICKR_SID_LOC_1930S = "72157603671370361"
FLICKR_SID_LOC_CIVIL_WAR_FACES = "72157625520211184"
FLICKR_SID_LOC_PHOTOCHROM_TRAVEL = "72157612249760312"
FLICKR_SID_LOC_GOTTLIEB_JAZZ = "72157624588645784"

FLICKR_UID_NA = "35740357@N03"
FLICKR_UID_SMU_LDC = "41131493@N06"


def get_photo_list():
    cfg = settings.get_config()
    flickr = flickrapi.FlickrAPI(cfg.flickr.api_key, cfg.flickr.api_secret, format='json')
    sets_json = flickr.photosets.getList(user_id=FLICKR_UID_LOC)

    sets = json.loads(sets_json.decode('utf-8'))

    return sets


def get_album_info():
    cfg = settings.get_config()
    flickr = flickrapi.FlickrAPI(cfg.flickr.api_key, cfg.flickr.api_secret, format='json')
    album_json = flickr.photosets.getInfo(
        user_id=FLICKR_UID_LOC,
        photoset_id=FLICKR_SID_LOC_1910S
    )

    album = json.loads(album_json.decode('utf-8'))
    return album


def get_album_photos():
    cfg = settings.get_config()
    flickr = flickrapi.FlickrAPI(cfg.flickr.api_key, cfg.flickr.api_secret, format='json')
    photos_json = flickr.photosets.getPhotos(
        user_id=FLICKR_UID_LOC,
        photoset_id=FLICKR_SID_LOC_1910S
    )

    photos = json.loads(photos_json.decode('utf-8'))
    return photos


def get_photo_info(photo_id):
    """
    {
        'id':       '2163445674',
        'secret':   '2b51f055b6',
        'server':   '2072',
        'farm':     3,
        'title':    'Orphans going to Coney Island in Autos, 6/7/11  (LOC)',
        'isprimary':'0',
        'ispublic': 1,
        'isfriend': 0,
        'isfamily': 0
    }
    """
    cfg = settings.get_config()
    flickr = flickrapi.FlickrAPI(cfg.flickr.api_key, cfg.flickr.api_secret, format='json')
    photo_info_json = flickr.photos.getInfo(photo_id=photo_id)

    photo_info = json.loads(photo_info_json.decode('utf-8'))

    return photo_info


def get_photo_sizes(photo_id):
    cfg = settings.get_config()
    flickr = flickrapi.FlickrAPI(cfg.flickr.api_key, cfg.flickr.api_secret, format='json')
    photo_size_json = flickr.photos.getSizes(photo_id=photo_id)

    photo_size = json.loads(photo_size_json.decode('utf-8'))

    return photo_size


def get_photo_exif(photo_id):
    cfg = settings.get_config()
    flickr = flickrapi.FlickrAPI(cfg.flickr.api_key, cfg.flickr.api_secret, format='json')
    photo_exif_json = flickr.photos.getExif(photo_id=photo_id)

    photo_exif = json.loads(photo_exif_json.decode('utf-8'))

    return photo_exif


def get_license_types():
    cfg = settings.get_config()
    flickr = flickrapi.FlickrAPI(cfg.flickr.api_key, cfg.flickr.api_secret, format='json')
    license_types_json = flickr.photos.licenses.getInfo()

    license_types = json.loads(license_types_json.decode('utf-8'))

    return license_types


print("### Photo Info ###", json.dumps(get_photo_info('2163445674'), indent=2))
print("### Photo Exif ###", json.dumps(get_photo_exif('2163445674'), indent=2))
print("### Photo Sizes ###", json.dumps(get_photo_sizes('2163445674'), indent=2))

print("### LICENSES ###", json.dumps(get_license_types(), indent=2))
