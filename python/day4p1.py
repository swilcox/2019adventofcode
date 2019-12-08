# 2019 Advent day 4 part 1

MIN = 145852
MAX = 616942

def main():
    current_number = MIN
    valid_count = 0
    while current_number <= MAX:
        has_repeat = False
        past_digit = ''
        increases = True
        for digit in str(current_number):
            if past_digit == digit:
                has_repeat = True
            if digit < past_digit:
                increases = False
                exit
            past_digit = digit
        if increases and has_repeat:
            valid_count += 1
        current_number += 1
    print(valid_count)

main()
