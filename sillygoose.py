from lexer import *
from parser import *
from emitter import *
import sys

def main():
    print("Compiler In Working")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source-file as argument")
    with open(sys.argv[1], 'r') as input_file:
        input_src = input_file.read()

    #Initialize the lexer and parser
    lexer = Lexer(input_src)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)

    parser.program() #Start parsing
    print("Parsing complete")

main()
