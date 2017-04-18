#!/usr/bin/python3

import abc
import pickle


class Undo(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self):
        self.__undos = []

    @abc.abstractproperty
    def can_undo(self):
        return bool(self.__undos)

    @abc.abstractmethod
    def undo(self):
        assert self.can_undo, 'Nothing more to undo.'
        self.__undos.pop()(self)

    def add_undo(self, undo):
        self.__undos.append(undo)

    def clear(self):
        self.__undos = []


class LoadSave:

    def __init__(self, filename, *attributes):
        self.filename = filename
        self.__attributes_names = []
        for attribute in attributes:
            if attribute.startswith('__'):
                attribute = '_{}{}'.format(self.__class__.__name__,
                                           attribute)
                self.__attributes_names.append(attribute)

    def save(self):
        with open(self.filename, 'wb') as fh:
            data = [getattr(self, attr)
                    for attr in self.__attributes_names]
            pickle.dump(data, fh, pickle.HIGHEST_PROTOCOL)

    def load(self):
        with open(self.filename, 'rb') as fh:
            data = pickle.load(fh)
            for attr, value in zip(self.__attributes_names, data):
                setattr(self, attr, value)


class FileStack(Undo, LoadSave):

    def __init__(self, filename):
        Undo.__init__()
        LoadSave.__init__(filename, '__stack')
        self.__stack = []

    def load(self):
        super().clear()
        self.load()

    def can_undo(self):
        super().can_undo()

    def undo(self):
        super().undo()

    def push(self, item):
        self.__stack.append(item)
        self.add_undo(lambda self: self.__stack.pop())

    def pop(self):
        item = self.__stack.pop()
        self.add_undo(lambda self: self.__stack.append(item))
        return item
