import copy
from lexical_analyzer.lexical_analyzer import RPAL_Scanner
from lexical_analyzer.lexical_analyzer import Token
from Env import *

# AST Node class representing nodes in the Abstract Syntax Tree
class ASTNode:
    def __init__(self, value, type):
        self.left = None    # Left child node
        self.right = None   # Right child node
        self.token = None   # Token associated with node
        self.type = type    # Type of node (ID, STR, INT, etc.)
        self.value = value  # Value of node
        self.indentation = 0  # Indentation level for printing

    # Factory method to create new nodes
    def createNode(self, value, type):
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

# Main parser class that builds the AST from tokens
class ASTParser:
    def __init__(self, tokens):
        self.tokens = tokens          # List of tokens to parse
        self.current_token = None     # Current token being processed
        self.index = 0                # Index of current token
        self.stack = []               # Stack used during parsing
        self.prevToken = None         # Previous token processed
        self.errorExist = False       # Flag for parsing errors

    # Core parsing methods
    def startParsing(self, astFlag):
        self.current_token = self.tokens[0]
        self.E()  # Start with E production rule
        
        if self.errorExist:
            print("Parsing error")
        elif astFlag == "-ast":
            self.preOrderTraversal(self.stack[0])
        elif astFlag == "":
            pass
        else:
            print("Input command incorrect.")

    def isAnError(self):
        return self.errorExist

    # Helper methods
    def read(self, value, type):
        self.current_token = self.tokens[self.index]

        if self.current_token.value != value and value != "UserDefined":
            print("Expected", self.current_token.value, "but got ", value)
            self.errorExist = True
            return

        self.prevToken = self.current_token
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token.value = self.prevToken.value
            self.current_token.type = ""

    def buildTree(self, token, type, numOfChilds):
        parentNode = ASTNode(token, type)
        head = None
        for i in range(numOfChilds):
            if len(self.stack) != 0:
                child = self.stack.pop()
                child.right = head
                head = child
            else:
                print("There's an error in code")
                self.errorExist = True
        parentNode.left = head
        self.stack.append(parentNode)

    def preOrderTraversal(self, node, depth=0):
        if node is not None:
            if node.type in ["ID", "STR", "INT"]:
                print("." * depth + "<" + node.type + ":" + node.value + ">")
            elif node.type in ["BOOL", "NIL", "DUMMY"]:
                print("." * depth + "<" + node.value + ">")
            else:
                print("." * depth + node.value)
            self.preOrderTraversal(node.left, depth + 1)
            self.preOrderTraversal(node.right, depth)

    # Terminal and basic non-terminal methods
    def parse_atom(self):
        if self.current_token.type == "<IDENTIFIER>":
            self.read("UserDefined", "<IDENTIFIER>")
            self.buildTree(self.prevToken.value, "ID", 0)
        elif self.current_token.type == "<INTEGER>":
            self.read("UserDefined", "<INTEGER>")
            self.buildTree(self.prevToken.value, "INT", 0)
        elif self.current_token.type == "<STRING>":
            self.read("UserDefined", "<STRING>")
            self.buildTree(self.prevToken.value, "STR", 0)
        elif self.current_token.value == "true":
            self.read("true", "<KEYWORD>")
            self.buildTree("true", "BOOL", 0)
        elif self.current_token.value == "false":
            self.read("false", "<KEYWORD>")
            self.buildTree("false", "BOOL", 0)
        elif self.current_token.value == "nil":
            self.read("nil", "<KEYWORD>")
            self.buildTree("nil", "NIL", 0)
        elif self.current_token.value == "(":
            self.read("(", "(")
            self.E()
            if self.current_token.value != ")":
                print("Error: expected )")
                self.errorExist = True
                return
            self.read(")", ")")
        elif self.current_token.value == "dummy":
            self.read("dummy", "<KEYWORD>")
            self.buildTree("dummy", "DUMMY", 0)

    def Vb(self):
        if self.current_token.type == "<IDENTIFIER>":
            self.read("UserDefined", "<IDENTIFIER>")
            self.buildTree(self.prevToken.value, "ID", 0)
        elif self.current_token.value == "(":
            self.read("(", "(")
            if self.current_token.type == "<IDENTIFIER>":
                self.Vl()
                if self.current_token.value != ")":
                    print("Error: expected in")
                    self.errorExist = True
                    return
                self.read(")", ")")
            else:
                if self.current_token.value != ")":
                    print("Error: expected in")
                    self.errorExist = True
                    return
                self.read(")", ")")
                self.buildTree("()", "KEYWORD", 0)

    def Vl(self):
        if self.current_token.type == "<IDENTIFIER>":
            self.read("UserDefined", "<IDENTIFIER>")
            self.buildTree(self.prevToken.value, "ID", 0)
            n = 0
            while self.current_token.value == ",":
                self.read(",", ",")
                self.read("UserDefined", "<IDENTIFIER>")
                self.buildTree(self.prevToken.value, "ID", 0)
                n += 1
            if n > 0:
                self.buildTree(",", "KEYWORD", n + 1)

    # Expression methods (ordered from lowest to highest precedence)
    def R(self):
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
            self.buildTree("gamma", "KEYWORD", 2)

    def Ap(self):
        self.R()
        while self.current_token.value == "@":
            self.read("@", "<OPERATOR>")
            self.read("UserDefined", "<IDENTIFIER>")
            self.buildTree(self.prevToken.value, "ID", 0)
            self.R()
            self.buildTree("@", "KEYWORD", 3)

    def Af(self):
        self.Ap()
        if self.current_token.value == "**":
            self.read("**", "<OPERATOR>")
            self.Af()
            self.buildTree("**", "KEYWORD", 2)

    def At(self):
        self.Af()
        while self.current_token.value in ["*", "/"]:
            if self.current_token.value == "*":
                self.read("*", "<OPERATOR>")
                self.Af()
                self.buildTree("*", "OPERATOR", 2)
            elif self.current_token.value == "/":
                self.read("/", "<OPERATOR>")
                self.Af()
                self.buildTree("/", "OPERATOR", 2)

    def A(self):
        if self.current_token.value == "+":
            self.read("+", "<OPERATOR>")
            self.At()
        elif self.current_token.value == "-":
            self.read("-", "<OPERATOR>")
            self.At()
            self.buildTree("neg", "KEYWORD", 1)
        else:
            self.At()
            while self.current_token.value in ["+", "-"]:
                if self.current_token.value == "+":
                    self.read("+", "<OPERATOR>")
                    self.At()
                    self.buildTree("+", "OPERATOR", 2)
                elif self.current_token.value == "-":
                    self.read("-", "<OPERATOR>")
                    self.At()
                    self.buildTree("-", "OPERATOR", 2)

    def Bp(self):
        self.A()
        if self.current_token.value in ["gr", ">"]:
            self.read(self.current_token.value, "<OPERATOR>")
            self.A()
            self.buildTree("gr", "KEYWORD", 2)
        elif self.current_token.value in ["ge", ">="]:
            self.read(self.current_token.value, "<OPERATOR>")
            self.A()
            self.buildTree("ge", "KEYWORD", 2)
        elif self.current_token.value in ["ls", "<"]:
            self.read(self.current_token.value, "<OPERATOR>")
            self.A()
            self.buildTree("ls", "KEYWORD", 2)
        elif self.current_token.value in ["le", "<="]:
            self.read(self.current_token.value, "<OPERATOR>")
            self.A()
            self.buildTree("le", "KEYWORD", 2)
        elif self.current_token.value == "eq":
            self.read("eq", "<OPERATOR>")
            self.A()
            self.buildTree("eq", "KEYWORD", 2)
        elif self.current_token.value == "ne":
            self.read("ne", "<OPERATOR>")
            self.A()
            self.buildTree("ne", "KEYWORD", 2)

    def Bs(self):
        if self.current_token.value == "not":
            self.read("not", "<OPERATOR>")
            self.Bp()
            self.buildTree("not", "KEYWORD", 1)
        else:
            self.Bp()

    def Bt(self):
        self.Bs()
        while self.current_token.value == "&":
            self.read("&", "<OPERATOR>")
            self.Bs()
            self.buildTree("&", "KEYWORD", 2)

    def B(self):
        self.Bt()
        while self.current_token.value == "or":
            self.read("or", "<OPERATOR>")
            self.Bt()
            self.buildTree("or", "KEYWORD", 2)

    def Tc(self):
        self.B()
        if self.current_token.value == "->":
            self.read("->", "<OPERATOR>")
            self.Tc()
            if self.current_token.value != "|":
                print("Error: expected |")
                self.errorExist = True
                return
            self.read("|", "<OPERATOR>")
            self.Tc()
            self.buildTree("->", "KEYWORD", 3)

    def Ta(self):
        self.Tc()
        while self.current_token.value == "aug":
            self.read("aug", "<KEYWORD>")
            self.Tc()
            self.buildTree("aug", "KEYWORD", 2)

    def T(self):
        self.Ta()
        if self.current_token.value == ",":
            self.read(",", ",")
            self.Ta()
            n = 1
            while self.current_token.value == ",":
                n += 1
                self.read(",", ",")
                self.Ta()
            self.buildTree("tau", "KEYWORD", n + 1)

    # Declaration methods
    def Db(self):
        if self.current_token.value == "(":
            self.read("(", "(")
            self.D()
            if self.current_token.value != ")":
                print("Error: expected )")
                self.errorExist = True
                return
            self.read(")", ")")
        n = 0
        if self.current_token.type == "<IDENTIFIER>":
            self.Vl()
            if self.current_token.value == "=":
                self.read("=", "<OPERATOR>")
                self.E()
                self.buildTree("=", "KEYWORD", 2)
            else:
                self.Vb()
                n = 1
                while self.current_token.type in ["<IDENTIFIER>", "("]:
                    self.Vb()
                    n += 1
                if self.current_token.value != "=":
                    print("Error: expected in")
                    self.errorExist = True
                    return
                self.read("=", "<OPERATOR>")
                self.E()
                self.buildTree("fcn_form", "KEYWORD", n + 2)

    def Dr(self):
        if self.current_token.value == "rec":
            self.read("rec", "<KEYWORD>")
            self.Db()
            self.buildTree("rec", "KEYWORD", 1)
        else:
            self.Db()

    def Da(self):
        self.Dr()
        n = 0
        while self.current_token.value == "and":
            self.read("and", "<KEYWORD>")
            self.Dr()
            n += 1
        if n > 0:
            self.buildTree("and", "KEYWORD", n + 1)

    def D(self):
        self.Da()
        while self.current_token.value == "within":
            self.read("within", "<KEYWORD>")
            self.D()
            self.buildTree("within", "KEYWORD", 2)

    # Top-level expression methods
    def Ew(self):
        self.T()
        if self.current_token.value == "where":
            self.read("where", "<KEYWORD>")
            self.Dr()
            self.buildTree("where", "KEYWORD", 2)

    def E(self):
        if self.current_token.value == "let":
            self.read("let", "<KEYWORD>")
            self.D()
            if self.current_token.value != "in":
                print("Error: expected in")
                self.errorExist = True
                return
            self.read("in", "<KEYWORD>")
            self.E()
            self.buildTree("let", "KEYWORD", 2)
        elif self.current_token.value == "fn":
            self.read("fn", "<KEYWORD>")
            self.Vb()
            n = 1
            while self.current_token.value in ["<IDENTIFIER>", "("]:
                self.Vb()
                n += 1
            if self.current_token.value != ".":
                print("Error: expected .")
                self.errorExist = True
                return
            self.read(".", "<OPERATOR>")
            self.E()
            self.buildTree("lambda", "KEYWORD", n + 1)
        else:
            self.Ew()