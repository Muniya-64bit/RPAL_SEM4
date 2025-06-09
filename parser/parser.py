import copy
from lexical_analyzer.lexical_analyzer import RPAL_Scanner
from lexical_analyzer.lexical_analyzer import Token
from Env import *

# AST Node class representing nodes in the Abstract Syntax Tree
class ASTNode:
    def __init__(self, value, type):
        self.left = None    # Left child node
        self.right = None   # Right child node (used for sibling nodes in n-ary trees)
        self.token = None   # Token associated with node
        self.type = type    # Type of node (ID, STR, INT, etc.)
        self.value = value  # Value of node
        self.indentation = 0  # Indentation level for pretty printing

    # Factory method to create new nodes
    def copy_ast_node(self, value, type):
        return ASTNode(value, type)

    # Setter methods
    def set_node_type(self, type):
        self.type = type

    def set_label(self, value):
        self.value = value

    # Getter methods
    def get_label(self):
        return self.value

    def get_node_type(self):
        return self.type

# Main parser class that builds the AST from tokens using recursive descent parsing
class ASTParser:
    def __init__(self, tokens):
        self.tokens = tokens          # List of tokens to parse
        self.current_token = None     # Current token being processed
        self.index = 0                # Index of current token in tokens list
        self.stack = []               # Stack used during AST construction
        self.prevToken = None         # Previous token processed (for error reporting)
        self.has_error = False       # Flag indicating parsing errors

    # Core parsing method that initiates the parsing process
    def parse_tokens(self, astFlag):
        self.current_token = self.tokens[0]
        self.parse_expression()  # Start with E production rule (top-level expression)
        
        # Handle parsing results based on flags and success
        if self.has_error:
            print("Parsing error")
        elif astFlag == "-ast":
            self.print_pre_order(self.stack[0])  # Print AST if requested
        elif astFlag == "":
            pass  # No output needed
        else:
            print("Input command incorrect.")

    # Error state check
    def isAnError(self):
        return self.has_error

    # Helper methods for parsing

    # Reads and consumes the next token, checking for expected values/types
    def read(self, value, type):
        self.current_token = self.tokens[self.index]

        # Check if current token matches expected (unless expecting any user-defined value)
        if self.current_token.value != value and value != "UserDefined":
            print("Expected", self.current_token.value, "but got ", value)
            self.has_error = True
            return

        # Update state for next token
        self.prevToken = self.current_token
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            # Handle end of token stream
            self.current_token.value = self.prevToken.value
            self.current_token.type = ""

    # Constructs an AST node with the given number of children from the stack
    def construct_ast_node(self, token, type, numOfChilds):
        parentNode = ASTNode(token, type)
        head = None
        # Pop children from stack and build right-linked list
        for i in range(numOfChilds):
            if len(self.stack) != 0:
                child = self.stack.pop()
                child.right = head  # Link siblings via right pointer
                head = child
            else:
                print("There's an error in code")
                self.has_error = True
        parentNode.left = head  # First child is left, others are right-linked
        self.stack.append(parentNode)

    # Prints the AST in pre-order with indentation
    def print_pre_order(self, node, depth=0):
        if node is not None:
            # Special formatting for different node types
            if node.type in ["ID", "STR", "INT"]:
                print("." * depth + "<" + node.type + ":" + node.value + ">")
            elif node.type in ["BOOL", "NIL", "DUMMY"]:
                print("." * depth + "<" + node.value + ">")
            else:
                print("." * depth + node.value)
            # Recursively print children
            self.print_pre_order(node.left, depth + 1)
            self.print_pre_order(node.right, depth)

    # Terminal and basic non-terminal parsing methods
    # Follows the RPAL grammar rules in order of increasing precedence

    # Parses atomic expressions (identifiers, literals, parenthesized expressions)
    def parse_atom(self):
        if self.current_token.type == "<IDENTIFIER>":
            self.read("UserDefined", "<IDENTIFIER>")
            self.construct_ast_node(self.prevToken.value, "ID", 0)
        elif self.current_token.type == "<INTEGER>":
            self.read("UserDefined", "<INTEGER>")
            self.construct_ast_node(self.prevToken.value, "INT", 0)
        elif self.current_token.type == "<STRING>":
            self.read("UserDefined", "<STRING>")
            self.construct_ast_node(self.prevToken.value, "STR", 0)
        elif self.current_token.value == "true":
            self.read("true", "<KEYWORD>")
            self.construct_ast_node("true", "BOOL", 0)
        elif self.current_token.value == "false":
            self.read("false", "<KEYWORD>")
            self.construct_ast_node("false", "BOOL", 0)
        elif self.current_token.value == "nil":
            self.read("nil", "<KEYWORD>")
            self.construct_ast_node("nil", "NIL", 0)
        elif self.current_token.value == "(":
            self.read("(", "(")
            self.parse_expression()
            if self.current_token.value != ")":
                print("Error: expected )")
                self.has_error = True
                return
            self.read(")", ")")
        elif self.current_token.value == "dummy":
            self.read("dummy", "<KEYWORD>")
            self.construct_ast_node("dummy", "DUMMY", 0)

    # Parses variable bindings (for function parameters and let expressions)
    def parse_variable_binding(self):
        if self.current_token.type == "<IDENTIFIER>":
            self.read("UserDefined", "<IDENTIFIER>")
            self.construct_ast_node(self.prevToken.value, "ID", 0)
        elif self.current_token.value == "(":
            self.read("(", "(")
            if self.current_token.type == "<IDENTIFIER>":
                self.parse_variable_list()
                if self.current_token.value != ")":
                    print("Error: expected in")
                    self.has_error = True
                    return
                self.read(")", ")")
            else:
                if self.current_token.value != ")":
                    print("Error: expected in")
                    self.has_error = True
                    return
                self.read(")", ")")
                self.construct_ast_node("()", "KEYWORD", 0)

    # Parses comma-separated lists of variables
    def parse_variable_list(self):
        if self.current_token.type == "<IDENTIFIER>":
            self.read("UserDefined", "<IDENTIFIER>")
            self.construct_ast_node(self.prevToken.value, "ID", 0)
            n = 0
            while self.current_token.value == ",":
                self.read(",", ",")
                self.read("UserDefined", "<IDENTIFIER>")
                self.construct_ast_node(self.prevToken.value, "ID", 0)
                n += 1
            if n > 0:
                self.construct_ast_node(",", "KEYWORD", n + 1)

    # Expression parsing methods (ordered from lowest to highest precedence)

    # Parses function applications (gamma nodes in AST)
    def parse_application(self):
        self.parse_atom()
        while self.current_token.type in [
            "<IDENTIFIER>",
            "<INTEGER>",
            "<STRING>",
        ] or self.current_token.value in [
            "true",
            "false",
            "nil",
            "(",
            "dummy",
        ]:
            self.parse_atom()
            self.construct_ast_node("gamma", "KEYWORD", 2)

    # Parses infix @ operator (function application with explicit function)
    def parse_access(self):
        self.parse_application()
        while self.current_token.value == "@":
            self.read("@", "<OPERATOR>")
            self.read("UserDefined", "<IDENTIFIER>")
            self.construct_ast_node(self.prevToken.value, "ID", 0)
            self.parse_application()
            self.construct_ast_node("@", "KEYWORD", 3)

    # Parses right-associative exponentiation
    def parse_exponentiation(self):
        self.parse_access()
        if self.current_token.value == "**":
            self.read("**", "<OPERATOR>")
            self.parse_exponentiation()
            self.construct_ast_node("**", "KEYWORD", 2)

    # Parses multiplicative operators (*, /)
    def parse_multiplication(self):
        self.parse_exponentiation()
        while self.current_token.value in ["*", "/"]:
            if self.current_token.value == "*":
                self.read("*", "<OPERATOR>")
                self.parse_exponentiation()
                self.construct_ast_node("*", "OPERATOR", 2)
            elif self.current_token.value == "/":
                self.read("/", "<OPERATOR>")
                self.parse_exponentiation()
                self.construct_ast_node("/", "OPERATOR", 2)

    # Parses additive operators (+, -) and unary negation
    def parse_addition(self):
        if self.current_token.value == "+":
            self.read("+", "<OPERATOR>")
            self.parse_multiplication()
        elif self.current_token.value == "-":
            self.read("-", "<OPERATOR>")
            self.parse_multiplication()
            self.construct_ast_node("neg", "KEYWORD", 1)
        else:
            self.parse_multiplication()
            while self.current_token.value in ["+", "-"]:
                if self.current_token.value == "+":
                    self.read("+", "<OPERATOR>")
                    self.parse_multiplication()
                    self.construct_ast_node("+", "OPERATOR", 2)
                elif self.current_token.value == "-":
                    self.read("-", "<OPERATOR>")
                    self.parse_multiplication()
                    self.construct_ast_node("-", "OPERATOR", 2)

    # Parses comparison operators (>, >=, <, <=, eq, ne)
    def parse_comparison(self):
        self.parse_addition()
        if self.current_token.value in ["gr", ">"]:
            self.read(self.current_token.value, "<OPERATOR>")
            self.parse_addition()
            self.construct_ast_node("gr", "KEYWORD", 2)
        elif self.current_token.value in ["ge", ">="]:
            self.read(self.current_token.value, "<OPERATOR>")
            self.parse_addition()
            self.construct_ast_node("ge", "KEYWORD", 2)
        elif self.current_token.value in ["ls", "<"]:
            self.read(self.current_token.value, "<OPERATOR>")
            self.parse_addition()
            self.construct_ast_node("ls", "KEYWORD", 2)
        elif self.current_token.value in ["le", "<="]:
            self.read(self.current_token.value, "<OPERATOR>")
            self.parse_addition()
            self.construct_ast_node("le", "KEYWORD", 2)
        elif self.current_token.value == "eq":
            self.read("eq", "<OPERATOR>")
            self.parse_addition()
            self.construct_ast_node("eq", "KEYWORD", 2)
        elif self.current_token.value == "ne":
            self.read("ne", "<OPERATOR>")
            self.parse_addition()
            self.construct_ast_node("ne", "KEYWORD", 2)

    # Parses logical negation or falls through to comparison
    def parse_negation_or_comparison(self):
        if self.current_token.value == "not":
            self.read("not", "<OPERATOR>")
            self.parse_comparison()
            self.construct_ast_node("not", "KEYWORD", 1)
        else:
            self.parse_comparison()

    # Parses logical AND (conjunction)
    def parse_conjunction(self):
        self.parse_negation_or_comparison()
        while self.current_token.value == "&":
            self.read("&", "<OPERATOR>")
            self.parse_negation_or_comparison()
            self.construct_ast_node("&", "KEYWORD", 2)

    # Parses logical OR (disjunction)
    def parse_disjunction(self):
        self.parse_conjunction()
        while self.current_token.value == "or":
            self.read("or", "<OPERATOR>")
            self.parse_conjunction()
            self.construct_ast_node("or", "KEYWORD", 2)

    # Parses conditional expressions (-> ... | ...)
    def parse_conditional(self):
        self.parse_disjunction()
        if self.current_token.value == "->":
            self.read("->", "<OPERATOR>")
            self.parse_conditional()
            if self.current_token.value != "|":
                print("Error: expected |")
                self.has_error = True
                return
            self.read("|", "<OPERATOR>")
            self.parse_conditional()
            self.construct_ast_node("->", "KEYWORD", 3)

    # Parses augmented expressions (with 'aug' operator)
    def parse_augmented_expr(self):
        self.parse_conditional()
        while self.current_token.value == "aug":
            self.read("aug", "<KEYWORD>")
            self.parse_conditional()
            self.construct_ast_node("aug", "KEYWORD", 2)

    # Parses tuple expressions (comma-separated with potential tau node)
    def parse_tuple(self):
        self.parse_augmented_expr()
        if self.current_token.value == ",":
            self.read(",", ",")
            self.parse_augmented_expr()
            n = 1
            while self.current_token.value == ",":
                n += 1
                self.read(",", ",")
                self.parse_augmented_expr()
            self.construct_ast_node("tau", "KEYWORD", n + 1)

    # Declaration parsing methods

    # Parses variable bindings in let/where expressions
    def parse_binding(self):
        if self.current_token.value == "(":
            self.read("(", "(")
            self.parse_definition()
            if self.current_token.value != ")":
                print("Error: expected )")
                self.has_error = True
                return
            self.read(")", ")")
        n = 0
        if self.current_token.type == "<IDENTIFIER>":
            self.parse_variable_list()
            if self.current_token.value == "=":
                self.read("=", "<OPERATOR>")
                self.parse_expression()
                self.construct_ast_node("=", "KEYWORD", 2)
            else:
                self.parse_variable_binding()
                n = 1
                while self.current_token.type in ["<IDENTIFIER>", "("]:
                    self.parse_variable_binding()
                    n += 1
                if self.current_token.value != "=":
                    print("Error: expected in")
                    self.has_error = True
                    return
                self.read("=", "<OPERATOR>")
                self.parse_expression()
                self.construct_ast_node("fcn_form", "KEYWORD", n + 2)

    # Parses recursive bindings (with 'rec' keyword)
    def parse_recursive_binding(self):
        if self.current_token.value == "rec":
            self.read("rec", "<KEYWORD>")
            self.parse_binding()
            self.construct_ast_node("rec", "KEYWORD", 1)
        else:
            self.parse_binding()

    # Parses multiple bindings joined with 'and'
    def parse_and_bindings(self):
        self.parse_recursive_binding()
        n = 0
        while self.current_token.value == "and":
            self.read("and", "<KEYWORD>")
            self.parse_recursive_binding()
            n += 1
        if n > 0:
            self.construct_ast_node("and", "KEYWORD", n + 1)

    # Parses definitions (let/in expressions)
    def parse_definition(self):
        self.parse_and_bindings()
        while self.current_token.value == "within":
            self.read("within", "<KEYWORD>")
            self.parse_definition()
            self.construct_ast_node("within", "KEYWORD", 2)

    # Top-level expression parsing methods

    # Parses where expressions (expr where binding)
    def parse_where_expression(self):
        self.parse_tuple()
        if self.current_token.value == "where":
            self.read("where", "<KEYWORD>")
            self.parse_recursive_binding()
            self.construct_ast_node("where", "KEYWORD", 2)

    # Main expression parsing method (handles let, fn, and where expressions)
    def parse_expression(self):
        if self.current_token.value == "let":
            self.read("let", "<KEYWORD>")
            self.parse_definition()
            if self.current_token.value != "in":
                print("Error: expected in")
                self.has_error = True
                return
            self.read("in", "<KEYWORD>")
            self.parse_expression()
            self.construct_ast_node("let", "KEYWORD", 2)
        elif self.current_token.value == "fn":
            self.read("fn", "<KEYWORD>")
            self.parse_variable_binding()
            n = 1
            while self.current_token.value in ["<IDENTIFIER>", "("]:
                self.parse_variable_binding()
                n += 1
            if self.current_token.value != ".":
                print("Error: expected .")
                self.has_error = True
                return
            self.read(".", "<OPERATOR>")
            self.parse_expression()
            self.construct_ast_node("lambda", "KEYWORD", n + 1)
        else:
            self.parse_where_expression()