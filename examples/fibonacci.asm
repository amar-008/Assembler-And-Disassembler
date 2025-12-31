# Fibonacci sequence generator
# Computes nth Fibonacci number (n in $a0)
# Result stored in $v0

    addi $a0, $zero, 10     # compute fib(10)

    # Base cases
    addi $t0, $zero, 1      # check if n <= 1
    slt $t1, $t0, $a0       # t1 = (1 < n)
    beq $t1, $zero, base    # if n <= 1, return n

    # Initialize: fib(0) = 0, fib(1) = 1
    addi $t0, $zero, 0      # prev = 0
    addi $t1, $zero, 1      # curr = 1
    addi $t2, $zero, 1      # i = 1

loop:
    beq $t2, $a0, done      # if i == n, exit
    add $t3, $t0, $t1       # next = prev + curr
    add $t0, $t1, $zero     # prev = curr
    add $t1, $t3, $zero     # curr = next
    addi $t2, $t2, 1        # i++
    j loop

base:
    add $v0, $a0, $zero     # return n
    jr $ra

done:
    add $v0, $t1, $zero     # return curr
    jr $ra
