#!/usr/bin/python3

import abc


class Undo(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self):
        self.__undos = []

    @abc.abstractmethod
    def can_undo(self):
        return bool(self.__undos)

    @abc.abstractmethod
    def undo(self):
        assert self.__undos, 'Nothing left to undo.'
        self.__undos.pop()(self)

    def add_undo(self, undo):
        self.__undos.append(undo)


class Stack(Undo):

    def __init__(self):
        super().__init__()
        self.__stack = []

    @property
    def can_undo(self):
        return super().can_undo()

    def undo(self):
        super().undo()

    def push(self, func):
        self.__stack.append(func)
        self.add_undo(lambda self: self.__stack.pop())

    def pop(self):
        func = self.__stack.pop()
        self.add_undo(lambda self: self.__stack.append(func))
        return func





