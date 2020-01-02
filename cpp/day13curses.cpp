#include<iostream>
#include<unordered_map>
#include<vector>
#include<array>
#include<string>
#include<curses.h>
#include<sstream>

using std::array;
using std::pair;
using std::vector;
using std::unordered_map;
using std::cout;
using std::cin;
using std::endl;
using std::string;
using std::stringstream;

const int MAX_PARAMS=3;

typedef vector<long> Vec;
typedef array<long, MAX_PARAMS> ParamArray;
typedef array<int, MAX_PARAMS> ParamModeArray;
typedef unordered_map<long, long> MemoryMap;
typedef unordered_map<int, wchar_t> BlockMap;
typedef ParamArray::size_type ArraySize;
typedef Vec::size_type VecSize;

enum State {stopped, running};
enum ParamMode {position=0, immediate=1, relative=2};
enum OpFunc {add=1, multiply=2, get_input=3, send_output=4, jump_if_true=5, jump_if_false=6, less_than=7, equals=8, adjust_base=9, end=99};


class GameScreen
{
    enum InputMode {X, Y, TILE};
    enum TileType {EMPTY, WALL, BLOCK, PADDLE, BALL};
    
    BlockMap block_map = {
        {EMPTY, ' '},
        {WALL, '|'},
        {BLOCK, '#'},
        {PADDLE, '-'},
        {BALL, '*'}
    };

    struct Point
    {
        int x;
        int y;
        bool operator==(const Point& p) const
        {
            return x == p.x && y == p.y;
        }
    };

    class PointHash {
        public:
        std::size_t operator() (const Point& p) const
        {
            return (((uint64_t)p.x)<<32) | ((uint64_t)p.y);
        }
    };

    public:
    GameScreen() {
        setlocale(LC_CTYPE, "C-UTF-8");
        initscr();
        cbreak();
        noecho();
        clear();
        curs_set(false);
    }    

    unordered_map<Point, int, PointHash> screen;
    int mode = InputMode::X;
    int next_x, next_y;
    int max_x = 0;
    int max_y = 0;
    long score = 0;
    Point ball_position;
    Point paddle_position;

    void processOutput(long value)
    {
        switch(mode)
        {
            case InputMode::X :
                next_x = (int) value;
                mode = InputMode::Y;
                if (next_x > max_x) max_x = next_x;
                break;
            case InputMode::Y :
                next_y = (int) value;
                mode = InputMode::TILE;
                if (next_y > max_y) max_y = next_y;
                break;
            case InputMode::TILE :
                if (next_x == -1){
                    score = value;
                    stringstream score_string;
                    score_string << "SCORE: " << value;
                    mvaddstr(0, 0, score_string.str().c_str());
                } 
                else {
                    screen[Point{next_x, next_y}] = (int) value;
                    mvaddch(next_y + 1, next_x, block_map[value]);
                    refresh();
                    if ((int) value == TileType::BALL) ball_position = Point{next_x, next_y};
                    else if ((int) value == TileType::PADDLE) paddle_position = Point{next_x, next_y};                     
                }
                mode = InputMode::X;
                break;
        }
    }

    void displayScreen()
    {
        cout << "SCORE: " << score << endl;
        for (int y=0;y<=max_y;y++)
        {
            for (int x=0;x<=max_x;x++)
            {
                char display_chr = screen.count(Point{x,y}) ? block_map[screen[Point{x,y}]] : block_map[0];
                cout << display_chr;
            }
            cout << endl;
        }
    }
};


struct OpCode
{
    int func; // an OpFunc
    ParamModeArray param_modes;
};


class OpMachine
{
    public:
    
    int pc = 0;
    int state = stopped;
    int relative_base = 0;
    bool debug = false;
    MemoryMap memory;
    GameScreen game_screen;

    OpMachine(const Vec &integers) 
    {
        for (VecSize x=0;x < integers.size();x++)
        {
            memory[x] = integers[x];
        }
    }

