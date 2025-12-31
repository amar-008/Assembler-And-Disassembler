# Greatest Common Divisor (Euclidean algorithm)
# Inputs: $a0 = a, $a1 = b
# Output: $v0 = gcd(a, b)

    addi $a0, $zero, 48     # a = 48
    addi $a1, $zero, 18     # b = 18

loop:
    beq $a1, $zero, done    # if b == 0, return a

    # Compute a % b using repeated subtraction
    add $t0, $a0, $zero     # temp = a

mod_loop:
    slt $t1, $t0, $a1       # t1 = (temp < b)
    bne $t1, $zero, mod_done
    sub $t0, $t0, $a1       # temp -= b
    j mod_loop

mod_done:
    add $a0, $a1, $zero     # a = b
    add $a1, $t0, $zero     # b = temp (which is a % b)
    j loop

done:
    add $v0, $a0, $zero     # return a
    jr $ra
