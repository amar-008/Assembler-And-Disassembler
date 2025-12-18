# MIPS32 Assembler & Disassembler

**Author:** Amarendra Mishra  
**Institution:** San Diego State University (SDSU)  
**Class Year:** 2028  
**Language:** Python 3

## Overview

A simple assembler and disassembler for MIPS32 architecture that converts between assembly language and machine code.

## Supported Instructions

**R-Type:** add, sub, and, or, xor, slt, sll, srl, jr  
**I-Type:** addi, slti, lw, sw, beq, bne, lui  
**J-Type:** j, jal  
**Special:** nop

## Usage

**Assemble (Assembly → Binary):**
```bash
python3 mips_tools.py assemble input.asm output.bin
```

**Disassemble (Binary → Assembly):**
```bash
python3 mips_tools.py disassemble input.bin output.asm
```

## Examples

```bash
# Assemble FizzBuzz
python3 main.py assemble fizzbuzz.asm fizzbuzz.bin

# Disassemble back
python3 main.py disassemble fizzbuzz.bin fizzbuzz.asm

# Run tests
bash test_roundtrip.sh
```

## Files Included

- `mips_tools.py` - Main assembler/disassembler
- `fizzbuzz.asm` - FizzBuzz example program
- `fizzbuzz.bin` - Assembled FizzBuzz binary


