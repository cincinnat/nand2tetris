// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

// R2 = 0
// mask = 1
// x = R0
// i = 31
// do:
//    if R1 & mask:
//        R2 = R2 + x
//    x = x * 2
//    mask = x * 2
//    i = i - 1
// while i >= 0

    // R2 = 0
    @R2
    M=0

    // mask = R0
    @mask
    M=1

    // x = R0
    @R0
    D=M
    @x
    M=D

    // i = 31
    @31
    D=A
    @i
    M=D

// do
(LOOP)
    // if R1 & mask
    @R1
    D=M
    @mask
    D=D&M
    @NEXT
    D; JEQ

        // R2 = R2 + x
        @x
        D=M
        @R2
        M=M+D

(NEXT)
    // x = x * 2
    @x
    D=M
    M=M+D

    // mask = mask * 2
    @mask
    D=M
    M=M+D

    // i = i - 1
    @i
    M=M-1

    // while i > 0
    D=M
    @LOOP
    D; JGT
// end LOOP

(END)
    @END
    0; JMP

