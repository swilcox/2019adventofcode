use std::collections::HashMap;
use std::convert::TryInto;
extern crate ncurses;
use ncurses::*;

type BigInt = i64;
const MAX_PARAMS: usize = 3;

#[derive(PartialEq, Eq, Debug, Copy, Clone)]
enum Tile {
    EMPTY, WALL, BLOCK, PADDLE, BALL
}

impl Tile {
    fn from_big_int(value: BigInt) -> Tile {
        match value {
            0 => Tile::EMPTY,
            1 => Tile::WALL,
            2 => Tile::BLOCK,
            3 => Tile::PADDLE,
            4 => Tile::BALL,
            _ => Tile::EMPTY,
        }
    }

    fn to_char(&self) -> char {
        match self {
            Tile::EMPTY => ' ',
            Tile::WALL => '\u{2588}',
            Tile::BLOCK => '\u{2591}',
            Tile::PADDLE => '\u{2594}',
            Tile::BALL => '\u{25CE}',
        }
    }
}

#[derive(PartialEq, Eq, Debug)]
enum InputMode {
    X, Y, T
}

struct GameScreen {
    screen: HashMap<(BigInt, BigInt), Tile>,
    pub ball_point: (BigInt, BigInt),
    pub paddle_point: (BigInt, BigInt),
    input_mode: InputMode,
    pub score: BigInt,
    max_x: BigInt,
    max_y: BigInt,
    next_x: BigInt,
    next_y: BigInt,
}


impl GameScreen {
    fn new() -> GameScreen {
        let locale_conf = LcCategory::all;
        setlocale(locale_conf, "en_US.UTF-8");
        initscr();  // ncurses initialize
        cbreak();
        noecho();
        clear();
        curs_set(ncurses::CURSOR_VISIBILITY::CURSOR_INVISIBLE);
        GameScreen {
            screen: HashMap::new(),
            ball_point: (0, 0),
            paddle_point: (0, 0),
            input_mode: InputMode::X,
            score: 0,
            max_x: 0,
            max_y: 0,
            next_x: 0,
            next_y: 0,
        }
    }

    fn set_screen(&mut self, point: &(BigInt, BigInt), tile: &Tile) {
        *self.screen.entry(*point).or_insert(Tile::EMPTY) = *tile;
    }

    fn take_input(&mut self, value: BigInt) {
        match self.input_mode {
            InputMode::X => {
                self.next_x = value;
                if value > self.max_x { self.max_x = value };
                self.input_mode = InputMode::Y;
            },
            InputMode::Y => {
                self.next_y = value;
                if value > self.max_y { self.max_y = value };
                self.input_mode = InputMode::T;
            },
            InputMode::T => {
                if self.next_x == -1 {
                    self.score = value;
                    mvaddstr(0, 0, &format!("SCORE: {}", value)[..]);
                } else {
                    let tile = Tile::from_big_int(value);
                    self.set_screen(&(self.next_x, self.next_y), &tile);
                    match tile {
                        Tile::BALL => self.ball_point = (self.next_x, self.next_y),
                        Tile::PADDLE => self.paddle_point = (self.next_x, self.next_y),
                        _ => ()
                    }
                    mvaddstr((self.next_y + 1).try_into().unwrap(), (self.next_x).try_into().unwrap(), &format!("{}", tile.to_char()));
                }
                self.input_mode = InputMode::X;
            }
        }
        refresh();
    }
}

// enums
#[derive(PartialEq, Eq, Debug)]
enum State {
    Running = 1,
    Stopped = 2
}

#[repr(i64)] #[derive(PartialEq, Eq, Debug)]
enum Op {
    Add = 1,
    Multiply = 2,
    GetInput = 3,
    SendOutput = 4,
    JumpIfTrue = 5,
    JumpIfFalse = 6,
    LessThan = 7,
    Equals = 8,
    AdjustBase = 9,
    Complete = 99,
    Unknown = 0
}

