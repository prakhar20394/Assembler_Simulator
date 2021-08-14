import sys
from inspect import currentframe

def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno


def outputError(user_input, error_code, line_number):
    print(f'{user_input} generates error: {error_mapping[error_code]}') 
    #print(f'Error generated at {line_number=}.')
    exit()

# initialising the values
variables = {}
labels = {}

source_code = sys.stdin.read().split("\n")
# remove blank lines, returns a list
source_code = [k.strip() for k in source_code if k.strip() != '']

semantics_op_dict = {'st': '00101', 'ld': '00100', 'add': '00000', 'sub': '00001', 'mul': '00110', 'xor': '01010',  \
                     'or': '01011', 'and': '01100', 'div': '00111', 'rs': '01000', 'ls': '01001', 'not': '01101',   \
                     'cmp': '01110', 'jmp': '01111', 'jlt': '10000', 'jgt': '10001', 'je': '10010', 'hlt': '10011'}

register_address = {"R0": "000", "R1": "001", "R2": "010", "R3": "011", "R4": "100", "R5": "101", "R6": "110",      \
                    "FLAGS": "111"}

error_mapping = {0: "No error", 1: "Typos in instruction name or register name or labels", 2: "Use of undefined variables",   \
                 3: "Use of undefined labels", 4: "Illegal use of FLAGS register",                                  \
                 5: "Illegal Immediate values (less than 0 or more than 255)",                                      \
                 6: "Misuse of labels as variables or vice-versa", 7: "Variables not declared at the beginning",    \
                 8: "Missing hlt instruction", 9: "hlt not being used as the last instruction",                     \
                 10: "Wrong syntax used for instructions",                                                          \
                 11: "Immediate is not numerical",                                                                  \
                 12: "Not enough arguments", 13: "Label already exists", 14: "Empty variable condition",            \
                 15: "Empty label condition", 16: "Memory address is not numerical"}

# variables 
counter = 0
syntax_count = len(source_code)
for i in range(syntax_count):
    temp_array = source_code[i].split()
    if temp_array[0] == "var":
        try:
            if temp_array[1] not in variables:
                variables[temp_array[1]] = format(syntax_count + counter, "08b")
                counter += 1
            else:
                print(f'Variable generates error: Variable already defined') 
            exit()
        except:
            print(f'Variable generates error: Empty variable condition') 
            exit()

        
    #elif source_code[i][0] in semantics_op_dict:
    else:
        break

source_code = source_code[i:]
syntax_count = len(source_code)

for i in range(syntax_count):
    temp_array = source_code[i].split()
    if temp_array[0] == "var":
        print(f'The line {i} generates error: Variables not declared at the beginning')
        exit()

# labels
for i in range(len(source_code)):
    # Note: Is label:add R3 R2 R1 a valid label?
    code_pro = source_code[i].split()
    if code_pro[0][-1] == ":":
        if code_pro[0][:-1] not in labels:
            labels[code_pro[0][:-1]] = format(i, "08b")
        else:
            print(f'The line {i} generates error: More than 1 address has same label')
            exit()
        

# gives error if the last entry is not halt
if source_code[-1] != "hlt":
    if ":" in source_code[-1]:
        code_pro_max_T = source_code[-1].split()
        if code_pro_max_T[-1] != 'hlt':
            print(f'The code generates error: Missing hlt instruction at end')
            exit()

#checks if there is halt in between
for i in range(len(source_code)):
    
    if source_code[i] == "hlt":
        if i != (len(source_code) - 1):
            print(f'The code generates error: hlt not being used as the last instruction(used in between)')
            exit()


