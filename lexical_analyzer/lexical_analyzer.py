# RPAL_Scanner.py
class Token:
    def __init__(self, value, type):
        self.value = value
        self.type = type


class RPAL_Scanner:
    
    punction = [")", "(", ";", ","]

    # List of operator symbols in RPAL language
    operator_symbol = [
        "+", "-", "*", "<", ">", "&", ".", "@", "/", ":", "=", "~", "|", "$",
        "!", "#", "%", "^", "_", "[", "]", "{", "}", '"', "`", "?"
    ]

    # Reserved keywords in RPAL
    # These keywords cannot be used as identifiers
    RESERVED_KEYWORDS = [
        "fn", "where", "let", "aug", "within", "in", "rec", "eq", "gr", "ge",
        "ls", "le", "ne", "or", "@", "not", "&", "true", "false", "nil",
        "dummy", "and", "|"
    ]

    # Elements that can be part of comments
    comment_elements = ['"', "\\", " ", "\t"]

    def __init__(self, file):
        self.file = file

    # Scanning function to tokenize the input file
    def Scanning(self):
        Input_Tokens = []

        # 
        with open(self.file, "r") as f:
            inputString = f.read()

            i = 0
            while i < len(inputString):

                # process identifiers and reserved keywords
                if inputString[i].isalpha():
                    temp = i
                    while i + 1 < len(inputString) and (
                        (inputString[i + 1].isalpha())
                        or (inputString[i + 1].isdigit())
                        or (inputString[i + 1] == "_")
                    ):
                        i += 1
                    token = inputString[temp : i + 1]
                    if token in RPAL_Scanner.RESERVED_KEYWORDS:
                        Input_Tokens.append(Token(token, token))  # Reserved keyword
                    else:
                        Input_Tokens.append(Token(token, "<IDENTIFIER>"))

                
                elif inputString[i].isdigit():
                    temp = i
                    while i + 1 < len(inputString) and inputString[i + 1].isdigit():
                        i += 1
                    token = inputString[temp : i + 1]
                    Input_Tokens.append(Token(token, "<INTEGER>"))

                # Handle whitespace characters and delete them
                elif (
                    inputString[i] == " "
                    or inputString[i] == "\t"
                    or inputString[i] == "\n"
                ):
                    temp = i
                    while i + 1 < len(inputString) and (
                        inputString[i + 1] == " "
                        or inputString[i + 1] == "\t"
                        or inputString[i + 1] == "\n"
                    ):
                        i += 1
                    token = inputString[temp : i + 1]
                    Input_Tokens.append(Token(repr(token), "<DELETE>"))

                # Process punctuation characters
                elif inputString[i] == "(":
                    token = "("
                    Input_Tokens.append(Token("(", "("))

                elif inputString[i] == ")":
                    token = ")"
                    Input_Tokens.append(Token(")", ")"))

                elif inputString[i] == ";":
                    token = ";"
                    Input_Tokens.append(Token(";", ";"))

                elif inputString[i] == ",":
                    token = ","
                    Input_Tokens.append(Token(",", ","))

                # Handle string literals enclosed in double quotes
                elif inputString[i] == "'":
                    temp = i
                    while (
                        i + 1 < len(inputString)
                        and (
                            inputString[i + 1] == "\t"
                            or inputString[i + 1] == "\n"
                            or inputString[i + 1] == "\\"
                            or inputString[i + 1] == "("
                            or inputString[i + 1] == ")"
                            or inputString[i + 1] == ";"
                            or inputString[i + 1] == ","
                            or inputString[i + 1] == " "
                            or inputString[i + 1].isalpha()
                            or inputString[i + 1].isdigit()
                            or inputString[i + 1] in RPAL_Scanner.operator_symbol
                        )
                        and inputString[i + 1] != "'"
                    ):
                        i += 1
                    if i + 1 < len(inputString) and inputString[i + 1] == "'":
                        i += 1
                        token = inputString[temp + 1 : i]  # exclude surrounding quotes
                        Input_Tokens.append(Token(token, "<STRING>"))

                # Process comments starting with "//"
                elif (
                    inputString[i] == "/"
                    and (i + 1 < len(inputString))
                    and inputString[i + 1] == "/"
                ):
                    temp = i
                    while i + 1 < len(inputString) and (
                        (inputString[i + 1] in RPAL_Scanner.comment_elements)
                        or inputString[i + 1] in RPAL_Scanner.punction
                        or inputString[i + 1].isalpha()
                        or inputString[i + 1].isdigit()
                        or inputString[i + 1] in RPAL_Scanner.operator_symbol
                        and (not (inputString[i + 1] == "\n"))
                    ):
                        i += 1

                    if i + 1 < len(inputString) and inputString[i + 1] == "\n":
                        i += 1
                        token = inputString[temp:i]  
                        Input_Tokens.append(Token(token, "<DELETE>"))

                # Handle operator symbols
                
                elif inputString[i] in RPAL_Scanner.operator_symbol:
                    temp = i
                    while (
                        i + 1 < len(inputString) and inputString[i + 1] in RPAL_Scanner.operator_symbol
                    ):
                        i += 1
                    token = inputString[temp : i + 1]
                    Input_Tokens.append(Token(token, "<OPERATOR>"))

                i += 1

        # Remove tokens of type "<DELETE>"
        Tokens = []
        for token in Input_Tokens:
            if token.type != "<DELETE>":
                Tokens.append(token)

        return Tokens
