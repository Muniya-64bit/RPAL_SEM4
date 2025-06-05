import copy
from Environment import Environment
from parser.parser import ASTNode

class standardizer:
    def __init__(self, tree):
        self.tree = tree
        self.ST = None

    def makeST(self, x):
        self.makeStandardTree(x)

    def createNode(self, x):
        t = ASTNode(x.value, x.type)
        t.left = x.left  # Shallow copy
        t.right = None  # Setting right to None as in original code
        return t

    def makeStandardTree(self, t):
        if t is None:
            return None

        self.makeStandardTree(t.left)
        self.makeStandardTree(t.right)

        if t.getVal() == "let":
            if t.left.getVal() == "=":
                t.setVal("gamma")
                t.setType("KEYWORD")
                P = self.createNode(t.left.right)
                X = self.createNode(t.left.left)
                E = self.createNode(t.left.left.right)
                t.left = ASTNode("lambda", "KEYWORD")
                t.left.right = E
                lambda_node = t.left
                lambda_node.left = X
                lambda_node.left.right = P

        elif t.getVal() == "and" and t.left.getVal() == "=":
            equal = t.left
            t.setVal("=")
            t.setType("KEYWORD")
            t.left = ASTNode(",", "PUNCTION")
            comma = t.left
            comma.left = self.createNode(equal.left)
            t.left.right = ASTNode("tau", "KEYWORD")
            tau = t.left.right

            tau.left = self.createNode(equal.left.right)
            tau = tau.left
            comma = comma.left
            equal = equal.right

            while equal is not None:
                comma.right = self.createNode(equal.left)
                comma = comma.right
                tau.right = self.createNode(equal.left.right)
                tau = tau.right
                equal = equal.right

        elif t.getVal() == "where":
            t.setVal("gamma")
            t.setType("KEYWORD")
            if t.left.right.getVal() == "=":
                P = self.createNode(t.left)
                X = self.createNode(t.left.right.left)
                E = self.createNode(t.left.right.left.right)
                t.left = ASTNode("lambda", "KEYWORD")
                t.left.right = E
                t.left.left = X
                t.left.left.right = P

        elif t.getVal() == "within":
            if t.left.getVal() == "=" and t.left.right.getVal() == "=":
                X1 = self.createNode(t.left.left)
                E1 = self.createNode(t.left.left.right)
                X2 = self.createNode(t.left.right.left)
                E2 = self.createNode(t.left.right.left.right)
                t.setVal("=")
                t.setType("KEYWORD")
                t.left = X2
                t.left.right = ASTNode("gamma", "KEYWORD")
                temp = t.left.right
                temp.left = ASTNode("lambda", "KEYWORD")
                temp.left.right = E1
                temp = temp.left
                temp.left = X1
                temp.left.right = E2

        elif t.getVal() == "rec" and t.left.getVal() == "=":
            X = self.createNode(t.left.left)
            E = self.createNode(t.left.left.right)

            t.setVal("=")
            t.setType("KEYWORD")
            t.left = X
            t.left.right = ASTNode("gamma", "KEYWORD")
            t.left.right.left = ASTNode("YSTAR", "KEYWORD")
            ystar = t.left.right.left

            ystar.right = ASTNode("lambda", "KEYWORD")
            ystar.right.left = self.createNode(X)
            ystar.right.left.right = self.createNode(E)

        elif t.getVal() == "fcn_form":
            P = self.createNode(t.left)
            V = t.left.right

            t.setVal("=")
            t.setType("KEYWORD")
            t.left = P

            temp = t
            while V.right.right is not None:
                temp.left.right = ASTNode("lambda", "KEYWORD")
                temp = temp.left.right
                temp.left = self.createNode(V)
                V = V.right

            temp.left.right = ASTNode("lambda", "KEYWORD")
            temp = temp.left.right

            temp.left = self.createNode(V)
            temp.left.right = V.right

        elif t.getVal() == "lambda":
            if t.left is not None:
                V = t.left
                temp = t
                if V.right is not None and V.right.right is not None:
                    while V.right.right is not None:
                        temp.left.right = ASTNode("lambda", "KEYWORD")
                        temp = temp.left.right
                        temp.left = self.createNode(V)
                        V = V.right

                    temp.left.right = ASTNode("lambda", "KEYWORD")
                    temp = temp.left.right
                    temp.left = self.createNode(V)
                    temp.left.right = V.right

        elif t.getVal() == "@":
            E1 = self.createNode(t.left)
            N = self.createNode(t.left.right)
            E2 = self.createNode(t.left.right.right)
            t.setVal("gamma")
            t.setType("KEYWORD")
            t.left = ASTNode("gamma", "KEYWORD")
            t.left.right = E2
            t.left.left = N
            t.left.left.right = E1

        self.ST = copy.deepcopy(t)
        return None

    def createControlStructures(self, x, setOfControlStruct):
        global index, j, i, betaCount

        #initial values of global varibales
        i = 0
        j = 0
        index = 1
        betaCount = 1

        if x is None:
            return

        if x.getVal() == "lambda":
            t1 = i
            k = 0
            setOfControlStruct[i][j] = ASTNode("", "")
            i = 0

            while setOfControlStruct[i][0] is not None:
                i += 1
                k += 1
            i = t1
            index += 1

            temp = ASTNode(str(k), "deltaNumber")
            setOfControlStruct[i][j] = temp
            j += 1
            setOfControlStruct[i][j] = x.left
            j += 1
            setOfControlStruct[i][j] = x
            j += 1

            myStoredIndex = i
            tempj = j + 3

            while setOfControlStruct[i][0] is not None:
                i += 1
            j = 0

            self.createControlStructures(x.left.right, setOfControlStruct)

            i = myStoredIndex
            j = tempj
        elif x.getVal() == "->":
            myStoredIndex = i
            tempj = j
            nextDelta = index
            k = i

            temp1 = ASTNode(str(nextDelta), "deltaNumber")
            setOfControlStruct[i][j] = temp1
            j += 1

            nextToNextDelta = index
            temp2 = ASTNode(str(nextToNextDelta), "deltaNumber")
            setOfControlStruct[i][j] = temp2
            j += 1

            beta = ASTNode("beta", "beta")
            setOfControlStruct[i][j] = beta
            j += 1

            while setOfControlStruct[k][0] is not None:
                k += 1
            firstIndex = k
            lamdaCount = index

            self.createControlStructures(x.left, setOfControlStruct)
            diffLc = index - lamdaCount

            while setOfControlStruct[i][0] is not None:
                i += 1
            j = 0

            self.createControlStructures(x.left.right, setOfControlStruct)

            while setOfControlStruct[i][0] is not None:
                i += 1
            j = 0

            self.createControlStructures(x.left.right.right, setOfControlStruct)

            if diffLc == 0 or i < lamdaCount:
                setOfControlStruct[myStoredIndex][tempj].setVal(str(firstIndex))
            else:
                setOfControlStruct[myStoredIndex][tempj].setVal(str(i - 1))

            setOfControlStruct[myStoredIndex][tempj + 1].setVal(str(i))

            i = myStoredIndex
            j = 0

            while setOfControlStruct[i][j] is not None:
                j += 1
            betaCount += 2
        elif x.getVal() == "tau":
            tauLeft = x.left
            numOfChildren = 0
            while tauLeft is not None:
                numOfChildren += 1
                tauLeft = tauLeft.right

            countNode = ASTNode(str(numOfChildren), "CHILDCOUNT")
            setOfControlStruct[i][j] = countNode
            j += 1

            tauNode = ASTNode("tau", "tau")
            setOfControlStruct[i][j] = tauNode
            j += 1

            self.createControlStructures(x.left, setOfControlStruct)
            x = x.left
            while x is not None:
                self.createControlStructures(x.right, setOfControlStruct)
                x = x.right
        else:
            setOfControlStruct[i][j] = ASTNode(x.getVal(), x.getType())
            j += 1
            self.createControlStructures(x.left, setOfControlStruct)
            if x.left is not None:
                self.createControlStructures(x.left.right, setOfControlStruct)

    def cse_machine(self, controlStructure):
        control = []  # Stack for control structure
        m_stack = []  # Stack for operands
        stackOfEnvironment = []  # Stack of environments
        getCurrEnvironment = []

        currEnvIndex = 0  # Initial environment
        currEnv = Environment()  # e0

        def isBinaryOperator(op):
            if op in [
                "+",
                "-",
                "*",
                "/",
                "**",
                "gr",
                "ge",
                "<",
                "<=",
                ">",
                ">=",
                "ls",
                "le",
                "eq",
                "ne",
                "&",
                "or",
                "><",
            ]:
                return True
            else:
                return False

        currEnvIndex += 1
        m_stack.append(ASTNode(currEnv.name, "ENV"))
        control.append(ASTNode(currEnv.name, "ENV"))
        stackOfEnvironment.append(currEnv)
        getCurrEnvironment.append(currEnv)

        tempDelta = controlStructure[0]  # Get the first control structure
        for node in tempDelta:
            control.append(
                node
            )  # Push each element of the control structure to the control stack

        while control:
            nextToken = control.pop()  # Get the top of the control stack

            if nextToken.value == "nil":
                nextToken.type = "tau"

            if (
                nextToken.type in ["INT", "STR"]
                or nextToken.value
                in [
                    "lambda",
                    "YSTAR",
                    "Print",
                    "Isinteger",
                    "Istruthvalue",
                    "Isstring",
                    "Istuple",
                    "Isfunction",
                    "Isdummy",
                    "Stem",
                    "Stern",
                    "Conc",
                    "Order",
                    "nil",
                ]
                or nextToken.type in ["BOOL", "NIL", "DUMMY"]
            ):
                if nextToken.value == "lambda":
                    boundVar = control.pop()  # Variable bouded to lambda
                    nextDeltaIndex = control.pop()
                    # Index of next control structure to access
                    env = ASTNode(currEnv.name, "ENV")

                    m_stack.append(
                        nextDeltaIndex
                    )  # Index of next control structure to access
                    m_stack.append(boundVar)  # Variable bouded to lambda
                    m_stack.append(env)  # Environment it was created in
                    m_stack.append(nextToken)  # Lambda Token
                else:
                    m_stack.append(nextToken)  # Push token to the stack
            elif nextToken.value == "gamma":  # If gamma is on top of control stack
                machineTop = m_stack[-1]
                if machineTop.value == "lambda":  # CSE Rule 4 (Apply lambda)
                    m_stack.pop()  # ************************************************************************************************************
                    prevEnv = m_stack.pop()
                    # Pop the environment in which it was created
                    boundVar = m_stack.pop()  # Pop variable bounded to lambda
                    nextDeltaIndex = m_stack.pop()
                    # Pop index of next control structure to access

                    newEnv = Environment()  # Create new environment
                    newEnv.name = "env" + str(currEnvIndex)

                    tempEnv = stackOfEnvironment.copy()
                    while (
                        tempEnv[-1].name != prevEnv.value
                    ):  # Get the previous environment node
                        tempEnv.pop()

                    newEnv.prev = tempEnv[-1]  # Set the previous environment node

                    # Bounding variables to the environment
                    if (
                        boundVar.value == "," and m_stack[-1].value == "tau"
                    ):  # If Rand is tau
                        boundVariables = []  # Vector of bound variables
                        leftOfComa = boundVar.left  # Get the left of the comma
                        while leftOfComa:
                            boundVariables.append(self.createNode(leftOfComa))
                            leftOfComa = leftOfComa.right

                        boundValues = []  # Vector of bound values
                        tau = m_stack.pop()  # Pop the tau token

                        tauLeft = tau.left  # Get the left of the tau
                        while tauLeft:
                            boundValues.append(tauLeft)
                            tauLeft = tauLeft.right  # Get the right of the tau

                        for i in range(len(boundValues)):
                            if boundValues[i].value == "tau":
                                res = []
                                self.arrangeTuple(boundValues[i], res)

                            nodeValVector = []
                            nodeValVector.append(boundValues[i])

                            # Insert the bound variable and its value to the environment
                            newEnv.boundVar[boundVariables[i]] = nodeValVector

                    elif m_stack[-1].value == "lambda":  # If Rand is lambda
                        nodeValVector = []
                        temp = []
                        for _ in range(4):
                            temp.append(m_stack.pop())

                        while temp:
                            fromStack = temp.pop()
                            nodeValVector.append(fromStack)

                        # Insert the bound variable and its value to the environment
                        newEnv.boundVar[boundVar] = nodeValVector

                    elif m_stack[-1].value == "Conc":  # If Rand is Conc
                        nodeValVector = []
                        temp = []
                        for _ in range(2):
                            temp.append(m_stack.pop())

                        while temp:
                            fromStack = temp.pop()
                            nodeValVector.append(fromStack)

                        # Insert the bound variable and its value to the environment
                        newEnv.boundVar[boundVar] = nodeValVector

                    elif m_stack[-1].getVal() == "eta":  # If Rand is eta
                        nodeValVector = []
                        temp = []
                        j = 0
                        while j < 4:
                            temp.append(m_stack.pop())
                            j += 1

                        while temp:
                            fromStack = temp.pop()
                            nodeValVector.append(fromStack)

                        # Insert the bound variable and its value to the environment
                        newEnv.boundVar[boundVar] = nodeValVector
                    else:  # If Rand is an Int
                        bindVarVal = m_stack.pop()
                        nodeValVector = []
                        nodeValVector.append(bindVarVal)

                        # Insert the bound variable and its value to the environment
                        newEnv.boundVar[boundVar] = nodeValVector

                    currEnv = newEnv
                    control.append(ASTNode(currEnv.name, "ENV"))
                    m_stack.append(ASTNode(currEnv.name, "ENV"))
                    stackOfEnvironment.append(currEnv)
                    getCurrEnvironment.append(currEnv)

                    deltaIndex = int(nextDeltaIndex.getVal())
                    nextDelta = controlStructure[
                        deltaIndex
                    ]  # Get the next control structure
                    for node in nextDelta:
                        control.append(
                            node
                        )  # Push each element of the next control structure to the control stack
                    currEnvIndex += 1

                elif machineTop.getVal() == "tau":  # CSE Rule 10 (Tuple Selection)
                    tau = m_stack.pop()  # Get tau node from top of stack
                    selectTupleIndex = (
                        m_stack.pop()
                    )  # Get the index of the child to be selected
                    tupleIndex = int(selectTupleIndex.getVal())

                    tauLeft = tau.left
                    while tupleIndex > 1:  # Get the child to be selected
                        tupleIndex -= 1
                        tauLeft = tauLeft.right

                    selectedChild = self.createNode(tauLeft)
                    if selectedChild.getVal() == "lamdaTuple":
                        getNode = selectedChild.left
                        while getNode is not None:
                            m_stack.append(self.createNode(getNode))
                            getNode = getNode.right
                    else:
                        m_stack.append(selectedChild)

                elif machineTop.getVal() == "YSTAR":  # CSE Rule 12 (Applying YStar)
                    m_stack.pop()  # Pop YSTAR token
                    if m_stack[-1].getVal() == "lambda":
                        etaNode = ASTNode(
                            m_stack[-1].getVal(), m_stack[-1].getType()
                        )  # Create eta node
                        etaNode.setVal("eta")
                        m_stack.pop()

                        boundEnv1 = m_stack.pop()  # Pop bounded environment
                        boundVar1 = m_stack.pop()  # Pop bounded variable
                        deltaIndex1 = (
                            m_stack.pop()
                        )  # Pop index of next control structure

                        # Push the required nodes to the stack
                        m_stack.append(deltaIndex1)
                        m_stack.append(boundVar1)
                        m_stack.append(boundEnv1)
                        m_stack.append(etaNode)
                    else:
                        print("Error")
                        return  # Error

                elif machineTop.getVal() == "eta":  # CSE Rule 13 (Applying f.p)
                    eta = m_stack.pop()  # Pop eta node
                    boundEnv1 = m_stack.pop()  # Pop bounded environment
                    boundVar1 = m_stack.pop()  # Pop bounded variable
                    deltaIndex1 = m_stack.pop()  # Pop index of next control structure

                    # Push the eta node back into the stack
                    m_stack.append(deltaIndex1)
                    m_stack.append(boundVar1)
                    m_stack.append(boundEnv1)
                    m_stack.append(eta)

                    # Push a lambda node with same parameters as the eta node
                    m_stack.append(deltaIndex1)
                    m_stack.append(boundVar1)
                    m_stack.append(boundEnv1)
                    m_stack.append(ASTNode("lambda", "KEYWORD"))

                    # Push two gamma nodes onto control stack
                    control.append(ASTNode("gamma", "KEYWORD"))
                    control.append(ASTNode("gamma", "KEYWORD"))

                elif machineTop.getVal() == "Print":  # Print next item on stack

                    m_stack.pop()
                    nextToPrint = m_stack[-1]  # Get item to print

                    if nextToPrint.getVal() == "tau":  # If the next item is a tuple
                        getTau = m_stack[-1]

                        res = []
                        self.arrangeTuple(getTau, res)  # Arrange the tuple into a list

                        getRev = res[::-1]  # Reverse the list

                        print("(", end="")  # Print the tuple
                        while len(getRev) > 1:
                            top_item = getRev[
                                -1
                            ]  # Get the top item of the stack (equivalent to getRev.top())
                            if top_item.getType() == "STR":
                                print(self.addSpaces(top_item.getVal()), end=", ")
                            else:
                                print(top_item.getVal(), end=", ")
                            getRev.pop()  # Remove the top item from the stack

                        top_item = getRev[-1]  # Get the remaining top item of the stack
                        if top_item.getType() == "STR":
                            print(self.addSpaces(top_item.getVal()), end=")")
                        else:
                            print(top_item.getVal(), end=")")
                        getRev.pop()  # Remove the last remaining item from the stack
                    elif (
                        nextToPrint.getVal() == "lambda"
                    ):  # If the next item is a lambda token
                        m_stack.pop()  # Pop lambda token

                        env = (
                            m_stack.pop()
                        )  # Get the environment in which it was created
                        boundVar = m_stack.pop()  # Get the variable bounded to lambda
                        num = (
                            m_stack.pop()
                        )  # Get the index of next control structure to access

                        print(f"[lambda closure: {boundVar.getVal()}: {num.getVal()}]")
                        return

                    else:  # If the next item is a string or integer
                        if m_stack[-1].getType() == "STR":
                            print(self.addSpaces(m_stack[-1].getVal()), end="")
                        else:
                            print(m_stack[-1].getVal(), end="")

                elif (
                    machineTop.getVal() == "Isinteger"
                ):  # Check if next item in stack is an integer
                    m_stack.pop()  # Pop Isinteger token

                    isNextInt = m_stack.pop()  # Get next item in stack

                    if isNextInt.getType() == "INT":
                        m_stack.append(ASTNode("true", "boolean"))
                    else:
                        m_stack.append(ASTNode("false", "boolean"))

                elif (
                    machineTop.getVal() == "Istruthvalue"
                ):  # Check if next item in stack is a boolean value
                    m_stack.pop()  # Pop Istruthvalue token

                    isNextBool = m_stack.pop()  # Get next item in stack

                    if isNextBool.getVal() == "true" or isNextBool.getVal() == "false":
                        m_stack.append(ASTNode("true", "BOOL"))
                    else:
                        m_stack.append(ASTNode("false", "BOOL"))

                elif (
                    machineTop.getVal() == "Isstring"
                ):  # Check if next item in stack is a string
                    m_stack.pop()  # Pop Isstring token

                    isNextString = m_stack.pop()  # Get next item in stack

                    if isNextString.getType() == "STR":
                        m_stack.append(ASTNode("true", "BOOL"))
                    else:
                        m_stack.append(ASTNode("false", "BOOL"))

                elif (
                    machineTop.getVal() == "Istuple"
                ):  # Check if next item in stack is a tuple
                    m_stack.pop()  # Pop Istuple token

                    isNextTau = m_stack.pop()  # Get next item in stack

                    if isNextTau.getType() == "tau":
                        resNode = ASTNode("true", "BOOL")
                        m_stack.append(resNode)
                    else:
                        resNode = ASTNode("false", "BOOL")
                        m_stack.append(resNode)

                elif (
                    machineTop.getVal() == "Isfunction"
                ):  # Check if next item in stack is a function
                    m_stack.pop()  # Pop Isfunction token

                    isNextFn = m_stack[-1] # Get next item in stack

                    if isNextFn.getVal() == "lambda":
                        resNode = ASTNode("true", "BOOL")
                        m_stack.append(resNode)
                    else:
                        resNode = ASTNode("false", "BOOL")
                        m_stack.append(resNode)

                elif (
                    machineTop.getVal() == "Isdummy"
                ):  # Check if next item in stack is dummy
                    m_stack.pop()  # Pop Isdummy token

                    isNextDmy = m_stack[-1]  # Get next item in stack

                    if isNextDmy.getVal() == "dummy":
                        resNode = ASTNode("true", "BOOL")
                        m_stack.append(resNode)
                    else:
                        resNode = ASTNode("false", "BOOL")
                        m_stack.append(resNode)

                elif machineTop.getVal() == "Stem":  # Get first character of string
                    m_stack.pop()  # Pop Stem token
                    isNextString = m_stack[-1]  # Get next item in stack

                    if isNextString.getVal() == "":
                        return

                    if isNextString.getType() == "STR":
                        strRes = (
                             isNextString.getVal()[0]
                        )  # Get first character
                        m_stack.pop()
                        m_stack.append(ASTNode(strRes, "STR"))

                elif (
                    machineTop.getVal() == "Stern"
                ):  # Get remaining characters other the first character
                    m_stack.pop()  # Pop Stern token
                    isNextString = m_stack[-1]  # Get next item in stack

                    if isNextString.getVal() == "":
                        return

                    if isNextString.getType() == "STR":
                        strRes = (

                            isNextString.getVal()[1:]

                            # "'" + isNextString.getVal()[:] + "'"
                        )  # Get remaining characters
                        m_stack.pop()
                        m_stack.append(ASTNode(strRes, "STR"))

                elif machineTop.getVal() == "Order":  # Get number of items in tuple
                    m_stack.pop()  # Pop Order token

                    numOfItems = 0
                    getTau = m_stack[-1]  # Get next item in stack

                    if getTau.left is not None:
                        getTau = getTau.left

                    while getTau is not None:
                        numOfItems += 1  # Count number of items
                        getTau = getTau.right

                    getTau = m_stack.pop()

                    if getTau.getVal() == "nil":
                        numOfItems = 0

                    orderNode = ASTNode(str(numOfItems), "INT")
                    m_stack.append(orderNode)

                elif machineTop.getVal() == "Conc":  # Concatenate two strings
                    concNode = m_stack.pop()  # Pop Conc token

                    firstString = m_stack.pop()  # Get first string

                    secondString = m_stack[-1]  # Get second string

                    if secondString.getType() == "STR" or (
                        secondString.getType() == "STR"
                        and secondString.left is not None
                        and secondString.left.getVal() == "true"
                    ):
                        m_stack.pop()
                        # res = (
                        #     "'"
                        #     + firstString.getVal()[1:-1]
                        #     + secondString.getVal()[1:-1]
                        #     + "'"
                        # )
                        res =  firstString.getVal() + secondString.getVal()
                        resNode = ASTNode(res, "STR")
                        m_stack.append(resNode)
                        control.pop()
                    else:
                        concNode.left = firstString
                        m_stack.append(concNode)
                        firstString.left = ASTNode("true", "flag")

            elif (
                nextToken.getVal()[0:3] == "env"
            ):  # If env token is on top of control stack (CSE Rule 5)
                removeFromMachineToPutBack = []
                if (
                    m_stack[-1].getVal() == "lambda"
                ):  # Pop lambda token and its parameters
                    removeFromMachineToPutBack.append(m_stack[-1])
                    m_stack.pop()
                    removeFromMachineToPutBack.append(m_stack[-1])
                    m_stack.pop()
                    removeFromMachineToPutBack.append(m_stack[-1])
                    m_stack.pop()
                    removeFromMachineToPutBack.append(m_stack[-1])
                    m_stack.pop()
                else:
                    removeFromMachineToPutBack.append(
                        m_stack[-1]
                    )  # Pop value from stack
                    m_stack.pop()

                remEnv = m_stack[-1]  # Get the environment to remove

                if (
                    nextToken.getVal() == remEnv.getVal()
                ):  # If the environment to remove is the same as the one on top of the control stack
                    m_stack.pop()

                    getCurrEnvironment.pop()
                    if getCurrEnvironment:
                        currEnv = getCurrEnvironment[-1]
                    else:
                        currEnv = None
                else:
                    return

                while (
                    len(removeFromMachineToPutBack) > 0
                ):  # Push the popped values back to the stack
                    m_stack.append(removeFromMachineToPutBack[-1])
                    removeFromMachineToPutBack.pop()

            # If any variables are on top of the control stack
            elif (
                nextToken.getType() == "ID"
                and nextToken.getVal() != "Print"
                and nextToken.getVal() != "Isinteger"
                and nextToken.getVal() != "Istruthvalue"
                and nextToken.getVal() != "Isstring"
                and nextToken.getVal() != "Istuple"
                and nextToken.getVal() != "Isfunction"
                and nextToken.getVal() != "Isdummy"
                and nextToken.getVal() != "Stem"
                and nextToken.getVal() != "Stern"
                and nextToken.getVal() != "Conc"
            ):
                temp = currEnv
                flag = 0
                while temp != None:
                    itr = temp.boundVar.items()
                    for key, value in itr:
                        if nextToken.getVal() == key.getVal():
                            temp = value
                            if (
                                len(temp) == 1
                                and temp[0].getVal() == "Conc"
                                and temp[0].left != None
                            ):
                                control.append(ASTNode("gamma", "KEYWORD"))
                                m_stack.append(temp[0].left)
                                m_stack.append(temp[0])
                            else:
                                i = 0
                                while i < len(temp):
                                    if temp[i].getVal() == "lamdaTuple":
                                        myLambda = temp[i].left
                                        while myLambda != None:
                                            m_stack.append(self.createNode(myLambda))
                                            myLambda = myLambda.right
                                    else:
                                        if temp[i].getVal() == "tau":
                                            res = []
                                            self.arrangeTuple(temp[i], res)
                                        m_stack.append(temp[i])
                                    i += 1
                            flag = 1
                            break
                    if flag == 1:
                        break
                    temp = temp.prev
                if flag == 0:
                    return

            # If a binary or unary operator is on top of the control stack (CSE Rule 6 and CSE Rule 7)
            elif (
                isBinaryOperator(nextToken.getVal())
                or nextToken.getVal() == "neg"
                or nextToken.getVal() == "not"
            ):
                op = nextToken.getVal()  # Get the operator
                if isBinaryOperator(
                    nextToken.getVal()
                ):  # If token is a binary operator
                    node1 = m_stack[-1]  # Get the first operand
                    m_stack.pop()

                    node2 = m_stack[-1]  # Get the second operand
                    m_stack.pop()

                    if node1.getType() == "INT" and node2.getType() == "INT":
                        num1 = int(float(node1.getVal()))
                        num2 = int(float(node2.getVal()))

                        res = 0
                        resPow = 0.0

                        # Perform the operation and create a node with the result
                        if op == "+":  # Addition
                            res = num1 + num2
                            res = str(res)
                            res = ASTNode(res, "INT")
                            m_stack.append(res)
                        elif op == "-":  # Subtraction
                            res = num1 - num2
                            res = str(res)
                            res = ASTNode(res, "INT")
                            m_stack.append(res)
                        elif op == "*":  # Multiplication
                            res = num1 * num2
                            res = str(res)
                            res = ASTNode(res, "INT")
                            m_stack.append(res)
                        elif op == "/":  # Division
                            if num2 == 0:  # If division by zero
                                print("Exception: STATUS_INTEGER_DIVIDE_BY_ZERO")
                            res = num1 / num2
                            res = str(res)
                            res = ASTNode(res, "INT")
                            m_stack.append(res)
                        elif op == "**":  # Power
                            resPow = pow(float(num1), float(num2))
                            resPow = str(resPow)
                            resPow = ASTNode(resPow, "INT")
                            m_stack.append(resPow)
                        elif op == "gr" or op == ">":  # Greater than
                            resStr = "true" if num1 > num2 else "false"
                            res = ASTNode(resStr, "bool")
                            m_stack.append(res)
                        elif op == "ge" or op == ">=":  # Greater than or equal to
                            resStr = "true" if num1 >= num2 else "false"
                            res = ASTNode(resStr, "bool")
                            m_stack.append(res)
                        elif op == "ls" or op == "<":  # Less than
                            resStr = "true" if num1 < num2 else "false"
                            res = ASTNode(resStr, "bool")
                            m_stack.append(res)
                        elif op == "le" or op == "<=":  # Less than or equal to
                            resStr = "true" if num1 <= num2 else "false"
                            res = ASTNode(resStr, "bool")
                            m_stack.append(res)
                        elif op == "eq" or op == "=":  # Equal
                            resStr = "true" if num1 == num2 else "false"
                            res = ASTNode(resStr, "bool")
                            m_stack.append(res)
                        elif op == "ne" or op == "><":  # Not equal
                            resStr = "true" if num1 != num2 else "false"
                            res = ASTNode(resStr, "bool")
                            m_stack.append(res)

                    elif node1.getType() == "STR" and node2.getType() == "STR":
                        if op == "ne" or op == "<>":
                            resStr = (
                                "true" if node1.getVal() != node2.getVal() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            m_stack.append(res)
                        elif op == "eq" or op == "==":
                            resStr = (
                                "true" if node1.getVal() == node2.getVal() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            m_stack.append(res)
                    elif (node1.getVal() == "true" or node1.getVal() == "false") and (
                        node2.getVal() == "false" or node2.getVal() == "true"
                    ):
                        if op == "ne" or op == "<>":
                            resStr = (
                                "true" if node1.getVal() != node2.getVal() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            m_stack.append(res)
                        elif op == "eq" or op == "==":
                            resStr = (
                                "true" if node1.getVal() == node2.getVal() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            m_stack.append(res)
                        elif op == "or":
                            if node1.getVal() == "true" or node2.getVal() == "true":
                                resStr = "true"
                                res = ASTNode(resStr, "BOOL")
                                m_stack.append(res)
                            else:
                                resStr = "false"
                                res = ASTNode(resStr, "BOOL")
                                m_stack.append(res)
                        elif op == "&":
                            if node1.getVal() == "true" and node2.getVal() == "true":
                                resStr = "true"
                                res = ASTNode(resStr, "BOOL")
                                m_stack.append(res)
                            else:
                                resStr = "false"
                                res = ASTNode(resStr, "BOOL")
                                m_stack.append(res)
                elif op == "neg" or op == "not":
                    if op == "neg":
                        node1 = m_stack[-1]
                        m_stack.pop()
                        num1 = int(node1.getVal())
                        res = -num1
                        stri = str(res)
                        resStr = ASTNode(stri, "INT")
                        m_stack.append(resStr)
                    elif op == "not" and (
                        m_stack[-1].getVal() == "true"
                        or m_stack[-1].getVal() == "false"
                    ):
                        if m_stack[-1].getVal() == "true":
                            m_stack.pop()
                            m_stack.append(ASTNode("false", "BOOL"))
                        else:
                            m_stack.pop()
                            m_stack.append(ASTNode("true", "BOOL"))

            elif nextToken.getVal() == "beta":
                boolVal = m_stack[-1]
                m_stack.pop()
                elseIndex = control[-1]
                control.pop()
                thenIndex = control[-1]
                control.pop()
                index = 0
                if boolVal.getVal() == "true":
                    index = int(thenIndex.getVal())
                else:
                    index = int(elseIndex.getVal())
                nextDelta = controlStructure[index]
                for i in range(len(nextDelta)):
                    control.append(nextDelta[i])
            elif nextToken.getVal() == "tau":
                tupleNode = ASTNode("tau", "tau")
                noOfItems = control[-1]
                control.pop()
                numOfItems = int(noOfItems.getVal())
                if m_stack[-1].getVal() == "lambda":
                    lamda = ASTNode(m_stack[-1].getVal(), m_stack[-1].getType())
                    m_stack.pop()
                    prevEnv = ASTNode(m_stack[-1].getVal(), m_stack[-1].getType())
                    m_stack.pop()
                    boundVar = ASTNode(m_stack[-1].getVal(), m_stack[-1].getType())
                    m_stack.pop()
                    nextDeltaIndex = ASTNode(
                        m_stack[-1].getVal(), m_stack[-1].getType()
                    )
                    m_stack.pop()
                    myLambda = ASTNode("lamdaTuple", "lamdaTuple")
                    myLambda.left = nextDeltaIndex
                    nextDeltaIndex.right = boundVar
                    boundVar.right = prevEnv
                    prevEnv.right = lamda
                    tupleNode.left = myLambda
                else:
                    tupleNode.left = self.createNode(m_stack[-1])
                    m_stack.pop()
                sibling = tupleNode.left
                for i in range(1, numOfItems):
                    temp = m_stack[-1]
                    if temp.getVal() == "lambda":
                        lamda = ASTNode(m_stack[-1].getVal(), m_stack[-1].getType())
                        m_stack.pop()
                        prevEnv = ASTNode(m_stack[-1].getVal(), m_stack[-1].getType())
                        m_stack.pop()
                        boundVar = ASTNode(m_stack[-1].getVal(), m_stack[-1].getType())
                        m_stack.pop()
                        nextDeltaIndex = ASTNode(
                            m_stack[-1].getVal(), m_stack[-1].getType()
                        )
                        m_stack.pop()
                        myLambda = ASTNode("lamdaTuple", "lamdaTuple")
                        myLambda.left = nextDeltaIndex
                        nextDeltaIndex.right = boundVar
                        boundVar.right = prevEnv
                        prevEnv.right = lamda
                        sibling.right = myLambda
                        sibling = sibling.right
                    else:
                        m_stack.pop()
                        sibling.right = temp
                        sibling = sibling.right
                m_stack.append(tupleNode)
            elif nextToken.getVal() == "aug":
                token1 = self.createNode(m_stack[-1])
                m_stack.pop()
                token2 = self.createNode(m_stack[-1])
                m_stack.pop()
                if token1.getVal() == "nil" and token2.getVal() == "nil":
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token1
                    m_stack.append(tupleNode)
                elif token1.getVal() == "nil":
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token2
                    m_stack.append(tupleNode)
                elif token2.getVal() == "nil":
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token1
                    m_stack.append(tupleNode)
                elif token1.getType() != "tau":
                    tupleNode = token2.left
                    while tupleNode.right != None:
                        tupleNode = tupleNode.right
                    tupleNode.right = self.createNode(token1)
                    m_stack.append(token2)
                elif token2.getType() != "tau":
                    tupleNode = token1.left
                    while tupleNode.right != None:
                        tupleNode = tupleNode.right
                    tupleNode.right = self.createNode(token2)
                    m_stack.append(token1)
                else:
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token1
                    tupleNode.left.right = token2
                    m_stack.append(tupleNode)

    def arrangeTuple(self, tau_node, res):
        if tau_node is None:
            return
        if tau_node.getVal() == "lamdaTuple":
            return
        if tau_node.getVal() != "tau" and tau_node.getVal() != "nil":
            res.append(tau_node)
        self.arrangeTuple(tau_node.left, res)
        self.arrangeTuple(tau_node.right, res)

    def addSpaces(self, temp):
        temp = temp.replace("\\n", '\n').replace("\\t", '\t')
        temp = temp.replace("'", "")
        return temp
