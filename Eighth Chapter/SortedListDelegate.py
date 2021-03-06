#!/usr/bin/python3

_identity = lambda x: x


def delegate(attribute_name, method_names):
    def decorator(cls):
        nonlocal attribute_name
        if attribute_name.startswith('__'):
            attribute_name = '_{}__{}'.format(cls.__name__,
                                              attribute_name)
            for method in method_names:
                setattr(cls, method, eval('lambda self, *args, **kwargs: '
                                          'self.{}.{}(*args, **kwargs)'.format(
                                           attribute_name, method)))
        return cls
    return decorator


@delegate('__list', ('pop', '__getitem__', '__delitem__', '__iter__'
                     '__reversed__', '__len__', '__str__'))
class SortedList:
    def __init__(self, sequence=None, key=None):
        self.__key = key or _identity
        if not sequence:
            self.__list = []
        elif (isinstance(sequence, SortedList) and
                        sequence.__key == self.__key):
            self.__list = sequence.__list[:]
        else:
            self.__list = sorted(list(sequence), key=self.__key)

    @property
    def key(self):
        return self.__key

    def add(self, value):
        index = self.__bisect_left(value)
        if index == len(self.__list):
            self.__list.append(value)
        else:
            self.__list.insert(index, value)

    def remove(self, value):
        index = self.__bisect_left(value)
        if index < len(self.__list) and self.__list[index] == value:
            del self.__list[index]
        else:
            raise ValueError('{}.remove(x): x not in list'.format(
                             self.__class__.__name__))

    def remove_every(self, value):
        count = 0
        index = self.__bisect_left(value)
        while index < len(self.__list) and self.__list[index] == value:
            del self.__list[index]
            count += 1
        return count

    def count(self, value):
        count = 0
        index = self.__bisect_left(value)
        while index < len(self.__list) and self.__list[index] == value:
            count += 1
            index += 1
        return count

    def index(self, value):
        index = self.__bisect_left(value)
        if index < len(self.__list) and self.__list[index] == value:
            return index
        else:
            raise ValueError('{}.index(x): x not in list'.format(
                             self.__class__.__name__))

    def __bisect_left(self, value):
        # binary search
        val_to_compare = self.__key(value)
        left, right = (0, len(self.__list))
        while left < right:
            middle = (left + right) // 2
            if self.__key(self.__list[middle]) < val_to_compare:
                left = middle + 1
            else:
                right = middle
        return left

    def clear(self):
        self.__list = []

    def copy(self):
        return SortedList(self, self.__key)

    def __setitem__(self, key, value):
        raise TypeError("use add() to insert a value and rely on "
                        "the list to put it in the right place")

    def __contains__(self, value):
        index = self.__bisect_left(value)
        return (index < len(self.__list) and
                self.__list[index] == value)

    __copy__ = copy