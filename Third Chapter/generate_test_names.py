#!/usr/bin/python3

import random


def main():
    forenames, surnames = get_forenames_and_surnames()
    fh = open('generated_names.txt', mode='w')
    for i in range(100):
        line = "{} {}\n".format(random.choice(forenames),
                              random.choice(surnames))
        fh.write(line)
    fh.close()


def get_forenames_and_surnames():
    forenames = []
    surnames = []
    for names, file in ((forenames, "data/forenames.txt"),
                         (surnames, "data/surnames.txt")):
        for name in open(file):
            names.append(name.rstrip())
    return forenames, surnames


main()