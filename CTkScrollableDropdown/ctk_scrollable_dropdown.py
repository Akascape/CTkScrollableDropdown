'''
Advanced Scrollable Dropdown class for customtkinter widgets
Author: Akash Bora
'''

from tkinter import *
from customtkinter import *
import sys
import time

class CTkScrollableDropdown(CTkToplevel):
    
    def __init__(self, attach, x=None, y=None, button_color=None, height: int = 200, width: int = None,
                 fg_color=None, button_height: int = 20, justify="center", scrollbar_button_color=None,
                 scrollbar=True, scrollbar_button_hover_color=None, frame_border_width=2, values=[],
                 command=None, image_values=[], alpha: float = 0.97, frame_corner_radius=20, double_click=False,
                 resize=True, frame_border_color=None, text_color=None, **button_kwargs):
        
        super().__init__(takefocus=1)
        
        self.focus()
        self.overrideredirect(True)
        self.alpha = alpha
        self.attributes('-alpha', self.alpha)
        self.corner = frame_corner_radius
        
        if sys.platform.startswith("win"):
            self.transparent_color = self._apply_appearance_mode(self._fg_color)
            self.attributes("-transparentcolor", self.transparent_color)
        elif sys.platform.startswith("darwin"):
            self.transparent_color = 'systemTransparent'
            self.attributes("-transparent", True)
        else:
            self.transparent_color = '#000001'
            self.corner = 0
    
        self.fg_color = ThemeManager.theme["CTkFrame"]["fg_color"] if fg_color is None else fg_color
        self.scroll_button_color = ThemeManager.theme["CTkScrollbar"]["button_color"] if scrollbar_button_color is None else scrollbar_button_color
        self.scroll_hover_color = ThemeManager.theme["CTkScrollbar"]["button_hover_color"] if scrollbar_button_hover_color is None else scrollbar_button_hover_color
        self.frame_border_color = ThemeManager.theme["CTkFrame"]["border_color"] if frame_border_color is None else frame_border_color
        self.button_color = ThemeManager.theme["CTkFrame"]["top_fg_color"] if button_color is None else button_color
        self.text_color = ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else text_color
        
        if scrollbar is False:
            self.scroll_button_color = self.fg_color
            self.scroll_hover_color = self.fg_color
            
        self.frame = CTkScrollableFrame(self, bg_color=self.transparent_color, fg_color=self.fg_color,
                                        scrollbar_button_hover_color=self.scroll_hover_color,
                                        corner_radius=self.corner, border_width=frame_border_width,
                                        scrollbar_button_color=self.scroll_button_color,
                                        border_color=self.frame_border_color)
        self.frame._scrollbar.grid_configure(padx=3)
        self.frame.pack(expand=True, fill="both")
        
        self.no_match = CTkLabel(self.frame, text="No Match")
        self.attach = attach
        self.height = height
        self.height_new = height
        self.width = width
        self.command = command
        self.fade = False
        self.resize = resize
        
        if justify.lower()=="left":
            self.justify = "w"
        elif justify.lower()=="right":
            self.justify = "e"
        else:
            self.justify = "c"
            
        self.button_height = button_height
        self.values = values
        self.button_num = len(self.values)
        self.image_values = None if len(image_values)!=len(self.values) else image_values
        
        self.resizable(width=False, height=False)
        self.transient(self.master)
        self.disable = False
        self._init_buttons(**button_kwargs)

        # Add binding for different ctk widgets
        if double_click or self.attach.winfo_name()=="!ctkentry" or self.attach.winfo_name()=="!ctkcombobox":
            self.attach.bind('<Double-Button-1>', lambda e: self._iconify(), add="+")
        else:
            self.attach.bind('<Button-1>', lambda e: self._iconify(), add="+")

        if self.attach.winfo_name()=="!ctkcombobox":
            self.attach._canvas.tag_bind("right_parts", "<Button-1>", lambda e: self._iconify())
            self.attach._canvas.tag_bind("dropdown_arrow", "<Button-1>", lambda e: self._iconify())

        if self.attach.winfo_name()=="!ctkoptionmenu":
            self.attach._canvas.bind("<Button-1>", lambda e: self._iconify())
            self.attach._text_label.bind("<Button-1>", lambda e: self._iconify())
            
        self.bind('<FocusOut>', lambda e: self.withdraw() if not self.disable else None)
        self.hide = False
        
        self.update_idletasks()
        self.x = x
        self.y = y
        self._iconify()
        
    def fade_out(self):
        for i in range(100,0,-10):
            if not self.winfo_exists():
                break
            self.attributes("-alpha", i/100)
            self.update()
            time.sleep(1/1000)
            
    def fade_in(self):
        for i in range(0,100,10):
            if not self.winfo_exists():
                break
            self.attributes("-alpha", i/100)
            self.update()
            time.sleep(1/1000)
            
    def _init_buttons(self, **button_kwargs):
        i = 0
        self.widgets = {}
        for row in self.values:                                
            self.widgets[i] = CTkButton(self.frame,
                                        text=row,
                                        height=self.button_height,
                                        fg_color=self.button_color,
                                        text_color=self.text_color,
                                        image=self.image_values[i] if self.image_values is not None else None,
                                        anchor=self.justify,
                                        command=lambda k=row: self._attach_key_press(k), **button_kwargs)
            self.widgets[i].pack(fill="x", pady=2)
            i+=1
             
        self.hide = False
            
    def destroy_popup(self):
        self.destroy()
        self.disable = True

    def place_dropdown(self):
        self.x_pos =  self.attach.winfo_rootx() if self.x is None else self.x
        self.y_pos = self.attach.winfo_rooty() + self.attach.winfo_reqheight() + 5 if self.y is None else self.y
        self.width_new = self.attach.winfo_width() if self.width is None else self.width
        
        if self.resize:
            if self.button_num==1:      
                self.height_new = self.button_height * self.button_num + 45
            else:
                self.height_new = self.button_height * self.button_num + 35
            if self.height_new>self.height:
                self.height_new = self.height

        self.geometry('{}x{}+{}+{}'.format(self.width_new, self.height_new,
                                           self.x_pos, self.y_pos))
        self.fade_in()
        self.attributes('-alpha', self.alpha)
        
    def _iconify(self):
        if self.disable: return
        if self.hide:
            self._deiconify()
            self.focus()
            self.hide = False
            self.place_dropdown()
        else:
            self.withdraw()
            self.hide = True
        
    def _attach_key_press(self, k):
        self.fade = True
        if self.command:
            self.command(k)
        self.fade = False
        self.fade_out()
        self.withdraw()
        self.hide = True
            
    def live_update(self, string=None):
        if self.disable: return
        if self.fade: return
        if string:
            self._deiconify()
            i=1
            for key in self.widgets.keys():
                s = self.widgets[key].cget("text")
                if not s.startswith(string):
                    self.widgets[key].pack_forget()
                else:
                    self.widgets[key].pack(fill="x", pady=2)
                    i+=1
                    
            if i==1:
                self.no_match.pack(fill="x", pady=2)
            else:
                self.no_match.pack_forget()
            self.button_num = i
            self.place_dropdown()
            
        else:
            self.no_match.pack_forget()
            self.button_num = len(self.values)
            for key in self.widgets.keys():
                self.widgets[key].destroy()
            self._init_buttons()
            self.place_dropdown()
           
    def _deiconify(self):
        if len(self.values)>0:
            self.deiconify()
            
    def configure(self, **kwargs):
        if "height" in kwargs:
            self.height = kwargs.pop("height")
            self.height_new = self.height
            
        if "alpha" in kwargs:
            self.alpha = kwargs.pop("alpha")
            
        if "width" in kwargs:
            self.width = kwargs.pop("width")
            
        if "fg_color" in kwargs:
            self.frame.configure(fg_color=kwargs.pop("fg_color"))
            
        if "values" in kwargs:
            self.values = kwargs.pop("values")
            self.image_values = None
            for key in self.widgets.keys():
                self.widgets[key].destroy()
            self._init_buttons()
            
        if "image_values" in kwargs:
            self.image_values = kwargs.pop("image_values")
            self.image_values = None if len(self.image_values)!=len(self.values) else self.image_values
            if self.image_values is not None:
                i=0
                for key in self.widgets.keys():
                    self.widgets[key].configure(image=self.image_values[i])
                    i+=1
                    
        if "button_color" in kwargs:
            for key in self.widgets.keys():
                self.widgets[key].configure(fg_color=kwargs.pop("button_color"))
                
        for key in self.widgets.keys():
            self.widgets[key].configure(**kwargs)
