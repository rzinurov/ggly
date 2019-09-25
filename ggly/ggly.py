import logging
import os
import random

import cv2
from numpy.core.records import ndarray

from ggly import img_utils

data_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/'


class Rect(object):
    def __init__(self, dimensions):
        (self.x, self.y, self.width, self.height) = dimensions

    @property
    def center(self):
        return int(self.x + self.width / 2), int(self.y + self.height / 2)


class Ggly(object):
    img_max_size = (2048, 2048)
    eye_img = cv2.imread(data_dir + '/img/googly_eye.png', -1)
    face_cascade = cv2.CascadeClassifier(data_dir + '/haarcascades/haarcascade_frontalface_default.xml')
    right_eye_cascade = cv2.CascadeClassifier(data_dir + '/haarcascades/haarcascade_righteye_2splits.xml')
    left_eye_cascade = cv2.CascadeClassifier(data_dir + '/haarcascades/haarcascade_lefteye_2splits.xml')
    debug = False

    def __init__(self, debug: bool = False):
        super().__init__()
        self.debug = debug

    def go(self, img: ndarray):
        img = img_utils.resize_to_fit(img.copy(), self.img_max_size[0], self.img_max_size[1])
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width, _ = img.shape

        faces = self.face_cascade.detectMultiScale(
            img_gray,
            scaleFactor=1.05,
            minNeighbors=2,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        face_count = 0
        for face in [Rect(x) for x in faces]:
            logging.debug("Found face at %s:%s" % (face.x, face.y))
            face_img_gray = img_gray[face.y:face.y + face.height, face.x:face.x + face.width]
            face_img = img[face.y:face.y + face.height, face.x:face.x + face.width]
            r_eye = self.__search_right_eye(face_img_gray, face)
            if r_eye:
                l_eye = self.__search_left_eye(face_img_gray, face)
                if not l_eye:
                    l_eye = self.__fake_left_eye(r_eye, face)
                self.__draw_eye(r_eye, face, face_img)
                self.__draw_eye(l_eye, face, face_img)
                face_count += 1
                if self.debug:
                    img_utils.draw_rect(face_img, l_eye, (0, 255, 0))
                    img_utils.draw_center_line(face_img, r_eye, l_eye, (0, 255, 0))
                    img_utils.draw_rect(face_img, r_eye, (255, 255, 0))
            if self.debug:
                img_utils.draw_rect(img, face, (255, 0, 255))
        return img, face_count

    def __search_right_eye(self, face_img_gray: ndarray, face: Rect):
        right_eyes = []
        for i in range(3, -1, -1):
            candidates = self.right_eye_cascade.detectMultiScale(face_img_gray, minNeighbors=i)
            right_eyes = [x for x in candidates if self.__is_right_eye_valid(Rect(x), face)]
            if len(right_eyes) > 0:
                logging.debug("Found right eye with accuracy %s" % i)
                break
        return Rect(right_eyes[0]) if right_eyes else None

    def __search_left_eye(self, face_img_gray: ndarray, face: Rect):
        left_eyes = []
        for i in range(3, -1, -1):
            candidates = self.left_eye_cascade.detectMultiScale(face_img_gray, minNeighbors=i)
            left_eyes = [x for x in candidates if self.__is_left_eye_valid(Rect(x), face)]
            if len(left_eyes) > 0:
                logging.debug("Found left eye with accuracy %s" % i)
                break
        return Rect(left_eyes[0]) if left_eyes else None

    @staticmethod
    def __fake_left_eye(r_eye: Rect, face: Rect):
        logging.debug("Made fake left eye")
        return Rect([r_eye.x + int(2 * (face.width / 2 - r_eye.center[0])), r_eye.y,
                     r_eye.width, r_eye.height])

    @staticmethod
    def __is_right_eye_valid(eye: Rect, face: Rect):
        if eye.center[0] > face.width / 2:  # left eye recognized as right eye
            return False
        if eye.center[1] > face.height / 2:  # nose recognized as right eye
            return False
        return True

    @staticmethod
    def __is_left_eye_valid(eye: Rect, face: Rect):
        if eye.center[0] < face.width / 2:  # right eye recognized as left eye
            return False
        if eye.center[1] > face.height / 2:  # noses recognized as left eye
            return False
        return True

    def __draw_eye(self, eye_rect: Rect, face: Rect, face_img: ndarray):
        scale_factor = 1.5
        eye_img = self.eye_img.copy()
        eye_img = img_utils.rotate(eye_img, random.randint(0, 360))
        eyes_width_scaled = int(eye_rect.width * scale_factor)
        eyes_height_scaled = int(eye_rect.height * scale_factor)
        x1 = max(eye_rect.center[0] - int(eyes_width_scaled / 2), 0)
        x2 = min(x1 + eyes_width_scaled, face.width)
        y1 = max(eye_rect.center[1] - int(eyes_height_scaled / 2), 0)
        y2 = min(y1 + eyes_height_scaled, face.height)
        eye_img = cv2.resize(eye_img, (x2 - x1, y2 - y1), interpolation=cv2.INTER_AREA)
        mask = eye_img[:, :, 3]
        mask_inv = cv2.bitwise_not(mask)
        eye_img = eye_img[:, :, 0:3]  # convert to BGR
        roi = face_img[y1:y2, x1:x2]
        roi_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        roi_fg = cv2.bitwise_and(eye_img, eye_img, mask=mask)
        dst = cv2.add(roi_bg, roi_fg)
        face_img[y1:y2, x1:x2] = dst
