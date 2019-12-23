# 2019 advent of code day 9 part 2
import sys
from enum import IntEnum
from dataclasses import dataclass
import typing
from itertools import permutations


class COLOR(IntEnum):
    BLACK = 0
    WHITE = 1


@dataclass
class Grid:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))


LEFT = 0
RIGHT = 1


class PaintRobot:

    DIRECTIONS = [
        (0, 1),
        (1, 0),
        (0, -1),
        (-1, 0),
    ]

    PAINT = 0
    TURN = 1

    def __init__(self):
        self.current_square = Grid(0, 0)
        self.current_color = COLOR.WHITE
        self.known_grid = {self.current_square: self.current_color}
        self.current_direction = 0  # index of DIRECTION
        self.next_action = self.PAINT

    def get_camera_input(self):
        return self.current_color
    
    def accept_output(self, value):
        if self.next_action == self.PAINT:
            self.paint(value)
            self.next_action = self.TURN
        else:
            self.turn_and_advance(value)
            self.next_action = self.PAINT

    def turn_and_advance(self, turn_dir: int):
        # (0, 1) -> (-1, 0) -> (0, -1) -> (1, 0) -> (0, 1)
        # (0, 1) -> (1, 0) -> (0, -1) -> (-1, 0) -> (0, 1)
        if turn_dir == LEFT:
            self.current_direction = self.current_direction - 1 if self.current_direction > 0 else 3
        else:
            self.current_direction = self.current_direction + 1 if self.current_direction < 3 else 0
        
        self.current_square = Grid(
            self.current_square.x + self.DIRECTIONS[self.current_direction][0],
            self.current_square.y + self.DIRECTIONS[self.current_direction][1]
        )
        self.current_color = self.known_grid.get(self.current_square, COLOR.BLACK)
        self.known_grid[self.current_square] = self.current_color

    def paint(self, color: COLOR):
        self.current_color = color
        self.known_grid[self.current_square] = color

    def show_grid(self):
        min_x = min(g.x for g in self.known_grid)
        max_x = max(g.x for g in self.known_grid)
        min_y = min(g.y for g in self.known_grid)
        max_y = max(g.y for g in self.known_grid)
        for y in range(max_y, min_y - 1, -1):
            for x in range(min_x, max_x + 1, 1):
                color = COLOR.BLACK
                print(".", end="") if self.known_grid.get(Grid(x, y), COLOR.BLACK) == COLOR.BLACK else print("#", end="")
            print()


class OpProgram(list):
    def __getitem__(self, index):
        if type(index) is int and index >= 0:
            try:
                return super().__getitem__(index)
            except IndexError as ex:
                while len(self) < index + 1:
                    self.append(0)
        return super().__getitem__(index)

    def __setitem__(self, index, value):
        if index >= 0:
            try:
                super().__setitem__(index, value)
            except IndexError as ex:
                while len(self) < index + 1:
                    self.append(0)
        super().__setitem__(index, value)


class PMODE(IntEnum):
    POSITION = 0
    IMMEDIATE = 1
    RELATIVE = 2


class STATE(IntEnum):
    init = 0
    running = 1
    complete = -1
    waiting_on_input = 2


@dataclass
class Op:
    func: 'typing.Any'
    num_params: int
    can_jump: bool
    stores_result: bool


class OpMachine:

    def __init__(self, program: list):
        self.machine = OpProgram(program)
        self.io_robot = PaintRobot()
        self.pc = 0
        self.input_buffer = []
        self.output_buffer = []
        self.state = STATE.init
        self.relative_offset = 0
        self.debug = False
        self.interactive_mode = True

    def _value(self, param: int, mode: int):
        if mode == PMODE.RELATIVE:
            return self.machine[param + self.relative_offset]
        elif mode == PMODE.IMMEDIATE:
            return param
        else:  # PMODE.POSITION
            return self.machine[param]

    def add(self, a: int, b: int) -> int:
        return a + b

    def multiply(self, a: int, b: int) -> int:
        return a * b

    def get_input(self, *args) -> int:
        if self.io_robot:
            return self.io_robot.get_camera_input()
        if self.input_buffer:
            return self.input_buffer.pop(0)
        elif self.interactive_mode:
            return int(input("Enter integer: "))
        else:
            self.state = STATE.waiting_on_input
        return None

    def send_output(self, a: int):
        if self.io_robot:
            self.io_robot.accept_output(a)
            
        self.output_buffer.append(a)

    def complete(self, *args):
        #print('end of program')
        self.state = STATE.complete

    def jit(self, a: int, *args) -> bool:
        return True if a else False

    def jif(self, a: int, *args) -> bool:
        return False if a else True

    def lt(self, a: int, b: int) -> bool:
        return a < b

    def eq(self, a: int, b: int) -> bool:
        return a == b

    def sro(self, offset: int):
        self.relative_offset += offset

    def decode_opcode(self, value: int) -> (int, list):
        opcode = value % 100
        mode_digits = f'{value // 100:03d}'
        param_modes = []
        for x in range(self.OPS[opcode].num_params):
            param_modes.append(int(mode_digits[~x]))
        return opcode, param_modes
    
    def run_program(self):
        opcode = 0
        self.state = STATE.running
        while opcode != 99 and not self.state == STATE.waiting_on_input:
            opcode, param_modes = self.decode_opcode(self.machine[self.pc])
            op = self.OPS[opcode]
            raw_params = self.machine[self.pc + 1 : self.pc + op.num_params + 1]
            params = [self._value(p, param_modes[i]) for i, p in enumerate(raw_params)]
            if op.stores_result:
                params[-1] = raw_params[-1] if param_modes[-1] in [PMODE.POSITION, PMODE.IMMEDIATE] else self.relative_offset + raw_params[-1]
            passed_params = params[:-1] if op.stores_result else params
            if self.debug:
                print(f"{self.pc} | {op} | {passed_params}")  
            result = op.func(self, *passed_params)
            if op.stores_result and self.state != STATE.waiting_on_input:
                self.machine[params[-1]] = result
            if op.can_jump and result:
                self.pc = params[-1]
            elif self.state != STATE.waiting_on_input:
                self.pc += op.num_params + 1

    def resume(self):
        self.run_program()
    
    OPS = {
        1: Op(add, 3, False, True),
        2: Op(multiply, 3, False, True),
        3: Op(get_input, 1, False, True),
        4: Op(send_output, 1, False, False),
        5: Op(jit, 2, True, False),
        6: Op(jif, 2, True, False),
        7: Op(lt, 3, False, True),
        8: Op(eq, 3, False, True),
        9: Op(sro, 1, False, False),
        99: Op(complete, 0, False, False),
    }


