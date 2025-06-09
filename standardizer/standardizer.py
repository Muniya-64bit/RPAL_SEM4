import copy
from Env.Env import *
from parser.parser import ASTNode

#initial values of global varibales
i = 0
j = 0
index = 1
betaCount = 1

class standardizer:
    def __init__(self, tree):
        self.tree = tree
        self.ST = None

    def standardize_tree(self, x):
        self.transform_node(x)

    def copy_ast_node(self, x):
        t = ASTNode(x.value, x.type)
        t.left = x.left  # Shallow copy
        t.right = None  # Setting right to None as in original code
        return t

    def transform_node(self, t):
        if t is None:
            return None

        self.transform_node(t.left)
        self.transform_node(t.right)

        if t.get_label() == "let":
            if t.left.get_label() == "=":
                t.set_label("gamma")
                t.set_node_type("KEYWORD")
                P = self.copy_ast_node(t.left.right)
                X = self.copy_ast_node(t.left.left)
                E = self.copy_ast_node(t.left.left.right)
                t.left = ASTNode("lambda", "KEYWORD")
                t.left.right = E
                lambda_node = t.left
                lambda_node.left = X
                lambda_node.left.right = P

        elif t.get_label() == "and" and t.left.get_label() == "=":
            equal = t.left
            t.set_label("=")
            t.set_node_type("KEYWORD")
            t.left = ASTNode(",", "PUNCTION")
            comma = t.left
            comma.left = self.copy_ast_node(equal.left)
            t.left.right = ASTNode("tau", "KEYWORD")
            tau = t.left.right

            tau.left = self.copy_ast_node(equal.left.right)
            tau = tau.left
            comma = comma.left
            equal = equal.right

            while equal is not None:
                comma.right = self.copy_ast_node(equal.left)
                comma = comma.right
                tau.right = self.copy_ast_node(equal.left.right)
                tau = tau.right
                equal = equal.right

        elif t.get_label() == "where":
            t.set_label("gamma")
            t.set_node_type("KEYWORD")
            if t.left.right.get_label() == "=":
                P = self.copy_ast_node(t.left)
                X = self.copy_ast_node(t.left.right.left)
                E = self.copy_ast_node(t.left.right.left.right)
                t.left = ASTNode("lambda", "KEYWORD")
                t.left.right = E
                t.left.left = X
                t.left.left.right = P

        elif t.get_label() == "within":
            if t.left.get_label() == "=" and t.left.right.get_label() == "=":
                X1 = self.copy_ast_node(t.left.left)
                E1 = self.copy_ast_node(t.left.left.right)
                X2 = self.copy_ast_node(t.left.right.left)
                E2 = self.copy_ast_node(t.left.right.left.right)
                t.set_label("=")
                t.set_node_type("KEYWORD")
                t.left = X2
                t.left.right = ASTNode("gamma", "KEYWORD")
                temp = t.left.right
                temp.left = ASTNode("lambda", "KEYWORD")
                temp.left.right = E1
                temp = temp.left
                temp.left = X1
                temp.left.right = E2

        elif t.get_label() == "rec" and t.left.get_label() == "=":
            X = self.copy_ast_node(t.left.left)
            E = self.copy_ast_node(t.left.left.right)

            t.set_label("=")
            t.set_node_type("KEYWORD")
            t.left = X
            t.left.right = ASTNode("gamma", "KEYWORD")
            t.left.right.left = ASTNode("YSTAR", "KEYWORD")
            ystar = t.left.right.left

            ystar.right = ASTNode("lambda", "KEYWORD")
            ystar.right.left = self.copy_ast_node(X)
            ystar.right.left.right = self.copy_ast_node(E)

        elif t.get_label() == "fcn_form":
            P = self.copy_ast_node(t.left)
            V = t.left.right

            t.set_label("=")
            t.set_node_type("KEYWORD")
            t.left = P

            temp = t
            while V.right.right is not None:
                temp.left.right = ASTNode("lambda", "KEYWORD")
                temp = temp.left.right
                temp.left = self.copy_ast_node(V)
                V = V.right

            temp.left.right = ASTNode("lambda", "KEYWORD")
            temp = temp.left.right

            temp.left = self.copy_ast_node(V)
            temp.left.right = V.right

        elif t.get_label() == "lambda":
            if t.left is not None:
                V = t.left
                temp = t
                if V.right is not None and V.right.right is not None:
                    while V.right.right is not None:
                        temp.left.right = ASTNode("lambda", "KEYWORD")
                        temp = temp.left.right
                        temp.left = self.copy_ast_node(V)
                        V = V.right

                    temp.left.right = ASTNode("lambda", "KEYWORD")
                    temp = temp.left.right
                    temp.left = self.copy_ast_node(V)
                    temp.left.right = V.right

        elif t.get_label() == "@":
            E1 = self.copy_ast_node(t.left)
            N = self.copy_ast_node(t.left.right)
            E2 = self.copy_ast_node(t.left.right.right)
            t.set_label("gamma")
            t.set_node_type("KEYWORD")
            t.left = ASTNode("gamma", "KEYWORD")
            t.left.right = E2
            t.left.left = N
            t.left.left.right = E1

        self.ST = copy.deepcopy(t)
        return None

    def build_control_structures(self, x, setOfControlStruct):
        global index, j, i, betaCount

        

        if x is None:
            return

        if x.get_label() == "lambda":
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

            self.build_control_structures(x.left.right, setOfControlStruct)

            i = myStoredIndex
            j = tempj
        elif x.get_label() == "->":
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

            self.build_control_structures(x.left, setOfControlStruct)
            diffLc = index - lamdaCount

            while setOfControlStruct[i][0] is not None:
                i += 1
            j = 0

            self.build_control_structures(x.left.right, setOfControlStruct)

            while setOfControlStruct[i][0] is not None:
                i += 1
            j = 0

            self.build_control_structures(x.left.right.right, setOfControlStruct)

            if diffLc == 0 or i < lamdaCount:
                setOfControlStruct[myStoredIndex][tempj].set_label(str(firstIndex))
            else:
                setOfControlStruct[myStoredIndex][tempj].set_label(str(i - 1))

            setOfControlStruct[myStoredIndex][tempj + 1].set_label(str(i))

            i = myStoredIndex
            j = 0

            while setOfControlStruct[i][j] is not None:
                j += 1
            betaCount += 2
        elif x.get_label() == "tau":
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

            self.build_control_structures(x.left, setOfControlStruct)
            x = x.left
            while x is not None:
                self.build_control_structures(x.right, setOfControlStruct)
                x = x.right
        else:
            setOfControlStruct[i][j] = ASTNode(x.get_label(), x.get_node_type())
            j += 1
            self.build_control_structures(x.left, setOfControlStruct)
            if x.left is not None:
                self.build_control_structures(x.left.right, setOfControlStruct)

    def run_cse_machine(self, controlStructure):
        control = []  # Stack for control structure
        m_stack = []  # Stack for operands
        stackOfEnv = []  # Stack of Envs
        getCurrEnv = []

        currEnvIndex = 0  # Initial Env
        currEnv = Env()  # e0

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
        stackOfEnv.append(currEnv)
        getCurrEnv.append(currEnv)

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
                    m_stack.append(env)  # Env it was created in
                    m_stack.append(nextToken)  # Lambda Token
                else:
                    m_stack.append(nextToken)  # Push token to the stack
            elif nextToken.value == "gamma":  # If gamma is on top of control stack
                machineTop = m_stack[-1]
                if machineTop.value == "lambda":  # CSE Rule 4 (Apply lambda)
                    m_stack.pop()  # ************************************************************************************************************
                    prevEnv = m_stack.pop()
                    # Pop the Env in which it was created
                    boundVar = m_stack.pop()  # Pop variable bounded to lambda
                    nextDeltaIndex = m_stack.pop()
                    # Pop index of next control structure to access

                    newEnv = Env()  # Create new Env
                    newEnv.name = "env" + str(currEnvIndex)

                    tempEnv = stackOfEnv.copy()
                    while (
                        tempEnv[-1].name != prevEnv.value
                    ):  # Get the previous Env node
                        tempEnv.pop()

                    newEnv.prev = tempEnv[-1]  # Set the previous Env node
                   
                    # Bounding variables to the Env
                    if (
                        boundVar.value == "," and m_stack[-1].value == "tau"
                    ):  # If Rand is tau
                        boundVariables = []  # Vector of bound variables
                        leftOfComa = boundVar.left  # Get the left of the comma
                        while leftOfComa:
                            boundVariables.append(self.copy_ast_node(leftOfComa))
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
                                self.flatten_tuple(boundValues[i], res)

                            nodeValVector = []
                            nodeValVector.append(boundValues[i])

                            # Insert the bound variable and its value to the Env
                            newEnv.boundVar[boundVariables[i]] = nodeValVector

                    elif m_stack[-1].value == "lambda":  # If Rand is lambda
                        nodeValVector = []
                        temp = []
                        for _ in range(4):
                            temp.append(m_stack.pop())

                        while temp:
                            fromStack = temp.pop()
                            nodeValVector.append(fromStack)

                        # Insert the bound variable and its value to the Env
                        newEnv.boundVar[boundVar] = nodeValVector

                    elif m_stack[-1].value == "Conc":  # If Rand is Conc
                        nodeValVector = []
                        temp = []
                        for _ in range(2):
                            temp.append(m_stack.pop())

                        while temp:
                            fromStack = temp.pop()
                            nodeValVector.append(fromStack)

                        # Insert the bound variable and its value to the Env
                        newEnv.boundVar[boundVar] = nodeValVector

                    elif m_stack[-1].get_label() == "eta":  # If Rand is eta
                        nodeValVector = []
                        temp = []
                        j = 0
                        while j < 4:
                            temp.append(m_stack.pop())
                            j += 1

                        while temp:
                            fromStack = temp.pop()
                            nodeValVector.append(fromStack)

                        # Insert the bound variable and its value to the Env
                        newEnv.boundVar[boundVar] = nodeValVector
                    else:  # If Rand is an Int
                        bindVarVal = m_stack.pop()
                        nodeValVector = []
                        nodeValVector.append(bindVarVal)

                        # Insert the bound variable and its value to the Env
                        newEnv.boundVar[boundVar] = nodeValVector
                    
                    currEnv = newEnv
                    control.append(ASTNode(currEnv.name, "ENV"))
                    m_stack.append(ASTNode(currEnv.name, "ENV"))
                    stackOfEnv.append(currEnv)
                    getCurrEnv.append(currEnv)

                    deltaIndex = int(nextDeltaIndex.get_label())
                    nextDelta = controlStructure[
                        deltaIndex
                    ]  # Get the next control structure
                    for node in nextDelta:
                        control.append(
                            node
                        )  # Push each element of the next control structure to the control stack
                    currEnvIndex += 1

                elif machineTop.get_label() == "tau":  # CSE Rule 10 (Tuple Selection)
                    tau = m_stack.pop()  # Get tau node from top of stack
                    selectTupleIndex = (
                        m_stack.pop()
                    )  # Get the index of the child to be selected
                    tupleIndex = int(selectTupleIndex.get_label())

                    tauLeft = tau.left
                    while tupleIndex > 1:  # Get the child to be selected
                        tupleIndex -= 1
                        tauLeft = tauLeft.right

                    selectedChild = self.copy_ast_node(tauLeft)
                    if selectedChild.get_label() == "lamdaTuple":
                        getNode = selectedChild.left
                        while getNode is not None:
                            m_stack.append(self.copy_ast_node(getNode))
                            getNode = getNode.right
                    else:
                        m_stack.append(selectedChild)

                elif machineTop.get_label() == "YSTAR":  # CSE Rule 12 (Applying YStar)
                    m_stack.pop()  # Pop YSTAR token
                    if m_stack[-1].get_label() == "lambda":
                        etaNode = ASTNode(
                            m_stack[-1].get_label(), m_stack[-1].get_node_type()
                        )  # Create eta node
                        etaNode.set_label("eta")
                        m_stack.pop()

                        boundEnv1 = m_stack.pop()  # Pop bounded Env
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

                elif machineTop.get_label() == "eta":  # CSE Rule 13 (Applying f.p)
                    eta = m_stack.pop()  # Pop eta node
                    boundEnv1 = m_stack.pop()  # Pop bounded Env
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

                elif machineTop.get_label() == "Print":  # Print next item on stack

                    m_stack.pop()
                    nextToPrint = m_stack[-1]  # Get item to print
                    
                    if nextToPrint.get_label() == "tau":  # If the next item is a tuple
                        getTau = m_stack[-1]

                        res = []
                        self.flatten_tuple(getTau, res)  # Arrange the tuple into a list

                        getRev = res[::-1]  # Reverse the list

                        print("(", end="")  # Print the tuple
                        while len(getRev) > 1:
                            top_item = getRev[
                                -1
                            ]  # Get the top item of the stack (equivalent to getRev.top())
                            if top_item.get_node_type() == "STR":
                                print(self.addSpaces(top_item.get_label()), end=", ")
                            else:
                                print(top_item.get_label(), end=", ")
                            getRev.pop()  # Remove the top item from the stack

                        top_item = getRev[-1]  # Get the remaining top item of the stack
                        if top_item.get_node_type() == "STR":
                            print(self.addSpaces(top_item.get_label()), end=")")
                        else:
                            print(top_item.get_label(), end=")")
                        getRev.pop()  # Remove the last remaining item from the stack
                    elif (
                        nextToPrint.get_label() == "lambda"
                    ):  # If the next item is a lambda token
                        m_stack.pop()  # Pop lambda token

                        env = (
                            m_stack.pop()
                        )  # Get the Env in which it was created
                        boundVar = m_stack.pop()  # Get the variable bounded to lambda
                        num = (
                            m_stack.pop()
                        )  # Get the index of next control structure to access

                        print(f"[lambda closure: {boundVar.get_label()}: {num.get_label()}]")
                        return

                    else:  # If the next item is a string or integer
                        if m_stack[-1].get_node_type() == "STR":
                            print(self.addSpaces(m_stack[-1].get_label()), end="")
                        else:
                            print(m_stack[-1].get_label(), end="")

                elif (
                    machineTop.get_label() == "Isinteger"
                ):  # Check if next item in stack is an integer
                    m_stack.pop()  # Pop Isinteger token

                    isNextInt = m_stack.pop()  # Get next item in stack

                    if isNextInt.get_node_type() == "INT":
                        m_stack.append(ASTNode("true", "boolean"))
                    else:
                        m_stack.append(ASTNode("false", "boolean"))

                elif (
                    machineTop.get_label() == "Istruthvalue"
                ):  # Check if next item in stack is a boolean value
                    m_stack.pop()  # Pop Istruthvalue token

                    isNextBool = m_stack.pop()  # Get next item in stack

                    if isNextBool.get_label() == "true" or isNextBool.get_label() == "false":
                        m_stack.append(ASTNode("true", "BOOL"))
                    else:
                        m_stack.append(ASTNode("false", "BOOL"))

                elif (
                    machineTop.get_label() == "Isstring"
                ):  # Check if next item in stack is a string
                    m_stack.pop()  # Pop Isstring token

                    isNextString = m_stack.pop()  # Get next item in stack

                    if isNextString.get_node_type() == "STR":
                        m_stack.append(ASTNode("true", "BOOL"))
                    else:
                        m_stack.append(ASTNode("false", "BOOL"))

                elif (
                    
                    machineTop.get_label() == "Istuple"
                ):  # Check if next item in stack is a tuple
                    m_stack.pop()  # Pop Istuple token
                    
                    isNextTau = m_stack.pop()  # Get next item in stack

                    if isNextTau.get_node_type() == "tau":
                        resNode = ASTNode("true", "BOOL")
                        m_stack.append(resNode)
                    else:
                        resNode = ASTNode("false", "BOOL")
                        m_stack.append(resNode)

                elif (
                    machineTop.get_label() == "Isfunction"
                ):  # Check if next item in stack is a function
                    m_stack.pop()  # Pop Isfunction token

                    isNextFn = m_stack[-1] # Get next item in stack

                    if isNextFn.get_label() == "lambda":
                        resNode = ASTNode("true", "BOOL")
                        m_stack.append(resNode)
                    else:
                        resNode = ASTNode("false", "BOOL")
                        m_stack.append(resNode)

                elif (
                    machineTop.get_label() == "Isdummy"
                ):  # Check if next item in stack is dummy
                    m_stack.pop()  # Pop Isdummy token

                    isNextDmy = m_stack[-1]  # Get next item in stack

                    if isNextDmy.get_label() == "dummy":
                        resNode = ASTNode("true", "BOOL")
                        m_stack.append(resNode)
                    else:
                        resNode = ASTNode("false", "BOOL")
                        m_stack.append(resNode)

                elif machineTop.get_label() == "Stem":  # Get first character of string
                    m_stack.pop()  # Pop Stem token
                    isNextString = m_stack[-1]  # Get next item in stack

                    if isNextString.get_label() == "":
                        return

                    if isNextString.get_node_type() == "STR":
                        strRes = (
                             isNextString.get_label()[0]
                        )  # Get first character
                        m_stack.pop()
                        m_stack.append(ASTNode(strRes, "STR"))

                elif (
                    machineTop.get_label() == "Stern"
                ):  # Get remaining characters other the first character
                    m_stack.pop()  # Pop Stern token
                    isNextString = m_stack[-1]  # Get next item in stack

                    if isNextString.get_label() == "":
                        return

                    if isNextString.get_node_type() == "STR":
                        strRes = (

                            isNextString.get_label()[1:]

                            # "'" + isNextString.get_label()[:] + "'"
                        )  # Get remaining characters
                        m_stack.pop()
                        m_stack.append(ASTNode(strRes, "STR"))

                elif machineTop.get_label() == "Order":  # Get number of items in tuple
                    m_stack.pop()  # Pop Order token

                    numOfItems = 0
                    getTau = m_stack[-1]  # Get next item in stack

                    if getTau.left is not None:
                        getTau = getTau.left

                    while getTau is not None:
                        numOfItems += 1  # Count number of items
                        getTau = getTau.right

                    getTau = m_stack.pop()

                    if getTau.get_label() == "nil":
                        numOfItems = 0

                    orderNode = ASTNode(str(numOfItems), "INT")
                    m_stack.append(orderNode)

                elif machineTop.get_label() == "Conc":  # Concatenate two strings
                    concNode = m_stack.pop()  # Pop Conc token

                    firstString = m_stack.pop()  # Get first string

                    secondString = m_stack[-1]  # Get second string

                    if secondString.get_node_type() == "STR" or (
                        secondString.get_node_type() == "STR"
                        and secondString.left is not None
                        and secondString.left.get_label() == "true"
                    ):
                        m_stack.pop()
                        # res = (
                        #     "'"
                        #     + firstString.get_label()[1:-1]
                        #     + secondString.get_label()[1:-1]
                        #     + "'"
                        # )
                        res =  firstString.get_label() + secondString.get_label()
                        resNode = ASTNode(res, "STR")
                        m_stack.append(resNode)
                        control.pop()
                    else:
                        concNode.left = firstString
                        m_stack.append(concNode)
                        firstString.left = ASTNode("true", "flag")

            elif (
                nextToken.get_label()[0:3] == "env"
            ):  # If env token is on top of control stack (CSE Rule 5)
                removeFromMachineToPutBack = []
                if (
                    m_stack[-1].get_label() == "lambda"
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

                remEnv = m_stack[-1]  # Get the Env to remove
                
                if (
                    nextToken.get_label() == remEnv.get_label()
                ):  # If the Env to remove is the same as the one on top of the control stack
                    m_stack.pop()

                    getCurrEnv.pop()
                    if getCurrEnv:
                        currEnv = getCurrEnv[-1]
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
                nextToken.get_node_type() == "ID"
                and nextToken.get_label() != "Print"
                and nextToken.get_label() != "Isinteger"
                and nextToken.get_label() != "Istruthvalue"
                and nextToken.get_label() != "Isstring"
                and nextToken.get_label() != "Istuple"
                and nextToken.get_label() != "Isfunction"
                and nextToken.get_label() != "Isdummy"
                and nextToken.get_label() != "Stem"
                and nextToken.get_label() != "Stern"
                and nextToken.get_label() != "Conc"
            ):
                temp = currEnv
               
                flag = 0
                while temp != None:
                    itr = temp.boundVar.items()
                    for key, value in itr:
                        if nextToken.get_label() == key.get_label():
                            temp = value
                            if (
                                len(temp) == 1
                                and temp[0].get_label() == "Conc"
                                and temp[0].left != None
                            ):
                                control.append(ASTNode("gamma", "KEYWORD"))
                                m_stack.append(temp[0].left)
                                m_stack.append(temp[0])
                            else:
                                i = 0
                                while i < len(temp):
                                    if temp[i].get_label() == "lamdaTuple":
                                        myLambda = temp[i].left
                                        while myLambda != None:
                                            m_stack.append(self.copy_ast_node(myLambda))
                                            myLambda = myLambda.right
                                    else:
                                        if temp[i].get_label() == "tau":
                                            res = []
                                            self.flatten_tuple(temp[i], res)
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
                isBinaryOperator(nextToken.get_label())
                or nextToken.get_label() == "neg"
                or nextToken.get_label() == "not"
            ):
                op = nextToken.get_label()  # Get the operator
            
                if isBinaryOperator(
                    nextToken.get_label()
                ):  # If token is a binary operator
                    node1 = m_stack[-1]  # Get the first operand
                    m_stack.pop()

                    node2 = m_stack[-1]  # Get the second operand
                    m_stack.pop()

                    if node1.get_node_type() == "INT" and node2.get_node_type() == "INT":
                        num1 = int(float(node1.get_label()))
                        num2 = int(float(node2.get_label()))

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

                    elif node1.get_node_type() == "STR" and node2.get_node_type() == "STR":
                        if op == "ne" or op == "<>":
                            resStr = (
                                "true" if node1.get_label() != node2.get_label() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            m_stack.append(res)
                        elif op == "eq" or op == "==":
                            resStr = (
                                "true" if node1.get_label() == node2.get_label() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            m_stack.append(res)
                    elif (node1.get_label() == "true" or node1.get_label() == "false") and (
                        node2.get_label() == "false" or node2.get_label() == "true"
                    ):
                        if op == "ne" or op == "<>":
                            resStr = (
                                "true" if node1.get_label() != node2.get_label() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            m_stack.append(res)
                        elif op == "eq" or op == "==":
                            resStr = (
                                "true" if node1.get_label() == node2.get_label() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            m_stack.append(res)
                        elif op == "or":
                            if node1.get_label() == "true" or node2.get_label() == "true":
                                resStr = "true"
                                res = ASTNode(resStr, "BOOL")
                                m_stack.append(res)
                            else:
                                resStr = "false"
                                res = ASTNode(resStr, "BOOL")
                                m_stack.append(res)
                        elif op == "&":
                            if node1.get_label() == "true" and node2.get_label() == "true":
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
                        num1 = int(node1.get_label())
                        res = -num1
                        stri = str(res)
                        resStr = ASTNode(stri, "INT")
                        m_stack.append(resStr)
                    elif op == "not" and (
                        m_stack[-1].get_label() == "true"
                        or m_stack[-1].get_label() == "false"
                    ):
                        if m_stack[-1].get_label() == "true":
                            m_stack.pop()
                            m_stack.append(ASTNode("false", "BOOL"))
                        else:
                            m_stack.pop()
                            m_stack.append(ASTNode("true", "BOOL"))

            elif nextToken.get_label() == "beta":
                boolVal = m_stack[-1]
                m_stack.pop()
                elseIndex = control[-1]
                control.pop()
                thenIndex = control[-1]
                control.pop()
                index = 0
                if boolVal.get_label() == "true":
                    index = int(thenIndex.get_label())
                else:
                    index = int(elseIndex.get_label())
                nextDelta = controlStructure[index]
                for i in range(len(nextDelta)):
                    control.append(nextDelta[i])
            elif nextToken.get_label() == "tau":
                tupleNode = ASTNode("tau", "tau")
                noOfItems = control[-1]
                control.pop()
                numOfItems = int(noOfItems.get_label())
                if m_stack[-1].get_label() == "lambda":
                    lamda = ASTNode(m_stack[-1].get_label(), m_stack[-1].get_node_type())
                    m_stack.pop()
                    prevEnv = ASTNode(m_stack[-1].get_label(), m_stack[-1].get_node_type())
                    m_stack.pop()
                    boundVar = ASTNode(m_stack[-1].get_label(), m_stack[-1].get_node_type())
                    m_stack.pop()
                    nextDeltaIndex = ASTNode(
                        m_stack[-1].get_label(), m_stack[-1].get_node_type()
                    )
                    m_stack.pop()
                    myLambda = ASTNode("lamdaTuple", "lamdaTuple")
                    myLambda.left = nextDeltaIndex
                    nextDeltaIndex.right = boundVar
                    boundVar.right = prevEnv
                    prevEnv.right = lamda
                    tupleNode.left = myLambda
                else:
                    tupleNode.left = self.copy_ast_node(m_stack[-1])
                    m_stack.pop()
                sibling = tupleNode.left
                for i in range(1, numOfItems):
                    temp = m_stack[-1]
                    if temp.get_label() == "lambda":
                        lamda = ASTNode(m_stack[-1].get_label(), m_stack[-1].get_node_type())
                        m_stack.pop()
                        prevEnv = ASTNode(m_stack[-1].get_label(), m_stack[-1].get_node_type())
                        m_stack.pop()
                        boundVar = ASTNode(m_stack[-1].get_label(), m_stack[-1].get_node_type())
                        m_stack.pop()
                        nextDeltaIndex = ASTNode(
                            m_stack[-1].get_label(), m_stack[-1].get_node_type()
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
            elif nextToken.get_label() == "aug":
                token1 = self.copy_ast_node(m_stack[-1])
                m_stack.pop()
                token2 = self.copy_ast_node(m_stack[-1])
                m_stack.pop()
                if token1.get_label() == "nil" and token2.get_label() == "nil":
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token1
                    m_stack.append(tupleNode)
                elif token1.get_label() == "nil":
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token2
                    m_stack.append(tupleNode)
                elif token2.get_label() == "nil":
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token1
                    m_stack.append(tupleNode)
                elif token1.get_node_type() != "tau":
                    tupleNode = token2.left
                    while tupleNode.right != None:
                        tupleNode = tupleNode.right
                    tupleNode.right = self.copy_ast_node(token1)
                    m_stack.append(token2)
                elif token2.get_node_type() != "tau":
                    tupleNode = token1.left
                    while tupleNode.right != None:
                        tupleNode = tupleNode.right
                    tupleNode.right = self.copy_ast_node(token2)
                    m_stack.append(token1)
                else:
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token1
                    tupleNode.left.right = token2
                    m_stack.append(tupleNode)

    def flatten_tuple(self, tau_node, res):
        if tau_node is None:
            return
        if tau_node.get_label() == "lamdaTuple":
            return
        if tau_node.get_label() != "tau" and tau_node.get_label() != "nil":
            res.append(tau_node)
        self.flatten_tuple(tau_node.left, res)
        self.flatten_tuple(tau_node.right, res)

    def addSpaces(self, temp):
        temp = temp.replace("\\n", '\n').replace("\\t", '\t')
        temp = temp.replace("'", "")
        return temp
