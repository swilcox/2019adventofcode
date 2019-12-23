# 2019 advent of code day 7 part 2
import sys
from enum import IntEnum
from dataclasses import dataclass
import typing
from itertools import permutations


DEBUG = True


class PMODE(IntEnum):
    POSITION = 0
    IMMEDIATE = 1


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
        self.machine = program
        self.pc = 0
        self.input_buffer = []
        self.output_buffer = []
        self.state = STATE.init

    def _value(self, param, mode):
        return self.machine[param] if mode == PMODE.POSITION else param

    def add(self, a: int, b: int) -> int:
        return a + b

    def multiply(self, a: int, b: int) -> int:
        return a * b

    def get_input(self, *args) -> int:
        if self.input_buffer:
            return self.input_buffer.pop(0)
        else:
            self.state = STATE.waiting_on_input
        return None

    def send_output(self, a: int):
        self.output_buffer.append(a)
        #self.input_buffer.append(a)
        #print("output -->", a)

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
                params[-1] = raw_params[-1]
            passed_params = params[:-1] if op.stores_result else params 
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
        99: Op(complete, 0, False, False),
    }


TEST1 = [3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0]
TEST2 = [3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0]
TEST3 = [3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0]
PROGRAM = [3,8,1001,8,10,8,105,1,0,0,21,46,59,84,93,102,183,264,345,426,99999,3,9,1002,9,4,9,1001,9,3,9,102,2,9,9,1001,9,5,9,102,3,9,9,4,9,99,3,9,1002,9,3,9,101,4,9,9,4,9,99,3,9,1002,9,4,9,1001,9,4,9,102,2,9,9,1001,9,2,9,1002,9,3,9,4,9,99,3,9,1001,9,5,9,4,9,99,3,9,1002,9,4,9,4,9,99,3,9,101,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,1,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,99,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,101,2,9,9,4,9,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,1,9,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,99,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,99,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,99]
TEST1 = [3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5]
TEST2 = [3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10]


def main():
    #OpMachine(PROGRAM).run_program()
    max_value = 0
    max_perm = None
    for p in permutations([9,8,7,6,5]):
        carry_over = 0
        amps = []
        for x in p:
            new_amp = OpMachine(PROGRAM[:])
            new_amp.input_buffer = [x]
            amps.append(new_amp)
        amps[0].input_buffer.append(0)
        # amps init'd, so run now
        for a in amps:
            a.run_program()
        while STATE.waiting_on_input in [a.state for a in amps]:
            for amp_num, amp in enumerate(amps):
                if amp.state == STATE.waiting_on_input:
                    feeding_amp_num = amp_num - 1 if amp_num > 0 else len(amps) - 1
                    if amps[feeding_amp_num].output_buffer:
                        amp.input_buffer.append(amps[feeding_amp_num].output_buffer.pop(0))
                        amp.resume()
        opm = amps[-1]
        if opm.output_buffer[-1] > max_value:
            max_value = opm.output_buffer[-1]
            max_perm = p
    print(max_value, max_perm)


if __name__ == "__main__":
    main()
