// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.


// state: 1: uninitialized, 0: white, -1: black
@state
M=1

// fill the screen with white
@WHITE
0; JMP

// loop forever
(LOOP)
    // check if a key is pressed
    @KBD
    D=M;
    @WHITE
    D; JEQ

(BLACK)
    @color
    M=-1
    @FILL
    0; JMP

(WHITE)
    @color
    M=0

(FILL)
    // if color == state: goto LOOP
    @color
    D=M
    @state
    D=D-M;
    @LOOP
    D; JEQ

    // while i > 0
    @8192
    D=A
    @i
    M=D
(FILL_LOOP)
        // D=--i
        @i
        M=M-1
        D=M

        // addr = SCREEN + i
        @SCREEN
        D=D+A
        @addr
        M=D

        // *addr = color
        @color
        D=M
        @addr
        A=M
        M=D

        @i
        D=M;
        @FILL_LOOP
        D; JNE

    // state = color
    @color
    D=M
    @state
    M=D

@LOOP
0; JMP
