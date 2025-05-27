'''
Advanced Scrollable Dropdown class for customtkinter widgets
Author: Akash Bora
'''

import customtkinter
import sys
import difflib

class CTkScrollableDropdown(customtkinter.CTkToplevel):
    
    def __init__(self, attach, x=None, y=None, button_color=None, max_height: int = 92, width: int = None,
                 fg_color=None, bg_color=None, button_height: int = 20, justify="center", scrollbar_button_color=None,
                 scrollbar=True, scrollbar_button_hover_color=None, frame_border_width=2, values=[],
                 command=None, image_values=[], alpha: float = 0.97, frame_corner_radius=20, double_click=False,
                 resize=True, frame_border_color=None, text_color=None, autocomplete=False, 
                 hover_color=None, **button_kwargs):
        
        super().__init__(master=attach.winfo_toplevel(), takefocus=1)
        
        self.focus()
        self.lift()
        self.alpha = alpha
        self.attach = attach
        self.corner = frame_corner_radius
        self.padding = 0
        self.focus_something = False
        self.disable = True
        self.update()
        
        # Fix for background colour clipping through corners of frame.
        self.bg_color = self._apply_appearance_mode(self._fg_color) if bg_color is None else bg_color

        if sys.platform.startswith("win"):
            self.after(100, lambda: self.overrideredirect(True))
            self.transparent_color = self.bg_color
            self.attributes("-transparentcolor", self.transparent_color)
        elif sys.platform.startswith("darwin"):
            self.overrideredirect(True)
            self.transparent_color = 'systemTransparent'
            self.attributes("-transparent", True)
            self.focus_something = True
        else:
            self.overrideredirect(True)
            self.transparent_color = frame_border_color
            self.corner = 0
            self.padding = 18
            self.withdraw()

        self.hide = True
        self.attach.bind('<Configure>', lambda e: self._withdraw() if not self.disable else None, add="+")
        self.attach.winfo_toplevel().bind('<Configure>', lambda e: self._withdraw() if not self.disable else None, add="+")
        self.attach.winfo_toplevel().bind("<ButtonPress>", lambda e: self._withdraw() if not self.disable else None, add="+")        
        self.bind("<Escape>", lambda e: self._withdraw() if not self.disable else None, add="+")
        
        self.attributes('-alpha', 0)
        self.disable = False
        self.fg_color = customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"] if fg_color is None else fg_color
        self.scroll_button_color = customtkinter.ThemeManager.theme["CTkScrollbar"]["button_color"] if scrollbar_button_color is None else scrollbar_button_color
        self.scroll_hover_color = customtkinter.ThemeManager.theme["CTkScrollbar"]["button_hover_color"] if scrollbar_button_hover_color is None else scrollbar_button_hover_color
        self.frame_border_color = customtkinter.ThemeManager.theme["CTkFrame"]["border_color"] if frame_border_color is None else frame_border_color
        self.button_color = customtkinter.ThemeManager.theme["CTkFrame"]["top_fg_color"] if button_color is None else button_color
        self.text_color = customtkinter.ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else text_color
        self.hover_color = customtkinter.ThemeManager.theme["CTkButton"]["hover_color"] if hover_color is None else hover_color
        
        
        if scrollbar is False:
            self.scroll_button_color = self.fg_color
            self.scroll_hover_color = self.fg_color
            
        self.frame = customtkinter.CTkScrollableFrame(self, bg_color=self.transparent_color, fg_color=self.fg_color,
                                        scrollbar_button_hover_color=self.scroll_hover_color,
                                        corner_radius=self.corner, border_width=frame_border_width,
                                        scrollbar_button_color=self.scroll_button_color,
                                        border_color=self.frame_border_color)
        self.frame._scrollbar.grid_configure(padx=3)
        self.frame.pack(expand=True, fill="both")
        self.max_height = max_height
        self.max_height_new = max_height
        self.height_new = 0  # Actual dynamic height will be set in place_dropdown.
        self.width = width
        self.command = command
        self.fade = False
        self.resize = resize
        self.autocomplete = autocomplete
        self.var_update = customtkinter.StringVar()
        self.appear = False
        
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
        self._init_buttons(**button_kwargs)

        # Add binding for different ctk widgets
        if double_click or type(self.attach) is customtkinter.CTkEntry or type(self.attach) is customtkinter.CTkComboBox:
            self.attach.bind('<Double-Button-1>', lambda e: self._iconify(), add="+")
        else:
            self.attach.bind('<Button-1>', lambda e: self._iconify(), add="+")

        if type(self.attach) is customtkinter.CTkComboBox:
            self.attach._canvas.tag_bind("right_parts", "<Button-1>", lambda e: self._iconify())
            self.attach._canvas.tag_bind("dropdown_arrow", "<Button-1>", lambda e: self._iconify())
            if self.command is None:
                self.command = self.attach.set
              
        if type(self.attach) is customtkinter.CTkOptionMenu:
            self.attach._canvas.bind("<Button-1>", lambda e: self._iconify())
            self.attach._text_label.bind("<Button-1>", lambda e: self._iconify())
            if self.command is None:
                self.command = self.attach.set
                
        self.attach.bind("<Destroy>", lambda _: self._destroy(), add="+")
        
        self.update_idletasks()
        self.x = x
        self.y = y

        if self.autocomplete:
            self.bind_autocomplete()
            
        self.withdraw()

        self.attributes("-alpha", self.alpha)

    def _destroy(self):
        self.after(500, self.destroy_popup)
        
    def _withdraw(self):
        if not self.winfo_exists():
            return
        if self.winfo_viewable() and self.hide:
            self.withdraw()
        
        self.event_generate("<<Closed>>")
        self.hide = True

    def _update(self, a, b, c):
        self.live_update(self.attach._entry.get())
        # Close dropdown if no text remains in the combobox entry section.
        if self.attach._entry.get() == "":
            self.withdraw()
            self.hide = True  # Fix for an issue where the dropdown would close, but two clicks were required to open it again.   
    
    def bind_autocomplete(self):
        def appear(x):
            self.appear = True
            
        if type(self.attach) is customtkinter.CTkComboBox:
            self.attach._entry.configure(textvariable=self.var_update)
            self.attach._entry.bind("<Key>", appear)
            self.attach.set(self.values[0])
            self.var_update.trace_add('write', self._update)
            
        if type(self.attach) is customtkinter.CTkEntry:
            self.attach.configure(textvariable=self.var_update)
            self.attach.bind("<Key>", appear)
            self.var_update.trace_add('write', self._update)
        
    def fade_out(self):
        for i in range(100,0,-10):
            if not self.winfo_exists():
                break
            self.attributes("-alpha", i/100)
            self.update()
            
    def fade_in(self):
        for i in range(0,100,10):
            if not self.winfo_exists():
                break
            self.attributes("-alpha", i/100)
            self.update()
            
    def _init_buttons(self, **button_kwargs):
        self.i = 0
        self.widgets = {}
        for row in self.values:
            self.widgets[self.i] = customtkinter.CTkButton(self.frame,
                                                          text=row,
                                                          height=self.button_height,
                                                          fg_color=self.button_color,
                                                          text_color=self.text_color,
                                                          image=self.image_values[self.i] if self.image_values is not None else None,
                                                          anchor=self.justify,
                                                          hover_color=self.hover_color,
                                                          command=lambda k=row: self._attach_key_press(k), **button_kwargs)
            self.widgets[self.i].pack(fill="x", pady=2, padx=(self.padding, 0))
            self.i+=1
 
        self.hide = False
            
    def destroy_popup(self):
        self.destroy()
        self.disable = True

    def place_dropdown(self):
        self.x_pos = self.attach.winfo_rootx() if self.x is None else self.x + self.attach.winfo_rootx()
        self.y_pos = self.attach.winfo_rooty() + self.attach.winfo_reqheight() + 5 if self.y is None else self.y + self.attach.winfo_rooty()
        self.width_new = self.attach.winfo_width() if self.width is None else self.width
        
        visible_buttons = self.button_num
        pady = 2  # Padding between buttons.
        if self.resize:
            # Calculate the total height of buttons including vertical padding.
            self.height_new = (self.button_height + 2 * pady) * visible_buttons + 20
            extra_padding = 5  # Extra padding to prevent clipping.
            self.height_new += extra_padding

            # Cap height to a maximum value so that the dropdown doesn't go offscreen.
            if self.height_new > self.max_height:
                self.height_new = self.max_height

        self.geometry('{}x{}+{}+{}'.format(self.width_new, self.height_new,
                                           self.x_pos, self.y_pos))
        self.fade_in()
        self.attributes('-alpha', self.alpha)
        #self.attach.focus()

    def _iconify(self):
        if self.attach.cget("state")=="disabled": return
        if self.disable: return
        if self.winfo_ismapped():
            self.hide = False
        if self.hide:
            self.event_generate("<<Opened>>")      
            #self.focus()
            self.hide = False

            # Reset dropdown to show all options regardless of entry text when the dropdown button is manually pressed.
            for key in self.widgets.keys():
                self.widgets[key].pack(fill="x", pady=2, padx=(self.padding, 0))
            self.button_num = len(self.values)
            
            self.place_dropdown()
            self._deiconify()
            
        else:
            self.withdraw()
            self.hide = True
            
    def _attach_key_press(self, k):
        self.event_generate("<<Selected>>")
        self.fade = True
        if self.command:
            self.command(k)
        self.fade = False
        self.fade_out()
        self.withdraw()
        self.hide = True
            
    def live_update(self, string=None):
        match_found = False
        if not self.appear: return
        if self.disable: return
        if self.fade: return
        if string:
            string = string.lower()
            visible_buttons = 0
            for key in self.widgets.keys():
                s = self.widgets[key].cget("text").lower()
                text_similarity = difflib.SequenceMatcher(None, s[0:len(string)], string).ratio()
                similar = s.startswith(string) or text_similarity > 0.75
                if not similar:
                    self.widgets[key].pack_forget()
                else:
                    self.widgets[key].pack(fill="x", pady=2, padx=(self.padding, 0))
                    match_found = True
                    visible_buttons += 1 
            if match_found:
                self._deiconify()
                self.button_num = visible_buttons
                self.place_dropdown()
            else:
                self.withdraw()
                self.hide = True
            
        else:
            self.button_num = len(self.values)
            for key in self.widgets.keys():
                self.widgets[key].destroy()
            self._init_buttons()
            self.place_dropdown()
            
        self.frame._parent_canvas.yview_moveto(0.0)
        self.appear = False
        
    def insert(self, value, **kwargs):
        self.widgets[self.i] = customtkinter.CTkButton(self.frame,
                                                       text=value,
                                                       height=self.button_height,
                                                       fg_color=self.button_color,
                                                       text_color=self.text_color,
                                                       hover_color=self.hover_color,
                                                       anchor=self.justify,
                                                       command=lambda k=value: self._attach_key_press(k), **kwargs)
        self.widgets[self.i].pack(fill="x", pady=2, padx=(self.padding, 0))
        self.i+=1
        self.values.append(value)
        
    def _deiconify(self):
        if len(self.values)>0:
            self.deiconify()

    def popup(self, x=None, y=None):
        self.x = x
        self.y = y
        self.hide = True
        self._iconify()

    def hide(self):
        self._withdraw()
        
    def configure(self, **kwargs):
        if "height" in kwargs:
            self.max_height = kwargs.pop("height")
            self.max_height_new = self.max_height
            
        if "alpha" in kwargs:
            self.alpha = kwargs.pop("alpha")
            
        if "width" in kwargs:
            self.width = kwargs.pop("width")
            
        if "fg_color" in kwargs:
            self.frame.configure(fg_color=kwargs.pop("fg_color"))
            
        if "values" in kwargs:
            self.values = kwargs.pop("values")
            self.image_values = None
            self.button_num = len(self.values)
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
            button_color = kwargs.pop("button_color")
            for key in self.widgets.keys():
                self.widgets[key].configure(fg_color=button_color)

        if "font" in kwargs:
            font = kwargs.pop("font")
            for key in self.widgets.keys():
                self.widgets[key].configure(font=font)
                
        if "hover_color" not in kwargs:
            kwargs["hover_color"] = self.hover_color
        
        for key in self.widgets.keys():
            self.widgets[key].configure(**kwargs)
