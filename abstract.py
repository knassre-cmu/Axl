from exceptions import *

class AST(object):
    def __init__(self, token):
        self.value = token.val

    def __repr__(self):
        return str(self.value)

    def visit(self, environment):
        return self.value

class Statements(AST):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return "; ".join([repr(statement) for statement in self.statements])
        
    def __iter__(self):
        yield from self.statements

    def visit(self, environment):
        for statement in self.statements:
            statement.visit(environment)

class Definition(AST):
    def __init__(self, variables, expressions):
        self.variables = variables
        self.expressions = expressions

    def __repr__(self):
        return f"{', '.join([repr(variable) for variable in self.variables])} is {', '.join([repr(expression) for expression in self.expressions])}"

    def visit(self, environment):
        results = []
        for expression in self.expressions:
            results.append(expression.visit(environment))
        for i in range(len(self.variables)):
            environment[self.variables[i]] = results[i]
            if isinstance(self.expressions[i], Function):
                results[i].locals[self.variables[i]] = results[i]

class While(AST):
    def __init__(self, conditional, body):
        self.conditional = conditional
        self.body = body

    def __repr__(self):
        return f"while ({self.conditional}) is true do ({self.body}"

    def visit(self, environment):
        while self.conditional.visit(environment):
            try:
                self.body.visit(environment)
            except EndloopException:
                break
            except SkiploopException:
                continue

class For(AST):
    def __init__(self, variable, iterable, body):
        self.variable = variable
        self.iterable = iterable
        self.body = body

    def __repr__(self):
        return f"for each element {self.variable} of ({self.iterable}) do ({self.body}"

    def visit(self, environment):
        iterable = self.iterable.visit(environment)
        for elem in iterable:
            try:
                environment[self.variable.val] = elem
                self.body.visit(environment)
            except EndloopException:
                break
            except SkiploopException:
                continue
            
class Conditional(AST):
    def __init__(self, conditional, trueCode, falseCode):
        self.conditional = conditional
        self.trueCode = trueCode
        self.falseCode = falseCode

    def __repr__(self):
        return f"if ({self.conditional}) is true then do ({self.trueCode}) otherwise do ({self.falseCode})"

    def visit(self, environment):
        if self.conditional.visit(environment):
            self.trueCode.visit(environment)
        else:
            self.falseCode.visit(environment)

class Match(AST):
    def __init__(self, expression, cases):
        self.expression = expression
        self.cases = cases

    def __repr__(self):
        cases = ' '.join([f"pattern ({pattern}) ({code})" for pattern, code in self.cases])
        return f"match ({self.expression}) with {cases}"

    def visit(self, environment):
        expression = self.expression.visit(environment)
        for pattern, code in self.cases:
            if pattern.matches(expression):
                pattern.bindPattern(expression, environment)
                code.visit(environment)
                return

class Output(AST):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"output {self.value}"

    def visit(self, environment):
        if len(self.value) == 1:
            results = self.value[0].visit(environment)
        else:
            results = [value.visit(environment) for value in self.value]
        raise OutputException(results)

class Endloop(AST):
    def __init__(self):
        pass

    def __repr__(self):
        return "endloop"

    def visit(self, environment):
        raise EndloopException()

class Skiploop(AST):
    def __init__(self):
        pass

    def __repr__(self):
        return "skiploop"

    def visit(self, environment):
        raise SkiploopException()

class Function(AST):
    def __init__(self, arguments, code):
        self.arguments = arguments
        self.code = code
        self.locals = {}

    def __repr__(self):
        # return "<function>"
        return f"({', '.join([repr(argument) for argument in self.arguments])}) -> ({', '.join([repr(statement) for statement in self.code])})"

    def visit(self, environment):
        self.locals = {**environment}
        return self

def readFile(path):
    with open(path, "r") as f:
        return f.read()

def writeFile(path, text):
    with open(path, "w") as f:
        f.write(text)