impl Op {
    fn from_big_int(value: BigInt) -> Op {
        match value {
            1 => Op::Add,
            2 => Op::Multiply,
            3 => Op::GetInput,
            4 => Op::SendOutput,
            5 => Op::JumpIfTrue,
            6 => Op::JumpIfFalse,
            7 => Op::LessThan,
            8 => Op::Equals,
            9 => Op::AdjustBase,
            99 => Op::Complete,
            _ => Op::Unknown 
        }
    }
}

enum ParamMode {
    Position = 0,
    Immediate = 1,
    Relative = 2
}

impl ParamMode {
    fn from_big_int(value: BigInt) -> ParamMode {
        match value {
            0 => ParamMode::Position,
            1 => ParamMode::Immediate,
            2 => ParamMode::Relative,
            _ => ParamMode::Position,
        }
    }
}


struct OpCode {
    pub func: Op,
    pub param_modes: [ParamMode; 3]
}


struct OpMachine {
    pub memory: HashMap<BigInt, BigInt>,
    pc: BigInt,
    state: State,
    pub debug: bool,
    relative_base: BigInt,
    pub game_screen: GameScreen
}

impl OpMachine {

    pub fn new(vec: Vec<BigInt>) -> OpMachine {
        let mut tmp_memory = HashMap::new();
        for i in 0..vec.len() {
            tmp_memory.entry((i as BigInt).try_into().unwrap()).or_insert(vec[i]);
        }
        OpMachine {
            memory: tmp_memory,
            pc: 0,
            state: State::Stopped,
            debug: false,
            relative_base: 0,
            game_screen: GameScreen::new() 
        }
    }

    fn get_input(&self) -> BigInt {
        if self.game_screen.ball_point.0 < self.game_screen.paddle_point.0 {
            -1
        }
        else if self.game_screen.ball_point.0 > self.game_screen.paddle_point.0 {
            1
        }
        else {
            0
        }
    }

    fn send_output(&mut self, a: BigInt) {
        self.game_screen.take_input(a);
        //println!("{}", a);
    }
    
    fn adjust_base(&mut self, a: BigInt) {
        self.relative_base += a;
    }

    fn complete(&mut self) {
        println!("complete!");
        self.state = State::Stopped;
    }

    fn decode_opcode(&self, value: BigInt) -> OpCode {
        let mut opcode = OpCode {func: Op::from_big_int(value % 100), param_modes: [ParamMode::Position, ParamMode::Position, ParamMode::Position]};
        for x in 0..MAX_PARAMS {
            opcode.param_modes[x] = ParamMode::from_big_int(value / BigInt::pow(10, (x + 2).try_into().unwrap()) % 10);
        }
        return opcode;
    }

    fn get_params(&mut self, opcode: &OpCode) -> (Vec<BigInt>, Vec<BigInt>) {
        let mut raw_params: Vec<BigInt> = vec![];
        let mut params: Vec<BigInt> = vec![];
        let mut write_params: Vec<BigInt> = vec![];
        for x in 0..3 {
            //println!("looping for x = {}", &x);
            raw_params.insert(x, *self.memory.entry(&self.pc + 1 + x as BigInt).or_insert(0));
            match opcode.param_modes[x] {
                ParamMode::Immediate => {
                    params.insert(x, raw_params[x]);
                    write_params.insert(x, raw_params[x]);
                },
                ParamMode::Position => {
                    params.insert(x, self.get_memory(raw_params[x]));
                    write_params.insert(x, raw_params[x]);
                },
                ParamMode::Relative => {
                    params.insert(x, self.get_memory(raw_params[x] + self.relative_base));
                    write_params.insert(x, raw_params[x] + self.relative_base);
                }
            }
        }
        return (params, write_params);
    }

    fn get_memory(&mut self, key: BigInt) -> BigInt {
        *self.memory.entry(key).or_insert(0)
    }

    fn set_memory(&mut self, key: BigInt, value: BigInt) {
        *self.memory.entry(key).or_insert(0) = value;
    }

