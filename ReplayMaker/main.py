# リプレイ動画を作成するプログラム
import cv2
import os
import threading
import wx
os.chdir(os.path.dirname(os.path.abspath(__file__)))


videos = []
_sum = 0


# ドラッグ&ドロップ
class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window


    # 実行処理
    def OnDropFiles(self, x, y, files):
        video = cv2.VideoCapture(files[0])
        if video.isOpened() == True:
            self.window.text_entry.SetLabel('\"{}\" が正常に読み込まれました．'.format(files[0]))
            videos.append(video)
            self.window.listbox.Append(files[0])
            
            global _sum
            _sum += video.get(cv2.CAP_PROP_FRAME_COUNT)
            _sum = int(_sum)
        else:
            self.window.text_entry.SetLabel('読み込みエラー')

        return 0


# GUI
class App(wx.Frame):
    def callback(self, event):
        th = threading.Thread(target=self.click_button, args=(event,))
        th.start()
        

    # ボタンを押したときの処理
    def click_button(self, event):
        dirname = 'replay'
        filename = '{}/replay.mp4'.format(dirname)
        sec = 1     # つなぎ目のモザイク時間（秒）を指定（動画の最後と最初にかけるので実質2倍の長さになることに注意）

        # 形式を指定
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

        # 一つ目の動画情報を取得
        fps = videos[0].get(cv2.CAP_PROP_FPS)
        height = videos[0].get(cv2.CAP_PROP_FRAME_HEIGHT)
        width  = videos[0].get(cv2.CAP_PROP_FRAME_WIDTH)

        l = fps * sec

        # dirnameで指定した名前のファイル（出力先のファイル）がなければ作る
        if not os.path.exists(dirname):
            os.mkdir(dirname)

        # 出力先のファイルを開く
        out = cv2.VideoWriter(filename, int(fourcc), fps, (int(width), int(height)))

        s_num = 1

        for v in videos:
            # 総フレーム数の情報を取得
            count = v.get(cv2.CAP_PROP_FRAME_COUNT)

            # 最初の1フレームを読み込む
            if v.isOpened() == True:
                ret, frame = v.read()
            else:
                ret = False
            
            num = 1
            ratio = 0.01
            if v == videos[0]:
                ratio = 0.1
                
            # フレームの読み込みに成功している間フレームを書き出し続ける
            while ret == True:
                if v != videos[0] and num <= l:
                    # モザイク処理（縮小，拡大）
                    red = cv2.resize(frame, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
                    frame = cv2.resize(red, frame.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
                    ratio = ratio + 0.09 / l

                if v != videos[-1] and num > count - l:
                    # モザイク処理（縮小，拡大）
                    red = cv2.resize(frame, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
                    frame = cv2.resize(red, frame.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
                    ratio = ratio - 0.09 / l

                # 読み込んだフレームを書き込み
                out.write(frame)

                global _sum
                self.text_entry.SetLabel('進行中．．． {} / {}'.format(s_num, _sum))

                # 次のフレームを読み込み
                ret, frame = v.read()

                num += 1
                s_num += 1

        self.text_entry.SetLabel('完了')
            

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


if __name__ == '__main__':
    app = wx.App()
    App(None, -1, 'ReplayMaker')
    app.MainLoop()
