#!/usr/bin/python3

import pprint

before = ["Nonmetals",
"    Hydrogen",
"    Carbon",
"    Nitrogen",
"    Oxygen",
"Inner Transitionals",
"    Lanthanides",
"        Cerium",
"        Europium",
"    Actinides",
"        Uranium",
"        Curium",
"        Plutonium",
"Alkali Metals",
"    Lithium",
"    Sodium",
"    Potassium"]


def sort_indented_list(ilist, indent='    '):
    KEY, ITEM, CHILD_ITEMS = range(3)

    def add_item(level, key, item, entries):
        if level == 0:
            entries.append((key, item, []))
        else:
            add_item(level -1, key, item,
                     entries[-1][CHILD_ITEMS])

    def update_ilist(entry):
        i_list.append(entry[ITEM])
        for sub_entry in sorted(entry[CHILD_ITEMS]):
            update_ilist(sub_entry)

    entries = []
    for item in ilist:
        level = 0
        start_idx = 0
        while item.startswith(indent, start_idx):
            level += 1
            start_idx += len(indent)
        add_item(level, item.strip().lower(),
                 item, entries)

    i_list = []
    for entry in sorted(entries):
        update_ilist(entry)
    return i_list


pprint.pprint(sort_indented_list(before))

