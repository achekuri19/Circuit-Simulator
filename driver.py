###################################################################
#Akshay Chekuri (andrewid: achekuri)
#driver.py
#README
#This file is the front end. It handles events and creates hitboxes
#for all the components of the circuit. This also calculates the
#colors of the voltages, etc. It basically handles user input
###################################################################


import math, copy
import numpy as np
from cmu_112_graphics import *
from cleanTermProject import *
from tkinter import *
import tkinter as tk
import string
import random
import decimal

#from http://www.cs.cmu.edu/~112/notes/notes-graphics-part2.html
def rgbString(red, green, blue):
    # Don't worry about how this code works yet.
    return "#%02x%02x%02x" % (red, green, blue)

#from http://www.cs.cmu.edu/~112/index.html
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))


#verifyInput from https://www.python-course.eu/tkinter_entry_widgets.php
def verifyInput(app,master,entries):
    fetch(app,entries)
    for num in app.entry:
        if(not isNumber(num) or int(num) <= 0):
            app.entry = None
            return
    master.destroy()


#copied from
#stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    

#fetch and makeform from https://www.python-course.eu/tkinter_entry_widgets.php
def fetch(app,entries):
    L=[]
    for entry in entries:
        field = entry[0]
        text  = entry[1].get()
        L.append(text)
    app.entry = L

def makeform(root, fields):
    entries = []
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=15, text=field, anchor='w')
        ent = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries.append((field, ent))
    return entries

#Graphics app from http://www.cs.cmu.edu/~112/notes/hw9.html
#CMU 112 Graphics (not made by me)
def appStarted(app):
    app.circuit  = Circuit()
    app.compToAdd = 0
    app.pressedNode = None
    app.releasedNode = None
    app.gridW = 20
    app.mouseX = app.width/2
    app.mouseY = app.height/2
    app.lineWidth = 3
    app.errorList = []
    app.errorTimer = []
    app.green = 150
    app.grey = rgbString(app.green,app.green,app.green)
    app.hoverColor = rgbString(0,255,255)
    app.hitBoxes = dict()
    app.fixNode = None
    app.moveNode = None
    app.moveComp = None
    app.entry = None
    app.ICAdd = None
    app.ICPinCounter = 0

    compAddError0 = 'Error: cannot connect two components to ground/voltage source'
    compAddError1 = 'Error: this pin is restricted'
    compAddError2 = 'Error: can only add one component to a pin'
    
    app.compAddErrorList = [compAddError0, compAddError1, compAddError2]
    
    groundError0 = 'Error: You must connect ground to a component'
    groundError1 = 'Error: Ground can be connected to only 1 component'
    groundError2 = 'Error: Cannot connect ground directly to a voltage source'
    app.groundErrorList = [groundError0,groundError1,groundError2]

    voltError0 = 'Error: You must connect a voltage source to a component'
    voltError1 = 'Error: Voltage sources can be connected to only 1 component'
    voltError2 = 'Error: Cannot connect a voltage source directly to ground'
    app.voltErrorList = [voltError0,voltError1,voltError2]

    solveError0 = 'Error: Cannot connect a voltage source to ground without resistance'
    solveError1 = 'Error: Unknown solving error'
    solveError2 = 'Error: Cannot connect a voltage source to voltage source without resistance'
    solveError3 = 'Error: Cannot connect an output pin to a voltage source without resistance'
    solveError4 = 'Error: Cannot connect input to output pin (To be added)'
    solveError5 = 'Error: Cannot read the assembly code that was given'
    app.solveErrorList = [solveError0,solveError1,solveError2,solveError3,solveError4]

def getColor(app,node,hover = False):
    if(hover):
        return app.hoverColor
    maxVoltage = app.circuit.getMaxVoltage()
    if(maxVoltage == 0):
        return app.grey
    volt = app.circuit.getCalcVolt(node)
    if(volt != None and volt >= 0):
        try:
            return rgbString(app.green-int(app.green*volt/maxVoltage),
                             app.green,
                             app.green-int(app.green*volt/maxVoltage))
        except:
            return app.grey
    else:
        try:
            return rgbString(app.green,
                             app.green+int(app.green*volt/maxVoltage),
                             app.green+int(app.green*volt/maxVoltage))
        except:
            return app.grey

def altKeyPressed(app,event):
    pass
def altKeyPressed2(app,event):
    pass
                             
def keyPressed(app, event):
    if(type(app.compToAdd)==bool):
        altKeyPressed(app,event)
        return
    if(app.ICAdd != None):
        altKeyPressed2(app,event)
        return
    if(event.key == 'v'):
        app.compToAdd = 0
    elif(event.key == 'w'):
        app.compToAdd = 1
    elif(event.key == 'r'):
        app.compToAdd = 2
    elif(event.key == 'g'):
        app.compToAdd = 3
    elif(event.key == 'b'):
        app.compToAdd = 4
    elif(event.key == 'Space'):
        app.compToAdd = None
    elif(event.key == 's'):
        app.compToAdd = 5
    elif(event.key == '1'):
        makeSampleCircuit(app)

def makeSampleCircuit(app):
    makeAtmega88p(app)
    app.ICAdd.initNodes(Node(15,10))
    app.ICAdd.codePath = 'SampleCode.txt'
    app.circuit.addIC(app.ICAdd)
    app.ICAdd = None
    newResistor(app,Resistor(Node(5,5),Node(10,5),resistance = 10))
    newACVolt(app,Node(5,5),voltage=15,frequency=50)
    newResistor(app,Resistor(Node (10,5),Node(15,19),resistance = 5))
    newResistor(app,Resistor(Node(10,5), Node(10,10),resistance=3))
    newGround(app,Node(10,10))
    newResistor(app,Resistor(Node(10,5),Node(13,5),resistance = 12))
    newACVolt(app,Node(13,5),voltage=15,frequency=30)

    newWire(app,Wire(Node(5,20),Node(15,22)))
    newWire(app,Wire(Node(5,19),Node(15,21)))
    newWire(app,Wire(Node(5,18),Node(15,20)))
    newWire(app,Wire(Node(5,17),Node(15,15)))
    newWire(app,Wire(Node(5,16),Node(15,14)))
    newWire(app,Wire(Node(5,15),Node(15,13)))
    newWire(app,Wire(Node(5,14),Node(15,12)))
    newWire(app,Wire(Node(5,13),Node(15,11)))

    app.circuit.scopeNode = Node(5,20)
    app.circuit.last50 = [0]*50

    
    
    
    

