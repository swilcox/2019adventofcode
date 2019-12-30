#include<iostream>
#include<unordered_map>
#include<vector>

enum State {stopped, running};

enum OpFunc {add=1, multiply=2, end=99};


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

    int get_param(int value)
    {
        return 0;
    }

    int add(int a, int b)
    {
        return a + b;
    }

    int multiply(int a, int b)
    {
        return a * b;
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
            int op_code = memory[pc];
            int pc_step = 1;
            switch(op_code)
            {
                case OpFunc::add :
                    pc_step += 3;
                    //std::cout << "add" << std::endl;
                    memory[memory[pc + 3]] = add(memory[memory[pc + 1]], memory[memory[pc + 2]]);
                    break;
                case OpFunc::multiply :
                    pc_step += 3;
                    //std::cout << "mult" << std::endl;
                    memory[memory[pc + 3]] = multiply(memory[memory[pc + 1]], memory[memory[pc + 2]]);
                    break;
                case OpFunc::end :
                    //std::cout << "end" << std::endl;
                    complete();
                    break;
                default :
                    std::cout << "uknown code: " << op_code << std::endl;
                    complete();
            }
            pc += pc_step;
        }
    }
};


int main ()
{
    //std::vector<int> program = {1,9,10,3,2,3,11,0,99,30,40,50};   
    std::vector<int> program = {1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,1,10,19,1,19,5,23,2,23,6,27,1,27,5,31,2,6,31,35,1,5,35,39,2,39,9,43,1,43,5,47,1,10,47,51,1,51,6,55,1,55,10,59,1,59,6,63,2,13,63,67,1,9,67,71,2,6,71,75,1,5,75,79,1,9,79,83,2,6,83,87,1,5,87,91,2,6,91,95,2,95,9,99,1,99,6,103,1,103,13,107,2,13,107,111,2,111,10,115,1,115,6,119,1,6,119,123,2,6,123,127,1,127,5,131,2,131,6,135,1,135,2,139,1,139,9,0,99,2,14,0,0};
    program[1] = 12;
    program[2] = 2;
    OpMachine o = OpMachine(program);
    o.execute();
    std::cout << "slot 0:" << o.memory[0] << std::endl;
    return 0;
}
