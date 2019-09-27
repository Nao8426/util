# リプレイ動画を作成するプログラム（OpenCV，wxPython 使用）
import cv2
import datetime
import os
import threading
import time
import wx
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# ドラッグ&ドロップ
class FileDropTarget(wx.FileDropTarget):
    videos = []
    _sum = 0

    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window


    # 実行処理
    def OnDropFiles(self, x, y, files):
        video = cv2.VideoCapture(files[0])
        if video.isOpened() == True:
            FileDropTarget.videos.append(video)
            self.window.listbox.Append('{}（フレーム数：{}）'.format(files[0], int(video.get(cv2.CAP_PROP_FRAME_COUNT))))
            FileDropTarget._sum += video.get(cv2.CAP_PROP_FRAME_COUNT)
            FileDropTarget._sum = int(FileDropTarget._sum)
            self.window.text_entry.SetLabel('\"{}\" が正常に読み込まれました．（総フレーム数：{}）'.format(files[0], FileDropTarget._sum))
        else:
            self.window.text_entry.SetLabel('読み込みエラー（総フレーム数：{}）'.format(FileDropTarget._sum))

        return 0


# ボタン
class Button():
    def __init__(self, window):
        self.window = window
        now = datetime.datetime.now()
        self.dirname = 'replay'
        self.filename = 'replay_{}.mp4'.format(now.strftime('%Y%m%d_%H%M%S'))
        self.sec = 1     # つなぎ目のモザイク時間（秒）を指定（動画の最後と最初にかけるので実質2倍の長さになることに注意）
        self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')     # 形式を指定
        self.fps = FileDropTarget.videos[0].get(cv2.CAP_PROP_FPS)
        self.height = FileDropTarget.videos[0].get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.width  = FileDropTarget.videos[0].get(cv2.CAP_PROP_FRAME_WIDTH)

    
    def click_button(self, event):
        l = self.fps * self.sec

        # dirnameで指定した名前のファイル（出力先のファイル）がなければ作る
        if not os.path.exists(self.dirname):
            os.mkdir(self.dirname)

        # 出力先のファイルを開く
        out = cv2.VideoWriter('{}/{}'.format(self.dirname, self.filename), int(self.fourcc), self.fps, (int(self.width), int(self.height)))

        s_num = 1

        start = time.time()

        for v in FileDropTarget.videos:
            # 総フレーム数の情報を取得
            count = v.get(cv2.CAP_PROP_FRAME_COUNT)

            # 最初の1フレームを読み込む
            if v.isOpened() == True:
                ret, frame = v.read()
            else:
                ret = False
            
            num = 1
            ratio = 0.01
            if v == FileDropTarget.videos[0]:
                ratio = 0.1
                
            # フレームの読み込みに成功している間フレームを書き出し続ける
            while ret == True:
                if v != FileDropTarget.videos[0] and num <= l:
                    # モザイク処理（縮小，拡大）
                    red = cv2.resize(frame, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
                    frame = cv2.resize(red, frame.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
                    ratio = ratio + 0.09 / l

                if v != FileDropTarget.videos[-1] and num > count - l:
                    # モザイク処理（縮小，拡大）
                    red = cv2.resize(frame, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
                    frame = cv2.resize(red, frame.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
                    ratio = ratio - 0.09 / l

                # 読み込んだフレームを書き込み
                out.write(frame)

                if s_num == 200:
                    elapsed = time.time() - start
                    pred = int(elapsed * FileDropTarget._sum / 200)
                    minute = int(pred / 60)
                    second = int(pred % 60)

                if s_num <= 200:
                    self.window.text_entry.SetLabel('進行中... {} / {} （計測中）'.format(s_num, FileDropTarget._sum))
                else:
                    if pred < 60:
                        self.window.text_entry.SetLabel('進行中... {} / {} （推定時間：{}秒）'.format(s_num, FileDropTarget._sum, pred))
                    else:
                        self.window.text_entry.SetLabel('進行中... {} / {} （推定時間：{}分{}秒）'.format(s_num, FileDropTarget._sum, minute, second))

                # 次のフレームを読み込み
                ret, frame = v.read()

                num += 1
                s_num += 1

        self.window.text_entry.SetLabel('完了')


# GUI
class App(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(700, 500), style=wx.DEFAULT_FRAME_STYLE)

        # パネル
        p = wx.Panel(self, wx.ID_ANY)

        label = wx.StaticText(p, wx.ID_ANY, 'ここにファイルをドロップしてください', style=wx.SIMPLE_BORDER | wx.TE_CENTER)
        label.SetBackgroundColour('#e0ffff')

        # リストボックス
        self.listbox = wx.ListBox(p, wx.ID_ANY, size=(700, 150), style=wx.LB_NEEDED_SB | wx.LB_HSCROLL)

        # ドロップ対象の設定
        label.SetDropTarget(FileDropTarget(self))

        # テキスト入力ウィジット
        self.text_entry = wx.TextCtrl(p, wx.ID_ANY)

        # ボタン
        button = wx.Button(p, wx.ID_ANY, '作成')
        button.Bind(wx.EVT_BUTTON, self.callback)

        # レイアウト
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(label, flag=wx.EXPAND | wx.ALL, border=10, proportion=1)
        layout.Add(self.listbox, flag=wx.EXPAND | wx.ALL, border=10)
        layout.Add(button)
        layout.Add(self.text_entry, flag=wx.EXPAND | wx.ALL, border=10)
        p.SetSizer(layout)

        self.Show()


    def callback(self, event):
        btn = Button(self)
        th = threading.Thread(target=btn.click_button, args=(event,))
        th.start()


if __name__ == '__main__':
    app = wx.App()
    App(None, -1, 'ReplayMaker')
    app.MainLoop()