def addVoltHitBox(app,node):
    x = node.x*app.gridW
    y = node.y*app.gridW
    app.hitBoxes[node] = [x-app.gridW/4,y-app.gridW/2,
                          x+app.gridW/4,y+app.gridW/2]

def addACHitBox(app,node):
    x = node.x*app.gridW
    y = node.y*app.gridW
    app.hitBoxes[node] = [x-3*app.gridW/4,y-2*app.gridW,
                          x+3*app.gridW/4,y+app.gridW/2]

def addNodeHitBox(app,node):
    x = node.x*app.gridW
    y = node.y*app.gridW
    app.hitBoxes[node] = [x-app.gridW/4,y-app.gridW/4,
                          x+app.gridW/4,y+app.gridW/4]

def addGroundHitBox(app,node):
    x = node.x*app.gridW
    y = node.y*app.gridW
    app.hitBoxes[node] = [x-app.gridW/3,y-app.gridW/4,
                          x+app.gridW/3,y+3*app.gridW/4]
    

def newDCVolt(app,node,voltage=5,frequency=None):
    output = app.circuit.addVoltage(node,voltage,frequency)
    if(output != None):
        app.errorList.append(app.voltErrorList[output])
        app.errorTimer.append(50)
    else:
        output = app.circuit.solveCircuit()
        addVoltHitBox(app,node)
        if(output != None):
            app.errorList.append(app.solveErrorList[output])
            app.errorTimer.append(50)
    app.pressedNode = None

def newGround(app,node):
    output = app.circuit.addGround(node)
    if(output != None):
        app.errorList.append(app.groundErrorList[output])
        app.errorTimer.append(50)
    else:
        output = app.circuit.solveCircuit()
        addGroundHitBox(app,node)
        if(output != None):
            app.errorList.append(app.solveErrorList[output])
            app.errorTimer.append(50)   
    app.pressedNode = None

def newACVolt(app,node,voltage=5,frequency=40):
    output = app.circuit.addVoltage(node,voltage,frequency)
    if(output != None):
        app.errorList.append(app.voltErrorList[output])
        app.errorTimer.append(50)
    else:
        output = app.circuit.solveCircuit()
        addACHitBox(app,node)
        if(output != None):
            app.errorList.append(app.solveErrorList[output])
            app.errorTimer.append(50)        
    app.pressedNode = None

