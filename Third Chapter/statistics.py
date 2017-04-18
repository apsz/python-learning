#!/usr/bin/python3

import sys
import math
import collections


Statistics = collections.namedtuple("Statistics", "mean mode median std_dev")


def main():
    sanity_check()

    numbers = []
    frequencies = collections.defaultdict(int)
    for file in sys.argv[1:]:
        read_data(file, numbers, frequencies)
    if numbers:
        statistics = calculate_statistics(numbers, frequencies)
        print_results(len(numbers), statistics)
    else:
        print('no numbers found.')


def sanity_check():
    if len(sys.argv) < 1 or sys.argv[1] in {'--help', '-h'}:
        print('usage: {} [file1] [file2] [fileN]...'.format(sys.argv[0]))
        sys.exit()


def read_data(file, numbers, frequencies):
    for line_number, line in enumerate(open(file), 1):
        for num in line.split():
            try:
                number = float(num)
                numbers.append(number)
                frequencies[number] += 1
            except ValueError as verr:
                print('{file}:{line_number} skipping {num}: {verr}'.format(**locals()))


def calculate_statistics(numbers, frequencies):
    mean = sum(numbers) / len(numbers)
    mode = calculate_mode(frequencies, 3)
    median = calculate_median(numbers)
    standard_dev = calculate_std_dev(numbers, mean)
    return Statistics(mean, mode, median, standard_dev)


def calculate_mode(frequencies, maximum_modes):
    highest_frequency = max(frequencies.values())
    mode = [number for number, frequency in frequencies.items()
            if frequency == highest_frequency]
    if not (1 <= len(mode) <= maximum_modes):
        mode = None
    else:
        mode.sort()
    return mode


def calculate_median(numbers):
    numbers = sorted(numbers)
    middle = len(numbers) // 2
    median = numbers[middle]
    if len(numbers) % 2 == 0:
        median = (median + numbers[middle - 1]) / 2
    return median


def calculate_std_dev(numbers, mean):
    total = 0
    for number in numbers:
        total += ((number - mean) ** 2)
    variance = total / (len(numbers) - 1)
    return math.sqrt(variance)


def print_results(count, statistics):
    real = "9.2f"
    if statistics.mode is None:
        modeline = ""
    elif len(statistics.mode) == 1:
        modeline = "mode = {0:{fmt}}\n".format(
            statistics.mode[0], fmt=real)
    else:
        modeline = ("mode = [" +
                ", ".join(["{0:.2f}".format(m)
                           for m in statistics.mode]) + "]\n")
    print("""\
    count = {0:6}
    mean = {mean:{fmt}}
    median = {median:{fmt}}
    {1}\
    std. dev. = {std_dev:{fmt}}""".format(
        count, modeline, fmt=real, **statistics._asdict()))


main()