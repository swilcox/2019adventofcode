# Advent of code day 1 part 1

def main():
    with open('day1input.txt', 'rt') as f:
        print(sum(int(l.strip()) // 3 - 2 for l in f.readlines()))


if __name__ == "__main__":
    main()
