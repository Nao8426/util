# 画像を線画化するプログラム
import csv
import cv2
import numpy as np
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Contour():
    def __init__(self):
        self.kernel = np.array([[1, 1, 1, 1, 1], 
                                [1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1]])

    def main(self, path):
        gray = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        dilated = cv2.dilate(gray, self.kernel, iterations=1)
        diff = cv2.absdiff(dilated, gray)
        contour = 255 - diff

        return contour


if __name__ == '__main__':
    contour = Contour()
    os.makedirs('.\\contour', exist_ok=True)
    with open('.\\filelist.csv') as f:
        reader = csv.reader(f)
        l = [row for row in reader]
        for x in zip(*l):
            l_T = list(x) 
        data_num = len(l_T)
        for num, i in enumerate(l_T):
            dirname = i.split('\\')[1]
            filename = i.split('\\')[2]
            os.makedirs('.\\contour\\{}'.format(dirname), exist_ok=True)
            img = contour.main('D:\\animeface-character-dataset\\{}'.format(i))
            cv2.imwrite('.\\contour\\{}\\{}'.format(dirname, filename), img)
            print('{}/{}'.format(num+1, data_num))
