"""
Pabuito Auto Scripts

This script contains all the one off scrips for automation on the Pabuito Grade Tool.

All scrips within this document should follow a couple of conventions. They need to return the grade information in the form of a dictionary

return {
        'grade_value': int, 
        'comment_text':'',
        'default_comments_text':'',
        'example_comments_text':'',
        }

the comments can remain '' without effecting the tools functionality. 

Written by: Adam Fatka
adam.fatka@gmail.com
www.fatkaforce.com

"""


import maya.cmds as cmds

class utilities():
    
    def __init__(self):
        masterNodes = []
        nodesWithSubs = []
        colectedNodes = []
        #this is a bucket to hold sorted nodes, not any specific type of sorted node.
        sortedNodes = []
        hasDefaultName = []
        notFrozen = []
        pivotNotCenter = []
        hasHistory = []
        visibleNodes = []
        triObjects = []
        triFaces = []
        nSidedObjects = []
        nSidedFaces = []
        nonManifoldObjects =[]
        nonManifoldComponents = []
        laminaObjects = []
        laminaFaces = []
        print "Utilities Class Initiated"
    
    #####
    #####
    #
    #This section is Maya specific utilities to run through categories that are typically graded for
    #
    #####
    #####
    
    
    #if returned array size = 1 than master group = yes else: no
    #
    #Procedure takes no input and returns all root nodes that are not cameras. 
    def masterGroupTest(self):
        assemblies = cmds.ls(long=1, assemblies=1)
        upperNodes = []
        for item in assemblies:
            temp = cmds.listRelatives(item, path=1)
            if (temp==None):
                upperNodes.append(item)
            else:
                if not(cmds.nodeType(temp[0])=='camera'):
                    upperNodes.append(item)
        return upperNodes
    
    #Checks to see if the supplied nodes have some child groups
    #
    #Procedure takes input of master nodes and checks if they have children nodes that are groups/transforms then returns subgroup nodes. 
    def subGroupsTest(self,masterNodes):
        nodesWithSubs = []
        NodesNoSubs =[]
        for node in masterNodes:
            children = cmds.listRelatives(node, path=1)
            for child in children:
                if (cmds.nodeType(child)=='transform'):
                    grandChildren = cmds.listRelatives(child,path=1)
                    if grandChildren != None:
                        if(cmds.nodeType(grandChildren[0])=='transform'):
                            nodesWithSubs.append(child)
                            
        return nodesWithSubs
        
        
    #Collects a node tree
    #
    #Procedure takes an input and returns all children of that input
    
    def nodeCollector(self, inputNode):
        inputNode = inputNode
        nodeList = []
        iterateList = []
        if(inputNode == None or len(inputNode)==0):
            cmds.error("Input is Null")
        elif(len(inputNode)==1):
            iterateList.append(inputNode[0])
        else:
            for object in inputNode:
                iterateList.append(object)
        for item in iterateList:
            descendents = cmds.listRelatives(item, allDescendents=1, path=1)
            if(descendents != None):
                if ('master' or 'Master' in item) and (cmds.nodeType(descendents[0])=='nurbsCurve'):
                    continue
                else:
                    nodeList.append(item)
                    for child in descendents:
                        nodeList.append(child)
                        
        return nodeList
    
    #Collects a list of a certain node type from a larger list
    #
    #Procedure takes an input of nodes and returns only the nodes that match input nodeType (input as a string 'transform')
    
    def sortNodeList(self, inputList, nodeType):
        nodeList = inputList
        sortedList = []
        for node in nodeList:
            if cmds.nodeType(node) == nodeType:
                sortedList.append(node)
        return sortedList
        
    #compares the names of the input to a list of default names
    #
    #Procedure takes an input of nodes and returns nodes that match default names list. 
    
    def compareDefaultNames(self, inputNodes):
        defaultNames = ["pCube", "pCylinder",  "pSphere", "pCone",
                        "pPlane", "pTorus", "pPrism", "pPyramid",
                        "pPipe", "pHelix", "pSolid", "nurbsSphere",
                        "curve", "nurbsCube", "nurbsCylinder", "nurbsCone",
                        "nurbsPlane", "nurbsTorus", "nurbsCircle", "nurbsSquare",
                        "revolvedSurface", "subdivSphere", "subdivCube", "subdivCylinder",
                        "subdivCone", "subdivPlane", "subdivTorus", "nurbsToPoly",
                        "polySurface", "pasted", "group", "mirroredCutMesh", "extrudedSurface"]
        hasDefaultName = []
        nodeList = inputNodes
        for object in nodeList:
            try:
                splitCatch = object.split('|')
            except AttributeError:
                continue
            if len(splitCatch) !=1:
                query = splitCatch[-1]
            else:
                query = object
            for name in defaultNames:
                if name in query:
                    if name=='group':
                        if('group' in query) and not (('_group' in query) or ('group_' in query)):
                            hasDefaultName.append(object)
                            continue
                        else:
                            continue
                    hasDefaultName.append(object)
        return hasDefaultName
    
    #checks for non zero translations and rotations and non-one scales
    #
    #Procedure takes an input of TRANSFORM nodes and returns nodes that are not frozen
    
    def frozenTransforms(self, inputNodes):
        transforms = inputNodes
        frozen = []
        for item in transforms:
            translation = cmds.xform(item, query=1, translation=1)
            rotation = cmds.xform(item, query=1, rotation =1)
            scale = cmds.xform(item, query=1,scale=1, relative=1)
            if(translation[0]==0 and translation[1]==0 and translation[2]==0 and
               rotation[0]==0 and rotation[1]==0 and rotation[2]==0 and
               scale[0]==1 and scale[1]==1 and scale[2]==1):
                frozen.append(item)
        notFrozen=[]
        
        
        for item in transforms:
            if item in frozen:
                continue
            else: notFrozen.append(item)
            
        return notFrozen
    
    #Checks for pivots that are not centered
    #
    #Procedure takes an input of TRANSFORM nodes and returns nodes that do not have centered pivots. 
    
    def pivotsCentered(self, inputNodes):
        pivots = inputNodes
        pivotCenter = []
        for item in pivots:
            pivotLocation = cmds.xform(item, ws=1, query=1, rotatePivot=1)
            pivotNewLocation = cmds.objectCenter(item)
            if(abs(float(pivotLocation[0]) - float(pivotNewLocation[0])) < 0.01):
                if(abs(float(pivotLocation[1]) - float(pivotNewLocation[1])) < 0.01):
                    if(abs(float(pivotLocation[2]) - float(pivotNewLocation[2])) < 0.01):
                        pivotCenter.append(item)
        pivotNotCenter = []
        for item in pivots:
            if item in pivotCenter:
                continue
            else: pivotNotCenter.append(item)
            
        return pivotNotCenter
    
    #Checks for construction history
    #
    #Procedure takes an input of TRANSFORM nodes and returns nodes that have construction history
    
    def historyFinder(self, inputNodes):
        nodeList = inputNodes
        falsePositiveList = ['displayLayer', 'groupId', 'shadingEngine', 'mesh', 'animCurveTL']
        historyList = []
        for item in nodeList:
            if cmds.listHistory(item, pruneDagObjects = 1):
                history = cmds.listHistory(item, pruneDagObjects = 1)
                for i in history:
                    historyType = cmds.nodeType(i)
                    if historyType not in falsePositiveList:
                        if item not in historyList:
                            historyList.append(item)
        return historyList
    
    #####
    #####
    #
    #This area holds methods dealing with display layers. 
    #
    #####
    #####
    #Checks for visible nodes
    #
    #Procedure takes an input of nodes and returns nodes that are visible
    def visibilityBulkTest(self, inputNodes):
        nodeList = inputNodes
        visibleNodes = []
        notVisibleNodes = []
        for node in nodeList:
            if self.visibilityTest(node):
                visibleNodes.append(node)
            else:
                notVisibleNodes.append(node)
        return visibleNodes 

    #Checks to see if a node is visible
    #
    #Procedure takes an input node and returns if that node is visible TRUE/FALSE

    def visibilityTest(self, inputNode):
        testNode = inputNode  
        #verify node exists
        if not cmds.objExists(testNode):return False
        #TEst to see if the object has a visibility attribute (and by extention a DAG node)
        if not cmds.attributeQuery('visibility', node = testNode, exists = True):return False
        #Gather objects visibility attribute
        isVisible = cmds.getAttr(testNode + '.visibility')
        #test if an oject has an intermediateObject attribute
        if cmds.attributeQuery('intermediateObject', node = testNode, exists = True):
            #tests if an object is an intermediateObject, and as such is not visible
            isVisible = isVisible and not cmds.getAttr(testNode + '.intermediateObject')
        #test if the object is in a display layer through the existence of an overrideEnabled attribute
        if cmds.attributeQuery('overrideEnabled', node = testNode, exists = True) and cmds.getAttr(testNode + '.overrideEnabled'):
            #test to see if the display layer is visible
            isVisible = isVisible and cmds.getAttr(testNode + '.overrideVisibility')
        #if the object tests visible so far, verify it's parents are visible
        if isVisible:
            nodeParents = cmds.listRelatives(testNode, parent = 1, path=1)
            if nodeParents != None:
                if len(nodeParents)> 0:
                    isVisible = isVisible and self.visibilityTest(nodeParents[0])
        #return a bollean as to whether the object is visible or not
        return isVisible


    def findLayers(self, ignore_layers=['defaultLayer']):
        layers = cmds.ls(long=True,type='displayLayer')
        for current_layer in ignore_layers:
            if current_layer in layers:
                layers.remove(current_layer)       
        return layers
    
    def collectLayerState(self,layers):
        layerState=[]
        for layer in layers:
            currentState = cmds.getAttr('%s.visibility' % layer)
            layerState.append(currentState)
        return layerState

    def setLayersVisibility(self,layers, values):
        counter = 0
        for layer in layers:        
            cmds.setAttr( '%s.visibility' % layer, values[counter])
            counter+=1
            
    def hideAllLayers(self,layers):
        hide_states = []
        for layer in layers:
            hide_states.append(0)
        self.setLayersVisibility(layers, hide_states)
    
    #####
    #####
    #
    #This area is utilities for manipulating data, breaking ranges, counting selections, and various tasks that don't really fit elsewhere
    #
    #####
    #####
    
    #takes a range **[1:5] and breaks it into a series 1,2,3,4,5**
    #
    #Procedure takes an input range num:num-end and breaks it into num, num+1, num+2, ...num-end
    
    def rangeSplit(self, inputRange):
        range = inputRange
        newRange = []
        k=0
        for r in range:
            item = r
            if len(range[k].split(':')) !=2:
                temp = range[k].split(':')
                range[k] = temp[-2] + ":" + temp[-1]
            colonSplit = range[k].split(':')
            k+=1
            leftSplit = colonSplit[0].split('[')
            rightSplit = colonSplit[1].split(']')
            try:
                i = int(leftSplit[1])
            except IndexError:
                newRange.append(r)
                continue
            while i <= int(rightSplit[0]):
                rangeItem = ("%s[%d]" % (leftSplit[0], i))
                newRange.append(rangeItem)
                i+=1
        return newRange
    
    #####
    #####
    #
    #This area identifies different types of geometry present in the scene. 
    #
    #####
    #####
    
    #checks for triangle geometry
    #
    #Procedure takes an input of TRANSFORM nodes and returns a list of triangle faces and objects with triangle faces REQUIRED:  Proc **self.rangeSplit**
    
    def triFinder(self, inputNodes):
        nodeList = inputNodes
        triObjects = []
        cmds.select(clear = 1)
        for node in nodeList:
            cmds.select(node, add=1)
        ##This line constrains the selection to faces with 3 sides and then selects them
        ##It also constrains the selection to tris so it must be reset before exiting
        cmds.polySelectConstraint(mode=3, type=8, size=1)
        triFaces = cmds.ls(selection=1)
        for item in triFaces:
            tempHolder = item.split('.')
            triObjects.append(tempHolder[0])
        newRange = []
        range = []
        for x in triFaces:
            if ":" in x:
                 triFaces.remove(x)
                 range.append(x)
        newRange = self.rangeSplit(range)
        for t in newRange:
             triFaces.append(t)
        ##This resets the selection to 'normal'
        cmds.polySelectConstraint(mode=0, type=8, size=0)
        triObjects = list(set(triObjects))
        cmds.select(clear=1)
            
        return triObjects, triFaces
    
    #Checks for N-gons
    #
    #Procedure takes an input of TRANSFORM nodes and returns a list of n-gon faces and objects with n-gon faces REQUIRED: Proc **self.rangeSplit**
    
    def nGonFinder(self, inputNodes):
        nodeList = inputNodes
        nSidedObjects = []
        cmds.select(clear = 1)
        for node in nodeList:
            cmds.select(node, add=1)
        ##This line constrains the selection to faces with more than 4 sides and then selects them.
        ##It also constrains the selection to N-gons so it must be reset before exiting.
        cmds.polySelectConstraint(mode=3, type=8, size=3)
        nSidedFaces = cmds.ls(selection=1)
        for item in nSidedFaces:
            tempHolder = item.split('.')
            nSidedObjects.append(tempHolder[0])
        newRange = []
        range = []
        for x in nSidedFaces:
            if ":" in x:
                nSidedFaces.remove(x)
                range.append(x)
        newRange = self.rangeSplit(range)
        for t in newRange:
            nSidedFaces.append(t)
        #This resets the selection to 'normal'
        cmds.polySelectConstraint(mode=0, type=8, size=0)
        nSidedObjects = list(set(nSidedObjects))
        cmds.select(clear=1)
        
        return nSidedObjects, nSidedFaces
    
    #Checks for non-manifold geometry. 
    #
    #Procedure takes an input of TRANSFORM nodes and returns a list of nonmanifold components and objects. REQUIRED: Proc **self.rangeSplit**
    
    def nonManifoldFinder(self, inputNodes):
        nodeList = inputNodes
        nonManifoldObjects = []
        newRange = []
        range = []
        nonManifoldComponents = cmds.polyInfo(nodeList, nonManifoldVertices = 1, nonManifoldEdges = 1)
        if nonManifoldComponents != None:
            for item in nonManifoldComponents:
                tempHolder = item.split('.')
                nonManifoldObjects.append(tempHolder[0])
                if ":" in item:
                    nonManifoldComponents.remove(item)
                    range.append(item)
            newRange = self.rangeSplit(range)
            for t in newRange:
                nonManifoldComponents.append(t)
            nonManifoldObjects = list(set(nonManifoldObjects))
        else:
            nonManifoldComponents = []
        
        return nonManifoldObjects, nonManifoldComponents
    
    #Checks for lamina faces
    #
    #Procedure takes an input of TRANSFORM nodes and returns a list of lamina faces and objects. REQUIRED: Proc **self.rangeSplit**
    
    def laminaFinder(self, inputNodes):
        nodeList = inputNodes
        laminaObjects = []
        laminaFaces = cmds.polyInfo(nodeList, laminaFaces = 1)
        if laminaFaces == None:
            laminaFaces = []
            return laminaObjects, laminaFaces
        for item in laminaFaces:
            tempHolder = item.split('.')
            laminaObjects.append(tempHolder[0])
        newRange = []
        range = []
        for x in laminaFaces:
            if ":" in x:
                laminaFaces.remove(x)
                range.append(x)
        newRange = self.rangeSplit(range)
        for t in newRange:
            laminaFaces.append(t)
            
        laminaObjects = list(set(laminaObjects))
        
        return laminaObjects, laminaFaces