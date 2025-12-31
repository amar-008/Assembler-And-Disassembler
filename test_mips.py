"""
Unit tests for MIPS32 Assembler and Disassembler
Run with: python -m pytest test_mips.py -v
"""

import unittest
import struct
import tempfile
import os
from main import Assembler, Disassembler


class TestAssemblerRegisters(unittest.TestCase):
    """Test register parsing"""

    def setUp(self):
        self.asm = Assembler()

    def test_parse_named_registers(self):
        self.assertEqual(self.asm.parse_register('$zero'), 0)
        self.assertEqual(self.asm.parse_register('$ra'), 31)
        self.assertEqual(self.asm.parse_register('$sp'), 29)
        self.assertEqual(self.asm.parse_register('$t0'), 8)
        self.assertEqual(self.asm.parse_register('$s0'), 16)

    def test_parse_register_with_comma(self):
        self.assertEqual(self.asm.parse_register('$t0,'), 8)

    def test_invalid_register(self):
        with self.assertRaises(ValueError):
            self.asm.parse_register('$invalid')


class TestAssemblerImmediate(unittest.TestCase):
    """Test immediate value parsing"""

    def setUp(self):
        self.asm = Assembler()

    def test_parse_decimal(self):
        self.assertEqual(self.asm.parse_immediate('100'), 100)
        self.assertEqual(self.asm.parse_immediate('-5'), -5)

    def test_parse_hex(self):
        self.assertEqual(self.asm.parse_immediate('0x10'), 16)
        self.assertEqual(self.asm.parse_immediate('0xFF'), 255)


class TestRTypeInstructions(unittest.TestCase):
    """Test R-type instruction encoding"""

    def setUp(self):
        self.asm = Assembler()

    def test_add_instruction(self):
        # add $t0, $t1, $t2 -> opcode=0, rs=$t1(9), rt=$t2(10), rd=$t0(8), shamt=0, funct=0x20
        code = self.asm.assemble_instruction('add $t0, $t1, $t2')
        # Expected: 0x012A4020
        self.assertEqual(code, 0x012A4020)

    def test_sub_instruction(self):
        # sub $s0, $s1, $s2 -> rs=$s1(17), rt=$s2(18), rd=$s0(16), funct=0x22
        code = self.asm.assemble_instruction('sub $s0, $s1, $s2')
        self.assertEqual(code, 0x02328022)

    def test_and_instruction(self):
        code = self.asm.assemble_instruction('and $t0, $t1, $t2')
        self.assertEqual(code, 0x012A4024)

    def test_or_instruction(self):
        code = self.asm.assemble_instruction('or $t0, $t1, $t2')
        self.assertEqual(code, 0x012A4025)

    def test_slt_instruction(self):
        code = self.asm.assemble_instruction('slt $t0, $t1, $t2')
        self.assertEqual(code, 0x012A402A)

    def test_sll_instruction(self):
        # sll $t0, $t1, 4 -> rd=$t0(8), rt=$t1(9), shamt=4
        code = self.asm.assemble_instruction('sll $t0, $t1, 4')
        self.assertEqual(code, 0x00094100)

    def test_srl_instruction(self):
        code = self.asm.assemble_instruction('srl $t0, $t1, 4')
        self.assertEqual(code, 0x00094102)

    def test_jr_instruction(self):
        # jr $ra -> rs=$ra(31)
        code = self.asm.assemble_instruction('jr $ra')
        self.assertEqual(code, 0x03E00008)

    def test_nop_instruction(self):
        code = self.asm.assemble_instruction('nop')
        self.assertEqual(code, 0x00000000)


class TestITypeInstructions(unittest.TestCase):
    """Test I-type instruction encoding"""

    def setUp(self):
        self.asm = Assembler()

    def test_addi_instruction(self):
        # addi $t0, $t1, 100 -> opcode=0x08, rs=$t1(9), rt=$t0(8), imm=100
        code = self.asm.assemble_instruction('addi $t0, $t1, 100')
        self.assertEqual(code, 0x21280064)

    def test_addi_negative(self):
        # addi $t0, $zero, -1
        code = self.asm.assemble_instruction('addi $t0, $zero, -1')
        self.assertEqual(code, 0x2008FFFF)

    def test_lw_instruction(self):
        # lw $t0, 0($sp) -> opcode=0x23, rs=$sp(29), rt=$t0(8), offset=0
        code = self.asm.assemble_instruction('lw $t0, 0($sp)')
        self.assertEqual(code, 0x8FA80000)

    def test_lw_with_offset(self):
        # lw $t0, 4($sp)
        code = self.asm.assemble_instruction('lw $t0, 4($sp)')
        self.assertEqual(code, 0x8FA80004)

    def test_sw_instruction(self):
        # sw $t0, 0($sp) -> opcode=0x2B
        code = self.asm.assemble_instruction('sw $t0, 0($sp)')
        self.assertEqual(code, 0xAFA80000)

    def test_lui_instruction(self):
        # lui $t0, 0x1234 -> opcode=0x0F, rt=$t0(8), imm=0x1234
        code = self.asm.assemble_instruction('lui $t0, 0x1234')
        self.assertEqual(code, 0x3C081234)


