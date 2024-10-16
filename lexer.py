import enum
import sys

class Lexer:
    def __init__(self, input):
        self.source = input + '\n' # Source code to lex as string, append newline
        self.cur_char = ''
        self.cur_pos = -1
        self.next_char()

    # Process next char
    def next_char(self):
        self.cur_pos += 1
        if self.cur_pos >= len(self.source):
            self.cur_char = '\0' #EOF
        else:
            self.cur_char = self.source[self.cur_pos]

    # Return the lookahead char
    def peek(self):
        if self.cur_pos + 1 >= len(self.source):
            return '\0'
        return self.source[self.cur_pos+1]

    # Invalid token found, print error message and exit
    def abort(self, message):
        sys.exit("Lexing error: " + message)

    # Skip whitespace except newlines which indicate EOF
    def skip_whitespace(self):
        while self.cur_char == ' ' or self.cur_char == '\t' or self.cur_char == '\r':
            self.next_char()


    # Skip comments in the code
    def skip_comment(self):
        if self.cur_char == '#':
            while self.cur_char != '\n':    #Find end of comment
                self.next_char()
    
    # Return next token
    def get_token(self):
        self.skip_whitespace()
        self.skip_comment()
        token = None

        # Check the first character to decide what kind of token it is
        if self.cur_char == '+':
            token = Token(self.cur_char, TokenType.PLUS)    #Plus token
        elif self.cur_char == '-':
            token = Token(self.cur_char, TokenType.MINUS)    #Minus token
        elif self.cur_char == '*':
            token = Token(self.cur_char, TokenType.ASTERISK)    #Asterisk token
        elif self.cur_char == '/':
            token = Token(self.cur_char, TokenType.SLASH)    #Slash token
        elif self.cur_char == '\n':
            token = Token(self.cur_char, TokenType.NEWLINE)    #Newline token
        elif self.cur_char == '\0':
            token = Token(self.cur_char, TokenType.EOF)    #EOF Token

        #### Double char tokens #####
        elif self.cur_char == '=':
            #Check whether token is '=' or an '=='
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.EQEQ)    #Equal token
            else:
                token = Token(self.cur_char, TokenType.EQ)      #Assign token
        
        elif self.cur_char == '>':
            #Check whether token is '>' or '>='
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.GTEQ)
            else:
                token = Token(self.cur_char, TokenType.GT)
        
        elif self.cur_char == '<':
            #Check whether token is '<' or '<='
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.LTEQ)
            else:
                token = Token(self.cur_char, TokenType.LT)

        elif self.cur_char == '!':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.NOTEQ)
            else:
                self.abort("Expected '!=', got '!'" + self.peek())
        
        #### Allow printing strings ####
        elif self.cur_char == '\"':
            # Get characters between quotations
            self.next_char()
            start_pos = self.cur_pos
            while self.cur_char != '\"':
                # Dont allow special chars in strings, e.i escape chars, newlines, tabs etc
                if self.cur_char == '\r' or self.cur_char == '\n' or self.cur_char == '\t' or self.cur_char == '\\' or self.cur_char == '%':
                    self.abort("Illegal character in string")
                self.next_char()
            token_text = self.source[start_pos : self.cur_pos] # Get substring
            token = Token(token_text, TokenType.STRING)

        #### Handling digits ####
        elif self.cur_char.isdigit():
            # Leading char is a digit, so must be a number
            # Get consecutive digits and decimals
            start_pos = self.cur_pos
            while self.peek().isdigit():
                self.next_char()
            if self.peek() == '.':      #Decimal
                self.next_char()
                # Must be atleast one digit after decimal
                if not self.peek().isdigit():
                    self.abort("Illegal character in number")
                while self.peek().isdigit():
                    self.next_char()

            token_text = self.source[start_pos : self.cur_pos +1] #Get the substring
            token = Token(token_text, TokenType.NUMBER)

        #### Identifiers & Keywords ####
        elif self.cur_char.isalpha():
            # Leading char is a letter, so this must be an identifier or a keyword
            # Get all consecutive alpha-numeric chars
            start_pos = self.cur_pos
            while self.peek().isalnum():
                self.next_char()
            #Check if the token is in the list of keywords
            token_text = self.source[start_pos : self.cur_pos + 1] # Get the substring
            keyword = Token.check_if_keyword(token_text)
            if keyword == None: #Identifier
                token = Token(token_text, TokenType.IDENT)
            else:
                token = Token(token_text, keyword)

        else:
            #Unknown token
            self.abort("Unknown token: " + self.cur_char)
        
        self.next_char()
        return token


# Token contains the original text and the type of token
class Token:
    def __init__(self, token_text, token_kind):
        self.text = token_text      #The tokens actual text (identifiers, strings & numbers)
        self.kind = token_kind      #The type of token

    @staticmethod
    def check_if_keyword(token_text):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX
            if kind.name == token_text and kind.value >= 100 and kind.value < 200:
                return kind
        return None


class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    COLON = 4
    #Keywords
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107      ####
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    #Gyppe specifics
    FOR = 112
    LIFT = 113
    LOWER = 114
    DRIVE = 115
    REVERSE = 116
    AND = 117
    WAIT = 118
    LOGON = 119
    INTERVAL = 120
    #Operators
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211