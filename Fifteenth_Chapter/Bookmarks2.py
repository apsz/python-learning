#!/usr/bin/python3


import os
import sys
import pickle
import tkinter
import tkinter.messagebox
import tkinter.filedialog
import webbrowser


class AddEditForm(tkinter.Toplevel):

    def __init__(self, parent, name=None, url=None):
        super().__init__(parent)
        self.parent = parent
        self.accepted = False
        self.transient(self.parent)
        self.title("Bookmarks - " + ("Edit" if name is not None else "Add"))
        self.nameVar = tkinter.StringVar()
        if name is not None:
            self.nameVar.set(name)
        self.urlVar = tkinter.StringVar()
        self.urlVar.set(url if url is not None else "http://")

        frame = tkinter.Frame(self)
        nameLabel = tkinter.Label(frame, text="Name:", underline=0)
        nameEntry = tkinter.Entry(frame, textvariable=self.nameVar)
        nameEntry.focus_set()
        urlLabel = tkinter.Label(frame, text="URL:", underline=0)
        urlEntry = tkinter.Entry(frame, textvariable=self.urlVar)
        okButton = tkinter.Button(frame, text="OK", command=self.ok)
        cancelButton = tkinter.Button(frame, text="Cancel",command=self.close)

        nameLabel.grid(row=0, column=0, sticky=tkinter.W, pady=3, padx=3)
        nameEntry.grid(row=0, column=1, columnspan=3, sticky=tkinter.EW, pady=3, padx=3)
        urlLabel.grid(row=1, column=0, sticky=tkinter.W, pady=3, padx=3)
        urlEntry.grid(row=1, column=1, columnspan=3, sticky=tkinter.EW, pady=3, padx=3)
        okButton.grid(row=2, column=2, sticky=tkinter.EW, pady=3, padx=3)
        cancelButton.grid(row=2, column=3, sticky=tkinter.EW, pady=3, padx=3)

        frame.grid(row=0, column=0, sticky=tkinter.NSEW)
        frame.columnconfigure(1, weight=1)
        window = self.winfo_toplevel()
        window.columnconfigure(0, weight=1)

        self.bind("<Alt-n>", lambda *ignore: nameEntry.focus_set())
        self.bind("<Alt-u>", lambda *ignore: urlEntry.focus_set())
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.close)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.grab_set()
        self.wait_window(self)

    def ok(self, event=None):
        self.name = self.nameVar.get()
        self.url = self.urlVar.get()
        self.accepted = True
        self.close()

    def close(self, event=None):
        self.parent.focus_set()
        self.destroy()


