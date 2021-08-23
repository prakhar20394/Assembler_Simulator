import sys
import numpy as np
import matplotlib.pyplot as matplot

'''
Remaining tasks:

 - Bonus


======================================================================================
######################################################################################
======================================================================================
'''
'''
_print = print

def print(*s, end='\n'):
    _print(*s, end=end)
    _print(*s, end=end, file=sys.stderr)
'''


def main():
    
    user_input = sys.stdin.read()

    global MEM
    global PC
    global EE
    global RF

    # Memory contains (code + variables)
    # Memory ~ RAM
    # heavy programs use more RAM on your laptop because they have big code + more variables
    MEM =   Memory(user_input)

    # ProgramCounter object keeps track of what line of code is running
    global PC
    PC  =   ProgramCounter(0)

    # ExecutionEngine ~ ALU of the CPU
    # All major processing is done here
    EE  =   ExecutionEngine()

    # Register file stores all registers.
    # It is different and disjoint from Memory/RAM.
    RF  =   RegisterFile()

    halted = False

    while not halted:
        # Fetch instruction
        instruction = MEM.get(PC)

        # Execute instruction and get new states
        halted, new_PC = EE.execute(instruction)

        # Print Program Counter
        PC.dump()

        # Print all registers
        RF.dump()

        # Change Program Counter to next instruction
        PC.update(new_PC)
    
    # Print all contents of memory
    MEM.dump()

    '''# Prints Scatter graph
    bonus_scatter_plot()'''

# ================================
# CLASSES
# ================================

class Memory():
    def __init__(self, user_input):
        # Load the program into Memory
        code_space = list(map(convertToDecimal, user_input.split("\n")))

        # Create space in Memory for variables
        variable_space = [0]*256

        # Cut to 512 bytes of space
        # 256 cells * 16 bits = 4096 bits = 512 bytes
        self.data = (code_space + variable_space)[:256] # Slice to size of 256
    
    def get(self, address):
        # INPUT: ADDRESS as (binary string OR decimal integer)
        # OUTPUT: Data at input address

        # Example
        # INPUT: "0000...101" or 5
        # OUTPUT: Data at address 5
        if type(address) == str:
            address = convertToDecimal(address)
        if type(address) == ProgramCounter:
            address = address.value
        return self.data[address]
    
    def set(self, address, value):
        # INPUT1: ADDRESS as (binary string OR decimal integer)
        # INPUT2: data

        # USE: stores data into Memory at address

        # Example: Both of the following inputs are equivalent
        # - (5,123)
        # - ("0000000000000101", 123)
        if type(address) == str:
            address = convertToDecimal(address)
        self.data[address] = value
    
    def dump(self):
        # Print contents of memory as output
        print()
        for memory in self.data:
            print(convertToBinary(memory)) 


class ProgramCounter():
    def __init__(self, value):
        # Value -> Value of ProgramCounter
        # Value is an integer between [0,255]
        self.value = value
    
    def dump(self):
        # Print PC.value as output
        # Please refer PDF to check format

        print(convertToBinary(self.value)[8:], end=" ") 
    
    def update(self, new_PC):
        # Set PC to next instruction
        self.value = new_PC


