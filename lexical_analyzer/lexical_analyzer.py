

class Token:
    def __init__(self, value, type):
        self.value = value
        self.type = type


class RPAL_Scanner:
    punction = [")", "(", ";", ","]

    operator_symbol = [
        "+",
        "-",
        "*",
        "<",
        ">",
        "&",
        ".",
        "@",
        "/",
        ":",
        "=",
        "~",
        "|",
        "$",
        "!",
        "#",
        "%",
        "^",
        "_",
        "[",
        "]",
        "{",
        "}",
        '"',
        "`",
        "?",
    ]


    RESERVED_KEYWORDS = [
        "fn",
        "where",
        "let",
        "aug",
        "within",
        "in",
        "rec",
        "eq",
        "gr",
        "ge",
        "ls",
        "le",
        "ne",
        "or",
        "@",
        "not",
        "&",
        "true",
        "false",
        "nil",
        "dummy",
        "and",
        "|",
    ]

    comment_elements = ['"', "\\", " ", "\t"]

    def __init__(self, file):
        self.file = file

    # Scannning
    def Scanning(self):
        Input_Tokens = []
        with open(self.file, "r") as f:
            inputString = f.read()

            i = 0
            while i < len(inputString):

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
                        Input_Tokens.append(Token(token, token))
                    else:
                        Input_Tokens.append(Token(token, "<IDENTIFIER>"))

                elif inputString[i].isdigit():
                    temp = i
                    while i + 1 < len(inputString) and inputString[i + 1].isdigit():
                        i += 1
                    token = inputString[temp : i + 1]
                    Input_Tokens.append(Token(token, "<INTEGER>"))

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
                        token = inputString[temp + 1 : i]   #without ' ' marks
                        Input_Tokens.append(Token(token, "<STRING>"))

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
                        # token = inputString[temp : i + 1]   #with last newline
                        token = inputString[temp:i]  # without newline
                        Input_Tokens.append(Token(token, "<DELETE>"))


                elif inputString[i] in RPAL_Scanner.operator_symbol:
                    temp = i
                    while (
                        i + 1 < len(inputString) and inputString[i + 1] in RPAL_Scanner.operator_symbol
                    ):
                        i += 1
                    token = inputString[temp : i + 1]
                    Input_Tokens.append(Token(token, "<OPERATOR>"))

                i += 1


        # Screening
        Tokens = []

        for token in Input_Tokens:
            if token.type != "<DELETE>":
                Tokens.append(token)

        return Tokens
