import os

from ggly.ggly import Ggly
from ggly.handlers.fb import FacebookHandler
from ggly.handlers.url import UrlHandler

ggly = Ggly()
url_handler = UrlHandler(ggly)
fb = FacebookHandler(ggly, os.environ.get('FB_ACCESS_TOKEN', None), os.environ.get('FB_VERIFY_TOKEN', None))


def handle_url(request):
    return url_handler.handle_http_request(request)


def handle_fb_webhook(request):
    return fb.handle_http_request(request)


def handle_fb_gcs_event(data, context):
    return fb.handle_gcs_event(data, context)
