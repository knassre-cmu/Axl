class Pattern(object):
    def __init__(self):
        pass

    def __repr__(self):
        return "_"

    def matches(self, value):
        return True

    def bindPattern(self, value, environment):
        pass
                
class PatternString(Pattern):
    def __init__(self, pattern):
        self.pattern = pattern

    def __repr__(self):
        return repr(self.pattern)

    def matches(self, value):
        if not isinstance(value, str):
            return False
        if "*" not in self.pattern:
            if len(value) != len(self.pattern):
                return False
            for i in range(len(self.pattern)):
                if self.pattern[i] != "_" and self.pattern[i] != value[i]:
                    return False
            return True
        else:
            i = self.pattern.index("*")
            prefixPattern = PatternString(self.pattern[:i])
            suffixPattern = PatternString(self.pattern[i+1:])
            prefixWord = value[:i]
            if not prefixPattern.matches(prefixWord):
                return False
            for j in range(i, len(value)+1):
                suffixWord = value[j:]
                if suffixPattern.matches(suffixWord):
                    return True
            return False

class PatternList(Pattern):
    def __init__(self, patterns):
        self.patterns = patterns

    def __repr__(self):
        return "[" + ', '.join([repr(pattern) for pattern in self.patterns]) + "]"

    def matches(self, value):
        if not isinstance(value, list):
            return False
        for i in range(len(self.patterns)):
            if isinstance(self.patterns[i], PatternStar):
                return True
            if i > len(value):
                return False
            if not (self.patterns[i].matches(value[i])):
                return False
        return len(self.patterns) == len(value)

    def bindPattern(self, value, environment):
        for i in range(len(self.patterns)):
            if isinstance(self.patterns[i], PatternStar):
                environment[self.patterns[i].pattern] = value[i:]
                return
            self.patterns[i].bindPattern(value[i], environment)

class PatternVariable(Pattern):
    def __init__(self, pattern):
        self.pattern = pattern

    def __repr__(self):
        return self.pattern

    def bindPattern(self, value, environment):
        environment[self.pattern] = value

class PatternStar(Pattern):
    def __init__(self, pattern):
        self.pattern = pattern

    def __repr__(self):
        return f"*{self.pattern}"

    def matches(self, value):
        return 42

    def bindPattern(self, value, environment):
        return 42
                
class PatternAnd(Pattern):
    def __init__(self, pattern1, pattern2):
        self.pattern1, self.pattern2 = pattern1, pattern2

    def __repr__(self):
        return f"{self.pattern1} & {self.pattern2}"

    def matches(self, value):
        return self.pattern1.matches(value) and self.pattern2.matches(value)

    def bindPattern(self, value, environment):
        self.pattern1.bindPattern(value, environment)
        self.pattern2.bindPattern(value, environment)
                
class PatternOr(Pattern):
    def __init__(self, pattern1, pattern2):
        self.pattern1, self.pattern2 = pattern1, pattern2

    def __repr__(self):
        return f"{self.pattern1} | {self.pattern2}"

    def matches(self, value):
        return self.pattern1.matches(value) or self.pattern2.matches(value)

    def bindPattern(self, value, environment):
        if self.pattern1.matches(value):
            self.pattern1.bindPattern(value, environment)
        else:
            self.pattern2.bindPattern(value, environment)
                
class PatternNumber(Pattern):
    def __init__(self, number):
        self.number = number

    def __repr__(self):
        return f"{self.number}"

    def matches(self, value):
        return value == self.number