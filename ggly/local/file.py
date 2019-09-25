import logging

import cv2

from ggly.ggly import Ggly

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
    img, _ = Ggly(debug=True).go(cv2.imread("./.test_img/test_1.jpg"))
    cv2.imwrite('./.test_img/test_ggly.jpg', img)