def assembler(user_input):
    # value Initialisation
    #print(f"{source_code=}")
    reg1, reg2, reg3, reg4, mem_addr, imm = 0,0,0,0,0,0
    assembly_code = []

    # Checking semantics type & OP code
    if ':' in user_input:
        user_input = user_input[user_input.find(':')+1:].strip()

    syntax = user_input.split()
    try: 
        instruction_name = syntax[0]
    except:
        print(f'The code generates error: Empty label condition')
        exit()

    if instruction_name in semantics_op_dict:
        op_code = semantics_op_dict[instruction_name]
        #print(f"{op_code=}")
        assembly_code.append(op_code)
    elif instruction_name == "mov":
        if '$' in user_input:
            op_code = "00010"
            assembly_code.append(op_code)
        else:
            op_code = "00011"
            assembly_code.append(op_code)
    else:
        outputError(user_input, 1, get_linenumber())

    # add R1 R2
    # 012345678
    # A
    if op_code == "00000" or op_code == "00001" or op_code == "00110" or op_code == "01010" or op_code == "01011" or op_code == "01100":
        if len(syntax) != 4:
            outputError(user_input, 12, get_linenumber())

        reg1 = syntax[1]
        reg2 = syntax[2]
        reg3 = syntax[3]
        if reg1 == "FLAGS" or reg2 == "FLAGS" or reg3 == "FLAGS":
            outputError(user_input, 4, get_linenumber())

        if reg1 not in register_address or reg2 not in register_address or reg3 not in register_address:
            outputError(user_input, 1, get_linenumber())

        assembly_code.append("00")
        assembly_code.append(register_address[reg1])
        assembly_code.append(register_address[reg2])
        assembly_code.append(register_address[reg3])

    # mov R3 $242
    # 012345678654
    # B
    elif op_code == "01000" or op_code == "01001" or op_code == "00010":
        if len(syntax) != 3:
            outputError(user_input, 12, get_linenumber())

        reg1 = syntax[1]
        imm = syntax[2]
        if reg1 == "FLAGS":
            outputError(user_input, 4, get_linenumber())
        

        if reg1 not in register_address:
            outputError(user_input, 1, get_linenumber())

        try:
            imm1= int(imm[1:])
        except Exception as e:
            outputError(user_input, 10, get_linenumber())
        
        if (isinstance(imm1, int)) != True :
            outputError(user_input, 11, get_linenumber())

        if imm1<0 or imm1>255:
            outputError(user_input, 5, get_linenumber())
        
        

        assembly_code.append(register_address[reg1])
        assembly_code.append(format(imm1, "08b"))

    # div R3 R2
    # 012345678
    # C
    elif op_code == "01101" or op_code == "01110" or op_code == "00111":
        if len(syntax) != 3:
            outputError(user_input, 12, get_linenumber())

        reg1 = syntax[1]
        reg2 = syntax[2]
        if reg1 == "FLAGS" or reg2 == "FLAGS":
            outputError(user_input, 4, get_linenumber())
        if reg1 not in register_address or reg2 not in register_address:
            outputError(user_input, 1, get_linenumber())
        assembly_code.append("00000")
        assembly_code.append(register_address[reg1])
        assembly_code.append(register_address[reg2])

    # mov R2 R3 or mov R2 FLAG
    # C special case of mov
    elif op_code == "00011" :
        if len(syntax) != 3:
            outputError(user_input, 12, get_linenumber())
        reg1 = syntax[1]
        reg2 = syntax[2]
        if reg1 == "FLAGS":
            outputError(user_input, 4, get_linenumber())
        if reg1 not in register_address or reg2 not in register_address:
            outputError(user_input, 1, get_linenumber())
        assembly_code.append("00000")
        assembly_code.append(register_address[reg1])
        assembly_code.append(register_address[reg2])

    # ld R1 234
    # 123456789
    # D
    elif op_code == "00100" or op_code == "00101":
        if len(syntax) != 3:
            outputError(user_input, 12, get_linenumber())
        reg1 = syntax[1]
        value = syntax[2]
        if value in variables:
            mem_addr = variables[value]
        elif value in labels:
            outputError(user_input, 6, get_linenumber())
        else:
            outputError(user_input, 2, get_linenumber())
        
        if reg1 == "FLAGS":
            outputError(user_input, 4, get_linenumber())
        if reg1 not in register_address:
            outputError(user_input, 1, get_linenumber())
        
        assembly_code.append(register_address[reg1])
        assembly_code.append(mem_addr)

    # jmp mem_addr
    # 123456789012
    # E
    elif op_code == '01111' or op_code == "10000" or op_code == "10001" or op_code == "10010":
        if len(syntax) != 2:
            outputError(user_input, 12, get_linenumber())

        mem_addr = syntax[1]

        if mem_addr not in labels:
            outputError(user_input, 3, get_linenumber())

        assembly_code.append("000")
        assembly_code.append(labels[mem_addr])

    # hlt
    # 123
    # F
    elif op_code == '10011':
        assembly_code.append("00000000000")
    else :
        outputError(user_input, 10, get_linenumber())

    return assembly_code

# print, store
binary_byte_code = []
for code_pro_max in source_code:
    #binary_byte_code.extend(assembler(code_pro_max))
    binary_byte_code.append(assembler(code_pro_max))

this_assembly_code = ""
for i in range(len(binary_byte_code)):
    #this_assembly_code += ''.join(binary_byte_code[i]) + ""
    this_assembly_code += ''.join(binary_byte_code[i]) + "\n"
    # If this line is throwing error, its not because its wrong
    # its because assembler() return wrong output. fix assembler()

# error detection and syntax printing
print(this_assembly_code)

print("DEBUG OUTPUT")
#print(f"{binary_byte_code=}")
print(f"{variables}")
print(f"{labels=}")

'''
# Remove label
asm_string = "label: mov R3 R2"
print(f"{asm_string=}")
if ':' in asm_string:
    print(f"{asm_string[asm_string.find(':')+1:].strip()=}")
else:
    print(f"{asm_string=}")
'''
