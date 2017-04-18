#!/usr/bin/python3

import os
import sys
import tkinter


class MainWindow(tkinter.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid(row=0, column=0)

        self.principal = tkinter.DoubleVar()
        self.principal.set(1000.0)
        self.rate = tkinter.DoubleVar()
        self.principal.set(5.0)

        self.years = tkinter.IntVar()
        self.amount = tkinter.StringVar()

        principal_label = tkinter.Label(self, text='Principal $:',
                                        anchor=tkinter.W, underline=0)
        principal_scale = tkinter.Scale(self, variable=self.principal,
                                        command=self.updateUi, from_=100, to=100000000,
                                        resolution=100, orient=tkinter.HORIZONTAL)
        rate_label = tkinter.Label(self, text='Rate %:', underline=0,
                                   anchor=tkinter.W)
        rate_scale = tkinter.Scale(self, variable=self.rate, from_=1, to=100, command=self.updateUi,
                                   resolution=0.25, digits=5, orient=tkinter.HORIZONTAL)
        years_label = tkinter.Label(self, text='Years:', underline=0,
                                    anchor=tkinter.W)
        years_scale = tkinter.Scale(self, variable=self.years, command=self.updateUi,
                                    from_=1, to=50, orient=tkinter.HORIZONTAL)
        amount_label = tkinter.Label(self, text='Amount $', anchor=tkinter.W)
        actual_amount_label = tkinter.Label(self, textvariable=self.amount, relief=tkinter.SUNKEN,
                                            anchor=tkinter.E)

        principal_label.grid(row=0, column=0, padx=2, pady=2,
                             sticky=tkinter.W)
        principal_scale.grid(row=0, column=1, padx=2, pady=2,
                             sticky=tkinter.EW)
        rate_label.grid(row=1, column=0, padx=2, pady=2,
                        sticky=tkinter.W)
        rate_scale.grid(row=1, column=1, padx=2, pady=2,
                        sticky=tkinter.EW)
        years_label.grid(row=2, column=0, padx=2, pady=2,
                         sticky=tkinter.W)
        years_scale.grid(row=2, column=1, padx=2, pady=2,
                         sticky=tkinter.EW)
        amount_label.grid(row=3, column=0, padx=2, pady=2,
                          sticky=tkinter.W)
        actual_amount_label.grid(row=3, column=1, padx=2, pady=2,
                                 sticky=tkinter.EW)

        principal_scale.focus_set()
        self.updateUi()
        parent.bind('Alt-p', lambda *ignore: principal_scale.focus_set())
        parent.bind("<Alt-r>", lambda *ignore: rate_scale.focus_set())
        parent.bind("<Alt-y>", lambda *ignore: years_scale.focus_set())
        parent.bind("<Control-q>", self.quit)
        parent.bind("<Escape>", self.quit)

    def updateUi(self, *ignore):
        amount = self.principal.get() * (
            (1 + (self.rate.get() / 100.0)) ** self.years.get())
        self.amount.set("{0:.2f}".format(amount))

    def quit(self, event=None):
        self.parent.destroy()


def main():
    app = tkinter.Tk()
    img_path = os.path.join(os.path.dirname(__file__), 'images/')
    if sys.platform.startswith('win'):
        icon = img_path + 'interest.ico'
    else:
        icon = '@' + img_path + 'interest.xbm'
    app.iconbitmap(icon)
    app.title('Interest')
    main_window = MainWindow(app)
    app.protocol('WM_DELETE_WINDOW', main_window.quit)
    app.mainloop()


if __name__ == '__main__':
    main()