    fn execute(&mut self) {
        self.state = State::Running;
        while self.state == State::Running {
            let opcode = self.decode_opcode(self.memory[&self.pc]);
            let (params, write_params) = self.get_params(&opcode);
            match opcode.func {
                Op::Add => {
                    self.set_memory(write_params[2], params[0] + params[1]);
                    self.pc += 4;
                },
                Op::Multiply => {
                    self.set_memory(write_params[2], params[0] * params[1]);
                    self.pc += 4;
                },
                Op::GetInput => {
                    self.set_memory(write_params[0], self.get_input());
                    self.pc += 2;
                },
                Op::SendOutput => {
                    self.send_output(params[0]);
                    self.pc += 2;
                },
                Op::JumpIfTrue => {
                    self.pc = if params[0] != 0 {params[1]} else {self.pc + 3};
                },
                Op::JumpIfFalse => {
                    self.pc = if params[0] == 0 {params[1]} else {self.pc + 3};
                },
                Op::LessThan => {
                    self.set_memory(write_params[2], if params[0] < params[1] {1} else {0});
                    self.pc += 4;
                },
                Op::Equals => {
                    self.set_memory(write_params[2], if params[0] == params[1] {1} else {0});
                    self.pc += 4;
                },
                Op::AdjustBase => {
                    self.adjust_base(params[0]);
                    self.pc += 2;
                },
                Op::Complete => self.complete(),
                _ => {
                    println!("Unknown function: {:?}", opcode.func);
                    self.complete();
                }
            }
        }
    }
}


