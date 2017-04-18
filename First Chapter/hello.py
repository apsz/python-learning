#/usr/bin python3

def get_int():
    while True:
        try:
            return(int(input('Please provide an integer: ')))
        except ValueError as verr:
            print(verr, 'is not a valid integer, please try again')
            continue

print(get_int())
