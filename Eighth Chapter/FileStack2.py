#!/usr/bin/python3

import abc
import pickle


class LoadSave:

    def __init__(self, filename, *attributes):
        self.filename = filename
        self.__attributes = []
        for attr in attributes:
            if attr.startswith('__'):
                attr = '_{}{}'.format(self.__class__.__name__, attr)
            self.__attributes.append(attr)

    def save(self):
        with open(self.filename, 'wb') as fh:
            data = [getattr(self, attr_name)
                    for attr_name in self.__attributes]
            pickle.dump(data, fh, pickle.HIGHEST_PROTOCOL)

    def load(self):
        with open(self.filename, 'rb') as fh:
            data = pickle.load(fh)
            for attr, value in zip(self.__attributes, data):
                setattr(self, attr, value)


class Undo(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self):
        self.__undos = []

    @abc.abstractproperty
    def can_undo(self):
        return bool(self.__undos)

    @abc.abstractmethod
    def undo(self):
        assert self.can_undo, 'Nothing to undo.'
        self.__undos.pop()(self)

    def add_undo(self, undo):
        self.__undos.append(undo)

    def clear(self):
        self.__undos = []


class FileStack(Undo, LoadSave):

    def __init__(self, filename):
        LoadSave.__init__(filename, '__stack')
        Undo.__init__()
        self.__stack = []

    def load(self):
        super().clear()
        self.load()

