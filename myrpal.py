# Import parser and standardizer modules
from parser.parser import *
import sys
from standardizer.standardizer import standardizer

# Flags to track different types of errors
hasParsingError = False
hasCSEError = False
hasInputError = False
astFlag = ""

# Parse command-line arguments
if len(sys.argv) == 2:
    file = sys.argv[1]
    astFlag = ""  # No AST flag provided

elif len(sys.argv) == 3 and sys.argv[1] == "-ast":
    file = sys.argv[2]
    astFlag = "-ast"  # AST flag provided

elif len(sys.argv) == 3 and sys.argv[1] != "-ast":
    hasInputError = True  # Invalid flag
    astFlag = "invalid"

else:
    hasInputError = True  # Invalid number of arguments
    astFlag = "invalid"


# For testing purposes
# file = "tests/wsum2"
# astFlag = "-ast"

if not hasInputError:
    scanner = RPAL_Scanner(file)  # Initialize scanner with input file

    try:
        tokens = scanner.Scanning()  # Perform lexical analysis

    except:
        hasInputError = True
        print("File doesn't exist :", file)  # File not found error

    if not hasInputError:
        myParser = ASTParser(tokens)  # Create parser with token list
        myParser.parse_tokens(astFlag)  # Start parsing process
        hasParsingError = myParser.isAnError()  # Check for parsing error

        if not hasParsingError:
            root = myParser.stack[0]  # Get root of the AST
            stand = standardizer(root)  # Create standardizer instance

            for i in range(10):
                stand.makeST(root)  # Standardize tree (run multiple times)

            # Initialize 2D array for control structures
            controlStructureArray = [[None for _ in range(200)] for _ in range(200)]
            stand.createControlStructures(root, controlStructureArray)  # Populate control structures

            # Determine actual size of control structure set
            size = 0
            while controlStructureArray[size][0] is not None:
                size += 1

            # Extract each control structure into a list
            setOfControlStruct = []
            for x in range(size):
                temp = []
                for y in range(200):
                    if controlStructureArray[x][y] is not None:
                        temp.append(controlStructureArray[x][y])
                setOfControlStruct.append(temp)

            # Run the CSE machine only if AST print flag is not enabled
            if astFlag != "-ast":
                try:
                    stand.cse_machine(setOfControlStruct)  # Execute control structure evaluation
                except Exception as e:
                    print("CSE machine error")
                    print(e)

        elif hasParsingError:
            pass  # Parser already printed error message

else:
    # Print usage instructions for incorrect input
    print("Input Format is Wrong")
    print("Input format ==>  python .\\myrpal.py file_name")
    print("To print the AST use -ast flag before the file name.")
