# -*- coding: UTF-8 -*-
import wx
import re
import pathlib
from PIL import Image

segs_read = [".png",".bmp",".jpg"]
pattern_read =  ".*(" + ")|(".join(segs_read) + ").*"
comp_read = re.compile(pattern_read)

segs_write = [".png",".bmp",".jpg",".pdf"]
pattern_write =  ".*(" + ")|(".join(segs_write) + ").*"
comp_write = re.compile(pattern_write)

def make_output_name(txt):
    return  txt[:-4]+"-trim" + txt[-4:]

def trim(image,trim_color=(255,255,255),margin=5):
    rgb_image = image.convert('RGB')
    size = rgb_image.size
    left = size[0]
    right = 0
    top = size[1]
    buttom = 0
    # check where is the border
    for x in range(size[0]):
        for y in range(size[1]):
            r,g,b = rgb_image.getpixel((x,y))
            if (r,g,b)!=trim_color:
                left = max(min(left,x-margin),0)
                right = min(max(right,x+margin),size[0])
                top = max(min(top,y-margin),0)
                buttom = min(max(buttom,y+margin),size[1])
    return image.crop( (left,top,right,buttom) )

def save_output_image(image_pil,file):
    dialog_message = None
    if comp_write.search(file)==None:
        dialog_message = "Unsupported extension:\n"+file
    elif pathlib.Path(file).exists()==True:
        dialog_message = "The file already exists:\n"+file

    if dialog_message==None:
        if file[-4:]==".jpg":
            image_pil.save(file,quality=95)
        elif file[-4:]==".pdf":
            image_pil.save(file,"PDF",resolution=100.0)
        else:
            image_pil.save(file)
    else:
        # error dialog
        dialog = wx.MessageDialog(None, dialog_message, 'Error', style=wx.OK)
        dialog.ShowModal()
        dialog.Destroy()

class FileDropTarget(wx.FileDropTarget):
    def __init__(self,window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        
    def OnDropFiles(self,x,y,filenames):
        try:
            for file in filenames:
                if comp_read.search(file)!=None:
                    self.window.text_orig.SetValue(file)
                    # get original image
                    image_pil = Image.open(file)

                    # put original image on frame
                    self.window.label_original = wx.StaticText(self.window.panel,-1,"Original",pos=(10,190))
                    self.window.put_image(image_pil,(10,200))
                else:
                    # error dialog
                    dialog_message = "Can't open the file:\n"+file
                    dialog = wx.MessageDialog(None, dialog_message, 'Error', style=wx.OK)
                    dialog.ShowModal()
                    dialog.Destroy()
            return True
        except:
            print("Error:OnDropFiles")
            return False

class MyFrame(wx.Frame):
    def on_click_exit(self,event):
        exit()

    def on_click_save(self,event):
        if self.isReady==True:
            save_output_image(\
                self.image_trim_pil,\
                self.text_out.GetLineText(0))

    def on_click_clear(self,event):
        self.text_orig.Clear()
        self.text_out.Clear()

    def put_image(self,image_pil_orig,place,size=(300,300)):
        image_pil_copy = image_pil_orig.copy()
        image_pil_copy.thumbnail((300,300), Image.ANTIALIAS)
        image_wx = wx.Image(image_pil_copy.size[0],image_pil_copy.size[1])
        image_wx.SetData(image_pil_copy.convert('RGB').tobytes())
        wx.StaticBitmap(self.panel, -1, image_wx.ConvertToBitmap(), place, size)

    def on_click_trim(self,event):
        file = self.text_orig.GetLineText(0)
        # check original file
        dialog_message = None
        if pathlib.Path(file).exists()==False:
            dialog_message = "The file does not exist:\n"+file
        elif comp_read.search(file)==None:
            dialog_message = "Can't open the file:\n"+file
        
        if dialog_message==None:
            # get original image
            self.image_pil = Image.open(file)

            # put original image on frame
            self.label_original = wx.StaticText(self.panel,-1,"Original",pos=(10,190))
            self.put_image(self.image_pil,(10,200))

            # create trimmed image
            trim_color = (\
                self.text_trim_r.GetLineText(0),\
                self.text_trim_g.GetLineText(0),\
                self.text_trim_b.GetLineText(0))
            trim_color = tuple(map(int,trim_color))
            margin = int(self.text_trim_margin.GetLineText(0))
            self.image_trim_pil = trim(self.image_pil,trim_color,margin)

            # put trimmed image on frame
            self.label_trim = wx.StaticText(self.panel,-1,"Trimmed",pos=(400,190))
            self.put_image(self.image_trim_pil,(400,200))

            # ready
            self.text_out.SetValue(make_output_name(file))
            self.isReady = True
        else:
            # error
            dialog = wx.MessageDialog(None, dialog_message, 'Error', style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
     
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "trim_image.py",size=(1000,650))
        self.panel = wx.Panel(self,-1)

        self.label_input = wx.StaticText(self.panel,-1,"original file",pos=(10,15))
        self.text_orig = wx.TextCtrl(self.panel, -1, pos=(100, 10),size=(400,-1))
        
        self.label_output = wx.StaticText(self.panel,-1,"output file",pos=(10,45))
        self.text_out = wx.TextCtrl(self.panel, -1, pos=(100, 40),size=(400,-1))

        self.button_trim = wx.Button(self.panel,-1,"Trim",pos=(10,70))
        self.button_save = wx.Button(self.panel,-1,"Save",pos=(10,100))
        self.button_clear = wx.Button(self.panel,-1,"Clear Texts",pos=(10,130))
        self.button_exit = wx.Button(self.panel,-1,"Exit",pos=(10,160))
        self.button_trim.Bind(wx.EVT_BUTTON, self.on_click_trim)
        self.button_clear.Bind(wx.EVT_BUTTON, self.on_click_clear)
        self.button_save.Bind(wx.EVT_BUTTON, self.on_click_save)
        self.button_exit.Bind(wx.EVT_BUTTON, self.on_click_exit)

        self.label_trim_r = wx.StaticText(self.panel,-1,"trim R",pos=(550,15))
        self.text_trim_r = wx.TextCtrl(self.panel, -1,"255", pos=(600, 10),size=(100,-1))
        self.label_trim_g = wx.StaticText(self.panel,-1,"trim G",pos=(550,45))
        self.text_trim_g = wx.TextCtrl(self.panel, -1, "255",pos=(600, 40),size=(100,-1))
        self.label_trim_b = wx.StaticText(self.panel,-1,"trim B",pos=(550,75))
        self.text_trim_b = wx.TextCtrl(self.panel, -1, "255",pos=(600, 70),size=(100,-1))
        self.label_trim_margin = wx.StaticText(self.panel,-1,"margin",pos=(550,105))
        self.text_trim_margin = wx.TextCtrl(self.panel, -1,"5", pos=(600, 100),size=(100,-1))

        self.dt = FileDropTarget(self)
        self.SetDropTarget(self.dt)
        self.isReady = False

class Application():
    def __init__(self):
        self.app = wx.App()
        self.frame = MyFrame()
    
    def start(self):
        self.frame.Show()
        self.app.MainLoop()
    
if __name__ == "__main__":
    app = Application().start()