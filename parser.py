import sys
from lexer import *

#Parser object keeps track of current troken and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

        self.cur_token = None
        self.peek_token = None
        self.next_token()
        self.next_token() #Call twice to init current and peek

    #Return true if the current token matches
    def check_token(self, kind):
        return kind == self.cur_token.kind

    #Return true if the next token matches
    def check_peek(self, kind):
        return kind == self.peek_token.kind

    #Try to match current token. If not, error. Advances the current token
    def match(self, kind):
        if not self.check_token(kind):
            self.abort("Expected " + kind.name + ", got " + self.cur_token.kind.name)
        self.next_token()

    #Advances the current token
    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.get_token()
        #Lexer handles EOF

    def abort(self, messages):
        sys.exit("Error: " + message)

    #Production rules

    # program ::= {statement}
    def program(self):
        print("PROGRAM")

        #Parse all statements in the program
        while not self.check_token(TokenType.EOF):
            self.statement()


    #Define grammar rules
    def statement(self):
        #Check first token to see what kind of statement it is
        if self.check_token(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.next_token()

            if self.check_token(TokenType.STRING):
                #Simple string
                self.next_token()
            else:
                #Expect an expression
                self.expression()

        #Newline
        self.nl()


    def nl(self):
        print("NEWLINE")

        #Require at least one newline
        self.match(TokenType.NEWLINE)
        #Allow extra newlines too
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
