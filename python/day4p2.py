# 2019 Advent day 4 part 1

MIN = 145852
MAX = 616942

def main():
    current_number = MIN
    valid_count = 0
    while current_number <= MAX:
        has_2_repeat = False
        past_digit = ''
        repeat_count = 1
        increases = True
        for digit in str(current_number):
            if past_digit == digit:
                repeat_count += 1
            else:
                if repeat_count == 2:
                    has_2_repeat = True
                repeat_count = 1
            if digit < past_digit:
                increases = False
                exit
            past_digit = digit
        if repeat_count == 2:
            has_2_repeat = True
        if increases and has_2_repeat:
            valid_count += 1
        current_number += 1
    print(valid_count)

main()
