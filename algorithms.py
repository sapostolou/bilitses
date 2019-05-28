import sys
from functions import Cell
import networkx as nx
import sys

def DPH(candidatesDict, APSP, T, ordering, checkForOverlaps=True):

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

            if sumValues < minValueOfRoot and v == ordering[-1]:
                minValueOfRoot = sumValues
                rootNodeWithMinValue = z
            matrix[z, v] = currentCell
        
        # if checkForOverlaps and (z,v) not in matrix:
        #     return None,None

    matrix[rootNodeWithMinValue,0].d[0] = rootNodeWithMinValue
    return minValueOfRoot, matrix[rootNodeWithMinValue,0].d

def DP(candidatesDict, APSP, T, ordering):
    return DPH(candidatesDict,APSP,T,ordering,False)

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

def TopDown(candidates,APSP,template,G,centralityDict):
    bfsEdges = nx.bfs_edges(template,0)
    maxRootCentrality = 0
    maxRootCentralityNode = None
    result = dict()
    resultSum = 0
    nodesUsed = set()

    # for root pick node with highest degree centrality
    for u in candidates[0]:
        if centralityDict[u]>maxRootCentrality:
            maxRootCentrality = centralityDict[u]
            maxRootCentralityNode = u
    result[0] = maxRootCentralityNode
    nodesUsed.add(maxRootCentralityNode)
    
    # for each successor pick the closest vertex in the respective candidate set
    for v,u in bfsEdges:
        closestNode = None
        closestNodeDistance = sys.maxsize
        for w in candidates[u]:
            if (w in nodesUsed) or (w not in APSP):
                continue
            currDist = APSP[result[v]][w]
            if currDist < closestNodeDistance:
                closestNodeDistance = currDist
                closestNode = w
        if closestNode == None:
            print("no node found")
        result[u] = closestNode
        resultSum = resultSum + closestNodeDistance
        nodesUsed.add(closestNode)
    return resultSum, result

def TopDownCheckAllForRoot(candidates,APSP,template,G,centralityDict):
    bfsEdges = list(nx.bfs_edges(template,0))
    result = dict()
    resultSum = 0
    rootCandidatesAndValues = dict()
    minRootValue = sys.maxsize
    minSolution = None

    for r in candidates[0]:

        nodesUsed_r = set()
        conflicts = set()
        nodesUsed_r.add(r)
        result_r = dict()
        result_r[0] = r
        sum_r = 0
    
        # for each successor pick the closest vertex in the respective candidate set
        for v,u in bfsEdges:
            closestNode = None
            closestNodeDistance = sys.maxsize
            candidates_u = candidates[u]
            for x in candidates_u:
                if APSP[result_r[v]][x] < closestNodeDistance and x not in nodesUsed_r:
                    closestNodeDistance = APSP[result_r[v]][x]
                    closestNode = x
            if closestNode == None:
                print("no node found")

            result_r[u] = closestNode
            sum_r += closestNodeDistance
            nodesUsed_r.add(closestNode)

        result_r[0] = r
        if sum_r < minRootValue:
            minRootValue = sum_r
            minSolution = result_r

    return minRootValue, minSolution

def rarestFirst(candidates, APSP):
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
                d = APSP[v][u]
                if d < closestNeighborDist:
                    closestNeighbor = u
                    closestNeighborDist = d
            
            solutionCost += closestNeighborDist
            solution[t] = closestNeighbor
        
        if solutionCost < bestSolutionCost:
            bestSolutionCost = solutionCost
            bestSolution = solution
    
    return bestSolutionCost, bestSolution