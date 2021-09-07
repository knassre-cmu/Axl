from lexer import *
from abstract import *
from pattern import *
from exceptions import *
from query import *

import sys
sys.setrecursionlimit(150)

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.currentToken = self.lexer.getNextToken()

    def error(self, message=""):
        print(self.lexer.text[self.lexer.pos:])
        raise ParserException(message)

    def eat(self, *tokenTypes):
        if self.currentToken.typ in tokenTypes:
            self.currentToken = self.lexer.getNextToken()
        else:
            self.error(f"Expected {'/'.join(tokenTypes)} got {self.currentToken.typ}")

    def parse(self):
        return self.statements(True)

    def statements(self, topLevel=False):
        statements = []
        while True:
            token = self.currentToken
            match token.typ:
                case "EOF" | "RPA":
                    if token.typ == "EOF" and not topLevel:
                        self.error("Expected ')' instead of EOF")
                    if token.typ == "RPA" and topLevel:
                        self.error("Expected EOF instead of ')'")
                    return Statements(statements)
                case "END":
                    self.eat("END")
                    statements.append(Endloop())
                case "SKI":
                    self.eat("SKI")
                    statements.append(Skiploop())
                case "VAR":
                    statements.append(self.definition())
                case "OUT":
                    statements.append(self.output())
                case "IF_":
                    statements.append(self.conditional())
                case "WHI":
                    statements.append(self.whileLoop())
                case "FOR":
                    statements.append(self.forLoop())
                case "MAT":
                    statements.append(self.match())
                case _:
                    self.error(f"Expected start of a new statement instead of {token}")
    
    def definition(self):
        variables = self.variables()
        self.eat("IS_")
        self.eat("LPA")
        expressions = self.expressions()
        self.eat("RPA")
        return Definition(variables, expressions)

    def output(self):
        self.eat("OUT")
        return Output(self.expressions())

    def whileLoop(self):
        self.eat("WHI")
        self.eat("LPA")
        condition = self.expression()
        self.eat("RPA")
        self.eat("IS_")
        self.eat("TRU")
        self.eat("DO_")
        self.eat("LPA")
        body = self.statements()
        self.eat("RPA")
        return While(condition, body)

    def forLoop(self):
        self.eat("FOR")
        self.eat("EAC")
        self.eat("ELE")
        variable = self.currentToken
        self.eat("VAR")
        self.eat("OF_")
        self.eat("LPA")
        iterable = self.expression()
        self.eat("RPA")
        self.eat("DO_")
        self.eat("LPA")
        body = self.statements()
        self.eat("RPA")
        return For(variable, iterable, body)

    def conditional(self):
        self.eat("IF_")
        self.eat("LPA")
        condition = self.expression()
        self.eat("RPA")
        self.eat("IS_")
        self.eat("TRU")
        self.eat("THE")
        self.eat("DO_")
        self.eat("LPA")
        trueCode = self.statements()
        self.eat("RPA")
        if self.currentToken.typ == "OTH":
            self.eat("OTH")
            self.eat("DO_")
            self.eat("LPA")
            falseCode = self.statements()
            self.eat("RPA")
        else:
            falseCode = Statements([])
        return Conditional(condition, trueCode, falseCode)

    def match(self):
        self.eat("MAT")
        self.eat("LPA")
        expression = self.expression()
        self.eat("RPA")
        self.eat("WIT")
        self.eat("LPA")
        patterns = self.patterns()
        self.eat("RPA")
        return Match(expression, patterns)

    def patterns(self):
        patterns = []
        while True:
            token = self.currentToken
            match token.typ:
                case "RPA":
                    return patterns
                case "PAT":
                    self.eat("PAT")
                    self.eat("LPA")
                    pattern = self.pattern()
                    self.eat("RPA")
                    self.eat("SUB")
                    self.eat("GRT")
                    self.eat("LPA")
                    code = self.statements()
                    self.eat("RPA")
                    patterns.append((pattern, code))
                case _:
                    self.error(f"Expected ')' or another pattern instead of {token.typ}")

    def pattern(self):
        pattern = self.basePattern()
        while True:
            token = self.currentToken
            match token.typ:
                case "AND":
                    self.eat("AND")
                    right = self.basePattern()
                    pattern = PatternAnd(pattern, right)
                case "OR_":
                    self.eat("OR_")
                    right = self.basePattern()
                    pattern = PatternOr(pattern, right)
                case _:
                    return pattern

    def basePattern(self):
        while True:
            token = self.currentToken
            match token.typ:
                case "LSB":
                    self.eat("LSB")
                    return self.listPattern()
                case "MUL":
                    self.eat("MUL")
                    variable = self.currentToken.val
                    self.eat("VAR")
                    return PatternStar(variable)
                case "STR":
                    self.eat("STR")
                    return PatternString(token.val)
                case "VAR":
                    self.eat("VAR")
                    return PatternVariable(token.val)
                case "INT":
                    self.eat("INT")
                    return PatternNumber(token.val)
                case "TRU":
                    self.eat("TRU")
                    return PatternNumber(True)
                case "FAL":
                    self.eat("FAL")
                    return PatternNumber(False)
                case "WIL":
                    self.eat("WIL")
                    return Pattern()
                case _:
                    self.error(f"Unexpected pattern value {token.typ}")

    def listPattern(self):
        if self.currentToken.typ == "RSB":
            self.eat("RSB")
            return PatternList([])
        elements = [self.pattern()]
        while True:
            token = self.currentToken
            match token.typ:
                case "RSB":
                    self.eat("RSB")
                    return(PatternList(elements))
                case "COM":
                    self.eat("COM")
                    elements.append(self.pattern())
                case _:
                    self.error(f"Expected ',' or ']', not {token.typ}")

    def variables(self):
        variables = [self.currentToken.val]
        self.eat("VAR")
        while True:
            token = self.currentToken
            match token.typ:
                case "IS_" | "RPA":
                    return variables
                case "COM":
                    self.eat("COM")
                    variables.append(self.currentToken.val)
                    self.eat("VAR")
                case _:
                    self.error(f"Expected ',', 'is' or ')', not {token.typ}")

    def expressions(self):
        expressions = [self.expression()]
        while True:
            token = self.currentToken
            match token.typ:
                case "RPA":
                    return expressions
                case "COM":
                    self.eat("COM")
                    expressions.append(self.expression())
                case _:
                    self.error(f"Expected ',' or ')', not {token.typ}")

    def expression(self):
        match self.currentToken.typ:
            case "FUN":
                return self.function()
            case _:
                return self.boolean()

    def function(self):
        self.eat("FUN")
        self.eat("OF_")
        self.eat("LPA")
        parameters = self.variables()
        self.eat("RPA")
        self.eat("SUB")
        self.eat("GRT")
        self.eat("LPA")
        code = self.statements()
        self.eat("RPA")
        return Function(parameters, code)

    def boolean(self):
        node = self.comparison()
        while True:
            token = self.currentToken
            match token.typ:
                case "AND" | "OR_":
                    self.eat(token.typ)
                case _:
                    return node
            node = BinaryOp(node, token, self.comparison())

    def comparison(self):
        node = self.mathPrecedence3()
        while True:
            token = self.currentToken
            match token.typ:
                case "LES" | "EQU" | "GRT":
                    self.eat(token.typ)
                case _:
                    return node
            node = BinaryOp(node, token, self.mathPrecedence3())

    def mathPrecedence3(self):
        node = self.mathPrecedence2()
        while True:
            token = self.currentToken
            match token.typ:
                case "ADD" | "SUB":
                    self.eat(token.typ)
                case _:
                    return node
            node = BinaryOp(node, token, self.mathPrecedence2())

    def mathPrecedence2(self):
        node = self.mathPrecedence1()
        while True:
            token = self.currentToken
            match token.typ:
                case "MUL" | "DIV" | "MOD":
                    self.eat(token.typ)
                case _:
                    return node
            node = BinaryOp(node, token, self.mathPrecedence1())

    def mathPrecedence1(self):
        node = self.functionTerm()
        while True:
            token = self.currentToken
            match token.typ:
                case "POW":
                    self.eat(token.typ)
                case _:
                    return node
            node = BinaryOp(node, token, self.functionTerm())

    def functionTerm(self):
        result = self.baseTerm()
        while True:
            token = self.currentToken
            match token.typ:
                case "OF_":
                    self.eat("OF_")
                    self.eat("LPA")
                    inputs = self.expressions()
                    self.eat("RPA")
                    result = Call(result, inputs)
                case _:
                    return result

    def baseTerm(self):
        token = self.currentToken
        match token.typ:
            case "ADD" | "SUB" | "NOT":
                self.eat("ADD", "SUB", "NOT")
                return UnaryOp(token, self.baseTerm())
            case "QUE":
                self.eat("QUE")
                self.eat("LPA")
                query = self.query()
                self.eat("RPA")
                return query
            case "INT":
                self.eat("INT")
                return Number(token)
            case "TRU":
                self.eat("TRU")
                return Boolean(True)
            case "FAL":
                self.eat("FAL")
                return Boolean(False)
            case "LPA":
                self.eat("LPA")
                result = self.expression()
                self.eat("RPA")
                return result
            case "LSB":
                return self.sequence()
            case "STR":
                self.eat("STR")
                return String(token)
            case "VAR":
                self.eat("VAR")
                return Variable(token)
            case "NUL":
                self.eat("NUL")
                return Nothing(Token("NUL", None))
            case _:
                self.error(token)

    def sequence(self):
        self.eat("LSB")
        if self.currentToken.typ == "RSB":
            self.eat("RSB")
            return Sequence([])
        elements = [self.expression()]
        while True:
            token = self.currentToken
            match token.typ:
                case "EOF":
                    self.error("Expecting ']' instead of EOF")
                case "RSB":
                    self.eat("RSB")
                    return Sequence(elements)
                case "COM":
                    self.eat("COM")
                    elements.append(self.expression())
                case _:
                    self.error("Expected ',' between elements")

    def query(self):
        chain = [self.queryTerm()]
        while True:
            token = self.currentToken
            match token.typ:
                case "AT_":
                    self.eat("AT_")
                    chain.append(self.queryTerm())
                case "RPA":
                    return Query(chain)
                case _:
                    self.error(f"Expexted '@' or ')' instead of {token.typ}")

    def queryTerm(self):
        token = self.currentToken
        match token.typ:
            case "EXT" | "SEL" | "UNI" | "ORD" | "REV" | "GRO" | "KEE" | "TAK" | "DRO" | "APP" | "COL" | "CMB" | "JOI": 
                self.eat(token.typ)
                return QueryTerm(token.typ)
            case _: return self.expression()

class Interpreter(object):
    def __init__(self, text):
        self.lexer = Lexer(text)
        self.parser = Parser(self.lexer)

    def interpret(self):
        tree = self.parser.parse()
        environment = {}
        tree.visit(environment)
        for key in environment:
            value = environment[key]
            if not isinstance(value, Function):
                print(f"{key} := {repr(environment[key])}\n")


if __name__ == "__main__":
    # with open("testfiles/basics.txt", "r") as f: code = f.read()
    # with open("testfiles/advanced.txt", "r") as f: code = f.read()
    # with open("testfiles/functional.txt", "r") as f: code = f.read()
    # with open("testfiles/patterns.txt", "r") as f: code = f.read()
    # with open("testfiles/queries.txt", "r") as f: code = f.read()
    I = Interpreter(code)
    I.interpret()

'''
TODO:
    - Fix recursive CPS environment bindings error
    >>> Eliminate globals, only use local bindings instead of generic environment
'''