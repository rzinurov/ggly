import cv2
import numpy as np


def rotate(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def resize_to_fit(image, width, height):
    (img_height, img_width) = image.shape[:2]
    if img_width <= width and img_height <= height:
        return image
    if img_width > width:
        scale = width / float(img_width)
        dim = (width, int(img_height * scale))
    else:
        scale = height / float(img_height)
        dim = (int(img_width * scale), height)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized


def draw_rect(img, rect, color):
    cv2.rectangle(img, (rect.x, rect.y), (rect.x + rect.width, rect.y + rect.height), color, 2)


def draw_center_line(img, rect1, rect2, color):
    cv2.line(img, rect1.center, rect2.center, color, 2)
