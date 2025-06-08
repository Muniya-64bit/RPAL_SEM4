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
    def setType(self, type):
        self.type = type

    def setVal(self, value):
        self.value = value

    # Getter methods
    def getVal(self):
        return self.value

    def getType(self):
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

    # Reads and validates the current token
    def read(self, value, type):
        self.current_token = self.tokens[self.index]

        # Check for value mismatch (except for user-defined values)
        if self.current_token.value != value and value != "UserDefined":
            print("Expected", self.current_token.value, "but got ", value)
            self.errorExist = True
            return

        # Move to next token
        self.prevToken = self.current_token
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            # Handle end of tokens
            self.current_token.value = self.prevToken.value
            self.current_token.type = ""

    # Prints the AST in pre-order with indentation
    def preOrderTraversal(self, node, depth=0):
        if node is not None:
            # Format output based on node type
            if node.type in ["ID", "STR", "INT"]:
                print("." * depth + "<" + node.type + ":" + node.value + ">")
            elif node.type in ["BOOL", "NIL", "DUMMY"]:
                print("." * depth + "<" + node.value + ">")
            else:
                print("." * depth + node.value)
            # Recursively traverse left and right children
            self.preOrderTraversal(node.left, depth + 1)
            self.preOrderTraversal(node.right, depth)

    # Starts the parsing process
    def startParsing(self, astFlag):
        self.current_token = self.tokens[0]
        self.E()  # Start with E production rule
        
        # Handle parsing results
        if self.errorExist:
            print("Parsing error")
        elif astFlag == "-ast":
            self.preOrderTraversal(self.stack[0])  # Print AST if flag is set
        elif astFlag == "":
            pass  # No action needed
        else:
            print("Input command incorrect.")

    def isAnError(self):
        return self.errorExist

    # Builds a subtree and pushes it onto the stack
    def buildTree(self, token, type, numOfChilds):
        parentNode = ASTNode(token, type)
        head = None
        # Pop children from stack and build right-linked list
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

    # Grammar production rules follow below
    # Each method implements a production rule from the RPAL grammar

    def E(self):
        # E -> 'let' D 'in' E
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

        # E -> 'fn' Vb+ '.' E
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

        # E -> Ew
        else:
            self.Ew()

    def Ew(self):
        self.T()
        # Ew -> T 'where' Dr
        if self.current_token.value == "where":
            self.read("where", "<KEYWORD>")
            self.Dr()
            self.buildTree("where", "KEYWORD", 2)

    def T(self):
        self.Ta()
        # T -> Ta (',' Ta)+
        if self.current_token.value == ",":
            self.read(",", ",")
            self.Ta()
            n = 1
            while self.current_token.value == ",":
                n += 1
                self.read(",", ",")
                self.Ta()
            self.buildTree("tau", "KEYWORD", n + 1)

    def Ta(self):
        self.Tc()
        # Ta -> Ta 'aug' Tc
        while self.current_token.value == "aug":
            self.read("aug", "<KEYWORD>")
            self.Tc()
            self.buildTree("aug", "KEYWORD", 2)

    def Tc(self):
        self.B()
        # Tc -> B '->' Tc '|' Tc
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

    def B(self):
        self.Bt()
        # B -> B 'or' Bt
        while self.current_token.value == "or":
            self.read("or", "<OPERATOR>")
            self.Bt()
            self.buildTree("or", "KEYWORD", 2)

    def Bt(self):
        self.Bs()
        # Bt -> Bt '&' Bs
        while self.current_token.value == "&":
            self.read("&", "<OPERATOR>")
            self.Bs()
            self.buildTree("&", "KEYWORD", 2)

    def Bs(self):
        # Bs -> 'not' Bp
        if self.current_token.value == "not":
            self.read("not", "<OPERATOR>")
            self.Bp()
            self.buildTree("not", "KEYWORD", 1)
        else:
            self.Bp()

    def Bp(self):
        self.A()
        # Bp -> A (comparison) A
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

    def A(self):
        # A -> '+' At
        if self.current_token.value == "+":
            self.read("+", "<OPERATOR>")
            self.At()
        # A -> '-' At
        elif self.current_token.value == "-":
            self.read("-", "<OPERATOR>")
            self.At()
            self.buildTree("neg", "KEYWORD", 1)
        else:
            self.At()
            # A -> A ('+' | '-') At
            while self.current_token.value in ["+", "-"]:
                if self.current_token.value == "+":
                    self.read("+", "<OPERATOR>")
                    self.At()
                    self.buildTree("+", "OPERATOR", 2)
                elif self.current_token.value == "-":
                    self.read("-", "<OPERATOR>")
                    self.At()
                    self.buildTree("-", "OPERATOR", 2)

    def At(self):
        self.Af()
        # At -> At ('*' | '/') Af
        while self.current_token.value in ["*", "/"]:
            if self.current_token.value == "*":
                self.read("*", "<OPERATOR>")
                self.Af()
                self.buildTree("*", "OPERATOR", 2)
            elif self.current_token.value == "/":
                self.read("/", "<OPERATOR>")
                self.Af()
                self.buildTree("/", "OPERATOR", 2)

    def Af(self):
        self.Ap()
        # Af -> Ap '**' Af
        if self.current_token.value == "**":
            self.read("**", "<OPERATOR>")
            self.Af()
            self.buildTree("**", "KEYWORD", 2)

    def Ap(self):
        self.R()
        # Ap -> Ap '@' ID R
        while self.current_token.value == "@":
            self.read("@", "<OPERATOR>")
            self.read("UserDefined", "<IDENTIFIER>")
            self.buildTree(self.prevToken.value, "ID", 0)
            self.R()
            self.buildTree("@", "KEYWORD", 3)

    def R(self):
        self.Rn()
        # R -> R Rn
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
            self.Rn()
            self.buildTree("gamma", "KEYWORD", 2)

    def Rn(self):
        # Rn -> ID | INT | STR | bool | nil | (E) | dummy
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

    def D(self):
        self.Da()
        # D -> Da 'within' D
        while self.current_token.value == "within":
            self.read("within", "<KEYWORD>")
            self.D()
            self.buildTree("within", "KEYWORD", 2)

    def Da(self):
        self.Dr()
        n = 0
        # Da -> Dr ('and' Dr)+
        while self.current_token.value == "and":
            self.read("and", "<KEYWORD>")
            self.Dr()
            n += 1
        if n > 0:
            self.buildTree("and", "KEYWORD", n + 1)

    def Dr(self):
        # Dr -> 'rec' Db
        if self.current_token.value == "rec":
            self.read("rec", "<KEYWORD>")
            self.Db()
            self.buildTree("rec", "KEYWORD", 1)
        else:
            self.Db()

    def Db(self):
        # Db -> (D)
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
            # Db -> Vl '=' E
            self.Vl()
            if self.current_token.value == "=":
                self.read("=", "<OPERATOR>")
                self.E()
                self.buildTree("=", "KEYWORD", 2)
            else:
                # Db -> ID Vb+ '=' E
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

    def Vb(self):
        # Vb -> ID | (Vl) | ()
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
        # Vl -> ID (',' ID)*
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