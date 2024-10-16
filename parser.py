import sys
from lexer import *

# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter
        self.symbols = set()            #Variables declared so far
        self.labels_declared = set()    #Labels declared so far
        self.labels_goto = set()        #Labels goto'ed so far
        self.cur_token = None
        self.peek_token = None
        self.next_token()
        self.next_token() #Calling this twice to initialize 'current' and 'peek'

    #Return true if the current token matches
    def check_token(self, kind):
        return kind == self.cur_token.kind

    #Return true if the next token matches
    def check_peek(self, kind):
        return kind == self.peek_token.kind

    #Try to match current token. If not, error. Advances the current token
    def match(self, kind):
        if not self.check_token(kind):
            self.abort("Expected: " + kind.name + ", got " + self.cur_token.kind.name)
        self.next_token()

    #Advances the current token
    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.get_token()
        # Dont need to handle passing the EOF, lexer takes care of that.

    def abort(self, message):
        sys.exit("Error: " + message)

    # nl ::= '\n'+
    def nl(self):
        print("NEWLINE")
        #Require atleast one newline
        self.match(TokenType.NEWLINE)
        #But will allow extra newlines too
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        print("COMPARISON")
        self.expression()
        #Must be atleast one comparison operator and another expression
        if self.is_comparison_operator():
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.cur_token.text)
        #Can have 0 or more comparison operator and expression
        while self.is_comparison_operator():
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.expression()

    #Return true if the current token is a comparison operator
    def is_comparison_operator(self):
        return (self.check_token(TokenType.GT) or self.check_token(TokenType.GTEQ) or 
        self.check_token(TokenType.LT) or self.check_token(TokenType.LTEQ) or 
        self.check_token(TokenType.EQEQ) or self.check_token(TokenType.NOTEQ))

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        print("EXPRESSION")
        self.term()
        #Can have 0 or more +/- and expressions
        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.term()

    # term ::= unary {( "/" | "*") unary}
    def term(self):
        print("TERM")
        self.unary()
        #Can have 0 or more *// and expressions
        while self.check_token(TokenType.ASTERISK) or self.check_token(TokenType.SLASH):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        print("UNARY")
        #Optional unary +/-
        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
        self.primary()

    # how to do this better? 
    def indent(self):
        self.emitter.emit("    ")

    # primary ::= number | ident
    def primary(self):
        print("PRIMARY (" + self.cur_token.text + ")")
        if self.check_token(TokenType.NUMBER):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
        elif self.check_token(TokenType.IDENT):
            #Ensure the variable exists
            if self.cur_token.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.cur_token.text)
            self.emitter.emit(self.cur_token.text)
            self.next_token()
        else:
            # Error
            self.abort("Unexpected token at " + self.cur_token.text)

    
    ### Main function, starting and finishing the parsing
    def program(self):
        #Boilerplate
        self.emitter.header_line('shock_mock_path = "rigs:dhu3s:pi6:backend:track_1:network_1:shock_mock_process"')
        self.emitter.header_line('tcs_mock_path="rigs:dhu3s:pi6:backend:track_1:network_1:tcs_mock_process"')
        self.emitter.header_line('keypad_mock_path = "rigs:dhu3s:pi6:backend:track_1:network_1:keypad_mock_process"')
        self.emitter.header_line('connection = PytteConnection("10.151.112.69:6388", "benjamin")')
        self.emitter.header_line("import threading")
        self.emitter.header_line("from gyppe_core import *")
        self.emitter.header_line("def main():")
        self.indent()
        

        #Skip excess newlines at the start of the input
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        #Parse all the statements in the program
        while not self.check_token(TokenType.EOF):
            print("TOKEN: ", self.cur_token.text)
            self.statement()

        #Finishing boilerplate
        self.emitter.emit_line("logoff(2)")
        self.emitter.emit_line("\n")
        self.emitter.emit_line("main()")

        #Check that each label referenced in a GOTO is declared
        for label in self.labels_goto:
            if label not in self.labels_declared:
                self.abort("Attempting to GOTO to undeclared label: " + label)

    #### Production rules ####
    def statement(self):    #Check the first token decide what kind of statement it is
        ### Rule: statement ::= "PRINT" (expression | string) nl
        if self.check_token(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.next_token()
            if self.check_token(TokenType.STRING):
                #Simple string
                self.emitter.emit_line("print(\"" + self.cur_token.text + "\")")
                self.next_token()
            else:
                #Expect an expression
                self.emitter.emit("print( + ")
                self.expression()
                self.emitter.emit_line(")")

        ### Rule: | "IF" comparison "THEN" nl {statement} "ENDIF" nl
        elif self.check_token(TokenType.IF):
            print("STATEMENT-IF")
            self.next_token()
            self.emitter.emit("if(")
            self.comparison()
            self.match(TokenType.THEN)
            self.emitter.emit("):")
            self.nl()
            #Zero or more statements in the body
            while not self.check_token(TokenType.ENDIF):
                self.statement()
            self.match(TokenType.ENDIF)

        ### Rule: | "WHILE" comparison "REPEAT" nl {statement nl} "ENDWHILE" nl
        elif self.check_token(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.next_token()
            self.emitter.emit("while ")
            self.comparison()
            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emit_line(":")
            #Zero or more statements in the loop body
            while not self.check_token(TokenType.ENDWHILE):
                self.statement()
            self.match(TokenType.ENDWHILE)

        ### Rule: | "LABEL" ident nl
        elif self.check_token(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.next_token()
            #Make sure label doesn't already exist, cannot declare same LABEL twice
            if self.cur_token.text in self.labels_declared:
                self.abort("Label already exists: " + self.cur_token.text)
            self.labels_declared.add(self.cur_token.text)   #Add label to set
            self.emitter.emit_line(self.cur_token.text + ":")
            self.match(TokenType.IDENT)

        ### Rule: | "GOTO" ident nl
        elif self.check_token(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.next_token()
            self.labels_goto.add(self.cur_token.text)
            self.emitter.emit_line("goto " + self.cur_token.text)
            self.match(TokenType.IDENT)

        ### Rule: | "LET" ident "=" expression nl
        elif self.check_token(TokenType.LET):
            print("STATEMENT-LET")
            self.next_token()
            #Check if ident exists in symbol-table. If not , declare it.
            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
                self.emitter.header_line(self.cur_token.text + " = None")
            self.emitter.emit_line(self.cur_token.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()

        ### Rule: | "INPUT" ident nl
        elif self.check_token(TokenType.INPUT):
            print("STATEMENT-INPUT")
            self.next_token()
            #If variable doesn't exist, declare it.
            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
                self.emitter.header_line("float " + self.cur_token.text)
            self.match(TokenType.IDENT)

        ### Rule: | "LOGON" primary
        elif self.check_token(TokenType.LOGON):
            print("STATEMENT-LOGON")
            self.next_token()
            self.emitter.emit("logon(")
            self.primary()
            self.emitter.emit_line(")")
            self.indent()

        ### Rule: | "LIFT" (FOR primary, REPEAT primary)
        elif self.check_token(TokenType.LIFT):
            print("STATEMENT-LIFT")
            self.next_token() #Maybe do control for an AND token here
            self.emitter.emit("lift(")
            if self.check_token(TokenType.FOR):
                self.next_token()
                self.emitter.emit("duration=")
                self.primary()
                if self.check_token(TokenType.REPEAT):
                    self.next_token()
                    self.emitter.emit(", repeat=")
                    self.primary()
                    if self.check_token(TokenType.INTERVAL):
                        self.next_token()
                        self.emitter.emit(", interval=")
                        self.primary()
                                    
            elif self.check_token(TokenType.REPEAT):
                self.next_token()
                self.emitter.emit("repeat=")
                self.primary()
            self.emitter.emit_line(")")
            self.indent()

        ### Rule: | "LOWER" (FOR primary, REPEAT primary)
        elif self.check_token(TokenType.LOWER):
            print("STATEMENT-LOWER")
            self.next_token()
            self.emitter.emit("lower(")
            if self.check_token(TokenType.FOR):
                self.next_token()
                self.emitter.emit("duration=")
                self.primary()
                if self.check_token(TokenType.REPEAT):
                    self.next_token()
                    self.emitter.emit(", repeat=")
                    self.primary()
                    if self.check_token(TokenType.INTERVAL):
                        self.next_token()
                        self.emitter.emit(", interval=")
                        self.primary()
            
            elif self.check_token(TokenType.REPEAT):
                self.next_token()
                self.emitter.emit("repeat=")
                self.primary()
            self.emitter.emit_line(")")
            self.indent()

        ### Rule: | "DRIVE" ((AND STATEMENT), FOR primary, REPEAT primary)
        elif self.check_token(TokenType.DRIVE):
            print("STATEMENT-DRIVE")
            self.next_token()
            #Check for drive_and_xxx
            if self.check_token(TokenType.AND):
                self.emitter.emit("drive_and_")
                self.next_token()
                if self.check_token(TokenType.LIFT):
                    self.next_token()
                    self.emitter.emit("lift(")
                elif self.check_token(TokenType.LOWER):
                    self.next_token()
                    self.emitter.emit("lower(")
            else:
                self.emitter.emit("drive(")
            if self.check_token(TokenType.FOR):
                self.next_token()
                self.emitter.emit("duration=")
                self.primary()
            if self.check_token(TokenType.REPEAT):
                self.next_token()
                self.emitter.emit(", repeat=")
                self.primary()
                if self.check_token(TokenType.INTERVAL):
                        self.next_token()
                        self.emitter.emit(", interval=")
                        self.primary()
            self.emitter.emit_line(")")
            self.indent()

        ### Rule: | "REVERSE" ((AND STATEMENT), FOR primary, REPEAT primary)
        elif self.check_token(TokenType.REVERSE):
            print("STATEMENT-REVERSE")
            self.next_token()
            #Check for drive_and_xxx
            if self.check_token(TokenType.AND):
                self.emitter.emit("reverse_and_")
                self.next_token()
                if self.check_token(TokenType.LIFT):
                    self.next_token()
                    self.emitter.emit("lift(")
                elif self.check_token(TokenType.LOWER):
                    self.next_token()
                    self.emitter.emit("lower(")
            else:
                self.emitter.emit("reverse(")
            if self.check_token(TokenType.FOR):
                self.next_token()
                self.emitter.emit("duration=")
                self.primary()
            if self.check_token(TokenType.REPEAT):
                self.next_token()
                self.emitter.emit(", repeat=")
                self.primary()
                if self.check_token(TokenType.INTERVAL):
                        self.next_token()
                        self.emitter.emit(", interval=")
                        self.primary()
            self.emitter.emit_line(")")
            self.indent()

        ### Rule: | "WAIT" primary
        elif self.check_token(TokenType.WAIT):
            print("STATEMENT-WAIT")
            self.next_token()
            self.emitter.emit("wait(")
            self.primary()
            self.emitter.emit_line(")")
            self.indent()

        #Not a valid statement, Error!
        else:
            self.abort("Invalid statement at " + self.cur_token.text + " (" + self.cur_token.kind.name + ")")

        #Newline
        self.nl()

    





