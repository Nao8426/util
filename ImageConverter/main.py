# 画像処理プログラム
import cv2
import numpy as np
import os
import threading
import wx
os.chdir(os.path.dirname(os.path.abspath(__file__)))


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
        # 指定した名前のファイル（出力先のファイル）がなければ作る
        if not os.path.exists('./output'):
            os.mkdir('./output')

        option = self.window.combobox.GetStringSelection()
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
            while 1:
                if not os.path.exists('./output/output{}.{}'.format(num, ext)):
                    cv2.imwrite('./output/output{}.{}'.format(num, ext), img)
                    break
                num += 1
            
        self.window.text_entry.SetLabel('変換完了')


# GUI
class App(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(700, 500), style=wx.DEFAULT_FRAME_STYLE)

        # パネル
        p = wx.Panel(self, wx.ID_ANY)

        label = wx.StaticText(p, wx.ID_ANY, 'ここにファイルをドロップしてください', style=wx.SIMPLE_BORDER | wx.TE_CENTER)
        label.SetBackgroundColour('#e0ffff')

        # ドロップ対象の設定
        label.SetDropTarget(FileDropTarget(self))

        # リストボッ
        self.listbox = wx.ListBox(p, wx.ID_ANY, size=(700, 150), style=wx.LB_NEEDED_SB | wx.LB_HSCROLL)
        element_array = ['gray', 'binary', 'contour']
        self.combobox = wx.ComboBox(p, wx.ID_ANY, '選択してください', choices=element_array, style=wx.CB_DROPDOWN)

        # ボタン
        button = wx.Button(p, wx.ID_ANY, 'ボタン')
        button.Bind(wx.EVT_BUTTON, self.callback)

        # テキスト入力ウィジット
        self.text_entry = wx.TextCtrl(p, wx.ID_ANY)

        # レイアウト
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(label, flag=wx.EXPAND | wx.ALL, border=10, proportion=1)
        layout.Add(self.listbox, flag=wx.EXPAND | wx.ALL, border=10)
        layout.Add(self.combobox, flag=wx.EXPAND | wx.ALL, border=10)
        layout.Add(button)
        layout.Add(self.text_entry, flag=wx.EXPAND | wx.ALL, border=10)
        p.SetSizer(layout)

        self.Show()


    def callback(self, event):
        btn = Button(self)
        th = threading.Thread(target=btn.click_button, args=(event,))
        th.start()


class Convert():
    def __init__(self, path):
        self.img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)


    def gray(self):
        return self.img


    def binary(self):
        b_img = cv2.threshold(self.img, 0, 255, cv2.THRESH_OTSU)
        
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


if __name__ == '__main__':
    app = wx.App()
    App(None, -1, 'GUI')
    app.MainLoop()
