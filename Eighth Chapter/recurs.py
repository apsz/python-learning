#!/usr/bin/python3

def aeiou(word):
    if len(word) <= 1:
        return word[0]
    elif word[0] in 'aeiou':
        return word[0] + aeiou(word[1:])
    else:
        return aeiou(word[1:])


print(aeiou('helloolleh'))