class ExecutionEngine():
    def __init__(self):
        # "instructions" has been defined at the end of this class
        # instruction_map maps numbers to instructions
        # 0 -> add
        # 1 -> sub
        # ...
        # 17 -> je
        # 18 -> hlt
        self.instruction_map = dict(enumerate(ExecutionEngine.instructions))

        # new_state tells what change the instruction has bought
        # halted tells if CPU should halt
        # PC tells which is the next instruction that should be run
        # TypeE instructions bring drastic changes to PC
        self.new_state = {'halted': False, 'PC': 0}
    
    def execute(self, instruction):
        # execute() does the following.
        # 1. take in instruction (opcode + unused_bits + operands)
        # 2. identify type of instruction
        # 3. call appropriate unit (add, sub, jmp, hlt, ...)

        # EXAMPLE INPUT: 83
        # Binary of 83: 00000_00_001_010_011
        # opcode = 00000 (ADD instruction)
        # unused_bits = 00
        # reg1 = 001 (R1)
        # reg2 = 010 (R2)
        # reg3 = 011 (R3)

        # OUTPUT: executes ADD(00_001_010_011)
        # Note: underscores (_) are for clarity. not actually there.
        instruction = convertToBinary(instruction)

        opcode, tail = instruction[:5],instruction[5:]
        executor = self.instruction_map[convertToDecimal(opcode)]

        # Call appropriate function
        executor(self, tail)

        # Return new CPU states to main() function
        return self.new_state['halted'], self.new_state['PC']

    # ================================
    # INDIVIDUAL INSTRUCTION EXECUTION
    # ================================

    def ADD(self, tail):
        # Type A

        # INPUT: ADD("00001010011")

        # Here,
        # unused-bits_reg1_reg2_reg3 = 00_001_010_011

        # OUTPUT:
        # set reg1 to "RF.get(reg2) + RF.get(reg3)"

        # Can be done through
        # RF.set(target_register, data)
        
        # which, here, is
        # RF.set(reg1, RF.get(reg2) + RF.get(reg3))
        unused_bits = tail[0:2]

        destination = tail[2:5]
        source1 = tail[5:8]
        source2 = tail[8:11]

        RF.clearFlags()
        result = RF.get(source1) + RF.get(source2)

        if result > 65535:
            result %= 65535
            RF.setOverflow()

        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1

    def SUB(self, tail):
        # Type A
        unused_bits = tail[0:2]

        destination = tail[2:5]
        source1 = tail[5:8]
        source2 = tail[8:11]

        RF.clearFlags()
        result = RF.get(source1) - RF.get(source2)

        if result < 0:
            result = 0
            RF.setOverflow()

        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1

    def MOV_IMMEDIATE(self, tail):
        # Type B

        unused_bits = None

        destination = tail[0:3]
        source = tail[3:11]

        RF.clearFlags()
        result = convertToDecimal(source)

        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1
    

    def MOV_REGISTER(self, tail):
        # Type C

        unused_bits = tail[0:5]

        destination = tail[5:8]
        source = tail[8:11]

        result = RF.get(source)
        RF.clearFlags()

        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1
    
    def LD(self, tail):
        # Type D

        unused_bits = None

        destination = tail[0:3]
        source = tail[3:11]

        RF.clearFlags()
        result = MEM.get(source)

        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1
    
    def ST(self, tail):
        # Type D

        unused_bits = None

        source = tail[0:3]
        destination = tail[3:11]

        RF.clearFlags()
        result = RF.get(source)

        MEM.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1

    def MUL(self, tail):
        # Type A
        

        unused_bits = tail[0:2]

        destination = tail[2:5]
        source1 = tail[5:8]
        source2 = tail[8:11]

        RF.clearFlags()
        result = RF.get(source1) * RF.get(source2)

        if result > 65535:
            result %= 65535
            RF.setOverflow()

        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1

    def DIV(self, tail):
        # Type C
    
        unused_bits = tail[0:5]

        source1 = tail[5:8]
        source2 = tail[8:11]

        RF.clearFlags()

        R0 = RF.get(source1)//RF.get(source2)
        R1 = RF.get(source1)%RF.get(source2)

        RF.set("0" , R0)
        RF.set("1" , R1)

        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1


    def RS(self, tail):
        # Type B

        unused_bits = None

        destination = tail[0:3]
        shift = tail[3:11]

        RF.clearFlags()
        result = RF.get(destination) >> convertToDecimal(shift)

        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1

    def LS(self, tail):
        # Type B

        unused_bits = None

        destination = tail[0:3]
        shift = tail[3:11]

        RF.clearFlags()
        result = RF.get(destination) << convertToDecimal(shift)

        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1

    def XOR(self, tail):
        # Type A

        unused_bits = tail[0:2]

        destination = tail[2:5]
        source1 = tail[5:8]
        source2 = tail[8:11]

        RF.clearFlags()
        result = RF.get(source1) ^ RF.get(source2)

        #print ('{0:b}'.format(result))
        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1

    def OR(self, tail):
        # Type A

        unused_bits = tail[0:2]

        destination = tail[2:5]
        source1 = tail[5:8]
        source2 = tail[8:11]

        RF.clearFlags()
        result = RF.get(source1) | RF.get(source2)
        #print ('{0:b}'.format(result))
        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1

    def AND(self, tail):
        # Type A

        unused_bits = tail[0:2]

        destination = tail[2:5]
        source1 = tail[5:8]
        source2 = tail[8:11]

        RF.clearFlags()
        result = RF.get(source1) & RF.get(source2)
        #print ('{0:b}'.format(result))
        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1

    def NOT(self, tail):
        # Type C

        unused_bits = tail[0:5]

        destination = tail[5:8]
        source = tail[8:11]

        RF.clearFlags()
        result = ~ RF.get(source) % 65536
        

        RF.set(destination, result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1


    def CMP(self, tail):
        # Type C

        unused_bits = tail[0:5]

        source1 = tail[5:8]
        source2 = tail[8:11]

        RF.clearFlags()
        result = cmp(RF.get(source1), RF.get(source2))

        RF.setCMP(result)
        self.new_state['halted'] = False
        self.new_state['PC'] = PC.value + 1
    

    def JMP(self, tail):
       # Type E

        unused_bits = tail[0:3]

        memory_address = tail[3:11]

        result = convertToDecimal(memory_address)
        RF.clearFlags()

        self.new_state['halted'] = False
        self.new_state['PC'] = result


    def JLT(self, tail):
        # Type E

        unused_bits = tail[0:3]

        memory_address = tail[3:11]

        if RF.getCMP() == -1:
            # if last "CMP reg1, reg2" was reg1 < reg2
            # JLT -> Jump if Less Than
            result = convertToDecimal(memory_address)
        else:
            result = PC.value + 1
        RF.clearFlags()
        
        self.new_state['halted'] = False
        self.new_state['PC'] = result

    def JGT(self, tail):
        # Type E
        unused_bits = tail[0:3]

        memory_address = tail[3:11]

        if RF.getCMP() == +1:
            result = convertToDecimal(memory_address)
        else:
            result = PC.value + 1
        RF.clearFlags()
        
        self.new_state['halted'] = False
        self.new_state['PC'] = result

        

    def JE(self, tail):
        # Type E

        unused_bits = tail[0:3]

        memory_address = tail[3:11]

        if RF.getCMP() == 0:
            result = convertToDecimal(memory_address)
        else:
            result = PC.value + 1
        RF.clearFlags()
        
        self.new_state['halted'] = False
        self.new_state['PC'] = result
    
    def HLT(self, tail):
        # Type F

        unused_bits = None
        
        self.new_state['halted'] = True
        self.new_state['PC'] = PC.value + 1
    
    # ====================================================================
    # Class level variables for ExecutionEngine:
    # 1. instructions
    # ====================================================================

    # List of all instructions, in order
    instructions = [ADD,SUB,MOV_IMMEDIATE,MOV_REGISTER,LD,ST,MUL,DIV,RS,LS,XOR,OR,AND,NOT,CMP,JMP,JLT,JGT,JE,HLT]

class RegisterFile():
    def __init__(self):
        # List of 8 registers
        self.data = [0]*8
    
    def dump(self):
        # Fancy way of printing all registers to output

        # it just prints the list in binary format
        print(' '.join(map(convertToBinary, self.data)))


    def get(self, address):
        # INPUT: binary string OR integer
        
        # INPUT: address = "000..00101"
        # OUTPUT: Data in R5

        # INPUT: address = 5
        # OUTPUT: Data in R5
        if type(address) == str:
            address = convertToDecimal(address)
        return self.data[address]

    def set(self, address, value):
        # INPUT1: binary string OR integer address
        # INPUT2: integer value to be stored as data
        
        # INPUT: address = "000..00101", value = 123
        # OUTPUT: Set Data in R5 = 123

        # INPUT: address = 5
        # OUTPUT: Set Data in R5 = 123

        if type(address) == str:
            address = convertToDecimal(address)
        self.data[address] = value

    def clearFlags(self):
        # Just set all bits of FLAGS to 0
        self.data[7] =0

    def setCMP(self, value):
        # INPUT: +1
        # OUTPUT: set Greater Than bit

        # INPUT: 0
        # OUTPUT: set Equal To bit

        # INPUT: -1
        # OUTPUT: set Lesser Than bit

        if value == 0:
            # E bit
            offset = 0
        elif value == 1:
            # G bit
            offset = 1
        elif value == -1:
            # L bit
            offset = 2
        
        self.data[-1] |= 1<<offset

    def getCMP(self):
        # OUTPUT:
        # +1 if G bit is set (Greater than)
        # 0 if E bit is set (Equal to)
        # -1 if E bit is set (Lesser to)

        if self.data[-1] & 1<<0:
            # E bit
            return 0
        elif self.data[-1] & 1<<1:
            # G bit
            return 1
        if self.data[-1] & 1<<2:
            # L bit
            return -1

    def setOverflow(self):
        # OUTPUT:
        # Sets 3rd bit of FLAGS to 1
        # 3rd bit in FLAGS if OVERFLOW bit

        self.data[-1] |= 1<<3



# ================================
# HELPER FUNCTIONS
# ================================

def convertToDecimal(x):
    # INPUT: "010"
    # output: 2
    x = int(x)

    decimal, i, n = 0, 0, 0
    while(x!= 0):
        dec = x%10
        decimal = decimal + dec * pow(2, i)
        x = x//10
        i += 1
   
    return decimal

def convertToBinary(x, n=16):
    # Convert x into an n-bit string
    # INPUT: (x=5, n=8)
    # output: "00000101"
    a = x
    #this will print a in binary
    bnr = bin(a).replace('0b','')
    x = bnr[::-1] #this reverses an array
    while len(x) < n:
        x += '0'
    bnr = x[::-1]

    return bnr

def cmp(a, b):
    # INPUT: 2 integers
    
    # OUTPUT: 
    # +1 if a > b
    # 0 if a == b
    # -1 if a < b

    # EXAMPLE:
    # cmp(3,10) = -1 because 3 < 10
    return (a > b) - (a < b) 

def bonus_scatter_plot(cycle_number, memory_address):

    x = range(cycle_number)
    y = x
    matplot.scatter(x, y, c='red')
    matplot.title('Scatter plot')
    matplot.xlabel('Cycle Number')
    matplot.ylabel('Memory Address')
    matplot.show()

    
# ================================
# END
# ================================

if __name__ == "__main__":
    main()
