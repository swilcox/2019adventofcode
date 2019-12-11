# 2019 advent of code day 5 part 2
import sys
from enum import IntEnum
from dataclasses import dataclass
import typing


class PMODE(IntEnum):
    POSITION = 0
    IMMEDIATE = 1


@dataclass
class Op:
    func: 'typing.Any'
    num_params: int
    can_jump: bool
    stores_result: bool


class OpMachine:

    def __init__(self, program: list):
        self.machine = program
        self.pc = 0

    def _value(self, param, mode):
        return self.machine[param] if mode == PMODE.POSITION else param

    def add(self, a: int, b: int) -> int:
        return a + b

    def multiply(self, a: int, b: int) -> int:
        return a * b

    def get_input(self, *args) -> int:
        return int(input('Enter integer: '))

    def send_output(self, a: int):
        print("output -->", a)

    def complete(self, *args):
        print('end of program')

    def jit(self, a: int, *args) -> bool:
        return True if a else False

    def jif(self, a: int, *args) -> bool:
        return False if a else True

    def lt(self, a: int, b: int) -> bool:
        return a < b

    def eq(self, a: int, b: int) -> bool:
        return a == b

    def decode_opcode(self, value: int) -> (int, list):
        opcode = value % 100
        mode_digits = f'{value // 100:03d}'
        param_modes = []
        for x in range(self.OPS[opcode].num_params):
            param_modes.append(int(mode_digits[~x]))
        return opcode, param_modes
    
    def run_program(self):
        opcode = 0
        while opcode != 99:
            opcode, param_modes = self.decode_opcode(self.machine[self.pc])
            op = self.OPS[opcode]
            raw_params = self.machine[self.pc + 1 : self.pc + op.num_params + 1]
            params = [self._value(p, param_modes[i]) for i, p in enumerate(raw_params)]
            if op.stores_result:
                params[-1] = raw_params[-1]
            passed_params = params[:-1] if op.stores_result else params 
            result = op.func(self, *passed_params)
            if op.stores_result:
                self.machine[params[-1]] = result
            if op.can_jump and result:
                self.pc = params[-1]
            else:
                self.pc += op.num_params + 1
        
    OPS = {
        1: Op(add, 3, False, True),
        2: Op(multiply, 3, False, True),
        3: Op(get_input, 1, False, True),
        4: Op(send_output, 1, False, False),
        5: Op(jit, 2, True, False),
        6: Op(jif, 2, True, False),
        7: Op(lt, 3, False, True),
        8: Op(eq, 3, False, True),
        99: Op(complete, 0, False, False),
    }


PROGRAM = [3,225,1,225,6,6,1100,1,238,225,104,0,2,171,209,224,1001,224,-1040,224,4,224,102,8,223,223,1001,224,4,224,1,223,224,223,102,65,102,224,101,-3575,224,224,4,224,102,8,223,223,101,2,224,224,1,223,224,223,1102,9,82,224,1001,224,-738,224,4,224,102,8,223,223,1001,224,2,224,1,223,224,223,1101,52,13,224,1001,224,-65,224,4,224,1002,223,8,223,1001,224,6,224,1,223,224,223,1102,82,55,225,1001,213,67,224,1001,224,-126,224,4,224,102,8,223,223,1001,224,7,224,1,223,224,223,1,217,202,224,1001,224,-68,224,4,224,1002,223,8,223,1001,224,1,224,1,224,223,223,1002,176,17,224,101,-595,224,224,4,224,102,8,223,223,101,2,224,224,1,224,223,223,1102,20,92,225,1102,80,35,225,101,21,205,224,1001,224,-84,224,4,224,1002,223,8,223,1001,224,1,224,1,224,223,223,1101,91,45,225,1102,63,5,225,1101,52,58,225,1102,59,63,225,1101,23,14,225,4,223,99,0,0,0,677,0,0,0,0,0,0,0,0,0,0,0,1105,0,99999,1105,227,247,1105,1,99999,1005,227,99999,1005,0,256,1105,1,99999,1106,227,99999,1106,0,265,1105,1,99999,1006,0,99999,1006,227,274,1105,1,99999,1105,1,280,1105,1,99999,1,225,225,225,1101,294,0,0,105,1,0,1105,1,99999,1106,0,300,1105,1,99999,1,225,225,225,1101,314,0,0,106,0,0,1105,1,99999,1008,677,677,224,1002,223,2,223,1006,224,329,101,1,223,223,1108,226,677,224,1002,223,2,223,1006,224,344,101,1,223,223,7,677,226,224,102,2,223,223,1006,224,359,1001,223,1,223,8,677,226,224,102,2,223,223,1005,224,374,1001,223,1,223,1107,677,226,224,102,2,223,223,1006,224,389,1001,223,1,223,1008,226,226,224,1002,223,2,223,1005,224,404,1001,223,1,223,7,226,677,224,102,2,223,223,1005,224,419,1001,223,1,223,1007,677,677,224,102,2,223,223,1006,224,434,1001,223,1,223,107,226,226,224,1002,223,2,223,1005,224,449,1001,223,1,223,1008,677,226,224,102,2,223,223,1006,224,464,1001,223,1,223,1007,677,226,224,1002,223,2,223,1005,224,479,1001,223,1,223,108,677,677,224,1002,223,2,223,1006,224,494,1001,223,1,223,108,226,226,224,1002,223,2,223,1006,224,509,101,1,223,223,8,226,677,224,102,2,223,223,1006,224,524,101,1,223,223,107,677,226,224,1002,223,2,223,1005,224,539,1001,223,1,223,8,226,226,224,102,2,223,223,1005,224,554,101,1,223,223,1108,677,226,224,102,2,223,223,1006,224,569,101,1,223,223,108,677,226,224,102,2,223,223,1006,224,584,1001,223,1,223,7,677,677,224,1002,223,2,223,1005,224,599,101,1,223,223,1007,226,226,224,102,2,223,223,1005,224,614,1001,223,1,223,1107,226,677,224,102,2,223,223,1006,224,629,101,1,223,223,1107,226,226,224,102,2,223,223,1005,224,644,1001,223,1,223,1108,677,677,224,1002,223,2,223,1005,224,659,101,1,223,223,107,677,677,224,1002,223,2,223,1006,224,674,1001,223,1,223,4,223,99,226]


def main():
    OpMachine(PROGRAM).run_program()
    #OpMachine(TEST1).run_program()


if __name__ == "__main__":
    main()
