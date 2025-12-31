"""
Roundtrip test: assemble -> disassemble -> reassemble and verify binaries match.
Run with: python3 test_roundtrip.py
"""

import os
import tempfile
from main import Assembler, Disassembler


def test_roundtrip(input_file):
    """Test that assembling, disassembling, and reassembling produces identical binary."""
    name = os.path.basename(input_file).replace('.asm', '')

    with tempfile.TemporaryDirectory() as tmpdir:
        original_bin = os.path.join(tmpdir, f'{name}_original.bin')
        disasm_asm = os.path.join(tmpdir, f'{name}_disasm.asm')
        reassembled_bin = os.path.join(tmpdir, f'{name}_reassembled.bin')

        # Step 1: Assemble original
        asm = Assembler()
        asm.assemble(input_file, original_bin)

        # Step 2: Disassemble
        disasm = Disassembler()
        disasm.disassemble(original_bin, disasm_asm)

        # Step 3: Reassemble
        asm2 = Assembler()
        asm2.assemble(disasm_asm, reassembled_bin)

        # Step 4: Compare binaries
        with open(original_bin, 'rb') as f:
            original_data = f.read()
        with open(reassembled_bin, 'rb') as f:
            reassembled_data = f.read()

        return original_data == reassembled_data


def main():
    print("=== MIPS Assembler/Disassembler Roundtrip Test ===\n")

    passed = 0
    failed = 0

    # Test fizzbuzz
    if os.path.exists('fizzbuzz.asm'):
        print("Testing fizzbuzz.asm... ", end='')
        try:
            if test_roundtrip('fizzbuzz.asm'):
                print("PASSED")
                passed += 1
            else:
                print("FAILED")
                failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1

    # Test examples directory
    if os.path.isdir('examples'):
        for filename in sorted(os.listdir('examples')):
            if filename.endswith('.asm'):
                filepath = os.path.join('examples', filename)
                print(f"Testing {filename}... ", end='')
                try:
                    if test_roundtrip(filepath):
                        print("PASSED")
                        passed += 1
                    else:
                        print("FAILED")
                        failed += 1
                except Exception as e:
                    print(f"ERROR: {e}")
                    failed += 1

    print(f"\n=== Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")
        exit(1)


if __name__ == '__main__':
    main()
