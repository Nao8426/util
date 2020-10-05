# GUI
import threading
import wx
# 自作モジュール
from util import FileDropTarget, Button


# GUI
class App(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(700, 500), style=wx.DEFAULT_FRAME_STYLE)

        # パネル
        panel = wx.Panel(self, wx.ID_ANY)

        label = wx.StaticText(panel, wx.ID_ANY, 'ここにファイルをドロップしてください', style=wx.SIMPLE_BORDER | wx.TE_CENTER)
        label.SetBackgroundColour('#e0ffff')

        # リストボックス
        self.listbox = wx.ListBox(panel, wx.ID_ANY, size=(700, 150), style=wx.LB_NEEDED_SB | wx.LB_HSCROLL)

        # ドロップ対象の設定
        label.SetDropTarget(FileDropTarget(self))

        # テキスト入力ウィジット
        self.text_entry = wx.TextCtrl(panel, wx.ID_ANY)

        # ボタン
        button = wx.Button(panel, wx.ID_ANY, '作成')
        button.Bind(wx.EVT_BUTTON, self.callback)

        # レイアウト
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(label, flag=wx.EXPAND | wx.ALL, border=10, proportion=1)
        layout.Add(self.listbox, flag=wx.EXPAND | wx.ALL, border=10)
        layout.Add(button)
        layout.Add(self.text_entry, flag=wx.EXPAND | wx.ALL, border=10)
        panel.SetSizer(layout)

        self.Show()

    def callback(self, event):
        btn = Button(self)
        th = threading.Thread(target=btn.click_button, args=(event,))
        th.start()
