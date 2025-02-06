import sys
from lexer import *

#Parser object keeps track of current troken and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set() # All variables declared so far
        self.labels_declared = set() # All labels declared so far
        self.labels_gotod = set() # All labels goto'ed

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
        self.emitter.header_line("#include <stdio.h>")
        self.emitter.header_line("int main(void){")

        # Skip excess newlines
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        # Parse all statements in the program
        while not self.check_token(TokenType.EOF):
            self.statement()

        self.emitter.emit_line("return 0;")
        self.emitter.emit_line("}")

        # Verify each label referenced in a GOTO is declared
        for label in self.labels_gotod:
            if label not in self.labels_declared:
                self.abort("Attempting to GOTO undeclared label: " + label)


    # Define grammar rules
    def statement(self):
        """
        - Check first token to see what kind of statement it is
        """
        #### PRINT (expression | string) ####
        if self.check_token(TokenType.PRINT):
            self.next_token()

            if self.check_token(TokenType.STRING):
                # Simple string
                self.emitter.emit_line("printf(\"" + self.cur_token.text + "\\n\");")
                self.next_token()
            else:
                # Expect an expression
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emit_line("));")

        #### IF comparison "THEN" block "ENDIF"
        elif self.check_token(TokenType.IF):
            self.next_token()
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emit_line("){")

            # Zero or more statements in body
            while not self.check_token(TokenType.ENDIF):

        #Newline
        self.nl()


    def nl(self):
        print("NEWLINE")
        #Require at least one newline
        self.match(TokenType.NEWLINE)
        #Allow extra newlines too
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
