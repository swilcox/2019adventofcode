class SpaceObject:
    objects = dict()

    def __init__(self, name: str):
        self.name = name
        self.parent = None
        self.objects[self.name] = self

    def __repr__(self):
        return f"{self.parent.name}){self.name}" if self.parent else self.name

    @classmethod
    def get_or_create(cls, name: str):
        return cls.objects[name] if name in cls.objects else cls(name)

    def compute_orbits(self):
        return 1 + self.parent.compute_orbits() if self.parent else 0

    @classmethod
    def compute_total_orbits(cls):
        return sum(o.compute_orbits() for o in cls.objects.values())

    @classmethod
    def from_str_def(cls, input_str: str):
        if ')' in input_str:
            parent_str, child_str = input_str.split(')')
            o = cls.get_or_create(child_str)
            o.parent = cls.get_or_create(parent_str)
        else:
            o = cls.get_or_create(input_str)
        return o

    def get_all_orbits(self):
        return [self.parent] + self.parent.get_all_orbits() if self.parent else []

    @classmethod
    def find_transfer_distance(cls, object1, object2):
        o1_orbits = object1.get_all_orbits()
        o2_orbits = object2.get_all_orbits()
        closest_common = None
        for xo in o1_orbits:
            if xo in o2_orbits:
                closest_common = xo
                break
        return -1 if not closest_common else o1_orbits.index(closest_common) + o2_orbits.index(closest_common)

def main():
    with open('day6input.txt', 'rt') as f:
        for line in f.readlines():
            SpaceObject.from_str_def(line.strip())

    print(SpaceObject.compute_total_orbits())

    print(
        SpaceObject.find_transfer_distance(
            SpaceObject.objects.get('YOU'),
            SpaceObject.objects.get('SAN')
        )
    )

if __name__ == "__main__":
    main()
