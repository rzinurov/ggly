import logging
import sys

import cv2

from ggly.ggly import Ggly

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        logging.error("Unable to capture video")
        sys.exit(-1)
    ggly = Ggly(debug=True)
    while True:
        ret, frame = video_capture.read()
        img, _ = ggly.go(frame)
        cv2.imshow('Press q to exit', cv2.flip(img, 1))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv2.destroyAllWindows()