def getPinToSet(IC,count):
    seriesList = IC.portSeries[True] + IC.portSeries[False]
    if(count <= IC.bits*len(seriesList)):
        return seriesList[(count-1)//IC.bits] + str((count-1)%IC.bits)
    elif(count == IC.bits*len(seriesList) + 2):
        return 'V'
    elif(count == IC.bits*len(seriesList) + 1):
        return 'G'
        

def altMousePressed(app,event):
    if(app.ICAdd != None):
        pinToSet = getPinToSet(app.ICAdd,app.ICPinCounter)
        tempIC = getTempIC(app)
        pressedNode = getNodeFromCoord(app,event.x,event.y)
        if pressedNode in tempIC.nodeList:
            ind = tempIC.nodeList.index(pressedNode)
            if(app.ICAdd.pins[ind] == None):
                app.ICAdd.pins[ind] = pinToSet
                app.ICPinCounter -= 1
        if(app.ICPinCounter == 0):
            app.compToAdd = None
            app.entry = None

def altMousePressed2(app,event):
    pressedNode = getNodeFromCoord(app,event.x,event.y)
    tempIC = getTempIC(app)
    tempIC.initNodes(pressedNode)
    BRNode = tempIC.nodeList[len(tempIC.nodeList)//2]
    if(BRNode.x*app.gridW > app.width-11*app.gridW or
       BRNode.y*app.gridW > app.height-app.gridW):
        app.errorList.append('Invalid placement of microcontroller')
        app.errorTimer.append(50)
        return
    output = app.circuit.addIC(tempIC)
    if(output == None):
        app.ICAdd = None
    else:
        app.errorList.append('Invalid placement of microcontroller')
        app.errorTimer.append(50)
        
def makeAtmega88p(app):
    app.compToAdd = None
    ic = Microcontroller('Atmega88p',[None,'D0','D1','D2','D3','D4','V',
                                      'GND','B6','B7','D5','D6','D7','B0',
                                      None,None,None,None,None,None,None,
                                      None,None,'B5','B4','B3','B2','B1'],
                         {True: ['B'], False: ['D']}, 32,3)
    app.ICAdd = ic

def makeAtmega8515(app):
    app.compToAdd = None
    ic = Microcontroller('Atmega8515',['B0','B1','B2','B3','B4','B5','B6','B7',None,'D0',
                                       'D1','D2','D3','D4','D5','D6','D7',None,None,'GND',
                                       'C0','C1','C2','C3','C4','C5','C6','C7',None,None,
                                       None,'A7','A6','A5','A4','A3','A2','A1','A0','V'],
                         {True: ['A','B'], False: ['C','D']},32,3)
    app.ICAdd = ic


    
def mousePressed(app,event):
    if(type(app.compToAdd)==bool):
        altMousePressed(app,event)
        return
    if(app.ICAdd != None):
        altMousePressed2(app,event)
    app.pressedNode = None
    g5 = 5*app.gridW
    if(event.x < app.width-2*g5):
        app.pressedNode = getNodeFromCoord(app,event.x,event.y)
        
    if(app.width-2*g5 <= event.x <= app.width-g5):
        if(0 <= event.y <= g5):
            app.compToAdd = 2
        elif(g5 <= event.y <= 2*g5):
            app.compToAdd = 0
        elif(2*g5 <= event.y <= 3*g5):
            app.compToAdd = 3
        elif(3*g5 <= event.y <= 4*g5):
            app.compToAdd = None
        elif(4*g5 <= event.y <= 5*g5):
            makeAtmega88p(app)
        return
    elif(app.width-g5 <= event.x <= app.width):
        if(0 <= event.y <= g5):
            app.compToAdd = 1
        elif(g5 <= event.y <= 2*g5):
            app.compToAdd = 4
        elif(2*g5 <= event.y <= 3*g5):
            app.compToAdd = 5
        elif(3*g5 <= event.y <= 4*g5):
            newICCircuit(app)
        elif(4*g5 <= event.y <= 5*g5):
            makeAtmega8515(app)
        return
    elif(app.compToAdd == 0):
        newDCVolt(app,app.pressedNode)
        
    elif(app.compToAdd == 3):
        newGround(app,app.pressedNode)
        
    elif(app.compToAdd == 4):
        newACVolt(app,app.pressedNode)
        
    elif(app.compToAdd == None and app.moveNode == None):
        hoverNode = getHoverNode(app)
        if(hoverNode != None):
            createMoveComp(app,hoverNode)
    elif(app.compToAdd == 5):
        changeScopeNode(app,app.pressedNode)

def changeScopeNode(app,node):
    if(node in app.circuit.nodes):
        if(node == app.circuit.scopeNode):
            app.circuit.scopeNode = None
        else:
            app.circuit.scopeNode = node
            app.circuit.last50 = [0]*50

def getHoverNode(app):
    hoverNode = None
    for node in app.circuit.nodes:
        if(isHitBoxed(app,node)):
            hoverNode = node
            break
    return hoverNode

def fullRMComp(app,comp):
    node1,node2 = tuple(comp.nodeSet)
    if(len(app.circuit.nodes[node1]) == 1):
        del app.hitBoxes[node1]
    if(len(app.circuit.nodes[node2]) == 1):
        del app.hitBoxes[node2]
    app.circuit.removeComp(comp)

def createMoveComp(app,hoverNode):
    app.moveComp = list(app.circuit.nodes[hoverNode])[0]
    node1,node2 = tuple(app.moveComp.nodeSet)
    if(len(app.circuit.nodes[node1]) == 1):
        del app.hitBoxes[node1]
    if(len(app.circuit.nodes[node2]) == 1):
        del app.hitBoxes[node2]
    app.moveNode = hoverNode
    if(node1 == hoverNode):
        app.fixNode = node2
    else:
        app.fixNode = node1
    app.circuit.removeComp(app.moveComp)
        
        
def CircuitContains(app,node1,node2):
    for comp in app.circuit.comps:
        if(comp.nodeSet == {node1,node2}):
            return True
    return False

def handleCompErrors(app,output,output2):
    if(output != None):
        app.errorList.append(app.solveErrorList[output])
        app.errorTimer.append(50)
    if(output2 != None):
        app.errorList.append(app.compAddErrorList[output2])
        app.errorTimer.append(50)
    

def newWire(app,wire):
    output2 = app.circuit.addComp(wire)
    node1,node2 = tuple(wire.nodeSet)
    if(output2 == None):
        addNodeHitBox(app,node1)
        addNodeHitBox(app,node2)
    output = app.circuit.solveCircuit()
    handleCompErrors(app,output,output2)

def newResistor(app,resistor):
    output2 = app.circuit.addComp(resistor)
    node1,node2 = tuple(resistor.nodeSet)
    if(output2 == None):
        addNodeHitBox(app,node1)
        addNodeHitBox(app,node2)
    output = app.circuit.solveCircuit()
    handleCompErrors(app,output,output2)

def createNodeHitBox(app,node):
    if(node.fixedVoltage != None):
        if(node.frequency != None):
            newACVolt(app,node,
                      node.fixedVoltage,
                      node.frequency)
        else:
            newDCVolt(app,node,
                      node.fixedVoltage)
    elif(node.grounded):
        newGround(app,node)

    else:
        addNodeHitBox(app,node)
    
def mouseReleased(app,event):
    if(type(app.compToAdd)==bool):
        return
    if(app.ICAdd != None):
        return
    g5 = 5*app.gridW
    if(app.width-2*g5 <= event.x <= app.width):
        app.pressedNode = None
        app.releasedNode = None
        app.fixNode = None
        app.moveNode = None
        app.moveComp = None
        return
    app.releasedNode = getNodeFromCoord(app,event.x,event.y)
    if(app.pressedNode != app.releasedNode and
       not CircuitContains(app,app.pressedNode,app.releasedNode) and
       app.compToAdd != None and app.compToAdd != False and app.pressedNode != None):
        output = None
        output2 = None
        if(app.compToAdd == 1):
            newWire(app,Wire(app.pressedNode,app.releasedNode))
        elif(app.compToAdd == 2):
            newResistor(app,Resistor(app.pressedNode,app.releasedNode))   
    elif(app.compToAdd == None and app.pressedNode != app.releasedNode): 
        if(app.moveComp != None):
            if(app.releasedNode != app.fixNode):
                newComp = app.moveComp
                newNode1 = app.releasedNode
                newNode2 = Node(app.fixNode.x,app.fixNode.y)
                newComp.nodeSet = {newNode1,newNode2}
                if(isinstance(newComp,Resistor)):
                    newResistor(app,newComp)
                elif(isinstance(newComp,Wire)):
                    newWire(app,newComp)
                createNodeHitBox(app,app.fixNode)
                if(app.moveNode.fixedVoltage != None):
                    if(app.moveNode.frequency != None):
                        newACVolt(app,app.releasedNode,
                                  app.moveNode.fixedVoltage,
                                  app.moveNode.frequency)
                    else:
                        newDCVolt(app,app.releasedNode,
                                  app.moveNode.fixedVoltage)
                elif(app.moveNode.grounded):
                    newGround(app,app.releasedNode)      
            else:
                app.circuit.addComp(app.moveComp)
                for node in app.moveComp.nodeSet:
                    createNodeHitBox(app,node)
    elif(app.compToAdd == None and app.pressedNode == app.releasedNode):
        if(app.moveComp != None):
            app.circuit.addComp(app.moveComp)
            for node in app.moveComp.nodeSet:
                createNodeHitBox(app,node)
        hoverNode = getHoverNode(app)
        if(hoverNode != None):
            if(app.circuit.isACVolt(hoverNode)):
                editACVolt(app,hoverNode)
            elif(app.circuit.isVoltSource(hoverNode)):
                editDCVolt(app,hoverNode)
                pass
            elif(app.circuit.isGrounded(hoverNode)):
                app.circuit.removeGround(hoverNode)
        else:
            hoverComp = getHoverComp(app)
            if(hoverComp != None):
                if(isinstance(hoverComp,Resistor)):
                    editResistor(app,hoverComp)
                elif(isinstance(hoverComp,Wire)):
                    editWire(app,hoverComp)
            else:
                ic = getHoverIC(app)
                hoverNode = getNodeFromCoord(app,event.x,event.y)
                if(ic != None):
                    if(hoverNode in ic.nodeList and ic.pins[ic.nodeList.index(hoverNode)] == 'V'):
                        changeICVoltage(app,ic)
                    else:
                        uploadICCode(app,ic)
    app.pressedNode = None
    app.releasedNode = None
    app.fixNode = None
    app.moveNode = None
    app.moveComp = None

def changeICVoltage(app,IC):
    master = tk.Toplevel()
    ents = makeform(master, ['Cutoff Voltage'])
    b1 = tk.Button(master, text='Okay',
                  command=(lambda e=ents: verifyICVoltage(app,master,IC,e)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)

def verifyICVoltage(app,master,IC,entries):
    while(app.entry == None):
        verifyInput(app,master,entries)
    for ic in app.circuit.ICs:
        if(ic == IC):
            ic.voltage = float(app.entry[0])
    app.entry = None
    
    
    

def uploadICCode(app,ic):
    master = tk.Toplevel()
    #from https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    master.filename = tk.filedialog.askopenfilename(initialdir=ROOT_DIR,title='Select code file',
                                                    filetypes=(('txt files','*.txt'),))
    app.circuit.uploadICCode(ic,master.filename)
    master.destroy()

def getHoverIC(app):
    mouseNode = getNodeFromCoord(app,app.mouseX,app.mouseY)
    for ic in app.circuit.ICs:
        if(mouseNode in ic.getRNodes()):
            return ic
    return None
def makeICFromEntry(app,entry):
    name = entry[0]
    pins = [None]*int(entry[1])
    portSeries = {True: entry[2].split(' '), False: entry[3].split(' ')}
    registers = int(entry[4])
    voltage = float(entry[5])
    return Microcontroller(name,pins,portSeries,registers,voltage)
    

def newICCircuit(app):
    master = tk.Toplevel()
    app.compToAdd = False
    ents = makeform(master, ['Name','# Pins 18<=n<=76','In Ports(Uppercase)',
                             'Out Ports(Uppercase)','# registers (n>=8)','Cutoff voltage'])
    b1 = tk.Button(master, text='Okay',
                  command=(lambda e=ents: verifyIC(app,master,e)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b2 = tk.Button(master, text='Cancel',
                  command=(lambda: cancelIC(app,master)))
    b2.pack(side=tk.LEFT, padx=5, pady=5)

def cancelIC(app,master):
    app.compToAdd = None
    app.entry = None
    app.ICAdd = None
    app.ICPinCounter = 0
    master.destroy()

def verifyIC(app,master,entries):
    while(app.entry == None):
        verifyICInput(app,master,entries)

    app.ICAdd = makeICFromEntry(app,app.entry)
    #app.entry = None
    
def verifyICInput(app,master,entries):
    fetch(app,entries)
    if(not isInt(app.entry[1]) or int(app.entry[1]) < 18 or
       (int(app.entry[1])%2 == 1) or int(app.entry[1]) > 76):
        app.entry = None
        return
    for c in app.entry[2].split(' '):
        if(len(c) != 1):
            app.entry = None
            return
        if(c not in string.ascii_uppercase or c == 'G' or c == 'V'):
            app.entry = None
            return
    for c in app.entry[3].split(' '):
        if(len(c) != 1):
            app.entry = None
            return
        if(c not in string.ascii_uppercase or c == 'G' or c == 'V'):
            app.entry = None
            return
    for c in app.entry[3].split(' '):
        if(c in app.entry[2].split(' ')):
            app.entry = None
            return
    if(not isInt(app.entry[4]) or int(app.entry[4]) < 8):
        app.entry = None
        return
    
    if(not isNumber(app.entry[5]) or int(app.entry[5]) <= 0):
        app.entry = None
        return

    if(len(app.entry[2].split(' ')) + len(app.entry[3].split(' ')) + 2 > int(app.entry[1])):
        app.entry = None
        return
    app.ICPinCounter = len(app.entry[2].split(' '))*8 + len(app.entry[3].split(' '))*8 + 2
    master.destroy()

#editResistor modified from https://www.python-course.eu/tkinter_entry_widgets.php
def editResistor(app,comp):
    master = tk.Toplevel()
    ents = makeform(master, ['Resistance'])
    b1 = tk.Button(master, text='Okay',
                  command=(lambda e=ents: verifyRes(app,master,comp,e)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b2 = tk.Button(master,text='Delete',
                   command=(lambda: destroyRes(app,master,comp)))
    b2.pack(side=tk.LEFT, padx=5, pady=5)

def verifyRes(app,master,comp,entries):
    while(app.entry == None):
        verifyInput(app,master,entries)
    resistance = float(app.entry[0])
    newComp = copy.deepcopy(comp)
    newComp.resistance = resistance
    app.circuit.removeComp(comp)
    app.circuit.addComp(newComp)
    app.entry = None

def destroyRes(app,master,comp):
    fullRMComp(app,comp)
    master.destroy()

def editWire(app,comp):
    master = tk.Toplevel()
    b2 = tk.Button(master,text='Delete',
                   command=(lambda: destroyRes(app,master,comp)))
    b2.pack(side=tk.LEFT, padx=5, pady=5)

#editACVolt modified from https://www.python-course.eu/tkinter_entry_widgets.php
def editACVolt(app,node):
    master = tk.Toplevel()
    ents = makeform(master, ['Voltage PP','Frequency'])
    b1 = tk.Button(master, text='Okay',
                  command=(lambda e=ents: verifyAC(app,master,node,e)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b2 = tk.Button(master,text='Delete',
                   command=(lambda: destroyAC(app,master,node)))
    b2.pack(side=tk.LEFT, padx=5, pady=5)

def verifyAC(app,master,node,entries):
    while(app.entry == None):
        verifyInput(app,master,entries)
    voltage,frequency = float(app.entry[0]),float(app.entry[1])
    app.circuit.addVoltage(node,voltage,frequency)
    app.entry = None

def destroyAC(app,master,node):
    app.circuit.addVoltage(node,voltage=None,frequency=None)
    master.destroy()

#editDCVolt modified from https://www.python-course.eu/tkinter_entry_widgets.php
def editDCVolt(app,node):
    master = tk.Toplevel()
    ents = makeform(master, ['Voltage'])
    b1 = tk.Button(master, text='Okay',
                  command=(lambda e=ents: verifyDC(app,master,node,e)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b2 = tk.Button(master,text='Delete',
                   command=(lambda: destroyAC(app,master,node)))
    b2.pack(side=tk.LEFT, padx=5, pady=5)

def verifyDC(app,master,node,entries):
    while(app.entry == None):
        verifyInput(app,master,entries)
    voltage = float(app.entry[0])
    app.circuit.addVoltage(node,voltage)
    app.entry = None 

def getHoverComp(app):
    for comp in app.circuit.comps:
        node1,node2 = tuple(comp.nodeSet)
        x1,y1 = node1.x*app.gridW,node1.y*app.gridW
        x2,y2 = node2.x*app.gridW,node2.y*app.gridW
        dist = distance(x1,y1,x2,y2)
        if(x1 == x2):
            if(abs(x1-app.mouseX) <= app.gridW/2 and
               distance(x1,y1,app.mouseX,app.mouseY) <= dist and
               distance(x2,y2,app.mouseX,app.mouseY) <= dist):
                return comp
        else:
            a = (-1)*(y2-y1)/(x2-x1)
            b = 1
            c = (y2-y1)*(x1)/(x2-x1)-y1
            if(abs(a*app.mouseX+b*app.mouseY+c)/(a**2+b**2)**0.5 <= app.gridW/2 and
               distance(x1,y1,app.mouseX,app.mouseY) <= dist and
               distance(x2,y2,app.mouseX,app.mouseY) <= dist):
                return comp
    return None
        
        
def getNodeFromCoord(app,x,y):
    nodeX = roundHalfUp(x/app.gridW)
    nodeY = roundHalfUp(y/app.gridW)
    return Node(nodeX,nodeY)

def mouseMoved(app,event):
    app.mouseX = event.x
    app.mouseY = event.y

def mouseDragged(app,event):
    app.mouseX = event.x
    app.mouseY = event.y    

def timerFired(app):
    for i in range(len(app.errorTimer)):
        app.errorTimer[i] -= 1
    if(len(app.errorTimer) > 0 and app.errorTimer[0] <= 0):
        app.errorList.pop(0)
        app.errorTimer.pop(0)
    app.circuit.timer += 1
    app.circuit.solveCircuit()
    if(app.circuit.scopeNode != None):
        volt = app.circuit.getCalcVolt(app.circuit.scopeNode)
        app.circuit.last50.pop(0)
        app.circuit.last50.append(volt)

def sizeChanged(app):
    app.gridW = app.height/40
        

def drawWire(app,canvas,wire,hover=False):
    node1,node2 = tuple(wire.nodeSet)
    canvas.create_line(app.gridW*node1.x,app.gridW*node1.y,
                       app.gridW*node2.x,app.gridW*node2.y,
                       width=app.lineWidth,fill=getColor(app,node1,hover))

def distance(x1,y1,x2,y2):
    return ((x1-x2)**2 + (y2-y1)**2)**0.5

def drawResistor(app,canvas,resistor,hover=False):
    defColor = app.grey
    if(hover):
        defColor = app.hoverColor
    node1,node2 = tuple(resistor.nodeSet)
    x1,y1 = app.gridW*node1.x,app.gridW*node1.y
    x2,y2 = app.gridW*node2.x,app.gridW*node2.y
    dist = distance(x1,y1,x2,y2)
    if(dist >= app.gridW*2):
        dX=(x1-x2)*app.gridW/(dist)
        dY=(y1-y2)*app.gridW/(dist)
        midX = (x1+x2)/2
        midY = (y1+y2)/2
        if(node2 in app.circuit.nodes):
            canvas.create_line(midX-dX,midY-dY,x2,y2,
                               width=app.lineWidth,fill=getColor(app,node2,hover))
        else:
            canvas.create_line(midX-dX,midY-dY,x2,y2,
                               width=app.lineWidth,fill=defColor)

        if(node1 in app.circuit.nodes):
            canvas.create_line(midX+dX,midY+dY,x1,y1,
                               width=app.lineWidth,fill=getColor(app,node1,hover))
        else:
            canvas.create_line(midX+dX,midY+dY,x1,y1,
                               width=app.lineWidth,fill=defColor)
        drawSquiggly(app,canvas,midX-dX,midY-dY,midX+dX,midY+dY,hover,resistor.resistance)
        
    else:
        drawSquiggly(app,canvas,x1,y1,x2,y2,hover,resistor.resistance)

def drawSquiggly(app,canvas,x1,y1,x2,y2,hover,resistance):
    defColor = app.grey
    if(hover):
        defColor = app.hoverColor
    d = distance(x1,y1,x2,y2)
    xInc = (x2-x1)/10
    yInc = (y2-y1)/10
    a = (app.gridW/2)*(y2-y1)/d
    b = (app.gridW/2)*(x2-x1)/d

    canvas.create_text(x1+5*xInc+2*a,y1+5*yInc-2*b,text=f'{resistance}',fill=app.grey)
    canvas.create_line(x1,y1,x1+xInc+a,y1+yInc-b,
                       width=app.lineWidth,fill=defColor)
    canvas.create_line(x1+xInc+a,y1+yInc-b,x1+3*xInc-a,y1+3*yInc+b,
                       width=app.lineWidth,fill=defColor)
    canvas.create_line(x1+3*xInc-a,y1+3*yInc+b,x1+5*xInc+a,y1+5*yInc-b,
                       width=app.lineWidth,fill=defColor)
    canvas.create_line(x1+5*xInc+a,y1+5*yInc-b,x1+7*xInc-a,y1+7*yInc+b,
                       width=app.lineWidth,fill=defColor)
    canvas.create_line(x1+7*xInc-a,y1+7*yInc+b,x1+9*xInc+a,y1+9*yInc-b,
                       width=app.lineWidth,fill=defColor)
    canvas.create_line(x1+9*xInc+a,y1+9*yInc-b,x2,y2,
                       width=app.lineWidth,fill=defColor)

def drawACVoltage(app,canvas,node,hover=False):
    x,y = node.x*app.gridW,node.y*app.gridW
    canvas.create_line(x,y-app.gridW/2,x,y+app.gridW/2,
                       width=app.lineWidth,fill=getColor(app,node,hover))
    
    canvas.create_text(x,y-3*app.gridW,text = f'{node.fixedVoltage} V',
                       fill = app.grey)
    canvas.create_text(x,y-2.5*app.gridW,text = f'{node.frequency} Hz',
                       fill = app.grey)
    cx = node.x*app.gridW
    cy = node.y*app.gridW - 5*app.gridW/4
    r = 3*app.gridW/4
    canvas.create_oval(cx-r,cy-r,
                       cx+r,cy+r,
                       width=app.lineWidth,outline=getColor(app,node,hover))
    canvas.create_line(cx-3*r/4,cy,cx-r/4,cy-3*r/4,
                       width=app.lineWidth,fill=getColor(app,node,hover))
    canvas.create_line(cx-r/4,cy-3*r/4,cx+r/4,cy+3*r/4,
                       width=app.lineWidth,fill=getColor(app,node,hover))
    canvas.create_line(cx+r/4,cy+3*r/4,cx+3*r/4,cy,
                       width=app.lineWidth,fill=getColor(app,node,hover))
    

def drawDCVoltage(app,canvas,node,hover=False):
    x,y = node.x*app.gridW,node.y*app.gridW
    canvas.create_line(x,y-app.gridW/2,x,y+app.gridW/2,
                       width=app.lineWidth,fill=getColor(app,node,hover))
    canvas.create_text(x,y-3*app.gridW/4,text = f'{node.fixedVoltage} V',
                       fill = app.grey)
    
    
def drawGround(app,canvas,node,hover=False):
    x,y = node.x*app.gridW,node.y*app.gridW
    color = app.grey
    if(hover):
        color = app.hoverColor
    canvas.create_line(x,y,x,y+app.gridW/4,width=app.lineWidth,fill=color)
    canvas.create_line(x-app.gridW/3,y+app.gridW/4,
                       x+app.gridW/3,y+app.gridW/4,width=app.lineWidth,fill=color)
    canvas.create_line(x-app.gridW/6,y+app.gridW/2,
                       x+app.gridW/6,y+app.gridW/2,width=app.lineWidth,fill=color)
    canvas.create_line(x-app.gridW/12,y+3*app.gridW/4,
                       x+app.gridW/12,y+3*app.gridW/4,width=app.lineWidth,fill=color)
    
def printNodeVoltage(app,canvas,node):
    canvas.create_text(app.width/2,app.height-20,fill=app.grey,
                       text=f'Voltage: {node.voltage}')

def drawErrors(app,canvas):
    for i in range(len(app.errorList)):
        canvas.create_text(2,app.height-(len(app.errorList)-i)*app.gridW,
                           text=f'{app.errorList[i]}',fill = 'red',anchor='nw')

def isHitBoxed(app,node):
    hitBox = app.hitBoxes[node]
    if(hitBox[0] <= app.mouseX <= hitBox[2] and
       hitBox[1] <= app.mouseY <= hitBox[3]):
        return True
    return False

def drawNode(app,canvas,node,hover=False):
    frequency = None
    if(not hover and node in app.circuit.nodes):
        if(isHitBoxed(app,node)):
            hover = True
        frequency = app.circuit.getFrequency(node)
    else:
        frequency = node.frequency
    if(node.grounded):
        drawGround(app,canvas,node,hover)
    elif(node.fixedVoltage != None):
        if(frequency == None): 
            drawDCVoltage(app,canvas,node,hover)
        else:
            drawACVoltage(app,canvas,node,hover)
    elif(hover):
        cx = app.gridW*node.x
        cy = app.gridW*node.y
        r = app.gridW/4
        canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill = app.hoverColor)

def drawComp(app,canvas,comp,hover=False):
    if(getHoverComp(app) == comp):
        node1,node2 = tuple(comp.nodeSet)
        if(not isHitBoxed(app,node1) and
           not isHitBoxed(app,node2)):
            hover = True
    if(isinstance(comp,Wire)):
        drawWire(app,canvas,comp,hover)
    elif(isinstance(comp,Resistor)):
        drawResistor(app,canvas,comp,hover)

def drawMoveComp(app,canvas):
    mouseNode = getNodeFromCoord(app,app.mouseX,app.mouseY)
    node2 = Node(mouseNode.x,mouseNode.y)
    node2.grounded = app.moveNode.grounded
    node2.fixedVoltage = app.moveNode.fixedVoltage
    node2.frequency = app.moveNode.frequency
    drawNode(app,canvas,app.fixNode,hover=True)
    drawNode(app,canvas,node2,hover=True)
    newComp = None
    if(isinstance(app.moveComp,Resistor)):
        newComp = Resistor(app.fixNode,node2)
        newComp.resistance = app.moveComp.resistance
    elif(isinstance(app.moveComp,Wire)):
        newComp = Wire(app.fixNode,node2)
    drawComp(app,canvas,newComp,hover=True)
    
    
def drawScopeVoltage(app,canvas):
    maxVolt = roundHalfUp(app.circuit.getMaxVoltage())
    x,y = app.circuit.scopeNode.x,app.circuit.scopeNode.y
    x *= app.gridW
    y *= app.gridW
    r = app.gridW/4
    canvas.create_oval(x-r,y-r,x+r,y+r,fill='red')
    xStep = app.gridW/5
    yR = 2.5*app.gridW
    yC = app.height-yR
    length = len(app.circuit.last50)
    canvas.create_text(app.width-length*xStep-2,yC,
                       text='0 V',fill='red',anchor='e')
    if(maxVolt != 0):
        canvas.create_text(app.width-length*xStep-2,app.height-2,
                           text=f'-{maxVolt} V',fill='red',anchor='se')
        canvas.create_text(app.width-length*xStep-2,app.height-2*yR,
                           text=f'{maxVolt} V',fill='red',anchor='e')
    for i in range(length-1):
        if(maxVolt != 0):
            try:
                canvas.create_line(app.width-(length-i)*xStep,
                                   yC-app.circuit.last50[i]*yR/maxVolt,
                                   app.width-(length-i-1)*xStep,
                                   yC-app.circuit.last50[i+1]*yR/maxVolt,
                                   width=1,fill='red')
            except:
                canvas.create_line(app.width-(length-i)*xStep,yC,
                                   app.width-(length-i-1)*xStep,yC,
                                   width=1,fill='red')
        else:
            canvas.create_line(app.width-(length-i)*xStep,yC,
                               app.width-(length-i-1)*xStep,yC,
                               width=1,fill='red')

def drawSideBar(app,canvas):
    canvas.create_line(app.width-10*app.gridW,0,
                       app.width-10*app.gridW,app.height,
                       width=app.lineWidth,fill=app.grey)
    canvas.create_line(app.width-5*app.gridW,0,
                       app.width-5*app.gridW,app.height-5*app.gridW,
                       width=app.lineWidth,fill=app.grey)
    for i in range(1,8):
        canvas.create_line(app.width-10*app.gridW,app.height-5*i*app.gridW,
                           app.width,app.height-5*i*app.gridW,
                           width=app.lineWidth,fill=app.grey)

    sampNode1 = getNodeFromCoord(app,app.width-10*app.gridW,2.5*app.gridW)
    sampNode2 = getNodeFromCoord(app,app.width-5*app.gridW,2.5*app.gridW)
    sampNode3 = getNodeFromCoord(app,app.width,2.5*app.gridW)
    sampNode4 = getNodeFromCoord(app,app.width-8*app.gridW,7.5*app.gridW)
    sampNode5 = getNodeFromCoord(app,app.width-3*app.gridW,9*app.gridW)
    sampNode6 = getNodeFromCoord(app,app.width-8*app.gridW,12.5*app.gridW)
    sampNode4.fixedVoltage = 5
    sampNode5.fixedVoltage = 5
    sampNode5.frequency = 40
    sampNode6.grounded = True
    if(app.compToAdd == 2):
        drawComp(app,canvas,Resistor(sampNode1,sampNode2),hover=True)
    else:
        drawComp(app,canvas,Resistor(sampNode1,sampNode2),hover=False)
    if(app.compToAdd == 1):
        drawComp(app,canvas,Wire(sampNode2,sampNode3),hover=True)
    else:
        drawComp(app,canvas,Wire(sampNode2,sampNode3),hover=False)
    if(app.compToAdd == 0):
        drawNode(app,canvas,sampNode4,hover=True)
    else:
        drawNode(app,canvas,sampNode4,hover=False)
    if(app.compToAdd == 4):
        drawNode(app,canvas,sampNode5,hover=True)
    else:
        drawNode(app,canvas,sampNode5,hover=False)
    if(app.compToAdd == 3):
        drawNode(app,canvas,sampNode6,hover=True)
    else:
        drawNode(app,canvas,sampNode6,hover=False)
    if(app.compToAdd == 5):
        canvas.create_text(app.width-2.5*app.gridW,12.5*app.gridW,
                           text='Oscilloscope',font='Arial 12',
                           fill='red')
    else:
        canvas.create_text(app.width-2.5*app.gridW,12.5*app.gridW,
                           text='Oscilloscope',font='Arial 12',
                           fill=app.grey)

    canvas.create_text(app.width-7.5*app.gridW,22.5*app.gridW,
                   text='Atmega88p',font='Arial 12',
                   fill=app.grey)
    canvas.create_text(app.width-2.5*app.gridW,22.5*app.gridW,
                   text='Atmega8515',font='Arial 12',
                   fill=app.grey)

    if(app.compToAdd == None):
        color = app.hoverColor
    else:
        color = app.grey
    xC,yC = app.width-8.5*app.gridW, 16.5*app.gridW
    canvas.create_polygon(xC,yC,
                          xC+app.gridW,yC+(5**0.5)*app.gridW,
                          xC+(1+5**0.5)*app.gridW/2-app.gridW/4,
                          yC+(1+5**0.5)*app.gridW/2-app.gridW/4,
                          fill = color)
    canvas.create_polygon(xC,yC,
                          xC+(5**0.5)*app.gridW,yC+app.gridW,
                          xC+(1+5**0.5)*app.gridW/2-app.gridW/4,
                          yC+(1+5**0.5)*app.gridW/2-app.gridW/4,
                          fill = color)

    canvas.create_line(xC+(1+5**0.5)*app.gridW/2-app.gridW/4,
                       yC+(1+5**0.5)*app.gridW/2-app.gridW/4,
                       xC+(2+5**0.5)*app.gridW/2,
                       yC+(2+5**0.5)*app.gridW/2,
                       width=5,fill=color)

    canvas.create_line(app.width-2.5*app.gridW,16*app.gridW,
                       app.width-2.5*app.gridW,19*app.gridW,
                       fill = app.grey, width = 9)

    canvas.create_line(app.width-4*app.gridW,17.5*app.gridW,
                       app.width-1*app.gridW,17.5*app.gridW,
                       fill = app.grey, width = 9)
    

def drawIC(app,canvas,IC):
    defColor = app.grey
    mouseNode = getNodeFromCoord(app,app.mouseX,app.mouseY)
    if(mouseNode in IC.getRNodes()):
        defColor = app.hoverColor
    if(IC.TLNode != None):
        canvas.create_text((IC.TLNode.x+1)*app.gridW,
                           (IC.TLNode.y-1)*app.gridW,
                           text = f'{IC.name}',fill=app.grey,
                           anchor = 's')
        mL = len(IC.pins)//2 - 1
        canvas.create_rectangle((IC.TLNode.x)*app.gridW,
                               (IC.TLNode.y)*app.gridW,
                               (IC.TLNode.x+2)*app.gridW,
                               (IC.TLNode.y+mL)*app.gridW,
                               width = app.lineWidth,outline=defColor)
        for i in range(len(IC.nodeList)):
            x = IC.nodeList[i].x*app.gridW
            y = IC.nodeList[i].y*app.gridW
            if(i < len(IC.pins)//2):
                canvas.create_line(x,y,x-app.gridW/4,y,width=app.lineWidth,fill=defColor)
                if(IC.pins[i] != None):
                    if(IC.pins[i] == 'V'):
                        canvas.create_text(x,y,text=f'{IC.voltage} {IC.pins[i]}',fill='red',anchor='nw',font='Arial 8')
                    else:
                        canvas.create_text(x,y,text=f'{IC.pins[i]}',fill='red',anchor='nw',font='Arial 8')
            else:
                canvas.create_line(x,y,x+app.gridW/4,y,width=app.lineWidth,fill=defColor)
                if(IC.pins[i] != None):
                    if(IC.pins[i] == 'V'):
                        canvas.create_text(x,y,text=f'{IC.voltage} {IC.pins[i]}',fill='red',anchor='ne',font='Arial 8')
                    else:
                        canvas.create_text(x,y,text=f'{IC.pins[i]}',fill='red',anchor='ne',font='Arial 8')
       
def getTempIC(app):
    center = getNodeFromCoord(app,app.width/2,app.height/2)
    mL = len(app.ICAdd.pins)//2 - 1
    tLX = center.x - 1
    tLY = center.y - mL//2
    sampIC = copy.deepcopy(app.ICAdd)
    sampIC.initNodes(Node(tLX,tLY))
    return sampIC
        

def altRedrawAll(app,canvas):
    if(app.ICAdd == None):
        return
    center = getNodeFromCoord(app,app.width/2,app.height/2)
    drawIC(app,canvas,getTempIC(app))

    pinToSet = getPinToSet(app.ICAdd,app.ICPinCounter)
    canvas.create_text(app.width/2,app.height - app.gridW,
                       text=f'Pin to Add: {pinToSet}',fill='red')
    

def redrawAll(app, canvas):
    canvas.create_rectangle(0,0,app.width,app.height,fill='black')
    if(type(app.compToAdd) == bool):
        altRedrawAll(app,canvas)
        return
        
    drawSideBar(app,canvas)
    drawErrors(app,canvas)
    
    for comp in app.circuit.comps:
        drawComp(app,canvas,comp)
    for node in app.circuit.nodes:
        drawNode(app,canvas,node)

    mouseNode = getNodeFromCoord(app,app.mouseX,app.mouseY)
    if(app.pressedNode != None and app.compToAdd != None):
        if(mouseNode != app.pressedNode):
            if(app.compToAdd == 1):
                drawWire(app,canvas,Resistor(app.pressedNode,mouseNode))
            elif(app.compToAdd == 2):
                drawResistor(app,canvas,Resistor(app.pressedNode,mouseNode))
    for node in app.circuit.nodes:
        if(mouseNode == node):
            printNodeVoltage(app,canvas,node)
            
    
    if(app.moveComp != None and mouseNode != app.fixNode):
        drawMoveComp(app,canvas)

    if(app.circuit.scopeNode != None):
        drawScopeVoltage(app,canvas)

    for ic in app.circuit.ICs:
        drawIC(app,canvas,ic)

    if(app.ICAdd != None):
        tempIC = getTempIC(app)
        tempIC.initNodes(mouseNode)
        drawIC(app,canvas,tempIC)

                
            
        

runApp(width=800,height=800)
