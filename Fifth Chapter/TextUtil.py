#!/usr/bin/python3


import string


def simplify(text, whitespace=string.whitespace, delete=''):
    return ' '.join((''.join([c for c in s if c not in delete]).strip(whitespace)) for s in text.split())


def long_simplify(text, whitespace=string.whitespace, delete=''):
    words = []
    word = ''
    for c in text:
        if c in delete:
            continue
        elif c in whitespace:
            if word:
                words.append(word)
                word = ''
        else:
            word += c
    if word:
        words.append(word)
    return ' '.join(words)


print(simplify("    this   and\n  that\t too"))
print(simplify(" some     text  with        spurious  whitespace    "))
print(simplify(" Washington D.C.\n", delete=",;:."))
print(simplify(" disemvoweled ", delete="aeiou"))
print(long_simplify(" some     text  with        spurious  whitespace    "))
print(long_simplify("    this   and\n  that\t too"))
print(long_simplify(" Washington D.C.\n", delete=",;:."))
print(long_simplify(" disemvoweled ", delete="aeiou"))


def is_balanced(text, brackets="()[]{}<>"):
    starting_dict = dict.fromkeys(brackets[::2], 0)
    closing_dict = dict.fromkeys(brackets[1::2], 0)
    for c in text:
        if c in starting_dict.keys():
            starting_dict[c] += 1
        elif c in closing_dict.keys():
            closing_dict[c] += 1
    return set(starting_dict.values()) == set(closing_dict.values())


def is_balanced_longer(text, brackets='()[]{}<>'):
    counts = {}
    left_for_right = {}
    for l, r in zip(brackets[::2], brackets[1::2]):
        assert l != r, "bracket characters must differ"
        counts[l] = 0
        left_for_right[r] = l
    for c in text:
        if c in counts:
            counts[c] += 1
        elif c in left_for_right:
            if counts[left_for_right[c]] == 0:
                return False
            counts[left_for_right[c]] -= 1
    return not any (counts.values())



print(is_balanced("(Python (is (not (lisp))))"))
print(is_balanced_longer("(Python (is (not (lisp))))"))