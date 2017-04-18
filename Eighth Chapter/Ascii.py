#!/usr/bin/python3

import string

is_ascii = lambda x: not any(ord(c) >= 127 for c in x)
is_ascii.__doc__ = \
    """
    >>> is_ascii("Universal suffrage")
    True
    >>> is_ascii("Cinema vérité")
    False
    """

is_ascii_punctuation = lambda x: all(c in string.punctuation for c in x)
is_ascii.__doc__ = \
    """
    >>> is_ascii_punctuation('Test')
    >>> False
    >>> is_ascii_punctuation('.,:')
    >>> True
    """

is_ascii_printable = lambda x: all(c in string.printable for c in x)
is_ascii.__doc__ = \
    """
    >>> is_ascii_printable("No way!")
    True
    >>> is_ascii_printable("@!?*\\t\\n")
    True
    >>> is_ascii_printable("@!?*\\t\\x05\\n")
    False
    >>> is_ascii_printable("Cinema vérité")
    False
    """

if __name__ == '__main__':
    import doctest

    doctest.testmod()
