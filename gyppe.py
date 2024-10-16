from lexer import *
from parser import *
from emitter import *
import sys

def main():
    # Example program (will automatically call logoff at end of program):
    """
    LOGON 11111
    LIFT FOR 10
    LIFT FOR 10 AND DRIVE FOR 5
    WAIT(5)
    LOWER FOR 5 REPEAT 10 INTERVAL 2
    DRIVE AND LOWER FOR 2
    REVERSE AND LOWER FOR 2
    """
    ## How to use ##
    #1. compile sourcefile: python3.10 sg.py sourcefile.sg
    #2. run file: python3.10 workingpass.

    print("|--Sillygoose Compiler--|")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs sourcefile as argument")
    with open(sys.argv[1], 'r') as input_file:
        input = input_file.read()

    #Initialize the lexer and parser
    lexer = Lexer(input)
    emitter = Emitter("workingpass.py")
    parser = Parser(lexer, emitter)

    parser.program() #Start parsing
    emitter.write_file() #Write the output to file
    print("Parsing completed!")

main()
