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

    numbers_entered = return_sorted(numbers_entered)
    median = numbers_entered[len(numbers_entered) // 2]
    if len(numbers_entered) % 2 == 0:
        median = (numbers_entered[len(numbers_entered) // 2] + numbers_entered[(len(numbers_entered) // 2) - 1]) / 2

    print("numbers: ", numbers_entered)
    print("count = {} sum = {} lowest = {} highest = {} mean = {} median = {}".format(
          len(numbers_entered), sum(numbers_entered), max(numbers_entered),
          min(numbers_entered), sum(numbers_entered) / len(numbers_entered),
          median))


def return_sorted(lst):
    sorted = True
    while sorted:
        print(lst)
        sorted = False
        for i in range(len(lst) -1):
            if lst[i] > lst[i + 1]:
                temp_val = lst[i]
                lst[i] = lst[i + 1]
                lst[i + 1] = temp_val
                sorted = True
    return lst

main()

