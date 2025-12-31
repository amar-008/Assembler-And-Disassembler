# Sum array elements
# Assumes array base address in $a0, length in $a1
# Result stored in $v0

    addi $v0, $zero, 0      # sum = 0
    addi $t0, $zero, 0      # i = 0

loop:
    beq $t0, $a1, done      # if i == length, exit
    sll $t1, $t0, 2         # offset = i * 4
    add $t1, $a0, $t1       # address = base + offset
    lw $t2, 0($t1)          # load array[i]
    add $v0, $v0, $t2       # sum += array[i]
    addi $t0, $t0, 1        # i++
    j loop

done:
    jr $ra                  # return
