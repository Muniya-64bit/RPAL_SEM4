import copy
from Env.Env import *
from parser.parser import ASTNode

# Default settings for global counters
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
        # Create new node with same properties as input
        node = ASTNode(x.value, x.type)
        node.left = x.left  # preserve left subtree
        node.right = None  # initialize right child as empty
        return node

    def transform_node(self, node):
        if node is None:
            return None

        # Process children first (post-order traversal)
        self.transform_node(node.left)
        self.transform_node(node.right)

        # Handle different node types
        if node.get_label() == "let":
            if node.left.get_label() == "=":
                node.set_label("gamma")
                node.set_node_type("KEYWORD")
                P = self.copy_ast_node(node.left.right)
                X = self.copy_ast_node(node.left.left)
                E = self.copy_ast_node(node.left.left.right)
                node.left = ASTNode("lambda", "KEYWORD")
                node.left.right = E
                lambda_node = node.left
                lambda_node.left = X
                lambda_node.left.right = P

        elif node.get_label() == "and" and node.left.get_label() == "=":
            equal = node.left
            node.set_label("=")
            node.set_node_type("KEYWORD")
            node.left = ASTNode(",", "PUNCTION")
            comma = node.left
            comma.left = self.copy_ast_node(equal.left)
            node.left.right = ASTNode("tau", "KEYWORD")
            tau = node.left.right

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

        elif node.get_label() == "where":
            node.set_label("gamma")
            node.set_node_type("KEYWORD")
            if node.left.right.get_label() == "=":
                P = self.copy_ast_node(node.left)
                X = self.copy_ast_node(node.left.right.left)
                E = self.copy_ast_node(node.left.right.left.right)
                node.left = ASTNode("lambda", "KEYWORD")
                node.left.right = E
                node.left.left = X
                node.left.left.right = P

        elif node.get_label() == "within":
            if node.left.get_label() == "=" and node.left.right.get_label() == "=":
                X1 = self.copy_ast_node(node.left.left)
                E1 = self.copy_ast_node(node.left.left.right)
                X2 = self.copy_ast_node(node.left.right.left)
                E2 = self.copy_ast_node(node.left.right.left.right)
                node.set_label("=")
                node.set_node_type("KEYWORD")
                node.left = X2
                node.left.right = ASTNode("gamma", "KEYWORD")
                temp = node.left.right
                temp.left = ASTNode("lambda", "KEYWORD")
                temp.left.right = E1
                temp = temp.left
                temp.left = X1
                temp.left.right = E2

        elif node.get_label() == "rec" and node.left.get_label() == "=":
            X = self.copy_ast_node(node.left.left)
            E = self.copy_ast_node(node.left.left.right)

            node.set_label("=")
            node.set_node_type("KEYWORD")
            node.left = X
            node.left.right = ASTNode("gamma", "KEYWORD")
            node.left.right.left = ASTNode("YSTAR", "KEYWORD")
            ystar = node.left.right.left

            ystar.right = ASTNode("lambda", "KEYWORD")
            ystar.right.left = self.copy_ast_node(X)
            ystar.right.left.right = self.copy_ast_node(E)

        elif node.get_label() == "fcn_form":
            P = self.copy_ast_node(node.left)
            V = node.left.right

            node.set_label("=")
            node.set_node_type("KEYWORD")
            node.left = P

            temp = node
            while V.right.right is not None:
                temp.left.right = ASTNode("lambda", "KEYWORD")
                temp = temp.left.right
                temp.left = self.copy_ast_node(V)
                V = V.right

            temp.left.right = ASTNode("lambda", "KEYWORD")
            temp = temp.left.right

            temp.left = self.copy_ast_node(V)
            temp.left.right = V.right

        elif node.get_label() == "lambda":
            if node.left is not None:
                V = node.left
                temp = node
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

        elif node.get_label() == "@":
            E1 = self.copy_ast_node(node.left)
            N = self.copy_ast_node(node.left.right)
            E2 = self.copy_ast_node(node.left.right.right)
            node.set_label("gamma")
            node.set_node_type("KEYWORD")
            node.left = ASTNode("gamma", "KEYWORD")
            node.left.right = E2
            node.left.left = N
            node.left.left.right = E1

        self.ST = copy.deepcopy(node)
        return None

    def build_control_structures(self, x, setOfControlStruct):
        global index, j, i, betaCount

        # Base case for recursion
        if x is None:
            return

        # Handle lambda expressions
        if x.get_label() == "lambda":
            t1 = i
            k = 0
            setOfControlStruct[i][j] = ASTNode("", "")
            i = 0

            # Find next available slot
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

            # Process child nodes
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

            # Find empty slot for new delta
            while setOfControlStruct[k][0] is not None:
                k += 1
            firstIndex = k
            lamdaCount = index

            self.build_control_structures(x.left, setOfControlStruct)
            diffLc = index - lamdaCount

            # Process right branches
            while setOfControlStruct[i][0] is not None:
                i += 1
            j = 0

            self.build_control_structures(x.left.right, setOfControlStruct)

            while setOfControlStruct[i][0] is not None:
                i += 1
            j = 0

            self.build_control_structures(x.left.right.right, setOfControlStruct)

            # Update delta references
            if diffLc == 0 or i < lamdaCount:
                setOfControlStruct[myStoredIndex][tempj].set_label(str(firstIndex))
            else:
                setOfControlStruct[myStoredIndex][tempj].set_label(str(i - 1))

            setOfControlStruct[myStoredIndex][tempj + 1].set_label(str(i))

            i = myStoredIndex
            j = 0

            # Move to next available position
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
            # Default case for other node types
            setOfControlStruct[i][j] = ASTNode(x.get_label(), x.get_node_type())
            j += 1
            self.build_control_structures(x.left, setOfControlStruct)
            if x.left is not None:
                self.build_control_structures(x.left.right, setOfControlStruct)

    def run_cse_machine(self, controlStructure):
        # Initialize execution stacks
        control = []  # Control flow stack
        execution_stack = []  # Data stack
        stackOfEnv = []  # Environment stack
        getCurrEnv = []

        currEnvIndex = 0  # Current environment pointer
        currEnv = Env()  # Root environment

        def isBinaryOperator(op):
            # Check if token is a binary operator
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
        
        # Initialize stacks with root environment
        execution_stack.append(ASTNode(currEnv.name, "ENV"))
        control.append(ASTNode(currEnv.name, "ENV"))
        stackOfEnv.append(currEnv)
        getCurrEnv.append(currEnv)

        # Load initial control structure
        tempDelta = controlStructure[0]
        for node in tempDelta:
            control.append(node)

        # Main execution loop
        while control:
            nextToken = control.pop()  # Fetch next instruction

            if nextToken.value == "nil":
                nextToken.type = "tau"

            # Handle different token types
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
                    # Process lambda expression
                    boundVar = control.pop()
                    nextDeltaIndex = control.pop()
                    env = ASTNode(currEnv.name, "ENV")

                    execution_stack.append(nextDeltaIndex)
                    execution_stack.append(boundVar)
                    execution_stack.append(env)
                    execution_stack.append(nextToken)
                else:
                    execution_stack.append(nextToken)
            elif nextToken.value == "gamma":
                # Handle function application
                machineTop = execution_stack[-1]
                if machineTop.value == "lambda":
                    execution_stack.pop()
                    prevEnv = execution_stack.pop()
                    boundVar = execution_stack.pop()
                    nextDeltaIndex = execution_stack.pop()

                    # Create new environment
                    newEnv = Env()
                    newEnv.name = "env" + str(currEnvIndex)

                    # Find parent environment
                    tempEnv = stackOfEnv.copy()
                    while tempEnv[-1].name != prevEnv.value:
                        tempEnv.pop()

                    newEnv.prev = tempEnv[-1]
                   
                    # Handle variable binding
                    if boundVar.value == "," and execution_stack[-1].value == "tau":
                        boundVariables = []
                        leftOfComa = boundVar.left
                        while leftOfComa:
                            boundVariables.append(self.copy_ast_node(leftOfComa))
                            leftOfComa = leftOfComa.right

                                               # Store bound values for environment binding
                        boundValues = []  
                        # Remove tau node from stack
                        tau = execution_stack.pop()  

                        # Traverse through tau children
                        tauLeft = tau.left  
                        while tauLeft:
                            boundValues.append(tauLeft)
                            tauLeft = tauLeft.right  

                        # Process each bound value
                        for i in range(len(boundValues)):
                            if boundValues[i].value == "tau":
                                res = []
                                self.flatten_tuple(boundValues[i], res)

                            nodeValVector = []
                            nodeValVector.append(boundValues[i])

                            # Create environment binding
                            newEnv.boundVar[boundVariables[i]] = nodeValVector

                    elif execution_stack[-1].value == "lambda":  # Handle lambda as right operand
                        nodeValVector = []
                        temp = []
                        # Pop lambda components from stack
                        for _ in range(4):
                            temp.append(execution_stack.pop())

                        # Reconstruct in correct order
                        while temp:
                            fromStack = temp.pop()
                            nodeValVector.append(fromStack)

                        # Create environment binding for lambda
                        newEnv.boundVar[boundVar] = nodeValVector

                    elif execution_stack[-1].value == "Conc":  # Handle string concatenation operand
                        nodeValVector = []
                        temp = []
                        # Pop concatenation components
                        for _ in range(2):
                            temp.append(execution_stack.pop())

                        while temp:
                            fromStack = temp.pop()
                            nodeValVector.append(fromStack)

                        # Create environment binding
                        newEnv.boundVar[boundVar] = nodeValVector

                    elif execution_stack[-1].get_label() == "eta":  # Handle eta expression operand
                        nodeValVector = []
                        temp = []
                        j = 0
                        # Pop eta components
                        while j < 4:
                            temp.append(execution_stack.pop())
                            j += 1

                        while temp:
                            fromStack = temp.pop()
                            nodeValVector.append(fromStack)

                        # Create environment binding
                        newEnv.boundVar[boundVar] = nodeValVector
                    else:  # Handle primitive value operand
                        bindVarVal = execution_stack.pop()
                        nodeValVector = []
                        nodeValVector.append(bindVarVal)

                        # Create simple environment binding
                        newEnv.boundVar[boundVar] = nodeValVector
                    
                    # Update current environment
                    currEnv = newEnv
                    control.append(ASTNode(currEnv.name, "ENV"))
                    execution_stack.append(ASTNode(currEnv.name, "ENV"))
                    stackOfEnv.append(currEnv)
                    getCurrEnv.append(currEnv)

                    # Load next control structure
                    deltaIndex = int(nextDeltaIndex.get_label())
                    nextDelta = controlStructure[
                        deltaIndex
                    ]  
                    for node in nextDelta:
                        control.append(
                            node
                        )  
                    currEnvIndex += 1

                elif machineTop.get_label() == "tau":  # Handle tuple selection operation
                    tau = execution_stack.pop()  
                    selectTupleIndex = (
                        execution_stack.pop()
                    )  
                    tupleIndex = int(selectTupleIndex.get_label())

                    # Traverse to selected tuple element
                    tauLeft = tau.left
                    while tupleIndex > 1:  
                        tupleIndex -= 1
                        tauLeft = tauLeft.right

                    # Push selected element to stack
                    selectedChild = self.copy_ast_node(tauLeft)
                    if selectedChild.get_label() == "lamdaTuple":
                        getNode = selectedChild.left
                        while getNode is not None:
                            execution_stack.append(self.copy_ast_node(getNode))
                            getNode = getNode.right
                    else:
                        execution_stack.append(selectedChild)

                elif machineTop.get_label() == "YSTAR":  # Handle Y-combinator application
                    execution_stack.pop()  
                    if execution_stack[-1].get_label() == "lambda":
                        # Create eta node for fixed-point computation
                        etaNode = ASTNode(
                            execution_stack[-1].get_label(), execution_stack[-1].get_node_type()
                        )  
                        etaNode.set_label("eta")
                        execution_stack.pop()

                        # Extract lambda components
                        boundEnv1 = execution_stack.pop()  
                        boundVar1 = execution_stack.pop()  
                        deltaIndex1 = (
                            execution_stack.pop()
                        )  

                        # Reconstruct with eta node
                        execution_stack.append(deltaIndex1)
                        execution_stack.append(boundVar1)
                        execution_stack.append(boundEnv1)
                        execution_stack.append(etaNode)
                    else:
                        print("Error")
                        return  

                elif machineTop.get_label() == "eta":  # Handle fixed-point expansion
                    eta = execution_stack.pop()  
                    boundEnv1 = execution_stack.pop()  
                    boundVar1 = execution_stack.pop()  
                    deltaIndex1 = execution_stack.pop()  

                    # Reconstruct original components
                    execution_stack.append(deltaIndex1)
                    execution_stack.append(boundVar1)
                    execution_stack.append(boundEnv1)
                    execution_stack.append(eta)

                    # Create parallel lambda structure
                    execution_stack.append(deltaIndex1)
                    execution_stack.append(boundVar1)
                    execution_stack.append(boundEnv1)
                    execution_stack.append(ASTNode("lambda", "KEYWORD"))

                    # Schedule two gamma applications
                    control.append(ASTNode("gamma", "KEYWORD"))
                    control.append(ASTNode("gamma", "KEYWORD"))

                elif machineTop.get_label() == "Print":  # Handle print operation
                    execution_stack.pop()
                    nextToPrint = execution_stack[-1]  
                    
                    if nextToPrint.get_label() == "tau":  # Print tuple contents
                        getTau = execution_stack[-1]

                        res = []
                        self.flatten_tuple(getTau, res)  

                        getRev = res[::-1]  

                        print("(", end="")  
                        while len(getRev) > 1:
                            top_item = getRev[
                                -1
                            ]  
                            if top_item.get_node_type() == "STR":
                                print(self.addSpaces(top_item.get_label()), end=", ")
                            else:
                                print(top_item.get_label(), end=", ")
                            getRev.pop()  

                        top_item = getRev[-1]  
                        if top_item.get_node_type() == "STR":
                            print(self.addSpaces(top_item.get_label()), end=")")
                        else:
                            print(top_item.get_label(), end=")")
                        getRev.pop()  
                    elif (
                        nextToPrint.get_label() == "lambda"
                    ):  
                        execution_stack.pop()  

                        env = (
                            execution_stack.pop()
                        )  
                        boundVar = execution_stack.pop()  
                        num = (
                            execution_stack.pop()
                        )  

                        print(f"[lambda closure: {boundVar.get_label()}: {num.get_label()}]")
                        return

                    else:  
                        if execution_stack[-1].get_node_type() == "STR":
                            print(self.addSpaces(execution_stack[-1].get_label()), end="")
                        else:
                            print(execution_stack[-1].get_label(), end="")

                elif (
                    machineTop.get_label() == "Isinteger"
                ):  # Integer type check
                    execution_stack.pop()  

                    isNextInt = execution_stack.pop()  

                    if isNextInt.get_node_type() == "INT":
                        execution_stack.append(ASTNode("true", "boolean"))
                    else:
                        execution_stack.append(ASTNode("false", "boolean"))

                elif (
                    machineTop.get_label() == "Istruthvalue"
                ):  # Boolean type check
                    execution_stack.pop()  

                    isNextBool = execution_stack.pop()  

                    if isNextBool.get_label() == "true" or isNextBool.get_label() == "false":
                        execution_stack.append(ASTNode("true", "BOOL"))
                    else:
                        execution_stack.append(ASTNode("false", "BOOL"))

                elif (
                    machineTop.get_label() == "Isstring"
                ):  # String type check
                    execution_stack.pop()  

                    isNextString = execution_stack.pop()  

                    if isNextString.get_node_type() == "STR":
                        execution_stack.append(ASTNode("true", "BOOL"))
                    else:
                        execution_stack.append(ASTNode("false", "BOOL"))

                elif (
                    machineTop.get_label() == "Istuple"
                ):  # Tuple type check
                    execution_stack.pop()  
                    
                    isNextTau = execution_stack.pop()  

                    if isNextTau.get_node_type() == "tau":
                        resNode = ASTNode("true", "BOOL")
                        execution_stack.append(resNode)
                    else:
                        resNode = ASTNode("false", "BOOL")
                        execution_stack.append(resNode)

                elif (
                    machineTop.get_label() == "Isfunction"
                ):  # Function type check
                    execution_stack.pop()  

                    isNextFn = execution_stack[-1] 

                    if isNextFn.get_label() == "lambda":
                        resNode = ASTNode("true", "BOOL")
                        execution_stack.append(resNode)
                    else:
                        resNode = ASTNode("false", "BOOL")
                        execution_stack.append(resNode)

                elif (
                    machineTop.get_label() == "Isdummy"
                ):  # Dummy value check
                    execution_stack.pop()  

                    isNextDmy = execution_stack[-1]  

                    if isNextDmy.get_label() == "dummy":
                        resNode = ASTNode("true", "BOOL")
                        execution_stack.append(resNode)
                    else:
                        resNode = ASTNode("false", "BOOL")
                        execution_stack.append(resNode)

                elif machineTop.get_label() == "Stem":  # String head operation
                    execution_stack.pop()  
                    isNextString = execution_stack[-1]  

                    if isNextString.get_label() == "":
                        return

                    if isNextString.get_node_type() == "STR":
                        strRes = (
                             isNextString.get_label()[0]
                        )  
                        execution_stack.pop()
                        execution_stack.append(ASTNode(strRes, "STR"))

                elif (
                    machineTop.get_label() == "Stern"
                ):  # String tail operation
                    execution_stack.pop()  
                    isNextString = execution_stack[-1]  

                    if isNextString.get_label() == "":
                        return

                    if isNextString.get_node_type() == "STR":
                        strRes = (
                            isNextString.get_label()[1:]
                        )  
                        execution_stack.pop()
                        execution_stack.append(ASTNode(strRes, "STR"))

                elif machineTop.get_label() == "Order":  # Tuple size operation
                    execution_stack.pop()  

                    numOfItems = 0
                    getTau = execution_stack[-1]  

                    if getTau.left is not None:
                        getTau = getTau.left

                    while getTau is not None:
                        numOfItems += 1  
                        getTau = getTau.right

                    getTau = execution_stack.pop()

                    if getTau.get_label() == "nil":
                        numOfItems = 0

                    orderNode = ASTNode(str(numOfItems), "INT")
                    execution_stack.append(orderNode)

                elif machineTop.get_label() == "Conc":  # String concatenation
                    concNode = execution_stack.pop()  

                    firstString = execution_stack.pop()  

                    secondString = execution_stack[-1]  

                    if secondString.get_node_type() == "STR" or (
                        secondString.get_node_type() == "STR"
                        and secondString.left is not None
                        and secondString.left.get_label() == "true"
                    ):
                        execution_stack.pop()
                        res =  firstString.get_label() + secondString.get_label()
                        resNode = ASTNode(res, "STR")
                        execution_stack.append(resNode)
                        control.pop()
                    else:
                        concNode.left = firstString
                        execution_stack.append(concNode)
                        firstString.left = ASTNode("true", "flag")

            elif (
                nextToken.get_label()[0:3] == "env"
            ):  # Environment switching operation
                removeFromMachineToPutBack = []
                if (
                    execution_stack[-1].get_label() == "lambda"
                ):  
                    removeFromMachineToPutBack.append(execution_stack[-1])
                    execution_stack.pop()
                    removeFromMachineToPutBack.append(execution_stack[-1])
                    execution_stack.pop()
                    removeFromMachineToPutBack.append(execution_stack[-1])
                    execution_stack.pop()
                    removeFromMachineToPutBack.append(execution_stack[-1])
                    execution_stack.pop()
                else:
                    removeFromMachineToPutBack.append(
                        execution_stack[-1]
                    )  
                    execution_stack.pop()

                remEnv = execution_stack[-1]  
                
                if (
                    nextToken.get_label() == remEnv.get_label()
                ):  
                    execution_stack.pop()
                    
                    getCurrEnv.pop()
                    if getCurrEnv:
                        currEnv = getCurrEnv[-1]
                    else:
                        currEnv = None
                else:
                    return

                while (
                    len(removeFromMachineToPutBack) > 0
                ):  # Put back removed nodes to machine stack
                    execution_stack.append(removeFromMachineToPutBack[-1])
                    removeFromMachineToPutBack.pop()

            # If an identifier is on top of the control stack (CSE Rule 5)
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
                                execution_stack.append(temp[0].left)
                                execution_stack.append(temp[0])
                            else:
                                i = 0
                                while i < len(temp):
                                    if temp[i].get_label() == "lamdaTuple":
                                        myLambda = temp[i].left
                                        while myLambda != None:
                                            execution_stack.append(self.copy_ast_node(myLambda))
                                            myLambda = myLambda.right
                                    else:
                                        if temp[i].get_label() == "tau":
                                            res = []
                                            self.flatten_tuple(temp[i], res)
                                        execution_stack.append(temp[i])
                                    i += 1
                            flag = 1
                            break
                    if flag == 1:
                        break
                    temp = temp.prev
                if flag == 0:
                    return

            # If a keyword is on top of the control stack
            elif (
                isBinaryOperator(nextToken.get_label())
                or nextToken.get_label() == "neg"
                or nextToken.get_label() == "not"
            ):
                op = nextToken.get_label()  
            
                if isBinaryOperator(
                    nextToken.get_label()
                ):  # Handle binary operators
                    node1 = execution_stack[-1]  
                    execution_stack.pop()

                    node2 = execution_stack[-1]  
                    execution_stack.pop()

                    if node1.get_node_type() == "INT" and node2.get_node_type() == "INT":
                        num1 = int(float(node1.get_label()))
                        num2 = int(float(node2.get_label()))

                        res = 0
                        resPow = 0.0

                        # Perform operation based on operator type
                        if op == "+":  # Addition
                            res = num1 + num2
                            res = str(res)
                            res = ASTNode(res, "INT")
                            execution_stack.append(res)
                        elif op == "-":  # Subtraction
                            res = num1 - num2
                            res = str(res)
                            res = ASTNode(res, "INT")
                            execution_stack.append(res)
                        elif op == "*":  # Multiplication
                            res = num1 * num2
                            res = str(res)
                            res = ASTNode(res, "INT")
                            execution_stack.append(res)
                        elif op == "/":  # Division
                            if num2 == 0:  # If division by zero
                                print("Exception: STATUS_INTEGER_DIVIDE_BY_ZERO")
                            res = num1 / num2
                            res = str(res)
                            res = ASTNode(res, "INT")
                            execution_stack.append(res)
                        elif op == "**":  # Power
                            resPow = pow(float(num1), float(num2))
                            resPow = str(resPow)
                            resPow = ASTNode(resPow, "INT")
                            execution_stack.append(resPow)
                        elif op == "gr" or op == ">":  # Greater than
                            resStr = "true" if num1 > num2 else "false"
                            res = ASTNode(resStr, "bool")
                            execution_stack.append(res)
                        elif op == "ge" or op == ">=":  # Greater than or equal to
                            resStr = "true" if num1 >= num2 else "false"
                            res = ASTNode(resStr, "bool")
                            execution_stack.append(res)
                        elif op == "ls" or op == "<":  # Less than
                            resStr = "true" if num1 < num2 else "false"
                            res = ASTNode(resStr, "bool")
                            execution_stack.append(res)
                        elif op == "le" or op == "<=":  # Less than or equal to
                            resStr = "true" if num1 <= num2 else "false"
                            res = ASTNode(resStr, "bool")
                            execution_stack.append(res)
                        elif op == "eq" or op == "=":  # Equal
                            resStr = "true" if num1 == num2 else "false"
                            res = ASTNode(resStr, "bool")
                            execution_stack.append(res)
                        elif op == "ne" or op == "><":  # Not equal
                            resStr = "true" if num1 != num2 else "false"
                            res = ASTNode(resStr, "bool")
                            execution_stack.append(res)

                    elif node1.get_node_type() == "STR" and node2.get_node_type() == "STR":
                        if op == "ne" or op == "<>":
                            resStr = (
                                "true" if node1.get_label() != node2.get_label() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            execution_stack.append(res)
                        elif op == "eq" or op == "==":
                            resStr = (
                                "true" if node1.get_label() == node2.get_label() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            execution_stack.append(res)
                    elif (node1.get_label() == "true" or node1.get_label() == "false") and (
                        node2.get_label() == "false" or node2.get_label() == "true"
                    ):
                        if op == "ne" or op == "<>":
                            resStr = (
                                "true" if node1.get_label() != node2.get_label() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            execution_stack.append(res)
                        elif op == "eq" or op == "==":
                            resStr = (
                                "true" if node1.get_label() == node2.get_label() else "false"
                            )
                            res = ASTNode(resStr, "BOOL")
                            execution_stack.append(res)
                        elif op == "or":
                            if node1.get_label() == "true" or node2.get_label() == "true":
                                resStr = "true"
                                res = ASTNode(resStr, "BOOL")
                                execution_stack.append(res)
                            else:
                                resStr = "false"
                                res = ASTNode(resStr, "BOOL")
                                execution_stack.append(res)
                        elif op == "&":
                            if node1.get_label() == "true" and node2.get_label() == "true":
                                resStr = "true"
                                res = ASTNode(resStr, "BOOL")
                                execution_stack.append(res)
                            else:
                                resStr = "false"
                                res = ASTNode(resStr, "BOOL")
                                execution_stack.append(res)
                elif op == "neg" or op == "not":
                    if op == "neg":
                        node1 = execution_stack[-1]
                        execution_stack.pop()
                        num1 = int(node1.get_label())
                        res = -num1
                        stri = str(res)
                        resStr = ASTNode(stri, "INT")
                        execution_stack.append(resStr)
                    elif op == "not" and (
                        execution_stack[-1].get_label() == "true"
                        or execution_stack[-1].get_label() == "false"
                    ):
                        if execution_stack[-1].get_label() == "true":
                            execution_stack.pop()
                            execution_stack.append(ASTNode("false", "BOOL"))
                        else:
                            execution_stack.pop()
                            execution_stack.append(ASTNode("true", "BOOL"))

            elif nextToken.get_label() == "beta":
                boolVal = execution_stack[-1]
                execution_stack.pop()
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
                if execution_stack[-1].get_label() == "lambda":
                    lamda = ASTNode(execution_stack[-1].get_label(), execution_stack[-1].get_node_type())
                    execution_stack.pop()
                    prevEnv = ASTNode(execution_stack[-1].get_label(), execution_stack[-1].get_node_type())
                    execution_stack.pop()
                    boundVar = ASTNode(execution_stack[-1].get_label(), execution_stack[-1].get_node_type())
                    execution_stack.pop()
                    nextDeltaIndex = ASTNode(
                        execution_stack[-1].get_label(), execution_stack[-1].get_node_type()
                    )
                    execution_stack.pop()
                    myLambda = ASTNode("lamdaTuple", "lamdaTuple")
                    myLambda.left = nextDeltaIndex
                    nextDeltaIndex.right = boundVar
                    boundVar.right = prevEnv
                    prevEnv.right = lamda
                    tupleNode.left = myLambda
                else:
                    tupleNode.left = self.copy_ast_node(execution_stack[-1])
                    execution_stack.pop()
                sibling = tupleNode.left
                for i in range(1, numOfItems):
                    temp = execution_stack[-1]
                    if temp.get_label() == "lambda":
                        lamda = ASTNode(execution_stack[-1].get_label(), execution_stack[-1].get_node_type())
                        execution_stack.pop()
                        prevEnv = ASTNode(execution_stack[-1].get_label(), execution_stack[-1].get_node_type())
                        execution_stack.pop()
                        boundVar = ASTNode(execution_stack[-1].get_label(), execution_stack[-1].get_node_type())
                        execution_stack.pop()
                        nextDeltaIndex = ASTNode(
                            execution_stack[-1].get_label(), execution_stack[-1].get_node_type()
                        )
                        execution_stack.pop()
                        myLambda = ASTNode("lamdaTuple", "lamdaTuple")
                        myLambda.left = nextDeltaIndex
                        nextDeltaIndex.right = boundVar
                        boundVar.right = prevEnv
                        prevEnv.right = lamda
                        sibling.right = myLambda
                        sibling = sibling.right
                    else:
                        execution_stack.pop()
                        sibling.right = temp
                        sibling = sibling.right
                execution_stack.append(tupleNode)
            elif nextToken.get_label() == "aug":
                token1 = self.copy_ast_node(execution_stack[-1])
                execution_stack.pop()
                token2 = self.copy_ast_node(execution_stack[-1])
                execution_stack.pop()
                if token1.get_label() == "nil" and token2.get_label() == "nil":
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token1
                    execution_stack.append(tupleNode)
                elif token1.get_label() == "nil":
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token2
                    execution_stack.append(tupleNode)
                elif token2.get_label() == "nil":
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token1
                    execution_stack.append(tupleNode)
                elif token1.get_node_type() != "tau":
                    tupleNode = token2.left
                    while tupleNode.right != None:
                        tupleNode = tupleNode.right
                    tupleNode.right = self.copy_ast_node(token1)
                    execution_stack.append(token2)
                elif token2.get_node_type() != "tau":
                    tupleNode = token1.left
                    while tupleNode.right != None:
                        tupleNode = tupleNode.right
                    tupleNode.right = self.copy_ast_node(token2)
                    execution_stack.append(token1)
                else:
                    tupleNode = ASTNode("tau", "tau")
                    tupleNode.left = token1
                    tupleNode.left.right = token2
                    execution_stack.append(tupleNode)

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
        temp = temp.replace("\\n", '\n').replace("\\node", '\node')
        temp = temp.replace("'", "")
        return temp
