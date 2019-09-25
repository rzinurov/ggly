import logging
import os
import tempfile

WORK_DIR = '%s/ggly/' % tempfile.gettempdir()
if not os.path.exists(WORK_DIR):
    os.makedirs(WORK_DIR)
logging.debug('Writing temp files to %s' % WORK_DIR)


def get_work_dir():
    return WORK_DIR


def delete_if_exists(local_file_path):
    if local_file_path and os.path.exists(local_file_path):
        os.remove(local_file_path)
