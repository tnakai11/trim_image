# -*- coding: UTF-8 -*-
import wx
import re
import pathlib

segs = [".png",".bmp",".jpg"]
pattern =  ".*(" + ")|(".join(segs) + ").*"
comp = re.compile(pattern)

class FileDropTarget(wx.FileDropTarget):
    def __init__(self,window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        

    def OnDropFiles(self,x,y,filenames):
        try:
            for file in filenames:
                if comp.search(file)!=None:
                    self.window.text.write(file)
                else:
                    dialog_message = "Can't open the file:\n"+file
                    dialog = wx.MessageDialog(None, dialog_message, 'Unsupported', style=wx.OK)
                    dialog.ShowModal()
                    dialog.Destroy()
        except:
            print("some error")

class MyFrame(wx.Frame):
    def on_click_exit(self,event):
        print("exit")
        exit()

    def on_click_flsh(self,event):
        keyinput = wx.UIActionSimulator()
        keyinput.Char(ord("\t")) # ごり押し
        keyinput.Char(ord("\t"))
        keyinput.Char(ord("\b"))
        

    def on_click_trim(self,event):
        file = self.text.GetLineText(0)
        dialog_message = None
        if pathlib.Path(file).exists()==False:
            dialog_message = "The file does not exist:\n"+file
        elif comp.search(file)==None:
            dialog_message = "Can't open the file:\n"+file
        
        if dialog_message==None:
            print("trim") # 処理部は未実装
            pass
        else:
            dialog = wx.MessageDialog(None, dialog_message, 'Error', style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()

            

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "trim_image.py",size=(500,500))
        self.panel = wx.Panel(self,-1)
        self.text = wx.TextCtrl(self.panel, -1, pos=(10, 10))
        self.button_trim = wx.Button(self.panel,-1,"Trim",pos=(10,40))
        self.button_flsh = wx.Button(self.panel,-1,"Flush",pos=(10,70))
        self.button_exit = wx.Button(self.panel,-1,"Exit",pos=(10,100))
        self.dt = FileDropTarget(self)
        self.SetDropTarget(self.dt)
        self.button_trim.Bind(wx.EVT_BUTTON, self.on_click_trim)
        self.button_flsh.Bind(wx.EVT_BUTTON, self.on_click_flsh)
        self.button_exit.Bind(wx.EVT_BUTTON, self.on_click_exit)

class Application():
    def __init__(self):
        self.app = wx.App()
        self.frame = MyFrame()
        print("set up")
    
    def start(self):
        print("start")
        self.frame.Show()
        self.app.MainLoop()
    

if __name__ == "__main__":
    app = Application().start()