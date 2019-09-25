import logging
import os
import tempfile

from flask import Flask, request

import main
from ggly.ggly import Ggly

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

img_dir = '%s/ggly/' % tempfile.gettempdir()
if not os.path.exists(img_dir):
    os.makedirs(img_dir)
logger.debug("Writing files to %s", img_dir)

ggly = Ggly(debug=True)
app = Flask(__name__)


@app.route('/ggly')
def ggly():
    return main.handle_url(request)
