TEST1 = """
.#..#
.....
#####
....#
...##"""


def count_visible(x, y, grid):
    
    return 0


def main():
    grid = []
    for line in TEST1.split('\n'):
        if line.strip():
            grid.append(list(line.strip()))
    for row in grid:
        print(row)


if __name__ == "__main__":
    main()
