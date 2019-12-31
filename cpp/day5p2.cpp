#include<iostream>
#include<unordered_map>
#include<vector>
#include<array>

enum State {stopped, running};
enum ParamMode {position, immediate};
enum OpFunc {add=1, multiply=2, get_input=3, send_output=4, jump_if_true=5, jump_if_false=6, less_than=7, equals=8, end=99};
const int MAX_PARAMS=3;

struct OpCode
{
    int func; // an OpFunc
    std::array<int, MAX_PARAMS> param_modes;
};

class OpMachine
{
    public:
    
    int pc = 0;
    int state = stopped;
    std::unordered_map<int, int> memory;

    OpMachine(const std::vector<int> &integers) 
    {
        for (int x=0;x < integers.size();x++)
        {
            memory[x] = integers[x];
        }
    }

    OpCode decode_opcode(int value)
    {
        OpCode opcode;
        opcode.func = value % 100;
        for (int x=0;x<MAX_PARAMS;x++) {
            opcode.param_modes[x] = (value / (100*(x+1))) % 10;
        }        
        return opcode;
    }

    int get_value(int value, int mode)
    {
        switch(mode) 
        {
            case ParamMode::immediate : return value;
            case ParamMode::position: return memory[value];
        }
        return value;
    }

    int add(int a, int b)
    {
        return a + b;
    }

    int multiply(int a, int b)
    {
        return a * b;
    }

    int get_input()
    {
        int value;
        std::cout << "Enter value: ";
        std::cin >> value;
        return value;
    }

    void send_output(int value)
    {
        std::cout << "output: " << value << std::endl;
    }

    bool jit(int a)
    {
        return (a != 0) ? true : false;
    }

    bool jif(int a)
    {
        return (a != 0) ? false : true;
    }

    bool eq(int a, int b)
    {
        return (a == b);
    }

    bool lt(int a, int b)
    {
        return (a < b);
    }

    void complete()
    {
        state = stopped;
    }

    void execute()
    {
        state = running;
        while (state == running)
        {
            OpCode op_code = decode_opcode(memory[pc]);
            std::array<int, MAX_PARAMS> raw_params;
            std::array<int, MAX_PARAMS> params;
            for (int x = 0;x < MAX_PARAMS;x++)
            {
                raw_params[x] = memory[pc + x + 1];
                params[x] = get_value(memory[pc + x + 1], op_code.param_modes[x]);
            }
  
            switch(op_code.func)
            {
                case OpFunc::add :
                    memory[raw_params[2]] = add(params[0], params[1]);
                    pc += 4;
                    break;
                case OpFunc::multiply :
                    memory[raw_params[2]] = multiply(params[0], params[1]);
                    pc += 4;
                    break;
                case OpFunc::get_input :
                    memory[raw_params[0]] = get_input();
                    pc += 2;
                    break;
                case OpFunc::send_output :
                    send_output(params[0]);
                    pc += 2;
                    break;
                case OpFunc::jump_if_true :
                    pc = jit(params[0]) ? params[1] : pc + 3;
                    break;
                case OpFunc::jump_if_false :
                    pc = jif(params[0]) ? params[1] : pc + 3;
                    break;
                case OpFunc::equals :
                    memory[raw_params[2]] = eq(params[0], params[1]);
                    pc += 4;
                    break;
                case OpFunc::less_than :
                    memory[raw_params[2]] = lt(params[0], params[1]);
                    pc += 4;
                    break;
                case OpFunc::end :
                    //std::cout << "end" << std::endl;
                    complete();
                    break;
                default :
                    std::cout << "unknown code: " << op_code.func << std::endl;
                    complete();
            }
        }
    }
};


int main ()
{
    std::vector<int> program = {3,225,1,225,6,6,1100,1,238,225,104,0,2,171,209,224,1001,224,-1040,224,4,224,102,8,223,223,1001,224,4,224,1,223,224,223,102,65,102,224,101,-3575,224,224,4,224,102,8,223,223,101,2,224,224,1,223,224,223,1102,9,82,224,1001,224,-738,224,4,224,102,8,223,223,1001,224,2,224,1,223,224,223,1101,52,13,224,1001,224,-65,224,4,224,1002,223,8,223,1001,224,6,224,1,223,224,223,1102,82,55,225,1001,213,67,224,1001,224,-126,224,4,224,102,8,223,223,1001,224,7,224,1,223,224,223,1,217,202,224,1001,224,-68,224,4,224,1002,223,8,223,1001,224,1,224,1,224,223,223,1002,176,17,224,101,-595,224,224,4,224,102,8,223,223,101,2,224,224,1,224,223,223,1102,20,92,225,1102,80,35,225,101,21,205,224,1001,224,-84,224,4,224,1002,223,8,223,1001,224,1,224,1,224,223,223,1101,91,45,225,1102,63,5,225,1101,52,58,225,1102,59,63,225,1101,23,14,225,4,223,99,0,0,0,677,0,0,0,0,0,0,0,0,0,0,0,1105,0,99999,1105,227,247,1105,1,99999,1005,227,99999,1005,0,256,1105,1,99999,1106,227,99999,1106,0,265,1105,1,99999,1006,0,99999,1006,227,274,1105,1,99999,1105,1,280,1105,1,99999,1,225,225,225,1101,294,0,0,105,1,0,1105,1,99999,1106,0,300,1105,1,99999,1,225,225,225,1101,314,0,0,106,0,0,1105,1,99999,1008,677,677,224,1002,223,2,223,1006,224,329,101,1,223,223,1108,226,677,224,1002,223,2,223,1006,224,344,101,1,223,223,7,677,226,224,102,2,223,223,1006,224,359,1001,223,1,223,8,677,226,224,102,2,223,223,1005,224,374,1001,223,1,223,1107,677,226,224,102,2,223,223,1006,224,389,1001,223,1,223,1008,226,226,224,1002,223,2,223,1005,224,404,1001,223,1,223,7,226,677,224,102,2,223,223,1005,224,419,1001,223,1,223,1007,677,677,224,102,2,223,223,1006,224,434,1001,223,1,223,107,226,226,224,1002,223,2,223,1005,224,449,1001,223,1,223,1008,677,226,224,102,2,223,223,1006,224,464,1001,223,1,223,1007,677,226,224,1002,223,2,223,1005,224,479,1001,223,1,223,108,677,677,224,1002,223,2,223,1006,224,494,1001,223,1,223,108,226,226,224,1002,223,2,223,1006,224,509,101,1,223,223,8,226,677,224,102,2,223,223,1006,224,524,101,1,223,223,107,677,226,224,1002,223,2,223,1005,224,539,1001,223,1,223,8,226,226,224,102,2,223,223,1005,224,554,101,1,223,223,1108,677,226,224,102,2,223,223,1006,224,569,101,1,223,223,108,677,226,224,102,2,223,223,1006,224,584,1001,223,1,223,7,677,677,224,1002,223,2,223,1005,224,599,101,1,223,223,1007,226,226,224,102,2,223,223,1005,224,614,1001,223,1,223,1107,226,677,224,102,2,223,223,1006,224,629,101,1,223,223,1107,226,226,224,102,2,223,223,1005,224,644,1001,223,1,223,1108,677,677,224,1002,223,2,223,1005,224,659,101,1,223,223,107,677,677,224,1002,223,2,223,1006,224,674,1001,223,1,223,4,223,99,226};
    OpMachine o = OpMachine(program);
    o.execute();
    //std::cout << "slot 0:" << o.memory[0] << std::endl;
    return 0;
}
