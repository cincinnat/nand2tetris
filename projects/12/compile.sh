#! /bin/bash

function jack {
    bash ~/projects/nand2tetris/nand2tetris/tools/JackCompiler.sh "$@"
}

for name in *.jack; do
    name="${name%.*}"
    cp ~/projects/nand2tetris/nand2tetris/tools/OS/*.vm ${name}Test/
    jack ${name}.jack
    cp ${name}.vm ${name}Test/
    jack ${name}Test/Main.jack
done
