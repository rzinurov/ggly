import unittest

import cv2

from ggly.ggly import Ggly


class TestGgly(unittest.TestCase):

    def test_group_1(self):
        _, face_count = Ggly().go(cv2.imread("./img/group_1.jpg"))
        self.assertEqual(face_count, 15)

    def test_group_2(self):
        _, face_count = Ggly().go(cv2.imread("./img/group_2.jpg"))
        self.assertEqual(face_count, 5)

    def test_selfie(self):
        _, face_count = Ggly().go(cv2.imread("./img/selfie.jpg"))
        self.assertEqual(face_count, 1)


if __name__ == '__main__':
    unittest.main()
