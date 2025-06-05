
import copy
from cse_machine import cse_machine
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
        # i = 0
        # j = 0
        # index = 1
        # betaCount = 1

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
    
    def cse_machine(self,controlStructure):
        return cse_machine(self,controlStructure)
       
       
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
