#!/usr/bin/python3

import os
import sys
import re
import tkinter


class MainWindow:

    def __init__(self, parent):
        self.parent = parent

        self.regex = tkinter.StringVar()
        self.text = tkinter.StringVar()
        self.dotall = tkinter.IntVar()
        self.ignore_case = tkinter.IntVar()
        self.captures = []
        for i in range(10):
            self.captures.append(tkinter.StringVar())
        self.message = tkinter.StringVar()

        main_frame = tkinter.Frame(self.parent)

        regex_label = tkinter.Label(main_frame, text='Regex:', underline=0)
        regex_entry = tkinter.Entry(main_frame, width=50, textvariable=self.regex)
        text_label = tkinter.Label(main_frame, text='Text:', underline=0)
        text_entry = tkinter.Entry(main_frame, width=50, textvariable=self.text)
        self.dotall_checkbox = tkinter.Checkbutton(main_frame, text='Dotall',
                                              textvariable=self.dotall, underline=0)
        self.ignore_case_checkbox = tkinter.Checkbutton(main_frame, text='Ignore Case',
                                                   textvariable=self.ignore_case, underline=0)

        regex_label.grid(row=0, column=0, padx=2, pady=2, sticky=tkinter.W)
        regex_entry.grid(row=0, column=1, columnspan=2, padx=2, pady=2, sticky=tkinter.EW)
        text_label.grid(row=1, column=0, padx=2, pady=2, sticky=tkinter.W)
        text_entry.grid(row=1, column=1, columnspan=2, padx=2, pady=2, sticky=tkinter.EW)
        self.dotall_checkbox.grid(row=2, column=0, columnspan=2, padx=2, pady=2, sticky=tkinter.E)
        self.ignore_case_checkbox.grid(row=2, column=2, columnspan=2, padx=2, pady=2, sticky=tkinter.E)

        self.groupLabels = []
        self.captureLabels = []
        row = 3
        for i in range(10):
            label = tkinter.Label(main_frame, text="Group {0}".format(i))
            label.grid(row=row + i, column=0, padx=2, pady=2, sticky=tkinter.W)
            self.groupLabels.append(label)
            capture = tkinter.Label(main_frame, relief=tkinter.RIDGE, anchor=tkinter.W, bg="aliceblue",
                                    textvariable=self.captures[i])
            capture.grid(row=row + i, column=1, columnspan=2, padx=2, pady=2, sticky=tkinter.EW)
            self.captureLabels.append(capture)

        self.message_label = tkinter.Label(main_frame, relief=tkinter.GROOVE, anchor=tkinter.W, bg="white",
                                           textvariable=self.message)
        self.message_label.grid(row=14, column=0, columnspan=3, padx=2, pady=2, sticky=tkinter.EW)

        main_frame.grid(row=0, column=0, sticky=tkinter.NSEW)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=999)
        main_frame.columnconfigure(2, weight=999)

        window = self.parent.winfo_toplevel()
        window.columnconfigure(0, weight=1)

        regex_entry.focus_set()
        parent.bind("<Alt-r>", lambda arg: regex_entry.focus_set())
        parent.bind("<Alt-t>", lambda arg: text_entry.focus_set())
        parent.bind("<Alt-i>", self.ignoreCaseChanged)
        parent.bind("<Alt-d>", self.dotallChanged)
        parent.bind("<Control-q>", self.quit)
        parent.bind("<Escape>", self.quit)
        regex_entry.bind("<Any-KeyRelease>", self.calculate)
        text_entry.bind("<Any-KeyRelease>", self.calculate)
        parent.title("Regex")
        self.calculate()

    def ignoreCaseChanged(self, *ignore):
        self.ignore_case_checkbox.invoke()
        self.calculate()

    def dotallChanged(self, *ignore):
        self.dotall_checkbox.invoke()
        self.calculate()

    def calculate(self, *ignore):
        for i in range(10):
            self.captures[i].set("")
            self.captureLabels[i]["bg"] = "aliceblue"
            self.groupLabels[i]["text"] = "Group {0}".format(i)
        if not self.regex.get():
            return
        try:
            flags = 0
            if self.ignore_case.get():
                flags |= re.IGNORECASE
            if self.dotall.get():
                flags |= re.DOTALL
            regex = re.compile(self.regex.get(), flags)
            match = regex.search(self.text.get())
        except re.error:
            self.message.set("Invalid regex")
            self.message_label["bg"] = "mistyrose"
        else:
            self.message.set("Matched" if match is not None
                             else "Unmatched")
            self.message_label["bg"] = "white"
            if match:
                groups = {v: k for k, v in match.groupdict().items()}
                limit = min(10, 1 + len(match.groups()))
                for i in range(limit):
                    group = match.group(i)
                    if group is not None:
                        self.captures[i].set(group)
                        if group in groups:
                            self.groupLabels[i]["text"] = (
                                "Group {0} '{1}'".format(
                                i, groups[group]))
                        self.captureLabels[i]["bg"] = "cornsilk"

    def quit(self, event=None):
        self.parent.destroy()


def main():
    app = tkinter.Tk()
    image_path = os.path.join(os.path.dirname(__file__), 'images/')
    if sys.platform.startswith('win'):
        icon = image_path + 'regex.ico'
    else:
        icon = '@' + image_path + 'regex.xpm'
    app.iconbitmap(icon)
    main_window = MainWindow(app)
    app.protocol('WM_DELETE_WINDOW', main_window.quit)
    app.mainloop()


if __name__ == '__main__':
    main()