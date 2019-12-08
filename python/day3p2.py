# 2019 advent day 3 part 2

MOVES = {
    'R': (lambda x: (x[0], x[1] + 1)),
    'L': (lambda x: (x[0], x[1] - 1)),
    'U': (lambda x: (x[0] + 1, x[1])),
    'D': (lambda x: (x[0] - 1, x[1])),
}


def build_route(directions: list) -> list:
    current_location = (0, 0)
    route = []
    for d in directions:
        direction, amount = d[0], int(d[1:])
        for _ in range(amount):
            current_location = MOVES[direction](current_location)
            route.append(current_location)
    return route


def find_intersections(r1: list, r2: list) -> set:
    return set(r1).intersection(set(r2))


def find_shortest_manhattan_distance(points: set) -> int:
    return min((abs(p[0]) + abs(p[1])) for p in points)


def find_shortest_intersection_distance(points: set, r1: list, r2: list) -> int:
    return min(r1.index(p) + r2.index(p) + 2 for p in points)


#R1 = 'R75,D30,R83,U83,L12,D49,R71,U7,L72'
#R2 = 'U62,R66,U55,R34,D71,R55,D58,R83'
#R1 = 'R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51'
#R2 = 'U98,R91,D20,R16,D67,R40,U7,R15,U6,R7'


def main():
    with open('day3input.txt') as f:
        line1, line2 = f.readlines()
    #line1, line2 = R1, R2
    route1 = build_route(line1.strip().split(','))
    route2 = build_route(line2.strip().split(','))

    print(
        find_shortest_intersection_distance(
            find_intersections(route1, route2),
            route1,
            route2
        )
    )


if __name__ == "__main__":
    main()
