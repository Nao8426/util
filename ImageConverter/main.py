# 画像処理プログラム
import os
import wx
# 自作モジュール
from GUI import App
os.chdir(os.path.dirname(os.path.abspath(__file__)))


app = wx.App()
App(None, -1, 'ImageConverter')
app.MainLoop()
