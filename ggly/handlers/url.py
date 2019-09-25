import logging
import random
import string
import time
import urllib.request

import cv2
from flask import Response, send_file
from pymessenger import Bot

from ggly.file_utils import get_work_dir, delete_if_exists
from ggly.gcs_utils import upload
from ggly.ggly import Ggly

IMG_GCS_BUCKET = 'ggly'


def generate_basename():
    letters = string.ascii_lowercase + string.digits
    return '%s_%s' % (int(time.time() * 1000), ''.join(random.choice(letters) for _ in range(5)))


class UrlHandler(object):
    verify_token: str = None
    bot: Bot = None
    ggly: Ggly = None
    work_dir: str = None

    def __init__(self, ggly: Ggly):
        super().__init__()
        self.ggly = ggly
        self.work_dir = get_work_dir()

    def handle_http_request(self, request):
        url = request.args.get('url')
        if not url:
            return Response('Please provide image URL', status=400, mimetype='text/plain')
        file_basename = generate_basename()
        src_path = '%s/%s.jpg' % (self.work_dir, file_basename)
        dest_path = '%s/%s_ggly.jpg' % (self.work_dir, file_basename)
        try:
            urllib.request.urlretrieve(url, src_path)
            output, face_count = self.ggly.go(cv2.imread(src_path))
            cv2.imwrite(dest_path, output)
            if face_count > 0:
                upload(IMG_GCS_BUCKET, src_path)
                dest_url = upload(IMG_GCS_BUCKET, dest_path, True)
                logging.debug('Image URL: %s' % dest_url)
                return send_file(dest_path, mimetype='image/jpg')
            else:
                return Response('Unable to detect face', mimetype='text/plain')
        except RequestException as e:
            return Response(e.message, status=e.status, mimetype='text/plain')
        except Exception as e:
            logging.error(e)
            return Response('Unable to process file', status=500, mimetype='text/plain')
        finally:
            delete_if_exists(src_path)
            delete_if_exists(dest_path)


class RequestException(Exception):
    status = 500
    message = 500

    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message
