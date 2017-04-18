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
        self.interest = tkinter.DoubleVar()
        self.interest.set(5.0)

        self.years = tkinter.IntVar()
        self.amount = tkinter.StringVar()

        principal_label = tkinter.Label(self, text='Principal $:',
                                        anchor=tkinter.W, underline=0)
        principal_scale = tkinter.Scale(self, variable=self.principal, command=self.updateUI,
                                        from_=100, to=1000000, resolution=100, orient=tkinter.HORIZONTAL)
        interest_label = tkinter.Label(self, text='Interest %:',
                                       anchor=tkinter.W, underline=0)
        interest_scale = tkinter.Scale(self, variable=self.interest, command=self.updateUI,
                                       from_=0.5, to=100, resolution=0.5, orient=tkinter.HORIZONTAL)
        year_label = tkinter.Label(self, text='Years:', anchor=tkinter.W, underline=0)
        year_scale = tkinter.Scale(self, variable=self.years, command=self.updateUI,
                                   from_=0.5, to=10, resolution=1, orient=tkinter.HORIZONTAL)
        amount_label = tkinter.Label(self, text='Amount $', anchor=tkinter.W)
        displayed_amount_label = tkinter.Label(self, textvariable=self.amount, relief=tkinter.SUNKEN,
                                               anchor=tkinter.E)

        principal_label.grid(row=0, column=0, padx=2, pady=2,
                             sticky=tkinter.W)
        principal_scale.grid(row=0, column=1, padx=2, pady=2,
                             sticky=tkinter.EW)
        interest_label.grid(row=1, column=0, padx=2, pady=2,
                        sticky=tkinter.W)
        interest_scale.grid(row=1, column=1, padx=2, pady=2,
                        sticky=tkinter.EW)
        year_label.grid(row=2, column=0, padx=2, pady=2,
                         sticky=tkinter.W)
        year_scale.grid(row=2, column=1, padx=2, pady=2,
                         sticky=tkinter.EW)
        amount_label.grid(row=3, column=0, padx=2, pady=2,
                          sticky=tkinter.W)
        displayed_amount_label.grid(row=3, column=1, padx=2, pady=2,
                                    sticky=tkinter.EW)

        principal_scale.focus_set()
        self.updateUI()
        parent.bind('Alt-p', lambda *ignore: principal_scale.focus_set())
        parent.bind("<Alt-r>", lambda *ignore: interest_scale.focus_set())
        parent.bind("<Alt-y>", lambda *ignore: year_scale.focus_set())
        parent.bind("<Control-q>", self.quit)
        parent.bind("<Escape>", self.quit)

    def updateUI(self, *ignore):
        amount = self.principal.get() * (
            (1 + (self.interest.get() / 100.0)) ** self.years.get())
        self.amount.set("{0:.2f}".format(amount))

    def quit(self, event=None):
        self.parent.destroy()


def main():
    app = tkinter.Tk()
    app.title('Interest')
    img_path = os.path.join(os.path.dirname(__file__) + '/images/')
    if sys.platform.startswith('win'):
        icon = img_path + 'interest.ico'
    else:
        icon = '@' + img_path + 'interest.xpm'
    app.iconbitmap(icon)
    main_window = MainWindow(app)
    app.protocol('WM_DELETE_WINDOW', main_window.quit)
    app.mainloop()


if __name__ == '__main__':
    main()
