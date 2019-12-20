###################################################################
#Akshay Chekuri (andrewid: achekuri)
#cleanTermProject.py
#README
#This file is the back end. It handles calculations for all the
#components of the circuit. This can be thought of as the "model".
#In the future, TODO add more components (capacitors)
###################################################################

import numpy as np
import math
import cmath
import copy
import decimal

#################################################
# Helper functions
#################################################

#isHex adapted from
#stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float
def isHex(n):
    try:
        int(n,16)
        return True
    except ValueError:
        return False

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)


def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

class Microcontroller(object):
    def __init__(self,name,pins,portSeries,registers,voltage):
        self.name = name
        self.pins = pins
        self.nodeList = []
        self.portSeries = portSeries
        self.TLNode = None
        self.bits = 8
        self.registerList = [[0]*self.bits for i in range(registers)]
        self.voltage=voltage
        self.codePath = ''
        self.commands = ['in','out','ldi','mov','and','or','andi','ori']
        
    def initNodes(self,TLNode):
        self.TLNode = TLNode
        self.nodeList = []
        for i in range(len(self.pins)):
            if(i < len(self.pins)//2):
                self.nodeList.append(Node(TLNode.x,TLNode.y+i))
            else:
                self.nodeList.append(Node(TLNode.x+2,TLNode.y+len(self.pins)-i-1))

    def getRegisterStrings(self):
        sList = []
        for i in range(len(self.registerList)):
            sList.append('r'+str(i))
        return sList
    def getInPortStrings(self):
        sList = []
        for port in self.portSeries[True]:
            sList.append('PORT'+port)
        return sList

    def getOutPortStrings(self):
        sList = []
        for port in self.portSeries[False]:
            sList.append('PORT'+port)
        return sList

    def getInNodes(self):
        if(self.TLNode == None):
            return set()
        nodeSet = set()
        for portType in self.portSeries[True]:
            nodeSet = nodeSet|self.getFromPortType(portType)
        return nodeSet
    
    def getOutNodes(self):
        if(self.TLNode == None):
            return set()
        nodeSet = set()
        for portType in self.portSeries[False]:
            nodeSet = nodeSet|self.getFromPortType(portType)
        return nodeSet

    def getFromPortType(self,portType):
        nodeSet = set()
        for i in range(len(self.pins)):
            if(self.pins[i] != None and self.pins[i][0] == portType):
                nodeSet.add(self.nodeList[i])
        return nodeSet
        

    def getRNodes(self):
        if(self.TLNode == None):
            return set()
        nodeSet = set()
        for i in range(len(self.pins)):
            if(self.pins[i] == None or self.pins[i][0] == 'V' or self.pins[i][0] == 'G'):
                nodeSet.add(self.nodeList[i])
        for i in range(len(self.pins)//2):
            nodeSet.add(Node(self.TLNode.x+1, self.TLNode.y+i))
        return nodeSet

    def runCode(self,circuit):
        if(self.codePath == ''):
            return
        file=open(self.codePath, 'r')
        lines = file.readlines()
        for line in lines:
            output = self.runLine(line.split(' '),circuit)
            if(output != None):
                return 0

    def runLine(self,line,circuit):
        if(line[0] not in self.commands):
            return 0
        else:
            if(line[0] == 'in'):
                output = self.doIn(line,circuit)
            elif(line[0] == 'out'):
                output = self.doOut(line,circuit)
            elif(line[0] == 'ldi'):
                output = self.doLDI(line)
            elif(line[0] == 'mov'):
                output = self.doMOV(line)
            elif(line[0] == 'and'):
                output = self.doAND(line)
            elif(line[0] == 'or'):
                output = self.doOR(line)
            if(output != None):
                return 0

    def doAND(self,line):
        if(len(line) != 3):
            return 0
        elif(line[1].rstrip() not in self.getRegisterStrings()):
            return 0
        elif(line[2].rstrip() not in self.getRegisterStrings()):
            return 0

        r1 = line[1].rstrip()
        r2 = line[2].rstrip()
        regNum1 = int(r1[1:])
        regNum2 = int(r2[1:])

        for i in range(8):
            self.registerList[regNum1][i] = (self.registerList[regNum1][i] and
                                             self.registerList[regNum2][i])

    def doOR(self,line):
        if(len(line) != 3):
            return 0
        elif(line[1].rstrip() not in self.getRegisterStrings()):
            return 0
        elif(line[2].rstrip() not in self.getRegisterStrings()):
            return 0

        r1 = line[1].rstrip()
        r2 = line[2].rstrip()
        regNum1 = int(r1[1:])
        regNum2 = int(r2[1:])

        for i in range(8):
            self.registerList[regNum1][i] = (self.registerList[regNum1][i] or
                                             self.registerList[regNum2][i])
    def doMOV(self,line):
        if(len(line) != 3):
            return 0
        elif(line[1].rstrip() not in self.getRegisterStrings()):
            return 0
        elif(line[2].rstrip() not in self.getRegisterStrings()):
            return 0

        r1 = line[1].rstrip()
        r2 = line[2].rstrip()
        regNum1 = int(r1[1:])
        regNum2 = int(r2[1:])

        self.registerList[regNum1] = self.registerList[regNum2]
        
        
    def doIn(self,line,circuit):
        if(len(line) != 3):
            return 0
        
        elif(line[2].rstrip() not in self.getInPortStrings()):
            return 0
        elif(line[1] not in self.getRegisterStrings()):
            return 0
        inBit = self.getInput(circuit,line[2][4])
        if(inBit == 0):
            return 0
        regNum = int(line[1][1:])
        self.registerList[regNum] = inBit

    def doOut(self,line,circuit):
        if(len(line) != 3):
            return 0
        elif(line[1] not in self.getOutPortStrings()):
            return 0
        elif(line[2].rstrip() not in self.getRegisterStrings()):
            return 0
        port = line[1][4]
        regNum = int(line[2][1:])
        outBit = self.registerList[regNum]
        for i in range(len(self.pins)):
            if(self.pins[i] != None and self.pins[i][0] == port):
                pinLabel = self.pins[i]
                pinNumber = int(pinLabel[1])
                node = self.nodeList[i]
                circuit.updateNode(node,outBit[pinNumber]*self.voltage)
                
    def hexToBit(self,hexNum):
        if(not isHex(hexNum)):
            return 0
        num = int(hexNum,16)
        if(num < 0 or num > 255):
            return 0
        bits = [0]*8
        for i in range(7,-1,-1):
            if(2**i <= num):
                num -= 2**i
                bits[i] = 1
        return bits
        
    def doLDI(self,line):
        if(len(line) != 3):
            return 0
        elif(line[1] not in self.getRegisterStrings()):
            return 0
        output = self.hexToBit(line[2].rstrip())
        if(output == 0):
            return 0
        regNum = int(line[1][1:])
        self.registerList[regNum] = output
    
    def getBitNum(self,node):
        ind = self.nodeList.index(node)
        return int(self.pins[ind][1])

    def getInput(self,circuit,port):
        if(port not in self.portSeries[True]):
            return 0
        nodeSet = self.getFromPortType(port)
        byte = [0]*self.bits
        for node in nodeSet:
            bitNum = self.getBitNum(node)
            if(node in circuit.nodes):
                if(circuit.getCalcVolt(node) >= self.voltage):
                    byte[bitNum] = 1
                else:
                    byte[bitNum] = 0
            else:
                byte[bitNum] = 0
        return byte   
        
    def __hash__(self):
        return hash((self.name,tuple(self.pins),self.TLNode))
    def __repr__(self):
        return self.name
    def __eq__(self,other):
        return isinstance(other,Microcontroller) and hash(self) == hash(other)
            

class Node(object): 
    def __init__(self,x,y,voltage=0):
        self.voltage = voltage
        self.x = x
        self.y = y
        self.grounded = False
        self.fixedVoltage = None
        self.frequency = None
    def __repr__(self):
        s = f'Node {self.x},{self.y}'
        if(self.grounded):
            s += ' grounded'
        if(self.fixedVoltage != None):
            s += f' {self.fixedVoltage} V'
        return s
    def __hash__(self):
        return hash((self.x,self.y))
    def __eq__(self,other):
        return isinstance(other,Node) and hash(self) == hash(other)

class Component(object):
    def __init__(self,node1,node2):
        self.nodeSet = {node1,node2}
    def orgNodeSetList(self):
        node1,node2 = tuple(self.nodeSet)
        if(hash(node1) <= hash(node2)):
            return [node1,node2]
        else:
            return [node2,node1]

class Resistor(Component):
    def __init__(self,node1,node2,resistance=5):
        super().__init__(node1,node2)
        self.resistance = resistance
    def __hash__(self):
        return hash((tuple(self.orgNodeSetList()),self.resistance))
    def __eq__(self,other):
        return isinstance(other,Resistor) and self.orgNodeSetList() == other.orgNodeSetList()
    def __repr__(self):
        return f'Resistor @ {self.nodeSet}'


class Wire(Component):
    def __init__(self,node1,node2):
        super().__init__(node1,node2)
        self.resistance = 10**-12
    def __hash__(self):
        return hash(tuple(self.orgNodeSetList()))
    def __eq__(self,other):
        return isinstance(other,Wire) and self.orgNodeSetList() == other.orgNodeSetList()
    def __repr__(self):
        return f'Wire @ {self.nodeSet}'
    

class ConnectedComp(object):
    def __init__(self,nodeSet,compSet):
        self.nodeSet = nodeSet
        self.compSet = compSet
    def __hash__(self):
        return hash(tuple(self.orgCompSetList()))
    def __eq__(self,other):
        return isinstance(other,ConnectedComp) and hash(self) == hash(other)    
    def __repr__(self):
        return f'Component Blob @ Nodes {self.nodeSet}'
    def orgCompSetList(self):
        hashList = []
        for comp in self.compSet:
            hashList.append(hash(comp))
        hashList.sort()
        return hashList
    def addComp(self,comp):
        self.nodeSet = self.nodeSet|comp.nodeSet
        self.compSet.add(comp)
    def removeComp(self,comp):
        self.compSet.remove(comp)
        self.nodeSet = Circuit.getNodesFromCompSet(self.compSet)

class Circuit(object):
    def __init__(self):
        self.nodes = dict()
        self.comps = set()
        self.connectedList = []
        self.eqList = []
        self.RHSList = []
        self.nodeDict = dict()
        self.timer = 0
        self.timeStep = 10**-3
        self.scopeNode = None
        self.last50 = [0]*50
        self.ICs = set()
        self.restricted = set()
        self.pinIn = set()
        self.pinOut = set()

    @staticmethod
    def getNodesFromCompSet(self,compSet):
        nodeSet = {}
        for comp in compSet:
            nodeSet = nodeSet|comp.nodeSet
        return nodeSet

    def generateSuperComps(self):
        combined = True
        self.connectedList = []
        for comp in self.comps:
            self.connectedList.append(ConnectedComp(comp.nodeSet,{comp}))

        while(combined):
            combined = False
            for i in range(len(self.connectedList)):
                for j in range(i+1,len(self.connectedList)):
                    comp1 = self.connectedList[i]
                    comp2 = self.connectedList[j]
                    if(comp1.nodeSet.intersection(comp2.nodeSet) != set()):
                        newComp = ConnectedComp(comp1.nodeSet|comp2.nodeSet,
                                                comp1.compSet|comp2.compSet)
                        self.connectedList.remove(comp1)
                        self.connectedList.remove(comp2)
                        self.connectedList.append(newComp)
                        combined = True
                    if(combined): break
                if(combined): break

    def getMaxVoltage(self):
        maxVoltage = 0
        for node in self.nodes:
            if node.fixedVoltage != None and node.fixedVoltage > maxVoltage:
                maxVoltage = node.fixedVoltage
        for ic in self.ICs:
            if ic.voltage > maxVoltage:
                maxVoltage = ic.voltage
        return maxVoltage

    def uploadICCode(self,IC,code):
        for ic in self.ICs:
            if(ic == IC):
                ic.codePath = code
                
    def addIC(self,micro):
        fullRestriction = set(micro.nodeList)|micro.getRNodes()
        for node in fullRestriction:
            if(node in self.nodes):
                return 0
        for node in fullRestriction:
            for ic in self.ICs:
                if(node in ic.nodeList or node in ic.getRNodes()):
                    return 0
        self.ICs.add(micro)
        self.restricted = self.restricted|micro.getRNodes()
        self.pinIn = self.pinIn|micro.getInNodes()
        self.pinOut = self.pinOut|micro.getInNodes()

    def pinFilled(self,node):
        for micro in self.ICs:
            if(node in self.nodes and
               (node in micro.nodeList or node in micro.getRNodes())):
                return True
        return False
        
    
    def addComp(self,comp):
        node1, node2 = tuple(comp.nodeSet)
        if(self.isVoltSource(node1) or self.isVoltSource(node2) or
           self.isGrounded(node1) or self.isGrounded(node2)):
            return 0
        elif(node1 in self.restricted or node2 in self.restricted):
            return 1
        elif(self.pinFilled(node1) or self.pinFilled(node2)):
            return 2
        
        self.comps.add(comp)
        if(node1 in self.nodes):
            self.nodes[node1].add(comp)
        else:
            self.nodes[node1] = {comp}
        if(node2 in self.nodes):
            self.nodes[node2].add(comp)
        else:
            self.nodes[node2] = {comp}
        self.generateSuperComps()
            

    def removeComp(self,comp):
        self.comps.remove(comp)
        node1, node2 = tuple(comp.nodeSet)
        self.nodes[node1].remove(comp)
        self.nodes[node2].remove(comp)
        if(self.nodes[node1] == set()):
            del self.nodes[node1]
        if(self.nodes[node2] == set()):
            del self.nodes[node2]
        self.generateSuperComps()

    def addGround(self,sampleNode):
        if(sampleNode not in self.nodes):
            return 0
        elif(len(self.nodes[sampleNode]) != 1):
            return 1
        elif(self.isVoltSource(sampleNode)):
            return 2
        for node in self.nodes:
            if(sampleNode == node):
                node.grounded = True
                for comp in self.nodes[node]:
                    self.comps.remove(comp)
                    node1,node2 = tuple(comp.nodeSet)
                    if(node1 == node):
                        comp.nodeSet = {node,node2}
                    else:
                        comp.nodeSet = {node,node1}
                    self.comps.add(comp)

    def removeGround(self,sampleNode):
        for node in self.nodes:
            if(sampleNode == node):
                node.grounded = False
                for comp in self.nodes[node]:
                    self.comps.remove(comp)
                    node1,node2 = tuple(comp.nodeSet)
                    if(node1 == node):
                        comp.nodeSet = {node,node2}
                    else:
                        comp.nodeSet = {node,node1}
                    self.comps.add(comp)
                    
    def connectsToOut(self,node):
        pinOutSet = set()
        for comp in self.connectedList:
            pinOutSet = pinOutSet|self.getPinOutNodes(comp)
        visitedSet = set()
        crawlNode = None
        pinComp = list(self.nodes[node])[0]
        if(isinstance(pinComp,Resistor)):
            return False
        
    def hasVoltToPinout(self,comp):
        pinOutNodes = self.getPinOutNodes(comp)
        for node in pinOutNodes:
            if(self.isVoltSource(node)):
                return True
            visitedSet = set()
            crawlNode = None
            pinComp = list(self.nodes[node])[0]
            if(isinstance(pinComp,Resistor)):
                continue
            visitedSet.add(pinComp)
            node1,node2 = tuple(pinComp.nodeSet)
            if(node1 == node):
                crawlNode = node2
            else:
                crawlNode = node1
            if(self.crawlToVolt(crawlNode,copy.deepcopy(visitedSet))):
                return True
        return False

    def hasInToOut(self,comp):
        inPin = False
        outPin = False
        for node in comp.nodeSet:
            if self.isInNode(node):
                inPin = True
            elif self.isOutNode(node):
                outPin = True
        return inPin and outPin
            

    def getPinOutNodes(self,comp):
        nodeSet = set()
        for node in comp.nodeSet:
            if(self.isOutNode(node)):
                nodeSet.add(node)
        return nodeSet

    def isOutNode(self,node):
        for micro in self.ICs:
            if node in micro.getOutNodes():
                return True
        return False

    def getPinInNodes(self,comp):
        nodeSet = set()
        for node in comp.nodeSet:
            if(self.isInNode(node)):
                nodeSet.add(node)
        return nodeSet
    
    def isInNode(self,node):
        for micro in self.ICs:
            if node in micro.getInNodes():
                return True
        return False
        
    def addVoltage(self,sampleNode,voltage=5,frequency=None):
        if(sampleNode not in self.nodes):
            return 0
        elif(len(self.nodes[sampleNode]) != 1):
            return 1
        elif(self.isGrounded(sampleNode)):
            return 2
        for node in self.nodes:
            if(sampleNode == node):
                node.fixedVoltage = voltage
                node.frequency = frequency
                for comp in self.nodes[node]:
                    self.comps.remove(comp)
                    node1,node2 = tuple(comp.nodeSet)
                    if(node1 == node):
                        comp.nodeSet = {node,node2}
                    else:
                        comp.nodeSet = {node,node1}
                    self.comps.add(comp)

    def isGrounded(self,node):
        for node2 in self.nodes:
            if(node2 == node and node2.grounded):
                return True
    def isVoltSource(self,node):
        for node2 in self.nodes:
            if(node2 == node and node2.fixedVoltage != None):
                return True
        return False

    def getVolt(self,node):
        for node2 in self.nodes:
            if(node2 == node and node2.fixedVoltage != None):
                fixVolt = node2.fixedVoltage
        frequency = self.getFrequency(node)
        
        if(frequency == None):
            return fixVolt

        else:
            return fixVolt*math.cos(2*math.pi*frequency*self.timer*self.timeStep)
            
    def getCalcVolt(self,node):
        for node2 in self.nodes:
            if(node2 == node):
                return node2.voltage

    def solveCircuit(self):
        for comp in self.connectedList:
            if(self.hasVoltToPinout(comp)):
                return 3
            if(self.hasInToOut(comp)):
                return 4
        newConnectList = []
        for comp in self.connectedList:
            if(self.getPinOutNodes(comp) != set()):
                newConnectList.append(comp)
            else:
                newConnectList.insert(0,comp)
        failedEq = False
        codeRan = False
        for comp in newConnectList:
            self.makeNodeDict(comp.nodeSet)
            self.makeZero(comp)
            if(self.getPinOutNodes(comp) != set() and not codeRan):
                output = self.runAllCode()
                if(output != None):
                    return 5
                codeRan = True
            for node in self.getVoltAndOut(comp):
                self.eqList = []
                self.RHSList = []
                output = self.solveSuperComp(comp,node)
                if(output == 0 or output == 2 or
                   output == 3 or output == 4):
                    return output
                elif(output == 1):
                    continue
                a = np.array(self.eqList)
                b = np.array(self.RHSList)
                try:
                    mat = np.linalg.solve(a, b)
                    for node in self.nodes:
                        if node in comp.nodeSet:
                            voltage = mat[self.nodeDict[node]]
                            if(not self.isOutNode(node)):
                                node.voltage += voltage
                except:
                    failedEq = True
                    break
            if(failedEq):
                continue

        if(failedEq):
            return 1

    def runAllCode(self):
        for ic in self.ICs:
            output = ic.runCode(self)
            if(output != None):
                return output
        

    def getGroundNodes(self,comp):
        groundedSet = set()
        for node in comp.nodeSet:
            if self.isGrounded(node):
                groundedSet.add(node)
        return groundedSet

    def isACVolt(self,node):
        if self.getFrequency(node) != None:
            return True
        return False

    def getFrequency(self,node):
        for node2 in self.nodes:
            if node2 == node:
                return node2.frequency

    def getVoltNodes(self,comp):
        voltSet = set()
        for node in comp.nodeSet:
            if self.isVoltSource(node):
                voltSet.add(node)
        return voltSet

    def getVoltAndOut(self,comp):
        voltSet = set()
        for node in comp.nodeSet:
            if self.isVoltSource(node) or self.isOutNode(node):
                voltSet.add(node)
        return voltSet

    def hasVoltToVolt(self,comp):
        voltNodes = self.getVoltNodes(comp)
        for node in voltNodes:
            visitedSet = set()
            crawlNode = None
            voltComp = list(self.nodes[node])[0]
            if(isinstance(voltComp,Resistor)):
                continue
            visitedSet.add(voltComp)
            node1,node2 = tuple(voltComp.nodeSet)
            if(node1 == node):
                crawlNode = node2
            else:
                crawlNode = node1

            if(self.crawlToVolt(crawlNode,copy.deepcopy(visitedSet))):
                return True
        return False

    def hasGroundToVolt(self,comp):
        groundNodes = self.getGroundNodes(comp)
        for node in groundNodes:
            visitedSet = set()
            crawlNode = None
            groundComp = list(self.nodes[node])[0]
            if(isinstance(groundComp,Resistor)):
                continue
            visitedSet.add(groundComp)
            node1,node2 = tuple(groundComp.nodeSet)
            if(node1 == node):
                crawlNode = node2
            else:
                crawlNode = node1

            if(self.crawlToVolt(crawlNode,copy.deepcopy(visitedSet))):
                return True
        return False

    def crawlToVolt(self,node,visitedSet):
        if(self.isVoltSource(node)):
            return True
        validPaths = self.nodes[node].difference(visitedSet)
        for comp in validPaths:
            if(isinstance(comp,Resistor)):
                continue
            visitedSet.add(comp)
            crawlNode = None
            node1,node2 = tuple(comp.nodeSet)
            if(node1 == node):
                crawlNode = node2
            else:
                crawlNode = node1
            if(self.crawlToVolt(crawlNode,copy.deepcopy(visitedSet))):
                return True
        return False
        
    def makeNodeDict(self,nodeSet):
        nodeDict = dict()
        i = 0
        for node in nodeSet:
            nodeDict[node] = i
            i += 1
        self.nodeDict = nodeDict

    def hasNoVolts(self,comp):
        for node in comp.nodeSet:
            if(self.isVoltSource(node) or self.isOutNode(node)):
                return False
        return True

    def makeZero(self,comp):
        for node in comp.nodeSet:
            if(not self.isOutNode(node)):
                self.updateNode(node,0)

    def updateNode(self,sampleNode,volt):
        for node in self.nodes:
            if(node == sampleNode):
                node.voltage = volt
                for comp in self.nodes[node]:
                    self.comps.remove(comp)
                    node1,node2 = tuple(comp.nodeSet)
                    if(node1 == node):
                        comp.nodeSet = {node,node2}
                    else:
                        comp.nodeSet = {node,node1}
                    self.comps.add(comp)
                    
    def solveSuperComp(self,comp,setNode):
        if(self.hasGroundToVolt(comp)):
            return 0
        elif(self.hasVoltToVolt(comp)):
            return 2
        elif(self.hasVoltToPinout(comp)):
            return 3
        elif(self.hasInToOut(comp)):
            return 4
        elif(self.hasNoVolts(comp)):
            self.makeZero(comp)
            return 1
        for node in comp.nodeSet:
            exp = [0]*len(self.nodeDict)
            if(self.isVoltSource(node) and node == setNode):
                exp[self.nodeDict[node]] = 1
                self.eqList.append(exp)
                self.RHSList.append(self.getVolt(node))
            elif(self.isOutNode(node) and node == setNode):
                exp[self.nodeDict[node]] = 1
                self.eqList.append(exp)
                self.RHSList.append(self.getCalcVolt(node))
            elif(self.isGrounded(node) or (self.isVoltSource(node) and node != setNode) or
                 (self.isOutNode(node) and node != setNode)):
                exp[self.nodeDict[node]] = 1
                self.eqList.append(exp)
                self.RHSList.append(0)
            elif(len(self.nodes[node]) == 1):
                loneComp = list(self.nodes[node])[0]
                node1,node2 = tuple(loneComp.nodeSet)
                exp[self.nodeDict[node1]] = 1
                exp[self.nodeDict[node2]] = -1
                self.eqList.append(exp)
                self.RHSList.append(0)
            else:
                compList = list(self.nodes[node])
                startComp = compList[-1]
                compList.pop()
                node1,node2 = tuple(startComp.nodeSet)
                frequency = self.getFrequency(setNode)
                if(node1 == node):
                    exp = self.getCompExp(startComp,node2,frequency)
                else:
                    exp = self.getCompExp(startComp,node1,frequency)
                for subComp in compList:
                    exp2 = self.getCompExp(subComp,node,frequency)
                    for i in range(len(self.nodeDict)):
                        exp[i] = exp[i] - exp2[i]
                self.eqList.append(exp)
                self.RHSList.append(0)
                
    def getCompExp(self,comp,startNode, frequency = None):
        exp = [0]*len(self.nodeDict)
        node1,node2 = tuple(comp.nodeSet)

        endNode = None
        if(startNode == node1):
            endNode = node2
            exp[self.nodeDict[node1]] = 1/comp.resistance
            exp[self.nodeDict[node2]] = -1/comp.resistance
        else:
            endNode = node1
            exp[self.nodeDict[node2]] = 1/comp.resistance
            exp[self.nodeDict[node1]] = -1/comp.resistance

            exp[self.nodeDict[startNode]] = 1/comp.resistance
            exp[self.nodeDict[endNode]] = -1/comp.resistance
        return exp

        
    

            
    
    




    