PROGRAM = [3,8,1005,8,337,1106,0,11,0,0,0,104,1,104,0,3,8,102,-1,8,10,101,1,10,10,4,10,1008,8,1,10,4,10,101,0,8,29,3,8,1002,8,-1,10,101,1,10,10,4,10,1008,8,0,10,4,10,102,1,8,51,1,1008,18,10,3,8,102,-1,8,10,1001,10,1,10,4,10,108,1,8,10,4,10,102,1,8,76,1006,0,55,1,1108,6,10,1,108,15,10,3,8,102,-1,8,10,1001,10,1,10,4,10,1008,8,1,10,4,10,101,0,8,110,2,1101,13,10,1,101,10,10,3,8,102,-1,8,10,1001,10,1,10,4,10,108,0,8,10,4,10,1001,8,0,139,1006,0,74,2,107,14,10,1,3,1,10,2,1104,19,10,3,8,1002,8,-1,10,1001,10,1,10,4,10,1008,8,1,10,4,10,1002,8,1,177,2,1108,18,10,2,1108,3,10,1,109,7,10,3,8,1002,8,-1,10,1001,10,1,10,4,10,108,0,8,10,4,10,101,0,8,210,1,1101,1,10,1,1007,14,10,2,1104,20,10,3,8,102,-1,8,10,1001,10,1,10,4,10,108,0,8,10,4,10,102,1,8,244,1,101,3,10,1006,0,31,1006,0,98,3,8,102,-1,8,10,1001,10,1,10,4,10,1008,8,1,10,4,10,1002,8,1,277,1006,0,96,3,8,1002,8,-1,10,101,1,10,10,4,10,1008,8,0,10,4,10,1002,8,1,302,1,3,6,10,1006,0,48,2,101,13,10,2,2,9,10,101,1,9,9,1007,9,1073,10,1005,10,15,99,109,659,104,0,104,1,21101,937108976384,0,1,21102,354,1,0,1105,1,458,21102,1,665750077852,1,21101,0,365,0,1105,1,458,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,21101,21478178856,0,1,21101,412,0,0,1105,1,458,21102,3425701031,1,1,21102,1,423,0,1106,0,458,3,10,104,0,104,0,3,10,104,0,104,0,21102,984458351460,1,1,21102,1,446,0,1105,1,458,21101,0,988220908388,1,21101,457,0,0,1105,1,458,99,109,2,22101,0,-1,1,21102,1,40,2,21101,489,0,3,21101,479,0,0,1105,1,522,109,-2,2106,0,0,0,1,0,0,1,109,2,3,10,204,-1,1001,484,485,500,4,0,1001,484,1,484,108,4,484,10,1006,10,516,1102,0,1,484,109,-2,2105,1,0,0,109,4,1201,-1,0,521,1207,-3,0,10,1006,10,539,21102,1,0,-3,21201,-3,0,1,21202,-2,1,2,21101,1,0,3,21101,558,0,0,1105,1,563,109,-4,2105,1,0,109,5,1207,-3,1,10,1006,10,586,2207,-4,-2,10,1006,10,586,22102,1,-4,-4,1106,0,654,21202,-4,1,1,21201,-3,-1,2,21202,-2,2,3,21102,1,605,0,1106,0,563,21201,1,0,-4,21102,1,1,-1,2207,-4,-2,10,1006,10,624,21102,1,0,-1,22202,-2,-1,-2,2107,0,-3,10,1006,10,646,22101,0,-1,1,21102,646,1,0,106,0,521,21202,-2,-1,-2,22201,-4,-2,-4,109,-5,2106,0,0]


def main():
    o = OpMachine(PROGRAM[:])
    #o.debug = True
    o.run_program()
    #print(o.output_buffer)
    print(len(o.io_robot.known_grid))
    o.io_robot.show_grid()


if __name__ == "__main__":
    main()
