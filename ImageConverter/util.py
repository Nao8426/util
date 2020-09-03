# 各種動作に対する処理
import cv2
import numpy as np
import os
import wx


# ドラッグ&ドロップ
class FileDropTarget(wx.FileDropTarget):
    imgs = []

    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    # ドロップされたときの処理
    def OnDropFiles(self, x, y, files):
        # ここに処理内容を書く（下記は例）
        FileDropTarget.imgs.append(files[0])
        self.window.listbox.Append(files[0])
        self.window.text_entry.SetLabel('\"{}\" が正常に読み込まれました．'.format(files[0]))

        return 0


# ボタン
class Button():
    def __init__(self, window):
        self.window = window
    
    # ボタンを押したときの処理
    def click_button(self, event):
        option = self.window.combobox.GetStringSelection()
        if option == '':
            self.window.text_entry.SetLabel('変換方法を指定してください')
            return
        num = 1
        self.window.text_entry.SetLabel('変換開始')
        for path in FileDropTarget.imgs:
            convert = Convert(path)
            if option == 'gray':
                img = convert.gray()
            elif option == 'binary':
                img = convert.binary()
            elif option == 'contour':
                img = convert.contour()
            ext = path.split('.')[-1]

            # 保存先のファイルを作成
            savepath = './output/output.{}'.format(ext)
            if os.path.exists('./output/output.{}'.format(ext)):
                while 1:
                    if os.path.exists('./output/output({}).{}'.format(num, ext)):
                        num += 1
                    else:
                        savepath = './output/output({}).{}'.format(num, ext)
                        break
            cv2.imwrite(savepath, img)
            
        self.window.text_entry.SetLabel('変換完了')


class Convert():
    def __init__(self, path):
        self.img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    def gray(self):
        return self.img

    def binary(self):
        b_img = cv2.threshold(self.img, 0, 255, cv2.THRESH_OTSU)[1]
        
        return b_img

    def contour(self):
        neiborhood24 = np.array([[1, 1, 1, 1, 1],
                             [1, 1, 1, 1, 1],
                             [1, 1, 1, 1, 1],
                             [1, 1, 1, 1, 1],
                             [1, 1, 1, 1, 1]],
                             np.uint8)

        dilated = cv2.dilate(self.img, neiborhood24, iterations=1)
        diff = cv2.absdiff(dilated, self.img)
        contour = 255 - diff

        return contour