class TestJTypeInstructions(unittest.TestCase):
    """Test J-type instruction encoding"""

    def setUp(self):
        self.asm = Assembler()

    def test_j_instruction(self):
        # j 0x00400000 -> opcode=0x02, target=0x100000
        code = self.asm.assemble_instruction('j 0x00400000')
        self.assertEqual(code, 0x08100000)

    def test_jal_instruction(self):
        # jal 0x00400000 -> opcode=0x03
        code = self.asm.assemble_instruction('jal 0x00400000')
        self.assertEqual(code, 0x0C100000)


class TestDisassembler(unittest.TestCase):
    """Test instruction disassembly"""

    def setUp(self):
        self.disasm = Disassembler()

    def test_disassemble_add(self):
        result = self.disasm.disassemble_r_type(0x012A4020)
        self.assertEqual(result, 'add $t0, $t1, $t2')

    def test_disassemble_sub(self):
        result = self.disasm.disassemble_r_type(0x02328022)
        self.assertEqual(result, 'sub $s0, $s1, $s2')

    def test_disassemble_sll(self):
        result = self.disasm.disassemble_r_type(0x00094100)
        self.assertEqual(result, 'sll $t0, $t1, 4')

    def test_disassemble_jr(self):
        result = self.disasm.disassemble_r_type(0x03E00008)
        self.assertEqual(result, 'jr $ra')

    def test_disassemble_nop(self):
        result = self.disasm.disassemble_r_type(0x00000000)
        self.assertEqual(result, 'nop')

    def test_disassemble_addi(self):
        result = self.disasm.disassemble_i_type(0x21280064)
        self.assertEqual(result, 'addi $t0, $t1, 100')

    def test_disassemble_lui(self):
        result = self.disasm.disassemble_i_type(0x3C081234)
        self.assertEqual(result, 'lui $t0, 4660')  # 0x1234 = 4660


class TestLabelResolution(unittest.TestCase):
    """Test label handling in assembler"""

    def setUp(self):
        self.asm = Assembler()

    def test_first_pass_labels(self):
        lines = [
            'start:',
            '    add $t0, $t1, $t2',
            'loop:',
            '    addi $t0, $t0, 1',
            '    j loop',
        ]
        self.asm.first_pass(lines)
        self.assertEqual(self.asm.labels['start'], 0)
        self.assertEqual(self.asm.labels['loop'], 4)


class TestRoundTrip(unittest.TestCase):
    """Test assembling and disassembling produces consistent results"""

    def test_roundtrip_r_type(self):
        asm = Assembler()
        disasm = Disassembler()

        instructions = [
            'add $t0, $t1, $t2',
            'sub $s0, $s1, $s2',
            'and $a0, $a1, $a2',
            'or $v0, $v1, $a0',
            'slt $t0, $t1, $t2',
            'jr $ra',
            'nop',
        ]

        for instr in instructions:
            code = asm.assemble_instruction(instr)
            result = disasm.disassemble_r_type(code)
            self.assertEqual(result, instr, f"Roundtrip failed for: {instr}")

    def test_roundtrip_shift(self):
        asm = Assembler()
        disasm = Disassembler()

        instructions = [
            'sll $t0, $t1, 4',
            'srl $t0, $t1, 8',
        ]

        for instr in instructions:
            code = asm.assemble_instruction(instr)
            result = disasm.disassemble_r_type(code)
            self.assertEqual(result, instr)


class TestFileIO(unittest.TestCase):
    """Test file-based assembly and disassembly"""

    def test_assemble_file(self):
        asm = Assembler()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False) as f:
            f.write('add $t0, $t1, $t2\n')
            f.write('sub $s0, $s1, $s2\n')
            input_file = f.name

        output_file = input_file.replace('.asm', '.bin')

        try:
            count = asm.assemble(input_file, output_file)
            self.assertEqual(count, 2)

            with open(output_file, 'rb') as f:
                data = f.read()
            self.assertEqual(len(data), 8)  # 2 instructions * 4 bytes
        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_disassemble_file(self):
        disasm = Disassembler()

        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            f.write(struct.pack('>I', 0x012A4020))  # add $t0, $t1, $t2
            f.write(struct.pack('>I', 0x02328022))  # sub $s0, $s1, $s2
            input_file = f.name

        output_file = input_file.replace('.bin', '.asm')

        try:
            count = disasm.disassemble(input_file, output_file)
            self.assertEqual(count, 2)

            with open(output_file, 'r') as f:
                content = f.read()
            self.assertIn('add $t0, $t1, $t2', content)
            self.assertIn('sub $s0, $s1, $s2', content)
        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)


if __name__ == '__main__':
    unittest.main()
