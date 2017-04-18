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
        self.ignore_case = tkinter.IntVar()
        self.dotall = tkinter.IntVar()

        self.regex.trace('w', self.updateRE)
        self.text.trace('w', self.updateRE)
        self.dotall.trace('w', self.updateRE)
        self.ignore_case.trace('w', self.updateRE)

        main_frame = tkinter.Frame(self.parent)

        regex_label = tkinter.Label(main_frame, text='Regex', underline=0)
        regex_entry = tkinter.Entry(main_frame, textvariable=self.regex)
        text_label = tkinter.Label(main_frame, text='Text', underline=0)
        text_entry = tkinter.Entry(main_frame, textvariable=self.text)
        ignore_case_checkbox = tkinter.Checkbutton(main_frame, text='Ignore case', variable=self.ignore_case)
        dotall_checkbox = tkinter.Checkbutton(main_frame, text='Dotall', variable=self.dotall)

        regex_label.grid(row=0, column=0, padx=2, pady=2, sticky=tkinter.W)
        regex_entry.grid(row=0, column=2, columnspan=4, padx=2, pady=2, sticky=tkinter.EW)
        text_label.grid(row=1, column=0, padx=2, pady=2, sticky=tkinter.W)
        text_entry.grid(row=1, column=2, columnspan=4, padx=2, pady=2, sticky=tkinter.EW)
        ignore_case_checkbox.grid(row=2, column=2, sticky=tkinter.EW)
        dotall_checkbox.grid(row=2, column=4, sticky=tkinter.EW)

        self.group_matches = []
        self.group_names = []
        for i in range(10):
            group_label = tkinter.Label(main_frame, text='Group {}'.format(i))
            group_name = tkinter.Label(main_frame, text='')
            group_match = tkinter.Entry(main_frame)
            group_label.grid(row=3+i, column=0, padx=2, pady=2, sticky=tkinter.W)
            group_name.grid(row=3+i, column=1, padx=2, pady=2, sticky=tkinter.W)
            group_match.grid(row=3+i, column=2, columnspan=3, padx=2, pady=2, sticky=tkinter.EW)
            self.group_names.append(group_name)
            self.group_matches.append(group_match)

        self.status_label = tkinter.Label(main_frame, text='', anchor=tkinter.W)
        self.status_label.grid(row=13, column=0, columnspan=4, sticky=tkinter.EW)

        main_frame.grid(row=0, column=0, sticky=tkinter.NSEW)

        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(2, weight=999)
        main_frame.rowconfigure(1, weight=999)
        for i in range(1, 13):
             main_frame.rowconfigure(i, weight=1)
        window = main_frame.winfo_toplevel()
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        self.parent.geometry("{0}x{1}+{2}+{3}".format(360, 480, 0, 50))
        self.parent.title("Regex")


    def updateRE(self, *ignore):
        re_raw = self.regex.get()
        text_to_match = self.text.get()
        flags = ''
        if not re_raw or not text_to_match:
            self.status_label['text'] = 'No match found.'
            return
        if self.dotall.get() or self.ignore_case.get():
            flags = '(?{}{})'.format('s' if self.dotall else '', 'i' if self.ignore_case.get() else '')
        try:
            re_compiled = re.compile(flags + re_raw)
            matched_all = re.findall(re_compiled, text_to_match)
            if not matched_all:
                self.status_label['text'] = 'No match found.'
            else:
                self.clear_matches()
                full_match = matched_all
                if not isinstance(matched_all[0], str):
                    full_match = ' '.join([''.join(i) for i in matched_all])
                self.group_matches[0].insert(tkinter.END, full_match if full_match[0] else '')
                group_index_to_name = {v: k for k, v in re_compiled.groupindex.items()}
                for i in range(1, re_compiled.groups + 1):
                    if i in group_index_to_name:
                        self.group_names[i]['text'] = '"{0:.10}"'.format(group_index_to_name[i])
                    if isinstance(matched_all[0], str):
                        self.group_matches[1].insert(tkinter.END, ' '.join(match for match in matched_all))
                        break
                    this_group_matches = ' '.join(match_tuple[i-1] for match_tuple in matched_all if match_tuple[i-1])
                    self.group_matches[i].insert(tkinter.END, this_group_matches)
                self.status_label['text'] = 'Matched.'
        except re.error:
            self.status_label['text'] = 'Invalid regex.'
            self.clear_matches()


    def clear_matches(self):
        for match_field in self.group_matches:
            match_field.delete(0, tkinter.END)

    def quit(self, *ignore):
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