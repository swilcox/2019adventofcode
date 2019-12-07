# 2019 advent of code day 2 part 1
import sys

def add(machine: list, *params):
    machine[params[2]] = machine[params[0]] + machine[params[1]]

def multiply(machine: list, *params):
    machine[params[2]] = machine[params[0]] * machine[params[1]]

def complete(machine: list, *params):
    print('result -->', machine[0])

OPS = {
    1: add,
    2: multiply,
    99: complete,
}

def execute(machine: list, pc: int):
    opcode = 0
    while opcode != 99:
        opcode, *params = machine[pc : pc+4]
        OPS[opcode](machine, *params)
        pc += 4


TEST1 = [1,0,0,0,99]
TEST2 = [2,3,0,3,99]
TEST3 = [2,4,4,5,99,0]
TEST4 = [1,1,1,4,99,5,6,0,99]
PROGRAM = [1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,1,10,19,1,19,5,23,2,23,6,27,1,27,5,31,2,6,31,35,1,5,35,39,2,39,9,43,1,43,5,47,1,10,47,51,1,51,6,55,1,55,10,59,1,59,6,63,2,13,63,67,1,9,67,71,2,6,71,75,1,5,75,79,1,9,79,83,2,6,83,87,1,5,87,91,2,6,91,95,2,95,9,99,1,99,6,103,1,103,13,107,2,13,107,111,2,111,10,115,1,115,6,119,1,6,119,123,2,6,123,127,1,127,5,131,2,131,6,135,1,135,2,139,1,139,9,0,99,2,14,0,0]

PROGRAM[1] = 12
PROGRAM[2] = 2
execute(PROGRAM, 0)
