"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.reg[7] = 0xF4

    def load(self):
        """Load a program into memory."""

        program = []
        if len(sys.argv) == 2:
            try:
                with open(sys.argv[1]) as f:
                    for line in f:
                        line = line.partition('#')[0]
                        line = line.rstrip()

                        if line != '':
                            program.append(int(line, 2))

            except FileNotFoundError as e:
                print('\n', e, '\n')

            for address, instruction in enumerate(program):
                self.ram[address] = instruction
                address += 1
        else:
            return print('\nPlease include a file to load!\n')

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        def add():
            self.reg[reg_a] += self.reg[reg_b]

        def sub():
            self.reg[reg_a] -= self.reg[reg_b]

        def mul():
            self.reg[reg_a] *= self.reg[reg_b]

        def div():
            self.reg[reg_a] /= self.reg[reg_b]

        operations = {
            0b10100000: add,
            0b10100001: sub,
            0b10100010: mul,
            0b10100011: div,
        }

        try:
            operations[op]()
        except KeyError:
            print('\nUnsupported ALU operation\n')

    def ldi(self):
        self.reg[self.ram_read(self.pc+1)] = self.ram_read(self.pc+2)

    def prn(self):
        print(self.reg[self.ram_read(self.pc+1)])

    def nop(self):
        pass

    def push(self, address=None):
        if address is None:
            self.reg[7] -= 1
            self.ram_write(self.reg[7], self.reg[self.ram_read(self.pc+1)])
        else:
            self.reg[7] -= 1
            self.ram_write(self.reg[7], address)

    def pop(self, ret=False):
        if self.reg[7] == 0xF4:
            return print('Stack is Empty!')
        if ret:
            pc = self.ram_read(self.reg[7])
            self.reg[7] += 1
            return pc
        self.reg[self.ram_read(self.pc+1)] = self.ram_read(self.reg[7])
        self.reg[7] += 1

    def call(self):
        self.push(self.pc+2)
        self.pc = self.reg[self.ram_read(self.pc+1)]

    def ret(self):
        self.pc = self.pop(True)

    def checkAlu(self, instruction):
        is_alu = (instruction & 0b00100000) >> 5

        if is_alu == 1:
            val1 = self.ram_read(self.pc+1)
            val2 = self.ram_read(self.pc+2)
            self.alu(instruction, val1, val2)
            return 0b00000000

        return instruction

    def pc_inc_cal(self, instruction):
        if (instruction & 0b00010000) >> 4 != 1:
            return (instruction >> 6) + 1
        return 0

    def run(self):
        """Run the CPU."""

        commands = {
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b00000000: self.nop,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret,
        }

        while self.ram_read(self.pc) != 0b00000001 and self.pc < len(self.ram) - 1:
            instruction = self.ram_read(self.pc)
            pc_increase = self.pc_inc_cal(instruction)
            instruction = self.checkAlu(instruction)

            try:
                commands[instruction]()
                self.pc += pc_increase

            except KeyError:
                return print(f'\nInstruction {instruction} not found at {self.pc}\n')
