#!/usr/bin/python3

from tkinter import *
import tkinter.messagebox


def read_Depots_List(file):
    depots_List = []
    try:
        with open(file, 'r') as file_with_depots:
            [(depots_List.append(line.strip())) for line in file_with_depots]
        return (depots_List)

    except IOError as iorr:
        tkinter.messagebox.showerror("Error while opening the file, consigment not recorded. %s" % iorr)


def save_Button_Action():
    depo_Text = depot.get()
    depot.set(None)
    desc_Text = description_Entry_Field.get()
    description_Entry_Field.delete(0, END)
    addr_Text = multiline_text_field.get("1.0", END)
    multiline_text_field.delete("1.0", END)

    try:
        with open('deliveries.txt', 'a') as deliveries:
            print("Depot:\n" + depo_Text, file=deliveries)
            print("Description:\n" + desc_Text, file=deliveries)
            print("Address:\n" + addr_Text, file=deliveries)
    except Exception as e_rror:
        tkinter.messagebox.showerror("Error", "Couldn't write to file. %s" % e_rror)


app = Tk()
app.title("test")
app.geometry('450x250+200+100')

# depot = StringVar()
# depot.set(None)
#
# #depots = read_Depots_List('depots.txt')
#
# depo_Label = Label(app, text="Depot:", pady=10, padx=10).pack()
# OptionMenu(app, depot, ['hello', 'hi']).pack()
description_Label = Label(app, text="Description:", pady=10, padx=10).pack()
description_Entry_Field = Entry(app)
description_Entry_Field.pack()
# address_Label = Label(app, text="Address:", pady=10, padx=10).pack()
# multiline_text_field = Text(app)
# multiline_text_field.pack()
# save_Button = Button(app, text="Save", width=20, pady=10, command=save_Button_Action).pack()

app.mainloop()