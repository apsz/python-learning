#!/usr/bin/python3

import os
import sys
import glob
import collections


class GetFunction:

    def __init__(self):
        self.__found = {}
        self.__lost = set()

    def __call__(self, module, attr_name):
        function = self.__found.get((attr_name, module), None)
        if function is None and \
        (attr_name, module) not in self.__lost:
            try:
                function = getattr(module, attr_name)
                if not isinstance(function, collections.Callable):
                    raise AttributeError()
                self.__found[attr_name, module] = function
            except AttributeError:
                function = None
        return function


def main():
    get_function = GetFunction()
    modules = load_modules()
    all_get_file_type_funcs = []
    for module in modules:
        get_file_type = get_function(module, 'get_file_type')
        if not get_file_type is None:
            all_get_file_type_funcs.append(get_file_type)

    for file in get_files(sys.argv[1:]):
        try:
            with open(file, 'rb') as fh:
                magic = fh.read(1000)
                for get_file_func in all_get_file_type_funcs:
                    file_type = get_file_func(magic, os.path.splitext(file)[1])
                    if not file_type is None:
                        print('{:.<20} {}'.format(file_type, file))
                else:
                    print('{:.<20} {}'.format('Unknown', file))
        except (EnvironmentError, IOError) as f_err:
            print('{} error: {}\nSkipping...'.format(file, f_err))


def load_modules():
    modules = []
    for file in os.listdir(os.path.dirname(__file__) or '.'):
        if file.endswith('.py') and 'magic' in file.lower():
            name = os.path.splitext(file)[0]
            if name.isidentifier() and name not in sys.modules:
                try:
                    with open(file, encoding='utf-8') as fh:
                        code = fh.read()
                        new_module = type(sys)(name)
                        exec(code, new_module.__dict__)
                        sys.modules[name] = new_module
                        modules.append(new_module)
                except (EnvironmentError, SyntaxError) as err:
                    sys.modules.pop(name, None)
                    print(err)
    return modules


if sys.platform.startswith('win'):
    def get_files(files_list):
        for file in files_list:
            if os.path.isfile(file):
                yield file
            else:
                for i_file in glob.iglob(file):
                    if os.path.isfile(i_file):
                        yield i_file
else:
    def get_files(files_list):
        return (file for file in files_list
                if os.path.isfile(file))


main()