# Axl
An interpreter for a customized language: AXL


* abstract.py: class definitions for Abstract Sytax Trees (ASTs)
* axl.py: the main file containing the parser and interpreter
* exceptions.py: definitions of various exception types used by AXL
  * OutputException: used to alter control flow when returning a value
  * SkiploopException: used to alter control flow when breaking out of a loop
  * EndloopException: used to alter control flow when continuing to the next iteration of a loop
  * LexerException: raised when an error occurs during reading of the text
  * ParserException: raised when an error occurs during parsing of the text
  * QueryException: raised when an error occurs during evaluation of a query expression
* lexer.py: definitions for Lexer class which generates tokens from the text
* pattern.py: class definitions for ASTs related to pattern matching
* query.py: class definitions for ASTs related to query expressions
* syntax.txt: explanations of how to use AXL's syntax
* testfiles: samples of AXL code to demonstrate its syntax and features
  * basic: variable definitions, basic expressions, calling builtin functions
  * advanced: function definitions, loops, recursion, conditionals, higher-order-functions
  * functional: higher-order-functions, currying, staging, CPS **(work in progress)**
  * patterns: pattern matching with lists, strings, literals, wildcards, unions and variables
  * queries: file I/O, query expressions
* textfiles: .txt files used by testfiles to demonstrate file I/O

Axl interpreter written in Python using version 3.10.0a6, which includes pattern matching. Previous versions of Python will be unable to run Axl since they do not include pattern matching.
