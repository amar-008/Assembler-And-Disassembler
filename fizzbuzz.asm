# FizzBuzz in MIPS32 Assembly
# Prints numbers 1-15, replacing multiples of 3 with "Fizz",
# multiples of 5 with "Buzz", and multiples of both with "FizzBuzz"

main:
    addi $t0, $zero, 1      # counter i = 1
    addi $t1, $zero, 16     # limit = 16 (loop while i < 16)
    
loop:
    beq $t0, $t1, end       # if i == 16, exit
    
    # Check if divisible by 15 (3*5)
    addi $t2, $zero, 15
    add $t3, $zero, $t0     # copy i to t3
    
check_fizzbuzz:
    slt $t4, $t3, $t2       # if t3 < 15
    bne $t4, $zero, check_fizz
    sub $t3, $t3, $t2       # t3 = t3 - 15
    beq $t3, $zero, print_fizzbuzz
    
check_fizz:
    addi $t2, $zero, 3
    add $t3, $zero, $t0     # reset t3 = i
    
fizz_loop:
    slt $t4, $t3, $t2       # if t3 < 3
    bne $t4, $zero, check_buzz
    sub $t3, $t3, $t2       # t3 = t3 - 3
    beq $t3, $zero, print_fizz
    j fizz_loop
    
check_buzz:
    addi $t2, $zero, 5
    add $t3, $zero, $t0     # reset t3 = i
    
buzz_loop:
    slt $t4, $t3, $t2       # if t3 < 5
    bne $t4, $zero, print_number
    sub $t3, $t3, $t2       # t3 = t3 - 5
    beq $t3, $zero, print_buzz
    j buzz_loop
    
print_fizzbuzz:
    # In real system, would print "FizzBuzz"
    # Here we store a marker value
    addi $v0, $zero, 15     # marker for FizzBuzz
    j increment
    
print_fizz:
    # Store marker for Fizz
    addi $v0, $zero, 3      # marker for Fizz
    j increment
    
print_buzz:
    # Store marker for Buzz
    addi $v0, $zero, 5      # marker for Buzz
    j increment
    
print_number:
    # Store the number itself
    add $v0, $zero, $t0     # marker for number
    
increment:
    addi $t0, $t0, 1        # i++
    j loop
    
end:
    # Program end
    jr $ra                  # return