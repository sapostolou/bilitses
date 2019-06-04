import sys
from functions import Cell
import networkx as nx
import sys

def DPH(candidatesDict, APSP, T, ordering, checkForOverlaps=True, fitDict=None):

    matrix = dict()
    # the id of the root node with the maximum value
    rootNodeWithMinValue = -1
    # the value of the root node in template tree with the maximum value
    minValueOfRoot = sys.maxsize
    minNodeDict = dict()
    minNode = None
    
    discardCandidate = False
    halt = False

    for v in ordering: # v is the node in the post ordering of the nodes in T. go bottom up in the template tree

        # for each candicate for position v
        for z in candidatesDict[v]:
            sumValues = 0
            nodeDict = dict()
            
            if z not in APSP:
                continue

            # for each successor of v in T
            for u in T.successors(v):
                minValue = sys.maxsize
                minNode = None
                minNodeDict = None

                # for each candidate for position u (the successor of v)
                for w in candidatesDict[u]:

                    if (w not in APSP) or (z not in APSP[w]):
                        continue

                    if checkForOverlaps:
                        nodesInCandidatesSubsolution = set(matrix[w,u].d.values())
                        forbiddenNodes = set(nodeDict.values()) | set([z])
                        if w in forbiddenNodes or nodesInCandidatesSubsolution & forbiddenNodes != set([]): 
                            continue

                    # find candidate whose value plus distance from z is minimum
                    if fitDict == None:
                        fit = 0
                    else:
                        fit = fitDict[w,T.node[u]['skill']]

                    if ((matrix[w, u].v + APSP[w][z]) + fit < minValue):
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

            if sumValues < minValueOfRoot and v == ordering[-1]:
                minValueOfRoot = sumValues
                rootNodeWithMinValue = z
            matrix[z, v] = currentCell
        
        # if checkForOverlaps and (z,v) not in matrix:
        #     return None,None

    matrix[rootNodeWithMinValue,0].d[0] = rootNodeWithMinValue
    return minValueOfRoot, matrix[rootNodeWithMinValue,0].d

def DP(candidatesDict, APSP, T, ordering, fitDict):
    return DPH(candidatesDict,APSP,T,ordering,False,fitDict)

def maxDegree(candidates, APSP, template, G, degreeDict):
    nodesUsed = set()
    maxDegNode = None
    maxDeg = 0
    result = dict()
    for v in candidates[0]:
        if degreeDict[v] > maxDeg:
            maxDeg = degreeDict[v]
            maxDegNode = v
    result[0] = maxDegNode
    nodesUsed.add(maxDegNode)

    resultCost = 0
    bfsEdges = nx.bfs_edges(template,0)
    for v,u in bfsEdges:
        maxDeg = 0
        maxDegNode = None
        for w in candidates[u]:
            if degreeDict[w] > maxDeg and w not in nodesUsed:
                maxDegNode = w
                maxDeg = degreeDict[w]
        result[u] = maxDegNode
        nodesUsed.add(maxDegNode)
        resultCost += APSP[result[v]][maxDegNode]
    return resultCost, result

def singleSourceTopDown(source, candidates, APSP, template, G, centrality, fit):
    bfsEdges = nx.bfs_edges(template,0)
    nodesUsed = set(int(source))
    result = {0: source}
    resultTotalCost = 0
    
    for v,u in bfsEdges:

        minCostNode = None
        minCost = sys.maxsize

        for w in candidates[u]:

            if (w in nodesUsed) or (w not in APSP):
                continue

            if fit == None:
                cost = APSP[result[v]][w]
            else:
                cost = APSP[result[v]][w] + fit[w,template.node[u]['skill']]

            if cost < minCost:
                minCost = cost
                minCostNode = w

        if minCostNode == None:
            return None

        result[u] = minCostNode
        resultTotalCost += minCost
        nodesUsed.add(minCostNode)

    return resultTotalCost, result
        

def TopDown(candidates,APSP,template,G,centralityDict, fitDict):
    
    maxRootCentrality = 0
    maxRootCentralityNode = None

    # for root pick node with highest degree centrality
    for u in candidates[0]:
        if centralityDict[u] > maxRootCentrality:
            maxRootCentrality = centralityDict[u]
            maxRootCentralityNode = u

    resultCost, result = singleSourceTopDown(maxRootCentralityNode, candidates, APSP, template, G, centralityDict, fitDict)
    return resultCost, result

def TopDownCheckAllForRoot(candidates,APSP,template,G,centralityDict, fitDict):

    minSolutionCost = sys.maxsize
    minSolution = None

    for r in candidates[0]:

        resultCost, result = singleSourceTopDown(r, candidates, APSP, template, G, centralityDict, fitDict)
    
        if resultCost < minSolutionCost:
            minSolutionCost = resultCost
            minSolution = result

    return minSolutionCost, minSolution

def rarestFirst(template, candidates, APSP, fitDict):
    # find rarest skill i.e. the one with the smallest candidate set
    rarestSkillCandidatesNum = sys.maxsize
    rarestSkill = None
    for s in candidates:
        l = len(candidates[s])
        if l < rarestSkillCandidatesNum:
            rarestSkillCandidatesNum = l
            rarestSkill = s

    bestSolutionCost = sys.maxsize
    bestSolution = None

    for v in candidates[rarestSkill]:
        solutionCost = 0
        solution = dict()
        for t in candidates:

            if t == rarestSkill:
                continue

            closestNeighborDist = sys.maxsize
            closestNeighbor = None

            for u in candidates[t]:
                # find the one closest to v
                if fitDict == None:
                    cost = APSP[v][u]
                else:
                    cost = APSP[v][u] + fitDict[u,template.node[t]['skill']]
                if cost < closestNeighborDist:
                    closestNeighbor = u
                    closestNeighborDist = cost
            
            solutionCost += closestNeighborDist
            solution[t] = closestNeighbor
        
        if solutionCost < bestSolutionCost:
            bestSolutionCost = solutionCost
            bestSolution = solution
    
    return bestSolutionCost, bestSolution