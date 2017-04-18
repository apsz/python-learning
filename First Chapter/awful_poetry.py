#!/usr/bin/python3

import random

ARTICLES = ('the', 'a', 'an')
SUBJECTS = ('cat', 'dog', 'man', 'woman')
VERBS = ('sang', 'ran', 'jumped')
ADVERBS = ('loudly', 'quietly', 'well', 'badly')

SENTENCE_TYPE = ('asva', 'asv')

def main():
    for i in range(5):
        sentence_type = random.choice(SENTENCE_TYPE)
        if sentence_type == 'asva':
            print(random.choice(ARTICLES), random.choice(SUBJECTS),
                  random.choice(VERBS), random.choice(ADVERBS))
        else:
            print(random.choice(ARTICLES), random.choice(SUBJECTS),
                  random.choice(VERBS))

main()