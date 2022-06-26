from lexer import *
from parser import *

def main():
    print("Compiler In Working")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source-file as argument")
    with open(sys.argv[1], 'r') as input_file:
        input = input_file.read()

    #Initialize the lexer and parser
    lexer = Lexer(input)
    parser = Parser(lexer)

    parser.program() #Start parsing
    print("Parsing complete")

main()