def datatype(elem):
    if isinstance(elem, list):
        return "list"
    if isinstance(elem, str):
        return "string"
    if isinstance(elem, int):
        return "integer"
    if isinstance(elem, bool):
        return "boolean"
    if isinstance(elem, None):
        return "nothing"

def evaluate(s):
    if s.isdigit():
        return int(s)
    elif s == "true":
        return True
    elif s == "false":
        return False
    elif s == "nothing":
        return None
    else:
        return s

class Call(AST):
    builtinFunctions = {
        "minimum": min,
        "maximum": max,
        "length": len,
        "sum": sum,
        "sort": sorted,
        "index": lambda L, i: L[i],
        "integer": int,
        "string": str,
        "print": print,
        "filewrite": writeFile,
        "fileread": readFile,
        "datatype": datatype,
        "evaluate": evaluate,
        "isletter": lambda s: s.isalpha(),
    }

    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments

    def __repr__(self):
        return f"{self.function} of ({', '.join([repr(arg) for arg in self.arguments])})"

    def call(function, inputs, environment):
        if isinstance(function, str):
            return Call.builtinFunctions[function](*inputs)
        else:
            try:
                environment = {**function.locals, **inputs}
                function.code.visit(environment)
            except OutputException as e:
                return e.outputValue

    def visit(self, environment):
        environment = {**environment}
        if repr(self.function) in Call.builtinFunctions:
            inputs = []
            for i in range(len(self.arguments)):
                inputs.append(self.arguments[i].visit(environment))
            return Call.call(repr(self.function), inputs, environment)
        else:
            function = self.function.visit(environment)
            inputs = {}
            for i in range(len(self.arguments)):
                argName = function.arguments[i]
                argVal = self.arguments[i].visit(environment)
                inputs[argName] = argVal
            return Call.call(function, inputs, environment)

class Variable(AST):
    def __init__(self, token):
        self.token = token
        self.name = token.val

    def __repr__(self):
        return self.name

    def visit(self, environment):
        return environment[self.name]

class Number(AST):
    pass

class String(AST):
    pass

class Nothing(AST):
    def __str__(self):
        return "foo"
        
    def __repr__(self):
        return "foo"

class Boolean(AST):
    def __init__(self, truthVal):
        self.truthVal = truthVal

    def __repr__(self):
        return repr(self.truthVal).lower()

    def visit(self, environment):
        return self.truthVal

class Sequence(AST):
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return repr(self.elements)

    def visit(self, environment):
        return [elem.visit(environment) for elem in self.elements]

class BinaryOp(AST):
    def __init__(self, left, operand, right):
        self.token = operand
        self.left = left
        self.operator = operand
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.operator.val} {self.right})"

    def visit(self, environment):
        match self.operator.typ:
            case "ADD":
                return self.left.visit(environment) + self.right.visit(environment)
            case "SUB":
                return self.left.visit(environment) - self.right.visit(environment)
            case "MUL":
                return self.left.visit(environment) * self.right.visit(environment)
            case "DIV":
                return self.left.visit(environment) // self.right.visit(environment)
            case "POW":
                return self.left.visit(environment) ** self.right.visit(environment)
            case "MOD":
                return self.left.visit(environment) % self.right.visit(environment)
            case "AND":
                return self.left.visit(environment) and self.right.visit(environment)
            case "OR_":
                return self.left.visit(environment) or self.right.visit(environment)
            case "LES":
                return self.left.visit(environment) < self.right.visit(environment)
            case "EQU":
                return self.left.visit(environment) == self.right.visit(environment)
            case "GRT":
                return self.left.visit(environment) > self.right.visit(environment)

class UnaryOp(AST):
    def __init__(self, operand, expression):
        self.token = operand
        self.operator = operand
        self.expression = expression

    def __repr__(self):
        return f"{self.operator.val}{self.expression}"

    def visit(self, environment):
        match self.operator.typ:
            case "ADD":
                return abs(self.expression.visit(environment))
            case "SUB":
                return -self.expression.visit(environment)
            case "NOT":
                return not self.expression.visit(environment)