    long getMemory(long address)
    {
        return memory.count(address) ? memory[address] : 0;
    }

    void setMemory(long address, long value)
    {
        memory[address] = value;
    }

    OpCode decode_opcode(long value)
    {
        OpCode opcode;
        opcode.func = value % 100;
        long digits = 10;
        for (int x=0;x<MAX_PARAMS;x++) {
            digits *= 10;
            opcode.param_modes[x] = (value / digits) % 10;
        }        
        return opcode;
    }

    long get_value(long value, int mode)
    {
        switch(mode) 
        {
            case ParamMode::immediate : return value;
            case ParamMode::position  : return getMemory(value);
            case ParamMode::relative  : return getMemory(value + relative_base);
        }
        return value;
    }

    long add(long a, long b)
    {
        return a + b;
    }

    long multiply(long a, long b)
    {
        return a * b;
    }

    long get_input()
    {
        //long value;
        // cout << "Enter value: ";
        // cin >> value;
        if (game_screen.paddle_position.x - game_screen.ball_position.x < 0) return 1;
        else if (game_screen.paddle_position.x - game_screen.ball_position.x > 0) return -1;
        return 0;
    }

    void send_output(long value)
    {
        game_screen.processOutput(value);
        //cout << "output: " << value << endl;
    }

    bool jit(long a)
    {
        return (a != 0) ? true : false;
    }

    bool jif(long a)
    {
        return (a != 0) ? false : true;
    }

    bool eq(long a, long b)
    {
        return (a == b);
    }

    bool lt(long a, long b)
    {
        return (a < b);
    }

    void adjust_base(long a)
    {
        relative_base += a;
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
            ParamArray raw_params;
            ParamArray params;
            ParamArray write_params;
            for (ArraySize x = 0;x < MAX_PARAMS;x++)
            {
                raw_params[x] = getMemory(pc + x + 1);
                params[x] = get_value(raw_params[x], op_code.param_modes[x]);
                write_params[x] = op_code.param_modes[x] == ParamMode::relative ? (raw_params[x] + relative_base) : raw_params[x];
            }
  
            switch(op_code.func)
            {
                case OpFunc::add :
                    memory[write_params[2]] = add(params[0], params[1]);
                    pc += 4;
                    break;
                case OpFunc::multiply :
                    memory[write_params[2]] = multiply(params[0], params[1]);
                    pc += 4;
                    break;
                case OpFunc::get_input :
                    memory[write_params[0]] = get_input();
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
                    memory[write_params[2]] = eq(params[0], params[1]);
                    pc += 4;
                    break;
                case OpFunc::less_than :
                    memory[write_params[2]] = lt(params[0], params[1]);
                    pc += 4;
                    break;
                case OpFunc::adjust_base :
                    adjust_base(params[0]);
                    pc += 2;
                    break;
                case OpFunc::end :
                    //cout << "end" << endl;
                    complete();
                    break;
                default :
                    cout << "unknown code: " << op_code.func << endl;
                    complete();
            }
        }
    }
};


