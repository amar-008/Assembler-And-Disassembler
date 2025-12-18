import sys
import struct
import re

R_TYPE_INSTRUCTIONS = {
    'add':  {'opcode': 0x00, 'funct': 0x20},
    'sub':  {'opcode': 0x00, 'funct': 0x22},
    'and':  {'opcode': 0x00, 'funct': 0x24},
    'or':   {'opcode': 0x00, 'funct': 0x25},
    'xor':  {'opcode': 0x00, 'funct': 0x26},
    'slt':  {'opcode': 0x00, 'funct': 0x2a},
    'sll':  {'opcode': 0x00, 'funct': 0x00},
    'srl':  {'opcode': 0x00, 'funct': 0x02},
    'jr':   {'opcode': 0x00, 'funct': 0x08},
}

I_TYPE_INSTRUCTIONS = {
    'addi': {'opcode': 0x08},
    'slti': {'opcode': 0x0a},
    'lw':   {'opcode': 0x23},
    'sw':   {'opcode': 0x2b},
    'beq':  {'opcode': 0x04},
    'bne':  {'opcode': 0x05},
}

J_TYPE_INSTRUCTIONS = {
    'j':    {'opcode': 0x02},
    'jal':  {'opcode': 0x03},
}

SPECIAL_INSTRUCTIONS = {
    'lui':  {'opcode': 0x0f},
    'nop':  {'opcode': 0x00},
}

# Register name to number mapping
REGISTERS = {
    '$zero': 0, '$0': 0,
    '$at': 1,
    '$v0': 2, '$v1': 3,
    '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7,
    '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11,
    '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15,
    '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19,
    '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23,
    '$t8': 24, '$t9': 25,
    '$k0': 26, '$k1': 27,
    '$gp': 28, '$sp': 29, '$fp': 30, '$ra': 31,
}

# Reverse mapping for disassembly
REG_NAMES = {v: k for k, v in REGISTERS.items() if k.startswith('$') and len(k) <= 3}


