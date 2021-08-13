from sys import stdin

variables = []

stage2_instruction = []
# variable
for code in stdin:
    temp_array = code.split()
    if temp_array[0] == "var":
        variables.append(temp_array[1])
    else:
        stage2_instruction.append(code)

# label
for coder_pro in stage2_instruction:
    temp_array = coder_pro.split()
    if type(temp_array[0][-1]) == ":":
        stage3_instruction = temp_array[1:]
    else:
        stage3_instruction.append(coder_pro)


for line in stdin:
    if line == 'hlt':  # If empty string is read then stop the loop
        print("1001100000000000")
        break
    elif line == ' ':
        continue
    else:
        assembler(line)  # perform some assembly(s) on given string

semantics_op_dict = {'st': '00101', 'ld': '00101', 'add': '00000', 'sub': '00001', 'mul': '00110', 'xor': '01010',
                     'or': '01011', 'and': '01100', 'div': '00111', 'rs': '01000', 'ls': '01001', 'not': '01101',
                     'cmp': '01110', 'jmp': '01111', 'jlt': '10000', 'jgt': '10001', 'je': '10010', 'hlt': '10011'}
register_address = {"R0": "000", "R1": "001", "R2": "010", "R3": "011", "R4": "100", "R5": "101", "R6": "110",
                    "FLAGS": "111"}

error_mapping = {0: "No error", 1: "Typos in instruction name or register name", 2: "Use of undefined variables",
                 3: "Use of undefined labels", 4: "Illegal use of FLAGS register",
                 5: "Illegal Immediate values (less than 0 or more than 255)",
                 6: "Misuse of labels as variables or vice-versa", 7: "Variables not declared at the beginning",
                 8: "Missing hlt instruction", 9: "hlt not being used as the last instruction",
                 10: "Wrong syntax used for instructions"}


def assembler(user_input):
    # value Initialisation
    reg1, reg2, reg3, reg4, mem_addr, imm = 0
    error = 0
    assembly_code = []
    assembly_code_order = []
    error_command = "This is error message, will change later"

    # Checking semantics type & OP code
    syntax = user_input.split()
    semantic = syntax[0]
    if semantic_code in semantics_op_dict:
        op_code = semantics_op_dict[semantic]
        assembly_code.append(op_code)
    else:
        op_code = error
        error = 1

    # differentiate between 2 mov conditions (type B and C)
    if op_code == "00010":
        if len(user_input) != 16:
            op_code = "00011"
            assembly_code[0] = op_code

    # add R1 R2
    # 012345678
    # A
    elif op_code == "00000" or "00001" or "00110" or "01010" or "01011" or "01100":
        reg1 = syntax[1]
        reg2 = syntax[2]
        reg3 = syntax[3]
        assembly_code.append("00")
        assembly_code.append(register_address[reg1])
        assembly_code.append(register_address[reg2])
        assembly_code.append(register_address[reg3])

    # mov R3 $242
    # 012345678654
    # B
    elif op_code == "01000" or "01001" or "00010":
        reg1 = syntax[1]
        imm = syntax[2]
        assembly_code.append(register_address[reg1])
        assembly_code.append(format(imm[1:], "08b"))

    # mov R3 R2
    # 012345678
    # C
    elif op_code == "00010" or "01101" or "01110" or "00111":
        reg1 = syntax[1]
        reg2 = syntax[2]
        assembly_code.append("00000")
        assembly_code.append(register_address[reg1])
        assembly_code.append(register_address[reg2])

    # ld R1 234
    # 123456789
    # D
    elif op_code == "00100" or "00101":
        reg1 = syntax[1]
        mem_addr = syntax[2]
        assembly_code.append(register_address[reg1])
        assembly_code.append((mem_addr, "08b"))

    # jmp mem_addr
    # 123456789012
    # E
    elif op_code == '01111' or "10000" or "10001" or "10010":
        mem_addr = syntax[1]
        assembly_code.append("000")
        assembly_code.append((mem_addr, "08b"))

    # hlt
    # 123
    # F
    elif op_code == '10011':
        assembly_code.append("00000000000")

    # print, store
    this_assembly_code = ""
    for i in range(len(assembly_code)):
        this_assembly_code += assembly_code[i]
        assembly_code_order.append(this_assembly_code)

    # error detection and syntax printing
    if error == 0:
        print(this_assembly_code)
    else:
        print(f'{this_assembly_code} shows error: {error_mapping[error]}')