class MainWindow:

    def __init__(self, parent):
        self.parent = parent

        self.filename = None
        self.data = {}
        self.dirty = False

        # setup menubar
        menubar = tkinter.Menu(self.parent)
        self.parent['menu'] = menubar

        # setup 'file' in menubar
        fileMenu = tkinter.Menu(menubar)
        for label, command, shortcut_text, shortcut in (
                ('New...', self.fileNew, 'Ctrl+N', '<Control-n>'),
                ("Open...", self.fileOpen, "Ctrl+O", "<Control-o>"),
                ("Save", self.fileSave, "Ctrl+S", "<Control-s>"),
                (None, None, None, None),
                ("Quit", self.fileQuit, "Ctrl+Q", "<Control-q>")):
            if label is None:
                fileMenu.add_separator()
            else:
                fileMenu.add_command(label=label, command=command, accelerator=shortcut_text,
                                     underline=0)
                self.parent.bind(shortcut, command)
        menubar.add_cascade(label='File', menu=fileMenu, underline=0)

        # setup main window frame
        main_frame = tkinter.Frame(self.parent)

        # setup toolbar
        self.toolbar_images = []
        toolbar = tkinter.Frame(main_frame)
        for image, command in (
                ("images/filenew.gif", self.fileNew),
                ("images/fileopen.gif", self.fileOpen),
                ("images/filesave.gif", self.fileSave),
                ("images/editadd.gif", self.editAdd),
                ("images/editedit.gif", self.editEdit),
                ("images/editdelete.gif", self.editDelete),
                ("images/editshowwebpage.gif", self.editShowWebPage)):
            image = os.path.join(os.path.dirname(__file__), image)
            try:
                image = tkinter.PhotoImage(file=image)
                self.toolbar_images.append(image)
                button = tkinter.Button(toolbar, image=image, command=command)
                button.grid(row=0, column=len(self.toolbar_images)-1)
            except (EnvironmentError, tkinter.TclError) as err:
                print(err)
        toolbar.grid(row=0, column=0, columnspan=2, sticky=tkinter.NW)

        # setup listbox and scrollbar
        scrollbar = tkinter.Scrollbar(main_frame, orient=tkinter.VERTICAL)
        self.listbox = tkinter.Listbox(main_frame, yscrollcommand=scrollbar.set)
        self.listbox.grid(row=1, column=0, sticky=tkinter.NSEW)
        self.listbox.focus_set()
        scrollbar['command'] = self.listbox.yview
        scrollbar.grid(row=1, column=1, sticky=tkinter.NS)

        # setup statusbar
        self.statusbar = tkinter.Label(main_frame, text='Ready...', anchor=tkinter.W)
        self.statusbar.after(5000, self.clearStatusBar)
        self.statusbar.grid(row=2, column=0, columnspan=2, sticky=tkinter.EW)

        # place main frame
        main_frame.grid(row=0, column=0, sticky=tkinter.NSEW)

        # handle resizing by giving weights
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=999)
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=999)
        main_frame.columnconfigure(0, weight=1)
        window = self.parent.winfo_toplevel()
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        # set initial size, pos & window title
        self.parent.geometry("{0}x{1}+{2}+{3}".format(400, 500, 0, 50))
        self.parent.title("Bookmarks - Unnamed")

    def clearStatusBar(self):
        self.statusbar['text'] = ''

    def setStatusBar(self, new_status, timeout=5000):
        self.statusbar['text'] = new_status
        if timeout:
            self.statusbar.after(timeout, self.clearStatusBar)

    def okToContinue(self):
        if not self.dirty:
            return True
        reply = tkinter.messagebox.askyesnocancel('Bookmarks - unsaved changes',
                                                  'Save changes?',
                                                   parent=self.parent)
        if reply is None:
            return False
        if reply:
            self.fileSave()
        return True

    def fileNew(self):
        if not self.okToContinue():
            return
        self.listbox.delete(0, tkinter.END)
        self.dirty = False
        self.filename = None
        self.data = {}
        self.parent.title('Bookmarks - Untitled')

    def fileQuit(self, event=None):
        if self.okToContinue():
            self.parent.destroy()

    def fileSave(self, *ignore):
        if self.filename is None:
            filename = tkinter.filedialog.asksaveasfilename(title='Bookmarks - Save File',
                                                            initialdir='.',
                                                            filetypes=[('Bookmarks files', '*.bmf')],
                                                            defaultextension='.bmf',
                                                            parent=self.parent)
            if not filename:
                return False
            self.filename = filename
            if not self.filename.endswith('.bmf'):
                self.filename += '.bmf'
        try:
            with open(self.filename, 'wb') as fh:
                pickle.dump(self.data, fh, pickle.HIGHEST_PROTOCOL)
            self.setStatusBar('Saved {} bookmarks to {}'.format(len(self.data), self.filename))
            self.parent.title("Bookmarks - {0}".format(os.path.basename(self.filename)))
        except (EnvironmentError, pickle.PickleError) as err:
            tkinter.messagebox.showwarning("Bookmarks - Error",
                                           "Failed to save {0}:\n{1}".format(
                                               self.filename, err), parent=self.parent)
        return True

    def fileOpen(self, *ignore):
        if not self.okToContinue():
            return
        dir = (os.path.dirname(self.filename) if self.filename is not None else ".")
        filename = tkinter.filedialog.askopenfilename(
                title="Bookmarks - Open File",
                initialdir=dir,
                filetypes=[("Bookmarks files", "*.bmf")],
                defaultextension=".bmf", parent=self.parent)
        if filename:
            self.fileLoad(filename)

    def fileLoad(self, filename):
        self.filename = filename
        self.listbox.delete(0, tkinter.END)
        self.dirty = False
        try:
            with open(self.filename, "rb") as fh:
                self.data = pickle.load(fh)
            for name in sorted(self.data, key=str.lower):
                self.listbox.insert(tkinter.END, name)
            self.setStatusBar("Loaded {0} bookmarks from {1}".format(self.listbox.size(), self.filename))
            self.parent.title("Bookmarks - {0}".format(os.path.basename(self.filename)))
        except (EnvironmentError, pickle.PickleError) as err:
            tkinter.messagebox.showwarning("Bookmarks - Error",
                                           "Failed to load {0}:\n{1}".format(
                                            self.filename, err), parent=self.parent)

    def editAdd(self, *ignore):
        form = AddEditForm(self.parent)
        if form.accepted and form.name:
            self.data[form.name] = form.url
            self.listbox.delete(0, tkinter.END)
            for name in sorted(self.data, key=str.lower):
                self.listbox.insert(tkinter.END, name)
            self.dirty = True

    def editEdit(self, *ignore):
        indexes = self.listbox.curselection()
        if not indexes or len(indexes) > 1:
            return
        index = indexes[0]
        name = self.listbox.get(index)
        form = AddEditForm(self.parent, name, self.data[name])
        if form.accepted and form.name:
            self.data[form.name] = form.url
            if form.name != name:
                del self.data[name]
                self.listbox.delete(0, tkinter.END)
                for name in sorted(self.data, key=str.lower):
                    self.listbox.insert(tkinter.END, name)
            self.dirty = True

    def editDelete(self, *ignore):
        indexes = self.listbox.curselection()
        if not indexes or len(indexes) > 1:
            return
        index = indexes[0]
        name = self.listbox.get(index)
        if tkinter.messagebox.askyesno("Bookmarks - Delete", "Delete '{0}'?".format(name)):
            self.listbox.delete(index)
            self.listbox.focus_set()
            del self.data[name]
            self.dirty = True

    def editShowWebPage(self, *ignore):
        indexes = self.listbox.curselection()
        if not indexes or len(indexes) > 1:
            return
        index = indexes[0]
        webbrowser.open_new_tab(self.data[self.listbox.get(index)])


def main():
    app = tkinter.Tk()
    image_path = os.path.join(os.path.dirname(__file__), 'images/')
    if sys.platform.startswith('win'):
        icon = image_path + 'bookmark.ico'
    else:
        icon = '@' + image_path + 'bookmark.xpm'
    app.iconbitmap(icon)
    main_window = MainWindow(app)
    app.protocol('WM_DELETE_WINDOW', main_window.fileQuit)
    app.mainloop()


if __name__ == '__main__':
    main()