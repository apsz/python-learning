#!/usr/bin/python3

import abc


class TextFilter(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def is_transformer(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def __call__(self):
        raise NotImplementedError()


class CharCounter(TextFilter):

    def is_transformer(self):
        return False

    def __call__(self, text, chars):
        counter = 0
        for c in text:
            if c in chars:
                counter += 1
        return counter
