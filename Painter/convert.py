# 画像を線画化するプログラム
import cv2
import numpy as np
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Convert():
    def __init__(self):
        self.kernel = np.array([1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1])


    def line(self, path):
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        


if __name__ == '__main__':
    convert = Convert()