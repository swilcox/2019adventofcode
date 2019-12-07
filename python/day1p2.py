# Advent of code day 1 part 2

def calc_fuel(amount):
    fuel = amount // 3 - 2
    return fuel + calc_fuel(fuel) if fuel > 0 else 0

def main():
    with open('day1input.txt', 'rt') as f:
        print(sum(calc_fuel(int(l.strip())) for l in f.readlines()))


if __name__ == "__main__":
    main()