fn main() {
    //let mut machine = OpMachine::new(vec![1101,2,3,0,4,0,99]);
    //let mut machine = OpMachine::new(vec![109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99]);
    //let mut machine = OpMachine::new(vec![1102,34463338,34463338,63,1007,63,34463338,63,1005,63,53,1102,1,3,1000,109,988,209,12,9,1000,209,6,209,3,203,0,1008,1000,1,63,1005,63,65,1008,1000,2,63,1005,63,902,1008,1000,0,63,1005,63,58,4,25,104,0,99,4,0,104,0,99,4,17,104,0,99,0,0,1102,1,37,1007,1102,24,1,1006,1102,26,1,1012,1101,528,0,1023,1102,256,1,1027,1102,466,1,1029,1102,1,629,1024,1101,0,620,1025,1101,0,0,1020,1102,1,30,1004,1101,39,0,1003,1102,36,1,1005,1102,531,1,1022,1102,32,1,1019,1101,0,27,1000,1101,0,28,1016,1101,1,0,1021,1101,23,0,1013,1102,1,25,1015,1102,1,21,1008,1102,1,22,1018,1102,1,34,1014,1102,475,1,1028,1101,33,0,1002,1101,0,35,1011,1102,1,20,1009,1102,38,1,1017,1101,259,0,1026,1101,31,0,1010,1101,0,29,1001,109,8,21102,40,1,10,1008,1018,40,63,1005,63,203,4,187,1105,1,207,1001,64,1,64,1002,64,2,64,109,7,21108,41,41,0,1005,1015,225,4,213,1106,0,229,1001,64,1,64,1002,64,2,64,109,1,1205,5,247,4,235,1001,64,1,64,1105,1,247,1002,64,2,64,109,20,2106,0,-9,1105,1,265,4,253,1001,64,1,64,1002,64,2,64,109,-38,1202,4,1,63,1008,63,33,63,1005,63,291,4,271,1001,64,1,64,1106,0,291,1002,64,2,64,109,6,2102,1,0,63,1008,63,29,63,1005,63,315,1001,64,1,64,1106,0,317,4,297,1002,64,2,64,109,10,21102,42,1,5,1008,1019,40,63,1005,63,341,1001,64,1,64,1105,1,343,4,323,1002,64,2,64,109,-13,2101,0,5,63,1008,63,24,63,1005,63,365,4,349,1105,1,369,1001,64,1,64,1002,64,2,64,109,7,1202,-6,1,63,1008,63,36,63,1005,63,389,1105,1,395,4,375,1001,64,1,64,1002,64,2,64,109,1,2107,31,-5,63,1005,63,411,1106,0,417,4,401,1001,64,1,64,1002,64,2,64,109,3,1206,8,431,4,423,1105,1,435,1001,64,1,64,1002,64,2,64,109,-8,2108,31,0,63,1005,63,451,1105,1,457,4,441,1001,64,1,64,1002,64,2,64,109,26,2106,0,-2,4,463,1001,64,1,64,1106,0,475,1002,64,2,64,109,-33,1207,6,38,63,1005,63,491,1106,0,497,4,481,1001,64,1,64,1002,64,2,64,109,3,2108,27,0,63,1005,63,515,4,503,1105,1,519,1001,64,1,64,1002,64,2,64,109,23,2105,1,0,1106,0,537,4,525,1001,64,1,64,1002,64,2,64,109,-30,1207,7,28,63,1005,63,559,4,543,1001,64,1,64,1106,0,559,1002,64,2,64,109,20,21101,43,0,0,1008,1013,43,63,1005,63,581,4,565,1105,1,585,1001,64,1,64,1002,64,2,64,109,-14,2102,1,1,63,1008,63,27,63,1005,63,611,4,591,1001,64,1,64,1105,1,611,1002,64,2,64,109,18,2105,1,7,4,617,1001,64,1,64,1106,0,629,1002,64,2,64,109,13,1206,-9,641,1105,1,647,4,635,1001,64,1,64,1002,64,2,64,109,-18,21107,44,45,-1,1005,1011,665,4,653,1105,1,669,1001,64,1,64,1002,64,2,64,109,-2,2107,28,-9,63,1005,63,687,4,675,1106,0,691,1001,64,1,64,1002,64,2,64,1205,10,701,1106,0,707,4,695,1001,64,1,64,1002,64,2,64,109,-6,1201,2,0,63,1008,63,21,63,1005,63,731,1001,64,1,64,1106,0,733,4,713,1002,64,2,64,109,-5,1208,7,23,63,1005,63,753,1001,64,1,64,1105,1,755,4,739,1002,64,2,64,109,16,1208,-8,37,63,1005,63,777,4,761,1001,64,1,64,1106,0,777,1002,64,2,64,109,3,21107,45,44,-8,1005,1010,797,1001,64,1,64,1105,1,799,4,783,1002,64,2,64,109,-8,1201,-5,0,63,1008,63,36,63,1005,63,821,4,805,1106,0,825,1001,64,1,64,1002,64,2,64,109,-9,2101,0,1,63,1008,63,31,63,1005,63,845,1105,1,851,4,831,1001,64,1,64,1002,64,2,64,109,6,21108,46,49,3,1005,1010,867,1106,0,873,4,857,1001,64,1,64,1002,64,2,64,109,5,21101,47,0,7,1008,1019,44,63,1005,63,897,1001,64,1,64,1106,0,899,4,879,4,64,99,21101,27,0,1,21102,913,1,0,1106,0,920,21201,1,30449,1,204,1,99,109,3,1207,-2,3,63,1005,63,962,21201,-2,-1,1,21101,940,0,0,1105,1,920,21202,1,1,-1,21201,-2,-3,1,21102,1,955,0,1106,0,920,22201,1,-1,-2,1105,1,966,22102,1,-2,-2,109,-3,2105,1,0]);
    let mut machine = OpMachine::new(vec![2,380,379,385,1008,2719,351522,381,1005,381,12,99,109,2720,1102,1,0,383,1101,0,0,382,20102,1,382,1,21002,383,1,2,21101,37,0,0,1105,1,578,4,382,4,383,204,1,1001,382,1,382,1007,382,40,381,1005,381,22,1001,383,1,383,1007,383,26,381,1005,381,18,1006,385,69,99,104,-1,104,0,4,386,3,384,1007,384,0,381,1005,381,94,107,0,384,381,1005,381,108,1106,0,161,107,1,392,381,1006,381,161,1102,1,-1,384,1105,1,119,1007,392,38,381,1006,381,161,1102,1,1,384,21002,392,1,1,21101,24,0,2,21101,0,0,3,21102,1,138,0,1105,1,549,1,392,384,392,20102,1,392,1,21101,0,24,2,21102,1,3,3,21101,0,161,0,1105,1,549,1101,0,0,384,20001,388,390,1,21001,389,0,2,21102,1,180,0,1106,0,578,1206,1,213,1208,1,2,381,1006,381,205,20001,388,390,1,21001,389,0,2,21101,205,0,0,1106,0,393,1002,390,-1,390,1101,1,0,384,20102,1,388,1,20001,389,391,2,21101,0,228,0,1105,1,578,1206,1,261,1208,1,2,381,1006,381,253,21002,388,1,1,20001,389,391,2,21102,253,1,0,1106,0,393,1002,391,-1,391,1101,0,1,384,1005,384,161,20001,388,390,1,20001,389,391,2,21102,1,279,0,1106,0,578,1206,1,316,1208,1,2,381,1006,381,304,20001,388,390,1,20001,389,391,2,21101,304,0,0,1106,0,393,1002,390,-1,390,1002,391,-1,391,1101,1,0,384,1005,384,161,21001,388,0,1,21002,389,1,2,21102,0,1,3,21102,338,1,0,1106,0,549,1,388,390,388,1,389,391,389,21001,388,0,1,20101,0,389,2,21101,4,0,3,21101,365,0,0,1106,0,549,1007,389,25,381,1005,381,75,104,-1,104,0,104,0,99,0,1,0,0,0,0,0,0,298,18,21,1,1,20,109,3,22101,0,-2,1,22101,0,-1,2,21102,1,0,3,21102,414,1,0,1106,0,549,21202,-2,1,1,22101,0,-1,2,21101,429,0,0,1106,0,601,2101,0,1,435,1,386,0,386,104,-1,104,0,4,386,1001,387,-1,387,1005,387,451,99,109,-3,2105,1,0,109,8,22202,-7,-6,-3,22201,-3,-5,-3,21202,-4,64,-2,2207,-3,-2,381,1005,381,492,21202,-2,-1,-1,22201,-3,-1,-3,2207,-3,-2,381,1006,381,481,21202,-4,8,-2,2207,-3,-2,381,1005,381,518,21202,-2,-1,-1,22201,-3,-1,-3,2207,-3,-2,381,1006,381,507,2207,-3,-4,381,1005,381,540,21202,-4,-1,-1,22201,-3,-1,-3,2207,-3,-4,381,1006,381,529,21201,-3,0,-7,109,-8,2106,0,0,109,4,1202,-2,40,566,201,-3,566,566,101,639,566,566,1201,-1,0,0,204,-3,204,-2,204,-1,109,-4,2105,1,0,109,3,1202,-1,40,593,201,-2,593,593,101,639,593,593,21001,0,0,-2,109,-3,2106,0,0,109,3,22102,26,-2,1,22201,1,-1,1,21102,1,523,2,21102,583,1,3,21102,1040,1,4,21101,0,630,0,1106,0,456,21201,1,1679,-2,109,-3,2105,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,2,2,0,2,0,0,2,0,2,2,2,0,2,0,2,0,2,2,0,0,0,2,2,2,0,2,0,0,0,1,1,0,2,2,0,2,0,2,0,0,2,0,0,0,2,2,2,0,0,0,2,0,2,0,0,0,2,2,0,0,0,2,0,0,0,2,0,2,0,1,1,0,2,0,2,0,2,0,2,2,2,0,0,2,0,0,0,0,0,2,0,0,0,2,0,2,0,2,2,0,2,2,0,2,2,2,2,0,0,1,1,0,0,0,0,0,0,2,2,2,2,0,0,2,0,0,0,0,0,0,2,0,2,2,0,0,2,2,2,2,2,2,2,0,2,2,2,2,0,1,1,0,2,0,0,2,0,0,0,0,0,2,0,0,0,0,0,2,2,0,0,2,2,2,0,0,0,2,2,2,0,2,0,0,0,2,0,0,0,1,1,0,0,2,0,0,0,0,0,0,0,2,2,2,2,0,0,0,0,2,0,0,2,0,2,0,0,0,2,2,2,2,0,2,2,2,2,0,0,1,1,0,2,2,0,0,0,0,2,2,0,2,0,0,0,2,2,2,0,2,0,0,0,2,0,0,0,0,0,2,2,0,2,2,2,0,0,0,0,1,1,0,0,0,0,0,2,0,2,0,0,2,2,2,2,0,2,2,0,0,2,0,0,2,2,0,2,2,2,0,0,2,2,0,0,0,2,0,0,1,1,0,0,0,2,0,2,0,2,0,2,0,0,2,2,2,2,0,0,0,2,0,2,0,2,2,2,0,0,2,2,2,0,0,0,2,0,0,0,1,1,0,0,2,0,0,0,2,2,2,0,2,0,0,0,2,2,0,0,0,0,0,0,0,2,2,0,2,0,2,0,2,2,2,2,2,0,0,0,1,1,0,0,2,2,2,2,0,2,0,0,0,2,2,2,2,0,2,0,2,2,0,2,0,2,0,0,2,0,0,0,2,2,0,0,0,2,0,0,1,1,0,2,0,0,2,2,0,0,0,2,0,0,2,0,0,0,2,0,2,0,0,0,0,0,0,0,2,2,0,2,0,2,2,2,0,2,0,0,1,1,0,2,0,2,0,2,0,2,0,2,0,2,0,0,0,2,0,2,2,0,2,2,2,2,2,0,0,2,2,0,2,2,2,0,2,0,0,0,1,1,0,0,2,2,0,0,0,2,0,0,0,0,2,0,0,2,2,0,2,2,2,0,0,2,2,2,2,2,2,0,2,0,2,2,0,0,2,0,1,1,0,2,2,2,0,2,0,0,0,2,2,2,2,0,0,2,2,2,0,0,0,2,2,2,0,2,0,2,0,2,0,2,2,0,0,0,2,0,1,1,0,0,0,0,0,2,2,2,0,0,2,0,2,2,0,0,0,2,0,0,2,2,2,2,0,0,2,0,0,0,2,0,2,0,0,2,0,0,1,1,0,0,0,2,0,2,2,0,2,2,2,2,0,0,0,0,0,2,2,0,2,0,0,2,0,2,2,2,2,2,0,2,2,2,0,0,0,0,1,1,0,2,2,2,0,0,0,0,0,0,2,0,2,0,2,0,2,2,0,0,0,0,0,2,0,2,0,0,0,2,0,0,0,0,0,2,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,94,63,98,14,55,98,64,9,39,55,40,3,77,79,41,40,52,25,26,46,83,8,72,65,35,58,50,6,78,78,40,77,45,49,98,98,47,68,93,85,87,19,71,89,59,81,2,62,12,53,10,21,45,23,11,95,37,33,57,32,82,63,2,97,43,93,91,66,32,55,20,53,14,7,50,62,41,32,12,63,85,86,2,83,63,7,1,91,7,67,6,57,74,63,21,14,50,92,96,13,73,52,27,39,1,17,82,87,58,45,30,31,29,85,70,59,95,71,75,74,12,51,62,83,38,53,15,13,45,6,71,35,98,36,88,9,77,37,4,5,52,59,53,83,77,7,8,97,56,97,14,40,82,93,1,81,37,38,49,89,70,9,60,1,12,79,5,22,7,86,41,42,79,24,51,9,1,8,72,3,53,71,76,49,55,57,95,87,68,33,6,28,7,50,81,75,57,72,95,67,12,29,19,77,52,69,72,38,16,21,4,91,15,1,11,3,70,46,54,95,24,93,13,40,23,14,93,58,59,87,54,79,84,38,7,97,66,40,66,42,1,66,45,82,64,65,95,19,43,16,20,36,94,39,95,25,2,75,96,55,7,63,30,8,86,92,68,54,75,81,49,75,29,77,3,85,23,72,19,44,8,5,40,48,65,23,67,76,43,87,72,52,46,61,22,42,86,86,23,46,17,58,67,86,83,36,93,95,53,69,14,58,54,69,25,2,51,2,51,35,24,57,92,75,82,23,61,19,94,15,34,4,29,10,24,81,2,88,48,5,84,72,64,28,11,57,3,30,71,58,88,7,63,54,15,66,48,4,5,78,35,37,24,89,89,68,90,38,85,81,9,73,36,28,5,89,42,14,5,76,72,2,38,97,49,46,80,86,17,71,3,27,2,4,28,91,31,9,83,89,63,47,53,38,30,35,21,66,27,51,3,68,70,17,30,57,83,80,66,32,92,52,84,80,29,4,79,20,86,41,17,31,39,67,25,39,97,41,53,63,78,26,85,57,76,82,25,48,81,92,66,49,29,95,89,56,65,87,62,71,63,17,46,98,4,86,39,26,12,14,51,73,38,46,27,98,66,1,19,65,56,98,25,27,98,78,31,49,47,42,32,13,3,60,1,11,14,42,69,11,76,86,95,17,19,92,77,8,19,85,81,69,22,18,48,68,27,2,24,3,10,25,6,27,3,28,64,23,3,7,94,96,84,27,18,9,60,90,60,37,72,58,93,72,36,21,85,62,11,64,34,5,3,6,9,31,85,25,81,34,87,86,88,35,69,8,7,18,31,24,8,79,71,45,51,41,83,13,81,39,34,3,44,17,27,71,7,13,36,89,70,77,79,61,31,62,51,15,78,72,37,32,82,62,10,32,84,79,64,19,89,56,51,52,87,44,31,18,75,96,26,79,58,51,2,54,84,42,17,60,37,34,66,33,4,20,93,43,8,90,43,92,10,90,43,9,34,18,39,79,32,1,36,69,90,29,49,56,63,60,36,46,38,79,6,57,1,97,65,78,47,82,78,25,33,3,14,22,89,37,29,81,68,82,41,31,16,91,13,73,68,4,79,6,86,91,87,69,85,46,41,85,6,36,87,93,18,74,55,84,3,9,88,19,30,46,47,33,79,94,67,75,36,8,66,14,52,10,92,91,93,5,63,52,42,11,11,48,45,66,51,30,5,39,39,49,66,38,57,19,54,90,44,60,31,11,21,31,56,35,76,35,67,79,70,18,11,50,6,97,59,5,72,50,54,75,41,19,54,12,47,56,42,80,70,69,69,34,97,57,43,6,60,52,39,43,52,34,4,41,86,47,2,80,41,15,60,50,24,31,24,83,34,19,40,55,42,25,93,39,85,29,98,95,67,55,62,4,26,19,61,93,14,11,45,50,40,81,61,57,17,44,3,75,7,74,20,70,2,63,29,52,48,47,29,90,8,36,39,77,62,97,11,43,31,13,25,5,66,2,6,20,49,89,48,67,79,66,74,48,79,45,5,35,31,33,50,95,23,56,33,40,75,24,81,84,56,35,96,11,95,29,7,55,17,37,18,20,32,41,4,71,74,67,7,46,1,86,70,9,13,40,17,12,64,31,65,60,40,4,6,42,57,89,15,40,53,88,14,2,35,5,16,44,62,6,53,83,76,87,26,82,1,7,25,66,65,53,60,52,57,64,9,16,88,2,93,33,62,82,27,17,29,17,40,68,83,4,28,83,62,6,91,45,69,30,8,39,55,78,97,46,13,2,7,80,74,19,68,20,2,5,35,55,62,25,32,55,3,76,92,70,62,36,73,14,55,12,4,25,46,25,17,41,63,19,74,70,86,4,80,50,97,44,65,51,44,7,78,59,351522]);
    machine.execute();
    endwin();   // ncurses exit
    println!("score: {:?}", machine.game_screen.score);
    println!("after execute");
}
