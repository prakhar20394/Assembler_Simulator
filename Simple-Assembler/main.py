from sys import stdin

# initialising the values
variables = {}
labels = {}
halt = False
address = 0
line_num = 0

source_code = sys.stdin.read().split("\n")
# remove blank lines, returns a list
source_code = [k.strip() for k in source_code if k.strip() != '']


semantics_op_dict = {'st': '00101', 'ld': '00100', 'add': '00000', 'sub': '00001', 'mul': '00110', 'xor': '01010',  \
                     'or': '01011', 'and': '01100', 'div': '00111', 'rs': '01000', 'ls': '01001', 'not': '01101',   \
                     'cmp': '01110', 'jmp': '01111', 'jlt': '10000', 'jgt': '10001', 'je': '10010', 'hlt': '10011'}

register_address = {"R0": "000", "R1": "001", "R2": "010", "R3": "011", "R4": "100", "R5": "101", "R6": "110",      \
                    "FLAGS": "111"}

error_mapping = {0: "No error", 1: "Typos in instruction name or register name", 2: "Use of undefined variables",   \
                 3: "Use of undefined labels", 4: "Illegal use of FLAGS register",                                  \
                 5: "Illegal Immediate values (less than 0 or more than 255)",                                      \
                 6: "Misuse of labels as variables or vice-versa", 7: "Variables not declared at the beginning",    \
                 8: "Missing hlt instruction", 9: "hlt not being used as the last instruction",                     \
                 10: "Wrong syntax used for instructions"                                                           \
                 11: "Immediate is not numerical"}                                                                  \
                 12: "Not enough arguments"

# variables
counter = 0

syntax_count = len(source_code)

for i in range(len(source_code)):
    temp_array = source_code[i].split()
    if temp_array[0] == "var":
        variables[temp_array[1]] = format(syntax_count + counter, "08b")
        counter += 1
    elif source_code[i][0] in semantics_op_dict:
        break

source_code = source_code[i:]

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
        labels[code_pro[0][:-1]] = i
        
# gives error if the last entry is not halt
if source_code[-1] != "hlt":
    print(f'The code generates error: Missing hlt instruction at end')
    exit()

#checks if there is halt in between
for i in source_code:
    if i == "hlt"

binary_byte_code = []
for code_pro_max in source_code:
    binary_byte_code.extend(assembler(code_pro_max))

# print, store
this_assembly_code = ""
for i in range(len(binary_byte_code)):
    this_assembly_code += ''.join(binary_byte_code[i]) + '\n'

# error detection and syntax printing
print(this_assembly_code)

def assembler(user_input):
    # value Initialisation
    reg1, reg2, reg3, reg4, mem_addr, imm = 0,0,0,0,0,0
    error = 0
    assembly_code = []
    assembly_code_order = []

    # Checking semantics type & OP code
    syntax = user_input.split()
    instruction_name = syntax[0]
    if instruction_name in semantics_op_dict:
        op_code = semantics_op_dict[instruction_name]
        assembly_code.append(op_code)
    else:
        error = 1
        print(f'{user_input} generates error: {error_mapping[error]}') 
        exit()

    # differentiate between 2 mov conditions (type B and C)
    if op_code == "00010":
        if len(user_input) != 16:    # ?
            op_code = "00011"
            assembly_code[0] = op_code  # Looks flawed. should be -1 not 0

    # add R1 R2
    # 012345678
    # A
    elif op_code == "00000" or op_code == "00001" or op_code == "00110" or op_code == "01010" or op_code == "01011" or op_code == "01100":
        if len(syntax) != 4:
            error = 12
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()

        reg1 = syntax[1]
        reg2 = syntax[2]
        reg3 = syntax[3]
        if reg1 == "FLAGS" or reg2 == "FLAGS" or reg3 == "FLAGS":
            error = 4
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()
        if reg1 not in register_address or reg2 not in register_address or reg3 not in register_address:
            error = 1
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()
        assembly_code.append("00")
        assembly_code.append(register_address[reg1])
        assembly_code.append(register_address[reg2])
        assembly_code.append(register_address[reg3])

    # mov R3 $242
    # 012345678654
    # B
    elif op_code == "01000" or op_code == "01001" or op_code == "00010":
        if len(syntax) != 3:
            error = 12
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()

        reg1 = syntax[1]
        imm = syntax[2]
        if reg1 == FLAGS:
            error = 4
            print(f'{user_input} shows error: {error_mapping[error]}') 
            exit()
        if reg1 not in register_address:
            error = 1
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()
        try:
            imm1= int(imm[1:])
        except Exception as e:
            error = 10
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()

        if imm1<0 or imm1>255:
            error = 5
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()

        assembly_code.append(register_address[reg1])
        assembly_code.append(format(int(imm[1:]), "08b"))

    # mov R3 R2
    # 012345678
    # C
    elif op_code == "00010" or op_code == "01101" or op_code == "01110" or op_code == "00111":
        if len(syntax) != 3:
            error = 12
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()

        reg1 = syntax[1]
        reg2 = syntax[2]
        if reg1 == "FLAGS" or reg2 == "FLAGS":
            error = 4
            print(f'{user_input} shows error: {error_mapping[error]}') 
            exit()
        if reg1 not in register_address or reg2 not in register_address:
            error = 1
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()
        assembly_code.append("00000")
        assembly_code.append(register_address[reg1])
        assembly_code.append(register_address[reg2])

    # ld R1 234
    # 123456789
    # D
    elif op_code == "00100" or op_code == "00101":
        if len(syntax) != 3:
            error = 12
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()

        reg1 = syntax[1]
        value = syntax[2]
        if value in variables:
            mem_addr = variables[value]
        if reg1 == FLAGS:
            error = 4
            print(f'{user_input} shows error: {error_mapping[error]}') 
            exit()
        if reg1 not in register_address:
            error = 1
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()
        assembly_code.append(register_address[reg1])
        assembly_code.append((int(mem_addr), "08b"))

    # jmp mem_addr
    # 123456789012
    # E
    elif op_code == '01111' or op_code == "10000" or op_code == "10001" or op_code == "10010":
        if len(syntax) != 2:
            error = 12
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()

        mem_addr = syntax[1]

        if mem_addr not in labels:
            error = 3
            print(f'{user_input} generates error: {error_mapping[error]}') 
            exit()

        assembly_code.append("000")
        assembly_code.append(labels[mem_addr])

    # hlt
    # 123
    # F
    elif op_code == '10011':
        assembly_code.append("00000000000")
    return assembly_code