int main ()
{
    Vec program = {1,380,379,385,1008,2719,351522,381,1005,381,12,99,109,2720,1102,1,0,383,1101,0,0,382,20102,1,382,1,21002,383,1,2,21101,37,0,0,1105,1,578,4,382,4,383,204,1,1001,382,1,382,1007,382,40,381,1005,381,22,1001,383,1,383,1007,383,26,381,1005,381,18,1006,385,69,99,104,-1,104,0,4,386,3,384,1007,384,0,381,1005,381,94,107,0,384,381,1005,381,108,1106,0,161,107,1,392,381,1006,381,161,1102,1,-1,384,1105,1,119,1007,392,38,381,1006,381,161,1102,1,1,384,21002,392,1,1,21101,24,0,2,21101,0,0,3,21102,1,138,0,1105,1,549,1,392,384,392,20102,1,392,1,21101,0,24,2,21102,1,3,3,21101,0,161,0,1105,1,549,1101,0,0,384,20001,388,390,1,21001,389,0,2,21102,1,180,0,1106,0,578,1206,1,213,1208,1,2,381,1006,381,205,20001,388,390,1,21001,389,0,2,21101,205,0,0,1106,0,393,1002,390,-1,390,1101,1,0,384,20102,1,388,1,20001,389,391,2,21101,0,228,0,1105,1,578,1206,1,261,1208,1,2,381,1006,381,253,21002,388,1,1,20001,389,391,2,21102,253,1,0,1106,0,393,1002,391,-1,391,1101,0,1,384,1005,384,161,20001,388,390,1,20001,389,391,2,21102,1,279,0,1106,0,578,1206,1,316,1208,1,2,381,1006,381,304,20001,388,390,1,20001,389,391,2,21101,304,0,0,1106,0,393,1002,390,-1,390,1002,391,-1,391,1101,1,0,384,1005,384,161,21001,388,0,1,21002,389,1,2,21102,0,1,3,21102,338,1,0,1106,0,549,1,388,390,388,1,389,391,389,21001,388,0,1,20101,0,389,2,21101,4,0,3,21101,365,0,0,1106,0,549,1007,389,25,381,1005,381,75,104,-1,104,0,104,0,99,0,1,0,0,0,0,0,0,298,18,21,1,1,20,109,3,22101,0,-2,1,22101,0,-1,2,21102,1,0,3,21102,414,1,0,1106,0,549,21202,-2,1,1,22101,0,-1,2,21101,429,0,0,1106,0,601,2101,0,1,435,1,386,0,386,104,-1,104,0,4,386,1001,387,-1,387,1005,387,451,99,109,-3,2105,1,0,109,8,22202,-7,-6,-3,22201,-3,-5,-3,21202,-4,64,-2,2207,-3,-2,381,1005,381,492,21202,-2,-1,-1,22201,-3,-1,-3,2207,-3,-2,381,1006,381,481,21202,-4,8,-2,2207,-3,-2,381,1005,381,518,21202,-2,-1,-1,22201,-3,-1,-3,2207,-3,-2,381,1006,381,507,2207,-3,-4,381,1005,381,540,21202,-4,-1,-1,22201,-3,-1,-3,2207,-3,-4,381,1006,381,529,21201,-3,0,-7,109,-8,2106,0,0,109,4,1202,-2,40,566,201,-3,566,566,101,639,566,566,1201,-1,0,0,204,-3,204,-2,204,-1,109,-4,2105,1,0,109,3,1202,-1,40,593,201,-2,593,593,101,639,593,593,21001,0,0,-2,109,-3,2106,0,0,109,3,22102,26,-2,1,22201,1,-1,1,21102,1,523,2,21102,583,1,3,21102,1040,1,4,21101,0,630,0,1106,0,456,21201,1,1679,-2,109,-3,2105,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,2,2,0,2,0,0,2,0,2,2,2,0,2,0,2,0,2,2,0,0,0,2,2,2,0,2,0,0,0,1,1,0,2,2,0,2,0,2,0,0,2,0,0,0,2,2,2,0,0,0,2,0,2,0,0,0,2,2,0,0,0,2,0,0,0,2,0,2,0,1,1,0,2,0,2,0,2,0,2,2,2,0,0,2,0,0,0,0,0,2,0,0,0,2,0,2,0,2,2,0,2,2,0,2,2,2,2,0,0,1,1,0,0,0,0,0,0,2,2,2,2,0,0,2,0,0,0,0,0,0,2,0,2,2,0,0,2,2,2,2,2,2,2,0,2,2,2,2,0,1,1,0,2,0,0,2,0,0,0,0,0,2,0,0,0,0,0,2,2,0,0,2,2,2,0,0,0,2,2,2,0,2,0,0,0,2,0,0,0,1,1,0,0,2,0,0,0,0,0,0,0,2,2,2,2,0,0,0,0,2,0,0,2,0,2,0,0,0,2,2,2,2,0,2,2,2,2,0,0,1,1,0,2,2,0,0,0,0,2,2,0,2,0,0,0,2,2,2,0,2,0,0,0,2,0,0,0,0,0,2,2,0,2,2,2,0,0,0,0,1,1,0,0,0,0,0,2,0,2,0,0,2,2,2,2,0,2,2,0,0,2,0,0,2,2,0,2,2,2,0,0,2,2,0,0,0,2,0,0,1,1,0,0,0,2,0,2,0,2,0,2,0,0,2,2,2,2,0,0,0,2,0,2,0,2,2,2,0,0,2,2,2,0,0,0,2,0,0,0,1,1,0,0,2,0,0,0,2,2,2,0,2,0,0,0,2,2,0,0,0,0,0,0,0,2,2,0,2,0,2,0,2,2,2,2,2,0,0,0,1,1,0,0,2,2,2,2,0,2,0,0,0,2,2,2,2,0,2,0,2,2,0,2,0,2,0,0,2,0,0,0,2,2,0,0,0,2,0,0,1,1,0,2,0,0,2,2,0,0,0,2,0,0,2,0,0,0,2,0,2,0,0,0,0,0,0,0,2,2,0,2,0,2,2,2,0,2,0,0,1,1,0,2,0,2,0,2,0,2,0,2,0,2,0,0,0,2,0,2,2,0,2,2,2,2,2,0,0,2,2,0,2,2,2,0,2,0,0,0,1,1,0,0,2,2,0,0,0,2,0,0,0,0,2,0,0,2,2,0,2,2,2,0,0,2,2,2,2,2,2,0,2,0,2,2,0,0,2,0,1,1,0,2,2,2,0,2,0,0,0,2,2,2,2,0,0,2,2,2,0,0,0,2,2,2,0,2,0,2,0,2,0,2,2,0,0,0,2,0,1,1,0,0,0,0,0,2,2,2,0,0,2,0,2,2,0,0,0,2,0,0,2,2,2,2,0,0,2,0,0,0,2,0,2,0,0,2,0,0,1,1,0,0,0,2,0,2,2,0,2,2,2,2,0,0,0,0,0,2,2,0,2,0,0,2,0,2,2,2,2,2,0,2,2,2,0,0,0,0,1,1,0,2,2,2,0,0,0,0,0,0,2,0,2,0,2,0,2,2,0,0,0,0,0,2,0,2,0,0,0,2,0,0,0,0,0,2,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,94,63,98,14,55,98,64,9,39,55,40,3,77,79,41,40,52,25,26,46,83,8,72,65,35,58,50,6,78,78,40,77,45,49,98,98,47,68,93,85,87,19,71,89,59,81,2,62,12,53,10,21,45,23,11,95,37,33,57,32,82,63,2,97,43,93,91,66,32,55,20,53,14,7,50,62,41,32,12,63,85,86,2,83,63,7,1,91,7,67,6,57,74,63,21,14,50,92,96,13,73,52,27,39,1,17,82,87,58,45,30,31,29,85,70,59,95,71,75,74,12,51,62,83,38,53,15,13,45,6,71,35,98,36,88,9,77,37,4,5,52,59,53,83,77,7,8,97,56,97,14,40,82,93,1,81,37,38,49,89,70,9,60,1,12,79,5,22,7,86,41,42,79,24,51,9,1,8,72,3,53,71,76,49,55,57,95,87,68,33,6,28,7,50,81,75,57,72,95,67,12,29,19,77,52,69,72,38,16,21,4,91,15,1,11,3,70,46,54,95,24,93,13,40,23,14,93,58,59,87,54,79,84,38,7,97,66,40,66,42,1,66,45,82,64,65,95,19,43,16,20,36,94,39,95,25,2,75,96,55,7,63,30,8,86,92,68,54,75,81,49,75,29,77,3,85,23,72,19,44,8,5,40,48,65,23,67,76,43,87,72,52,46,61,22,42,86,86,23,46,17,58,67,86,83,36,93,95,53,69,14,58,54,69,25,2,51,2,51,35,24,57,92,75,82,23,61,19,94,15,34,4,29,10,24,81,2,88,48,5,84,72,64,28,11,57,3,30,71,58,88,7,63,54,15,66,48,4,5,78,35,37,24,89,89,68,90,38,85,81,9,73,36,28,5,89,42,14,5,76,72,2,38,97,49,46,80,86,17,71,3,27,2,4,28,91,31,9,83,89,63,47,53,38,30,35,21,66,27,51,3,68,70,17,30,57,83,80,66,32,92,52,84,80,29,4,79,20,86,41,17,31,39,67,25,39,97,41,53,63,78,26,85,57,76,82,25,48,81,92,66,49,29,95,89,56,65,87,62,71,63,17,46,98,4,86,39,26,12,14,51,73,38,46,27,98,66,1,19,65,56,98,25,27,98,78,31,49,47,42,32,13,3,60,1,11,14,42,69,11,76,86,95,17,19,92,77,8,19,85,81,69,22,18,48,68,27,2,24,3,10,25,6,27,3,28,64,23,3,7,94,96,84,27,18,9,60,90,60,37,72,58,93,72,36,21,85,62,11,64,34,5,3,6,9,31,85,25,81,34,87,86,88,35,69,8,7,18,31,24,8,79,71,45,51,41,83,13,81,39,34,3,44,17,27,71,7,13,36,89,70,77,79,61,31,62,51,15,78,72,37,32,82,62,10,32,84,79,64,19,89,56,51,52,87,44,31,18,75,96,26,79,58,51,2,54,84,42,17,60,37,34,66,33,4,20,93,43,8,90,43,92,10,90,43,9,34,18,39,79,32,1,36,69,90,29,49,56,63,60,36,46,38,79,6,57,1,97,65,78,47,82,78,25,33,3,14,22,89,37,29,81,68,82,41,31,16,91,13,73,68,4,79,6,86,91,87,69,85,46,41,85,6,36,87,93,18,74,55,84,3,9,88,19,30,46,47,33,79,94,67,75,36,8,66,14,52,10,92,91,93,5,63,52,42,11,11,48,45,66,51,30,5,39,39,49,66,38,57,19,54,90,44,60,31,11,21,31,56,35,76,35,67,79,70,18,11,50,6,97,59,5,72,50,54,75,41,19,54,12,47,56,42,80,70,69,69,34,97,57,43,6,60,52,39,43,52,34,4,41,86,47,2,80,41,15,60,50,24,31,24,83,34,19,40,55,42,25,93,39,85,29,98,95,67,55,62,4,26,19,61,93,14,11,45,50,40,81,61,57,17,44,3,75,7,74,20,70,2,63,29,52,48,47,29,90,8,36,39,77,62,97,11,43,31,13,25,5,66,2,6,20,49,89,48,67,79,66,74,48,79,45,5,35,31,33,50,95,23,56,33,40,75,24,81,84,56,35,96,11,95,29,7,55,17,37,18,20,32,41,4,71,74,67,7,46,1,86,70,9,13,40,17,12,64,31,65,60,40,4,6,42,57,89,15,40,53,88,14,2,35,5,16,44,62,6,53,83,76,87,26,82,1,7,25,66,65,53,60,52,57,64,9,16,88,2,93,33,62,82,27,17,29,17,40,68,83,4,28,83,62,6,91,45,69,30,8,39,55,78,97,46,13,2,7,80,74,19,68,20,2,5,35,55,62,25,32,55,3,76,92,70,62,36,73,14,55,12,4,25,46,25,17,41,63,19,74,70,86,4,80,50,97,44,65,51,44,7,78,59,351522};
    program[0] = 2; // put the quarters in ;-)
    OpMachine o = OpMachine(program);
    o.execute();
    o.game_screen.displayScreen();
    endwin();
    return 0;
}
