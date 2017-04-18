#!/usr/bin/python3

class FuzzyBool():
    def __init__(self, val):
        self.val = val

    @property
    def val(self):
        return self.__val


    @val.setter
    def val(self, value):
        if not (isinstance(value, float) and 0.0 <= value <= 1.0): raise TypeError()
        self.__val = value


    def conjunction(self, *args):
        for arg in args:
            if not isinstance(arg, FuzzyBool): raise TypeError()
            while 0.0 <= self.__val <= 1.0:
                self.val += arg
        return self.val


    def disjunction(self, *args):
        for arg in args:
            if not isinstance(arg, FuzzyBool): raise TypeError()
            while 0.0 <= self.__val <= 1.0:
                self.val -= arg
        return self.val


    def __lt__(self, other):
        if not isinstance(other, FuzzyBool): raise NotImplementedError()
        return self.val < other.val


    def __le__(self, other):
        if not isinstance(other, FuzzyBool): raise NotImplementedError()
        return self.val <= other.val


    def __eq__(self, other):
        if not isinstance(other, FuzzyBool): raise NotImplementedError()
        return self.val == other.val


    def __invert__(self):
        return not self.val


    def __and__(self, other):
        if not isinstance(other, FuzzyBool): raise TypeError()
        return self.val and other.val


    def __or__(self, other):
        if not isinstance(other, FuzzyBool): raise TypeError()
        return self.val or other.val


    def __bool__(self):
        return True if self.val >= 0.5 else False


    def __int__(self):
        return int(self.val)


    def __float__(self):
        return self.val


    def __str__(self):
        return repr(self)


    def __repr__(self):
        return 'FuzzyBool({0:!r})'.format(self.val)


    def __hash__(self):
        return self.val





