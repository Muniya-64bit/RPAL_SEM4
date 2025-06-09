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
        token_list = []

        # 
        with open(self.file, "r") as f:
            text_buffer = f.read()

            i = 0
            while i < len(text_buffer):

                # process identifiers and reserved keywords
                if text_buffer[i].isalpha():
                    temp = i
                    while i + 1 < len(text_buffer) and (
                        (text_buffer[i + 1].isalpha())
                        or (text_buffer[i + 1].isdigit())
                        or (text_buffer[i + 1] == "_")
                    ):
                        i += 1
                    lexeme = text_buffer[temp : i + 1]
                    if lexeme in RPAL_Scanner.RESERVED_KEYWORDS:
                        token_list.append(Token(lexeme, lexeme))  # Reserved keyword
                    else:
                        token_list.append(Token(lexeme, "<IDENTIFIER>"))

                
                elif text_buffer[i].isdigit():
                    temp = i
                    while i + 1 < len(text_buffer) and text_buffer[i + 1].isdigit():
                        i += 1
                    lexeme = text_buffer[temp : i + 1]
                    token_list.append(Token(lexeme, "<INTEGER>"))

                # Handle whitespace characters and delete them
                elif (
                    text_buffer[i] == " "
                    or text_buffer[i] == "\t"
                    or text_buffer[i] == "\n"
                ):
                    temp = i
                    while i + 1 < len(text_buffer) and (
                        text_buffer[i + 1] == " "
                        or text_buffer[i + 1] == "\t"
                        or text_buffer[i + 1] == "\n"
                    ):
                        i += 1
                    lexeme = text_buffer[temp : i + 1]
                    token_list.append(Token(repr(lexeme), "<DELETE>"))

                # Process punctuation characters
                elif text_buffer[i] == "(":
                    lexeme = "("
                    token_list.append(Token("(", "("))

                elif text_buffer[i] == ")":
                    lexeme = ")"
                    token_list.append(Token(")", ")"))

                elif text_buffer[i] == ";":
                    lexeme = ";"
                    token_list.append(Token(";", ";"))

                elif text_buffer[i] == ",":
                    lexeme = ","
                    token_list.append(Token(",", ","))

                # Handle string literals enclosed in double quotes
                elif text_buffer[i] == "'":
                    temp = i
                    while (
                        i + 1 < len(text_buffer)
                        and (
                            text_buffer[i + 1] == "\t"
                            or text_buffer[i + 1] == "\n"
                            or text_buffer[i + 1] == "\\"
                            or text_buffer[i + 1] == "("
                            or text_buffer[i + 1] == ")"
                            or text_buffer[i + 1] == ";"
                            or text_buffer[i + 1] == ","
                            or text_buffer[i + 1] == " "
                            or text_buffer[i + 1].isalpha()
                            or text_buffer[i + 1].isdigit()
                            or text_buffer[i + 1] in RPAL_Scanner.operator_symbol
                        )
                        and text_buffer[i + 1] != "'"
                    ):
                        i += 1
                    if i + 1 < len(text_buffer) and text_buffer[i + 1] == "'":
                        i += 1
                        lexeme = text_buffer[temp + 1 : i]  # exclude surrounding quotes
                        token_list.append(Token(lexeme, "<STRING>"))

                # Process comments starting with "//"
                elif (
                    text_buffer[i] == "/"
                    and (i + 1 < len(text_buffer))
                    and text_buffer[i + 1] == "/"
                ):
                    temp = i
                    while i + 1 < len(text_buffer) and (
                        (text_buffer[i + 1] in RPAL_Scanner.comment_elements)
                        or text_buffer[i + 1] in RPAL_Scanner.punction
                        or text_buffer[i + 1].isalpha()
                        or text_buffer[i + 1].isdigit()
                        or text_buffer[i + 1] in RPAL_Scanner.operator_symbol
                        and (not (text_buffer[i + 1] == "\n"))
                    ):
                        i += 1

                    if i + 1 < len(text_buffer) and text_buffer[i + 1] == "\n":
                        i += 1
                        lexeme = text_buffer[temp:i]  
                        token_list.append(Token(lexeme, "<DELETE>"))

                # Handle operator symbols
                
                elif text_buffer[i] in RPAL_Scanner.operator_symbol:
                    temp = i
                    while (
                        i + 1 < len(text_buffer) and text_buffer[i + 1] in RPAL_Scanner.operator_symbol
                    ):
                        i += 1
                    lexeme = text_buffer[temp : i + 1]
                    token_list.append(Token(lexeme, "<OPERATOR>"))

                i += 1

        # Remove tokens of type "<DELETE>"
        Tokens = []
        for lexeme in token_list:
            if lexeme.type != "<DELETE>":
                Tokens.append(lexeme)
        return Tokens
