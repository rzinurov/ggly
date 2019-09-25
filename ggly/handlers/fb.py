import logging
import random
import string
import time
import urllib.request

import cv2
from flask import Response
from pymessenger import Bot

from ggly.file_utils import get_work_dir, delete_if_exists
from ggly.gcs_utils import download_json, update_metadata, upload, upload_as_json
from ggly.ggly import Ggly

IMG_GCS_BUCKET = 'ggly'
WORKER_GCS_BUCKET = 'ggly-tasks-fb'

KEY_STATUS = 'status'
BLOB_STATUS_PENDING = 'pending'
STATUS_PROCESSING = 'processing'
BLOB_STATUS_DONE = 'done'
BLOB_STATUS_ERROR = 'error'


def verify_fb_token(request, verify_token):
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == verify_token:
        return Response(challenge, status=200)
    return Response('Invalid verification token', status=403)


def filter_attachments(attachments):
    return [x for x in attachments if x['type'] == 'image' and x['payload'].get('sticker_id') is None]


def generate_basename():
    letters = string.ascii_lowercase + string.digits
    return '%s_%s' % (int(time.time() * 1000), ''.join(random.choice(letters) for _ in range(5)))


class FacebookHandler(object):
    verify_token: str = None
    bot: Bot = None
    ggly: Ggly = None
    work_dir: str = None

    def __init__(self, ggly: Ggly, access_token: str, verify_token: str):
        super().__init__()
        if access_token is None:
            logging.warning("Facebook access token not set. You will not be able to use messenger bot.")
        self.verify_token = verify_token
        self.bot = Bot(access_token)
        self.ggly = ggly
        self.work_dir = get_work_dir()

    def handle_http_request(self, request):
        if request.method == 'GET':
            logging.debug('FB verify token request')
            return verify_fb_token(request, self.verify_token)
        else:
            payload = request.get_json()
            logging.info('FB request: %s', payload)
            for event in payload['entry']:
                for msg in event['messaging']:
                    msg_recipient_id = msg['sender']['id']
                    if msg.get('message'):
                        msg_img_attachments = filter_attachments(msg['message'].get('attachments', []))
                        if len(msg_img_attachments) == 0:
                            self.__send_text(msg_recipient_id, "Send me a picture of a human face")
                        else:
                            upload_as_json(WORKER_GCS_BUCKET, generate_basename() + '.json', msg)
                    else:
                        self.__send_text(msg_recipient_id, "Send me a picture of a human face")
            return Response('OK', status=200)

    def handle_gcs_event(self, data, context):
        logging.info('FB event: %s %s', data, context)
        gcs_file_path = format(data['name'])
        msg, metadata = download_json(WORKER_GCS_BUCKET, gcs_file_path)
        if metadata.get(KEY_STATUS, BLOB_STATUS_PENDING) != BLOB_STATUS_PENDING:
            logging.warning('Ignoring blob %s because of its status', gcs_file_path)
            return
        update_metadata(WORKER_GCS_BUCKET, gcs_file_path, {KEY_STATUS: STATUS_PROCESSING})
        msg_recipient_id = msg['sender']['id']
        try:
            self.__send_text(msg_recipient_id, "Let's see what we've got here")
            msg_img_attachments = filter_attachments(msg['message'].get('attachments', []))
            for idx, attachment in enumerate(msg_img_attachments):
                file_basename = gcs_file_path.split('/')[-1].replace('.json', '_' + str(idx))
                self.__process_url(msg_recipient_id, file_basename, attachment)
            update_metadata(WORKER_GCS_BUCKET, gcs_file_path, {KEY_STATUS: BLOB_STATUS_DONE})
        except Exception as e:
            logging.error(e)
            if msg_recipient_id:
                self.__send_text(msg_recipient_id, "I couldn't make it")
            update_metadata(WORKER_GCS_BUCKET, gcs_file_path, {KEY_STATUS: BLOB_STATUS_ERROR})

    def __process_url(self, msg_recipient_id, file_basename, attachment):
        src_path = '%s/%s.jpg' % (self.work_dir, file_basename)
        dest_path = '%s/%s_ggly.jpg' % (self.work_dir, file_basename)
        try:
            urllib.request.urlretrieve(attachment['payload']['url'], src_path)
            upload(IMG_GCS_BUCKET, src_path)
            output, face_count = self.ggly.go(cv2.imread(src_path))
            if face_count > 0:
                cv2.imwrite(dest_path, output)
                dest_url = upload(IMG_GCS_BUCKET, dest_path, True)
                self.__send_image_url(msg_recipient_id, dest_url)
            else:
                self.__send_text(msg_recipient_id, "I can't recognize any faces on the picture")
            return face_count
        finally:
            delete_if_exists(src_path)
            delete_if_exists(dest_path)

    def __send_text(self, recipient_id, text):
        logging.debug("Sending text message `%s` to %s", text, recipient_id)
        self.bot.send_text_message(recipient_id, text)

    def __send_image_url(self, recipient_id, image_url):
        logging.debug("Sending image URL `%s` to %s", image_url, recipient_id)
        self.bot.send_image_url(recipient_id, image_url)
