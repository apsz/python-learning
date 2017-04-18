#!/usr/bin/python3

import sys
import random

ARTICLES = ('the', 'a', 'an')
SUBJECTS = ('cat', 'dog', 'man', 'woman')
VERBS = ('sang', 'ran', 'jumped')
ADVERBS = ('loudly', 'quietly', 'well', 'badly')

SENTENCE_TYPE = ('asva', 'asv')

def main():
    try:
        number_of_lines = 5
        if 1 <= int(sys.argv[1]) <= 10:
            number_of_lines = int(sys.argv[1])
    except IndexError:
        pass
    except ValueError as verr:
        print("not a valid number", verr)

    for i in range(number_of_lines):
        sentence_type = random.choice(SENTENCE_TYPE)
        if sentence_type == 'asva':
            print(random.choice(ARTICLES), random.choice(SUBJECTS),
                  random.choice(VERBS), random.choice(ADVERBS))
        else:
            print(random.choice(ARTICLES), random.choice(SUBJECTS),
                  random.choice(VERBS))

main()