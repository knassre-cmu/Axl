from abstract import *
from exceptions import *

class QueryTerm(object):
    def __init__(self, term):
        self.term = term

    def __repr__(self):
        return self.term.lower()

    def error(self, msg=""):
        raise QueryException(msg)

    def extraction(self, stack):
        if len(stack) < 2: self.error("Insufficient arguments for extract")
        rows = stack.pop()
        source = stack.pop()
        stack.append([source[i] for i in rows])

    def selection(self, stack):
        if len(stack) < 2: self.error("Insufficient arguments for select")
        cols = stack.pop()
        source = stack.pop()
        stack.append([[row[i] for i in cols] for row in source])

    def unique(self, stack):
        if len(stack) < 1: self.error("Insufficient arguments for unique")
        source = stack.pop()
        stack.append([source[i] for i in range(len(source)) if source[i] not in source[:i]])

    def reverse(self, stack):
        if len(stack) < 1: self.error("Insufficient arguments for reverse")
        source = stack.pop()
        stack.append(source[::-1])

    def ordering(self, stack):
        if len(stack) < 2: self.error("Insufficient arguments for order")
        ordinals = stack.pop()
        source = stack.pop()
        cmpFn = lambda L: [L[i] for i in ordinals]
        stack.append(sorted(source, key=cmpFn))

    def keep(self, stack, environment):
        if len(stack) < 2: self.error("Insufficient arguments for keep")
        condition = stack.pop()
        source = stack.pop()
        output = []
        if repr(condition) in Call.builtinFunctions:
            for elem in source:
                output.append(Call.call(repr(condition)), [[elem]], environment)
        else:
            for elem in source:
                inputs = {condition.arguments[0]: elem}
                if Call.call(condition, inputs, environment):
                    output.append(elem)
        stack.append(output)

    def apply(self, stack, environment):
        if len(stack) < 2: self.error("Insufficient arguments for apply")
        condition = stack.pop()
        source = stack.pop()
        output = []
        if repr(condition) in Call.builtinFunctions:
            for elem in source:
                output.append(Call.call(repr(condition)), [[elem]], environment)
        else:
            for elem in source:
                inputs = {condition.arguments[0]: elem}
                output.append(Call.call(condition, inputs, environment))
        stack.append(output)

    def grouping(self, stack):
        if len(stack) < 2: self.error("Insufficient arguments for grouping")
        cols = stack.pop()
        source = stack.pop()
        output = {}
        for elem in source:
            key = tuple([elem[i] for i in cols])
            output[key] = output.get(key, []) + [elem]
        stack.append([list(key) + [output[key]] for key in output])

    def collate(self, stack):
        if len(stack) < 1: self.error("Insufficient arguments for collate")
        source = stack.pop()
        output = []
        for elem in source:
            output += elem
        stack.append(output)

    def combine(self, stack, environment):
        if len(stack) < 3: self.error("Insufficient arguments for combine")
        result = stack.pop()
        cmbFn = stack.pop()
        source = stack.pop()
        if repr(cmbFn) in Call.builtinFunctions:
            for elem in source:
                result = Call.call(repr(cmbFn), [[elem]], environment)
        else:
            for elem in source:
                inputs = {cmbFn.arguments[0]: result, cmbFn.arguments[1]: elem}
                result = Call.call(cmbFn, inputs, environment)
        stack.append(result)

    def join(self, stack):
        if len(stack) < 4: self.error("Insufficient arguments for drop")
        cols2 = stack.pop()
        cols1 = stack.pop()
        source2 = stack.pop()
        source1 = stack.pop()
        output = []
        for i in range(len(source1)):
            for j in range(len(source2)):
                elems1 = [source1[i][k] for k in cols1]
                elems2 = [source2[j][k] for k in cols2]
                if elems1 == elems2: output.append(source1[i] + source2[j])
        stack.append(output)

    def take(self, stack):
        if len(stack) < 2: self.error("Insufficient arguments for take")
        elems = stack.pop()
        source = stack.pop()
        stack.append(source[:elems])

    def drop(self, stack):
        if len(stack) < 2: self.error("Insufficient arguments for drop")
        elems = stack.pop()
        source = stack.pop()
        stack.append(source[elems:])

    def enact(self, stack, environment):
        match self.term:
            case "EXT": self.extraction(stack)
            case "SEL": self.selection(stack)
            case "UNI": self.unique(stack)
            case "ORD": self.ordering(stack)
            case "REV": self.reverse(stack)
            case "KEE": self.keep(stack, environment)
            case "APP": self.apply(stack, environment)
            case "GRO": self.grouping(stack)
            case "COL": self.collate(stack)
            case "CMB": self.combine(stack, environment)
            case "JOI": self.join(stack)
            case "TAK": self.take(stack)
            case "DRO": self.drop(stack)

class Query(AST):
    def __init__(self, chain):
        self.chain = chain

    def __repr__(self):
        chain = [repr(elem) for elem in self.chain]
        return f"query ({' @ '.join(chain)})"

    def visit(self, environment):
        stack = []
        for elem in self.chain:
            if isinstance(elem, QueryTerm):
                elem.enact(stack, environment)
            else:
                stack.append(elem.visit(environment))
        return stack[-1]