class Assembler:
    def __init__(self):
        self.labels = {}
        self.instructions = []
        self.current_address = 0
        
    def parse_register(self, reg_str):
        """Convert register string to register number"""
        reg_str = reg_str.strip().rstrip(',')
        if reg_str not in REGISTERS:
            raise ValueError(f"Unknown register: {reg_str}")
        return REGISTERS[reg_str]
    
    def parse_immediate(self, imm_str):
        """Parse immediate value (decimal or hex)"""
        imm_str = imm_str.strip().rstrip(',')
        if imm_str.startswith('0x'):
            return int(imm_str, 16)
        return int(imm_str)
    
    def first_pass(self, lines):
        """First pass: collect labels and their addresses"""
        address = 0
        for line in lines:
            line = line.split('#')[0].strip()  # Remove comments
            if not line:
                continue
                
            if ':' in line:
                label = line.split(':')[0].strip()
                self.labels[label] = address
                line = line.split(':', 1)[1].strip()
                if not line:
                    continue
            
            # Count instruction
            parts = line.split()
            if parts:
                address += 4
    
    def encode_r_type(self, instr, parts):
        """Encode R-type instruction"""
        opcode = instr['opcode']
        funct = instr['funct']
        
        if parts[0] == 'sll' or parts[0] == 'srl':
            # Shift instructions: sll $rd, $rt, shamt
            rd = self.parse_register(parts[1])
            rt = self.parse_register(parts[2])
            shamt = self.parse_immediate(parts[3])
            rs = 0
            return (opcode << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (shamt << 6) | funct
        elif parts[0] == 'jr':
            # Jump register: jr $rs
            rs = self.parse_register(parts[1])
            return (opcode << 26) | (rs << 21) | funct
        else:
            # Normal R-type: add $rd, $rs, $rt
            rd = self.parse_register(parts[1])
            rs = self.parse_register(parts[2])
            rt = self.parse_register(parts[3])
            return (opcode << 26) | (rs << 21) | (rt << 16) | (rd << 11) | funct
    
    def encode_i_type(self, instr, parts):
        """Encode I-type instruction"""
        opcode = instr['opcode']
        
        if parts[0] in ['lw', 'sw']:
            # Memory instructions: lw $rt, offset($rs)
            rt = self.parse_register(parts[1])
            # Parse offset($rs)
            mem_match = re.match(r'(-?\d+)\((\$\w+)\)', parts[2])
            if not mem_match:
                raise ValueError(f"Invalid memory format: {parts[2]}")
            offset = int(mem_match.group(1))
            rs = self.parse_register(mem_match.group(2))
            
            # Convert to signed 16-bit
            if offset < 0:
                offset = (1 << 16) + offset
            
            return (opcode << 26) | (rs << 21) | (rt << 16) | (offset & 0xFFFF)
        
        elif parts[0] in ['beq', 'bne']:
            # Branch: beq $rs, $rt, label or address
            rs = self.parse_register(parts[1])
            rt = self.parse_register(parts[2])
            target = parts[3].strip()
            
            # Check if target is a hex address or label
            if target.startswith('0x'):
                target_addr = int(target, 16)
            else:
                target_addr = self.labels.get(target, 0)
            
            # Calculate offset
            offset = (target_addr - (self.current_address + 4)) // 4
            
            # Convert to signed 16-bit
            if offset < 0:
                offset = (1 << 16) + offset
            
            return (opcode << 26) | (rs << 21) | (rt << 16) | (offset & 0xFFFF)
        
        else:
            # Normal I-type: addi $rt, $rs, immediate
            rt = self.parse_register(parts[1])
            rs = self.parse_register(parts[2])
            imm = self.parse_immediate(parts[3])
            
            # Convert to signed 16-bit
            if imm < 0:
                imm = (1 << 16) + imm
            
            return (opcode << 26) | (rs << 21) | (rt << 16) | (imm & 0xFFFF)
    
    def encode_j_type(self, instr, parts):
        """Encode J-type instruction"""
        opcode = instr['opcode']
        target = parts[1].strip()
        
        # Check if target is a hex address or label
        if target.startswith('0x'):
            target_addr = int(target, 16)
        else:
            target_addr = self.labels.get(target, 0)
        
        # Get target address
        address = (target_addr >> 2) & 0x3FFFFFF
        
        return (opcode << 26) | address
    
    def assemble_instruction(self, line):
        """Assemble a single instruction"""
        parts = line.split()
        if not parts:
            return None
        
        mnemonic = parts[0].lower()
        
        # Handle NOP specially
        if mnemonic == 'nop':
            return 0x00000000
        
        # Handle LUI specially
        if mnemonic == 'lui':
            rt = self.parse_register(parts[1])
            imm = self.parse_immediate(parts[2])
            opcode = SPECIAL_INSTRUCTIONS['lui']['opcode']
            return (opcode << 26) | (rt << 16) | (imm & 0xFFFF)
        
        # R-type
        if mnemonic in R_TYPE_INSTRUCTIONS:
            return self.encode_r_type(R_TYPE_INSTRUCTIONS[mnemonic], parts)
        
        # I-type
        if mnemonic in I_TYPE_INSTRUCTIONS:
            return self.encode_i_type(I_TYPE_INSTRUCTIONS[mnemonic], parts)
        
        # J-type
        if mnemonic in J_TYPE_INSTRUCTIONS:
            return self.encode_j_type(J_TYPE_INSTRUCTIONS[mnemonic], parts)
        
        raise ValueError(f"Unknown instruction: {mnemonic}")
    
    def assemble(self, input_file, output_file):
        """Assemble MIPS assembly file to binary"""
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        # First pass: collect labels
        self.first_pass(lines)
        
        # Second pass: assemble instructions
        machine_code = []
        self.current_address = 0
        
        for line in lines:
            line = line.split('#')[0].strip()
            if not line:
                continue
            
            # Remove label if present
            if ':' in line:
                line = line.split(':', 1)[1].strip()
                if not line:
                    continue
            
            try:
                code = self.assemble_instruction(line)
                if code is not None:
                    machine_code.append(code)
                    self.current_address += 4
            except Exception as e:
                print(f"Error assembling line '{line}': {e}")
                raise
        
        # Write binary output
        with open(output_file, 'wb') as f:
            for code in machine_code:
                f.write(struct.pack('>I', code))  # Big-endian 32-bit
        
        print(f"Assembled {len(machine_code)} instructions to {output_file}")
        return len(machine_code)


class Disassembler:
    def __init__(self):
        self.address = 0
        
    def get_register_name(self, reg_num):
        """Get register name from number"""
        return REG_NAMES.get(reg_num, f"${reg_num}")
    
    def disassemble_r_type(self, instruction):
        """Disassemble R-type instruction"""
        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        rd = (instruction >> 11) & 0x1F
        shamt = (instruction >> 6) & 0x1F
        funct = instruction & 0x3F
        
        # Find instruction by funct code
        for name, info in R_TYPE_INSTRUCTIONS.items():
            if info['funct'] == funct:
                if name in ['sll', 'srl']:
                    if rd == 0 and rt == 0 and shamt == 0:
                        return 'nop'
                    return f"{name} {self.get_register_name(rd)}, {self.get_register_name(rt)}, {shamt}"
                elif name == 'jr':
                    return f"{name} {self.get_register_name(rs)}"
                else:
                    return f"{name} {self.get_register_name(rd)}, {self.get_register_name(rs)}, {self.get_register_name(rt)}"
        
        return f"unknown_r 0x{instruction:08x}"
    
    def disassemble_i_type(self, instruction):
        """Disassemble I-type instruction"""
        opcode = (instruction >> 26) & 0x3F
        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        imm = instruction & 0xFFFF
        
        # Convert to signed
        if imm & 0x8000:
            imm_signed = imm - 0x10000
        else:
            imm_signed = imm
        
        # Find instruction by opcode
        for name, info in I_TYPE_INSTRUCTIONS.items():
            if info['opcode'] == opcode:
                if name in ['lw', 'sw']:
                    return f"{name} {self.get_register_name(rt)}, {imm_signed}({self.get_register_name(rs)})"
                elif name in ['beq', 'bne']:
                    target = self.address + 4 + (imm_signed * 4)
                    return f"{name} {self.get_register_name(rs)}, {self.get_register_name(rt)}, 0x{target:x}"
                else:
                    return f"{name} {self.get_register_name(rt)}, {self.get_register_name(rs)}, {imm_signed}"
        
        # Check for LUI
        if opcode == SPECIAL_INSTRUCTIONS['lui']['opcode']:
            return f"lui {self.get_register_name(rt)}, {imm}"
        
        return f"unknown_i 0x{instruction:08x}"
    
    def disassemble_j_type(self, instruction):
        """Disassemble J-type instruction"""
        opcode = (instruction >> 26) & 0x3F
        address = instruction & 0x3FFFFFF
        target = address << 2
        
        for name, info in J_TYPE_INSTRUCTIONS.items():
            if info['opcode'] == opcode:
                return f"{name} 0x{target:x}"
        
        return f"unknown_j 0x{instruction:08x}"
    
    def disassemble(self, input_file, output_file):
        """Disassemble binary to MIPS assembly"""
        with open(input_file, 'rb') as f:
            data = f.read()
        
        # Verify file size is multiple of 4
        if len(data) % 4 != 0:
            raise ValueError("Binary file size must be multiple of 4 bytes")
        
        instructions = []
        self.address = 0
        
        for i in range(0, len(data), 4):
            word = struct.unpack('>I', data[i:i+4])[0]
            opcode = (word >> 26) & 0x3F
            
            # Determine instruction type
            if opcode == 0x00:
                instr = self.disassemble_r_type(word)
            elif opcode in [0x02, 0x03]:
                instr = self.disassemble_j_type(word)
            else:
                instr = self.disassemble_i_type(word)
            
            instructions.append(f"    {instr}")
            self.address += 4
        
        # Write output
        with open(output_file, 'w') as f:
            f.write("# Disassembled MIPS code\n\n")
            for instr in instructions:
                f.write(instr + '\n')
        
        print(f"Disassembled {len(instructions)} instructions to {output_file}")
        return len(instructions)


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Assemble:     python mips_tools.py assemble <input.asm> <output.bin>")
        print("  Disassemble:  python mips_tools.py disassemble <input.bin> <output.asm>")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    input_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not output_file:
        if command == 'assemble':
            output_file = input_file.replace('.asm', '.bin')
        else:
            output_file = input_file.replace('.bin', '.asm')
    
    try:
        if command == 'assemble':
            assembler = Assembler()
            assembler.assemble(input_file, output_file)
        elif command == 'disassemble':
            disassembler = Disassembler()
            disassembler.disassemble(input_file, output_file)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()