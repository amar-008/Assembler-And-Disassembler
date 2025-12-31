# Factorial calculation
# Computes factorial of n (stored in $a0)
# Result stored in $v0

# Initialize: n = 5, result = 1
    addi $a0, $zero, 5      # n = 5
    addi $v0, $zero, 1      # result = 1

loop:
    beq $a0, $zero, done    # if n == 0, exit
    add $t0, $v0, $zero     # temp = result
    addi $t1, $zero, 0      # counter = 0

multiply:
    beq $t1, $a0, next      # if counter == n, done multiplying
    add $v0, $v0, $t0       # result += temp
    addi $t1, $t1, 1        # counter++
    j multiply

next:
    addi $a0, $a0, -1       # n--
    j loop

done:
    jr $ra                  # return
