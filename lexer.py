from exceptions import *

class Token(object):
    __match_args__ = ["typ", "val"]

    def __init__(self, tokenType, tokenValue=""):
        self.typ = tokenType
        self.val = tokenValue

    def __repr__(self):
        return f"Token({repr(self.typ)}, {repr(self.val)})"

    def __eq__(self, other):
        return isinstance(other, Token) and (self.typ, self.val) == (other.typ, other.val)

class Lexer(object):
    keywords = {
        "is" : "IS_",
        "while" : "WHI", 
        "true" : "TRU", 
        "false" : "FAL", 
        "do" : "DO_",
        "for" : "FOR", 
        "each" : "EAC", 
        "element" : "ELE", 
        "of" : "OF_",
        "if" : "IF_", 
        "then" : "THE", 
        "otherwise" : "OTH",
        "match" : "MAT", 
        "with" : "WIT", 
        "pattern" : "PAT",
        "output" : "OUT",
        "function" : "FUN",
        "nothing" : "NUL",
        "endloop" : "END",
        "skiploop" : "SKI",
        "query" : "QUE",
        "extract" : "EXT",
        "select" : "SEL",
        "order" : "ORD",
        "unique" : "UNI",
        "reverse" : "REV",
        "apply" : "APP",
        "grouping" : "GRO",
        "collate" : "COL",
        "keep" : "KEE",
        "take" : "TAK",
        "drop" : "DRO",
        "combine" : "CMB",
        "join" : "JOI",
    }

    escapeChars = {
        "t" : "\t",
        "n" : "\n",
        "\\" : "\\",
    }

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.currentChar = self.text[self.pos]

    def error(self, message=""):
        raise LexerException(message)

    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.currentChar = None
        else:
            self.currentChar = self.text[self.pos]

    def skipWhitespace(self):
        while self.currentChar != None and self.currentChar.isspace():
            self.advance()

    def skipComment(self):
        while self.currentChar != None and self.currentChar != "\n":
            self.advance()
        self.advance()

    def extractInteger(self):
        result = ''
        while self.currentChar != None and self.currentChar.isdigit():
            result += self.currentChar
            self.advance()
        return int(result)

    def extractString(self):
        result = ''
        self.advance()
        while self.currentChar != '"':
            if self.currentChar == None:
                self.error("End of string not found")
            elif self.currentChar == "\\":
                self.advance()
                result += Lexer.escapeChars.get(self.currentChar, "\\")
                self.advance()
            else:
                result += self.currentChar
                self.advance()
        self.advance()
        return result

    def extractVariable(self):
        result = ''
        while self.currentChar != None and self.currentChar.isalnum():
            result += self.currentChar
            self.advance()
        if result in Lexer.keywords:
            return Token(Lexer.keywords[result])
        return Token("VAR", result)

    def getNextToken(self):
        while self.currentChar != None:
            symbol = self.currentChar
            match symbol:
                case "\n" | "\t" | "\r" | " ": self.skipWhitespace()
                case "$": self.skipComment()
                case "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
                    return Token("INT", self.extractInteger())
                case "(": self.advance(); return Token("LPA", symbol)
                case ")": self.advance(); return Token("RPA", symbol)
                case "[": self.advance(); return Token("LSB", symbol)
                case "]": self.advance(); return Token("RSB", symbol)
                case ",": self.advance(); return Token("COM", symbol)
                case "+": self.advance(); return Token("ADD", symbol)
                case "-": self.advance(); return Token("SUB", symbol)
                case "*": self.advance(); return Token("MUL", symbol)
                case "/": self.advance(); return Token("DIV", symbol)
                case "^": self.advance(); return Token("POW", symbol)
                case "%": self.advance(); return Token("MOD", symbol)
                case "&": self.advance(); return Token("AND", symbol)
                case "|": self.advance(); return Token("OR_", symbol)
                case "!": self.advance(); return Token("NOT", symbol)
                case "<": self.advance(); return Token("LES", symbol)
                case "=": self.advance(); return Token("EQU", symbol)
                case ">": self.advance(); return Token("GRT", symbol)
                case "_": self.advance(); return Token("WIL", symbol)
                case "@": self.advance(); return Token("AT_", symbol)
                case '"': return Token("STR", self.extractString())
                case _: return self.extractVariable()
        return Token("EOF", None)