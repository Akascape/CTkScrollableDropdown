from CTkScrollableDropdown import CTkScrollableDropdown
import customtkinter

root = customtkinter.CTk()

customtkinter.CTkLabel(root, text="Different Dropdown Styles").pack(pady=5)

# Some option list
values = ["python","tkinter","customtkinter","widgets","options","menu","combobox","dropdown","search"]

# Attach to OptionMenu 
optionmenu = customtkinter.CTkOptionMenu(root, width=240)
optionmenu.pack(fill="x", padx=10, pady=10)

CTkScrollableDropdown(optionmenu, values=values, command=lambda e: optionmenu.set(e))

# Attach to Combobox
combobox = customtkinter.CTkComboBox(root, width=240)
combobox.pack(fill="x", padx=10, pady=10)
CTkScrollableDropdown(combobox, values=values, justify="left", button_color="transparent", command=lambda e: combobox.set(e))

# Live Entry Search
def search(a,b,c):
    dropdown_3.live_update(var.get())
    
var = customtkinter.StringVar()
var.trace_add('write', search)

customtkinter.CTkLabel(root, text="Live Search Values").pack()

entry = customtkinter.CTkEntry(root, width=240, textvariable=var)
entry.pack(fill="x", padx=10, pady=10)

dropdown_3 = CTkScrollableDropdown(entry, values=values, command=lambda e: var.set(e))

# the same trace method can be implemented to combobox using:
# combobox._entry.configure(textvariable=var)

# Attach to Button 
button = customtkinter.CTkButton(root, text="choose options", width=240)
button.pack(fill="x", padx=10, pady=10)

CTkScrollableDropdown(button, values=values, height=270, resize=False, button_height=30,
                      scrollbar=False, command=lambda e: button.configure(text=e))

root.mainloop()
