#!/usr/bin/python3

import random


def main():
    forenames, surnames = get_forenames_and_surnames()
    fh = open('generated_names2.txt', mode='w')
    limit = 100
    years = tuple(range(1970, 2013))*3
    for name, surname, year in zip(
                                    random.sample(forenames, limit),
                                    random.sample(surnames, limit),
                                    random.sample(years, limit)):
        fullname = '{} {}'.format(name, surname)
        line = '{:<.25} {}'.format(fullname, year)
        fh.write(line + '\n')
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