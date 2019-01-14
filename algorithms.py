import sys
from functions import Cell

def DPH(candidatesDict, APSP, T, ordering, checkForOverlaps=True):

    matrix = dict()
    counter = 0
    # the id of the root node with the maximum value
    rootNodeWithMinValue = -1
    # the value of the root node in template tree with the maximum value
    minValueOfRoot = sys.maxint
    # when true this is the final iteration, i.e. the last node of the template is examined
    finalIter = False
    minNodeDict = dict()
    minNode = None
    
    discardCandidate = False
    halt = False

    for v in ordering: # v is the node in the post ordering of the nodes in T. go bottom up in the template tree
        # if true this is the final iteration so switch the value of finalIter
        if counter == (T.number_of_nodes() - 1):
            finalIter = True

        counter += 1

        # for each candicate for position v
        for z in list(candidatesDict[v]):
            sumValues = 0
            nodeDict = dict()
            
            if z not in APSP:
                continue

            # for each successor of v in T
            for u in T.successors(v):
                minValue = sys.maxint
                minNode = None
                minNodeDict = None

                # for each candidate for position u (the successor of v)
                for w in list(candidatesDict[u]):

                    if (w not in APSP) or (z not in APSP[w]):
                        continue

                    if checkForOverlaps:
                        nodesInCandidatesSubsolution = set(matrix[w,u].d.values())
                        forbiddenNodes = set(nodeDict.values()) | set([z])
                        if w in forbiddenNodes or nodesInCandidatesSubsolution & forbiddenNodes != set([]): 
                            continue

                    # find candidate whose value plus distance from z is minimum
                    if ((matrix[w, u].v + APSP[w][z]) < minValue):
                        minValue = matrix[w, u].v + APSP[w][z]
                        minNode = w
                        minNodeDict = matrix[w, u].d

                if minNode == None:
                    discardCandidate = True
                    break
                
                # the following lines are required to merge the dict of minNode and nodeDict in order to form the dict of the parent
                nodeDictNew = minNodeDict.copy()
                nodeDictNew.update(nodeDict)

                nodeDict = nodeDictNew
                nodeDict[u]=minNode
                sumValues = sumValues + minValue

            if discardCandidate:
                discardCandidate = False
                continue
            
            currentCell = Cell(sumValues, nodeDict)

            if sumValues < minValueOfRoot and finalIter:
                minValueOfRoot = sumValues
                rootNodeWithMinValue = z
            matrix[z, v] = currentCell
        
        if checkForOverlaps and (z,v) not in matrix:
            return None,None

    matrix[rootNodeWithMinValue,0].d[0] = rootNodeWithMinValue
    return minValueOfRoot, matrix[rootNodeWithMinValue,0].d

def DP(candidatesDict, APSP, T, ordering):
    return DPH(candidatesDict,APSP,T,ordering,False)