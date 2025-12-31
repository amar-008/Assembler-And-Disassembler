# MIPS32 Assembler & Disassembler

A bidirectional translation toolchain that converts MIPS32 assembly language to machine code and vice versa.

## Features

- **Two-pass assembler** with symbol table for forward reference resolution
- **Disassembler** that reconstructs assembly from raw binary
- **18 MIPS instructions** across R-type, I-type, and J-type formats
- **Label support** for branches and jumps
- **Roundtrip verification** - assemble, disassemble, reassemble produces identical binaries

## Supported Instructions

| Type | Instructions |
|------|-------------|
| **R-Type** | `add`, `sub`, `and`, `or`, `xor`, `slt`, `sll`, `srl`, `jr` |
| **I-Type** | `addi`, `slti`, `lw`, `sw`, `beq`, `bne`, `lui` |
| **J-Type** | `j`, `jal` |
| **Special** | `nop` |

## Usage

```bash
# Assemble: convert .asm to binary
python3 main.py assemble input.asm output.bin

# Disassemble: convert binary to .asm
python3 main.py disassemble input.bin output.asm
```

## Examples

```bash
# Assemble the FizzBuzz example
python3 main.py assemble fizzbuzz.asm fizzbuzz.bin

# Disassemble it back
python3 main.py disassemble fizzbuzz.bin output.asm

# Run unit tests
python3 -m pytest test_mips.py -v

# Run roundtrip verification
python3 test_roundtrip.py
```

## Project Structure

```
├── main.py              # Assembler and Disassembler implementation
├── test_mips.py         # Unit tests (34 test cases)
├── test_roundtrip.py    # Roundtrip verification tests
├── fizzbuzz.asm         # FizzBuzz example program
└── examples/
    ├── factorial.asm    # Factorial calculation
    ├── fibonacci.asm    # Fibonacci sequence
    ├── gcd.asm          # Euclidean GCD algorithm
    └── sum_array.asm    # Array summation
```

## Technical Details

### Instruction Encoding

Each MIPS instruction is encoded as a 32-bit word:

**R-Type Format:**
```
| opcode (6) | rs (5) | rt (5) | rd (5) | shamt (5) | funct (6) |
```

**I-Type Format:**
```
| opcode (6) | rs (5) | rt (5) | immediate (16) |
```

**J-Type Format:**
```
| opcode (6) | address (26) |
```

### Two-Pass Assembly

1. **First pass**: Scan for labels and build symbol table with addresses
2. **Second pass**: Encode instructions, resolving label references

### Key Implementation Details

- PC-relative branch offset calculation: `offset = (target - (PC + 4)) / 4`
- Signed immediate values use two's complement representation
- Big-endian binary output format

## Testing

```bash
# Run all unit tests
python3 -m pytest test_mips.py -v

# Run with coverage
python3 -m pytest test_mips.py --cov=main

# Roundtrip test all examples
python3 test_roundtrip.py
```

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Author

Amarendra Mishra
San Diego State University
