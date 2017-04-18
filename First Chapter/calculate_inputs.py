#!/usr/bin/python3

def main():
    numbers_entered = []

    while True:
        try:
            user_number = input("enter a number or Enter to finish:")
            if user_number == "":
                break
            user_number = int(user_number)
            numbers_entered.append(user_number)
        except ValueError as verr:
            print("Not a valid number:", verr)
            continue

    print("numbers: ", numbers_entered)
    print("count = {} sum = {} lowest = {} highest = {} mean = {}".format(
          len(numbers_entered), sum(numbers_entered), max(numbers_entered),
          min(numbers_entered), sum(numbers_entered) / len(numbers_entered)))

main()

