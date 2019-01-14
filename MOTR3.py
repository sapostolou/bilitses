# In this file the greedy algorithm for the generic problem is implemented.
# Heuristic1 only evaluates all candidates for the root node in the template and then greedily picks the best node for the root and moves downwards to the children
# Pick the candidate with max degree

import networkx as nx
from collections import Counter
import csv
import sys
import pickle
from collections import defaultdict
import random
random.seed()
#from test import total_size
from multiprocessing import Pool
import datetime
import json
import os.path
import copy
from math import floor,log,ceil
from functions import validSolution, addNodeToTemplate
from algorithms import DP,DPH

# def validSolution(solution, template, candidates):
#     if solution == None:
#         print 'failure'
#         return True
#     numKeys = len(solution)
#     if numKeys != template.number_of_nodes():
#         print 'not valid 1',solution
#         return False
#     duplicates = [k for k,v in Counter(solution.values()).items() if v>1]
#     if len(duplicates) > 0:
#         print 'not valid 2',solution
#         return False
#     for k in solution:
#         if solution[k] not in candidates[k]:
#             print 'not valid 3'
#             return False
#     return True

# def DPwithOverlapCheck(initialDict, APSP, T, ordering):
#     candidatesDict = copy.deepcopy(initialDict)
#     matrix = dict()
#     counter = 0
#     # the id of the root node with the maximum value
#     rootNodeWithMinValue = -1
#     # the value of the root node in template tree with the maximum value
#     minValueOfRoot = sys.maxint
#     # when true this is the final iteration, i.e. the last node of the template is examined
#     finalIter = False
#     minNodeDict = dict()
#     minNode = None
    
#     halt = False

#     for v in ordering: # v is the node in the post ordering of the nodes in T. go bottom up in the template tree
#         # if true this is the final iteration so switch the value of finalIter
#         if counter == (T.number_of_nodes() - 1):
#             finalIter = True

#         counter += 1

#         # for each candicate for position v
#         for z in list(candidatesDict[v]):
#             sumValues = 0
#             nodeDict = dict()
            
#             if z not in APSP:
#                 continue

#             # for each successor of v in T
#             for u in T.successors(v):
#                 minValue = sys.maxint
#                 minNode = None
#                 minNodeDict = None

#                 # for each candidate for position u (the successor of v)
#                 for w in list(candidatesDict[u]):

#                     if (w not in APSP) or (z not in APSP[w]):
#                         continue

#                     nodesInCandidatesSubsolution = set(matrix[w,u].d.values())
#                     forbiddenNodes = set(nodeDict.values()) | set([z])
#                     if w in forbiddenNodes or nodesInCandidatesSubsolution & forbiddenNodes != set([]): 
#                         continue

#                     # find candidate whose value plus distance from z is minimum
#                     if ((matrix[w, u].v + APSP[w][z]) < minValue):
#                         minValue = matrix[w, u].v + APSP[w][z]
#                         minNode = w
#                         minNodeDict = matrix[w, u].d

#                 if minNode == None:
#                     # print "\nNoone found for position",u,"with skill",T.node[u]['skill'],"and with",z,"in position",v
#                     # print "Candidates for",v,":",len(candidatesDict[v])
#                     # print "Candidates for",u,":",len(candidatesDict[u])
#                     return None, None
#                 # the following lines are required to merge the dict of minNode and nodeDict in order to form the dict of the parent
#                 nodeDictNew = minNodeDict.copy()
#                 nodeDictNew.update(nodeDict)

#                 nodeDict = nodeDictNew
#                 nodeDict[u]=minNode
#                 sumValues = sumValues + minValue

#             currentCell = Cell(sumValues, nodeDict)

#             if sumValues < minValueOfRoot and finalIter:
#                 minValueOfRoot = sumValues
#                 rootNodeWithMinValue = z
#             matrix[z, v] = currentCell
#     matrix[rootNodeWithMinValue,0].d[0] = rootNodeWithMinValue
#     return minValueOfRoot, matrix[rootNodeWithMinValue,0].d

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
        closestNodeDistance = sys.maxint
        for w in candidates[u]:
            if (w in nodesUsed) or (w not in APSP):
                continue
            currDist = APSP[result[v]][w]
            if currDist < closestNodeDistance:
                closestNodeDistance = currDist
                closestNode = w
        if closestNode == None:
            print "no node found"
        result[u] = closestNode
        resultSum = resultSum + closestNodeDistance
        nodesUsed.add(closestNode)
    return resultSum, result

def TopDownCheckAllForRoot(candidates,APSP,template,G,centralityDict):
    bfsEdges = list(nx.bfs_edges(template,0))
    result = dict()
    resultSum = 0
    rootCandidatesAndValues = dict()
    minRootValue = sys.maxint
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
            closestNodeDistance = sys.maxint
            candidates_u = list(candidates[u])
            for x in candidates_u:
                if APSP[result_r[v]][x] < closestNodeDistance and x not in nodesUsed_r:
                    closestNodeDistance = APSP[result_r[v]][x]
                    closestNode = x
            if closestNode == None:
                print "no node found"

            result_r[u] = closestNode
            sum_r += closestNodeDistance
            nodesUsed_r.add(closestNode)

        result_r[0] = r
        if sum_r < minRootValue:
            minRootValue = sum_r
            minSolution = result_r

    return minRootValue, minSolution

def runSingleIteration(candidatesDict,template, APSP, degreeDict, centralityDict, G):
    # Create ordering
    postOrdering = list(nx.dfs_postorder_nodes(template, 0))

    # Execute algorithms

    currentValues = []
    currentTimes = []

    for i in range(0,5):

        before = datetime.datetime.now()

        if i == 0:
            value, solution = DPH(candidatesDict, APSP, template, postOrdering)
        elif i == 1:
            value, solution = maxDegree(candidatesDict, APSP, template, G, degreeDict)
        elif i == 2:
            value, solution = maxDegree(candidatesDict, APSP, template, G, centralityDict)
        elif i == 3:
            value, solution = TopDown(candidatesDict, APSP, template, G, centralityDict)
        elif i == 4:
            value, solution = TopDownCheckAllForRoot(candidatesDict, APSP, template, G, centralityDict)
        
        time = (datetime.datetime.now() - before).total_seconds()

        currentValues.append(value)
        currentTimes.append(time)
    
    return currentValues, currentTimes

    # before = datetime.datetime.now()
    # value, solution = DPH(candidatesDict, APSP, template, postOrdering)
    # time = (datetime.datetime.now() - before).total_seconds()

    # # if not validSolution(solution, template, candidatesDict):
    # #     return
    # # if value != None:
    # #     valueMeasurements[i+1][0].append(value)
    # #     timeMeasurements[i+1][0].append(time)
    # currentValues.append(value)
    # currentTimes.append(time)

    # before = datetime.datetime.now()
    # value, solution = maxDegree(candidatesDict, APSP, template, G, degreeDict)
    # time = (datetime.datetime.now() - before).total_seconds()
    # if not validSolution(solution, template, candidatesDict):
    #     print "not valid solution maxDegree"
    #     return
    # # valueSums[i+1]['maxDeg'] += value
    # # timeSums[i+1]['maxDeg'] += time
    # if value != None:
    #     valueMeasurements[i+1][1].append(value)
    #     timeMeasurements[i+1][1].append(time)
    # currentValues.append(value)
    # currentTimes.append(time)

    # before = datetime.datetime.now()
    # value, solution = maxDegree(candidatesDict, APSP, template, G, centralityDict)
    # time = (datetime.datetime.now() - before).total_seconds()
    # if not validSolution(solution, template, candidatesDict):
    #     print "not valid solution maxCen"
    #     return
    # # valueSums[i+1]['maxCen'] += value
    # # timeSums[i+1]['maxCen'] += time
    # if value != None:
    #     valueMeasurements[i+1][2].append(value)
    #     timeMeasurements[i+1][2].append(time)
    # currentValues.append(value)
    # currentTimes.append(time)

    # before = datetime.datetime.now()
    # value, solution = TopDown(candidatesDict, APSP, template, G, centralityDict)
    # time = (datetime.datetime.now() - before).total_seconds()
    # if not validSolution(solution, template, candidatesDict):
    #     print "not valid solution TopDown"
    #     return
    # # valueSums[i+1]['topDown'] += value
    # # timeSums[i+1]['topDown'] += time
    # if value != None:
    #     valueMeasurements[i+1][3].append(value)
    #     timeMeasurements[i+1][3].append(time)
    # currentValues.append(value)
    # currentTimes.append(time)

    # before = datetime.datetime.now()
    # value, solution = TopDownCheckAllForRoot(candidatesDict, APSP, template, G, centralityDict)
    # time = (datetime.datetime.now() - before).total_seconds()
    # if not validSolution(solution, template, candidatesDict):
    #     print "not valid solution TopDown+"
    #     return
    # # valueSums[i+1]['topDownPlus'] += value
    # # timeSums[i+1]['topDownPlus'] += time
    # if value != None:
    #     valueMeasurements[i+1][4].append(value)
    #     timeMeasurements[i+1][4].append(time)
    # currentValues.append(value)
    # currentTimes.append(time)

def main():

    with open('config.json') as data_file:    
        config = json.load(data_file,'utf-8')
    
    fileLocation = str(config['filesBasePath'])
    edgesFileLocation = fileLocation + str(config['edgesFileName'])
    authorAndFieldFileLocation = fileLocation + str(config['authorIDandFieldFileName'])
    authorAndConfFileLocation = fileLocation + str(config['authorIDandConfFileName'])
    confsAndFieldsFileLocation = fileLocation + str(config['conferencesAndFieldsFilename'])
    authorsAndSen = fileLocation + str(config['authorsAndSeniorityFilename'])

    templateType = str(config['templateStructure'])
    repeatedSkillsInTemplate = bool(config['repeatedSkillsInTemplate'])
    manySkillsPerWorker = bool(config['manySkillsPerWorker'])
    useFields = bool(config['useFields'])

    print 'Reading edge list and creating G...'

    G = max(nx.connected_component_subgraphs(nx.read_edgelist(edgesFileLocation)),key=len)
    print 'Nodes: ',G.number_of_nodes()
    print 'Edges: ',G.number_of_edges()
        
    print 'Creating APSP aaaaand...',
    before = datetime.datetime.now()
    APSP = nx.all_pairs_shortest_path_length(G)
    print "Done. It took:", (datetime.datetime.now() - before).total_seconds(), "seconds."        

    print 'Calculating centrality'
    centralityDict = nx.closeness_centrality(G)

    print 'Calculating degrees'
    degreeDict = G.degree()

    # skillToWorkers contains a map of skill to person ids relative to it
    skillToWorkers= defaultdict(list)
    skills = set()
    confToFieldMapping = dict()
    # with open(confsAndFieldsFileLocation) as tsv:
    #     for line in csv.reader(tsv, delimiter =' '):
    #         confName = line[0]
    #         fieldName = line[1]
    #         if useFields:
    #             skills.add(fieldName)
    #         else:
    #             skills.add(confName)
    #         confToFieldMapping[confName]=fieldName
    if fileLocation.find('movies')>-1:
        dlmtr = ','
    else:
        dlmtr = ' '
    print 'Assigning skills to workers...'
    with open(authorAndFieldFileLocation) as tsv:
        for line in csv.reader(tsv,delimiter=dlmtr):
            workerID = line[0]
            authorSkills = line[1:]
            if manySkillsPerWorker:
                for s in authorSkills:
                    skills.add(s)
                    if G.has_node(workerID):
                        skillToWorkers[s].append(workerID)
            else:
                skills.add(authorSkills[0])
                if G.has_node(workerID):
                    skillToWorkers[authorSkills[0]].append(workerID)

    # print 'Matching seniority and workers'
    # seniorityToAuthor = defaultdict(list)
    # with open(authorsAndSen) as f:
    #     for line in f:
    #         t = line.split(' ')
    #         authorID = t[0]
    #         seniority = t[1]

    #         if seniority[-1] == "\n":
    #             seniority = seniority[:-1]

    #         if seniority not in seniorityToAuthor:
    #             seniorityToAuthor[seniority] = [authorID]
    #         else:
    #             seniorityToAuthor[seniority].append(authorID)
        
    # template = nx.DiGraph()
    # template.add_node(0)
    # randomSkill = random.sample(skills, 1)[0]
    # template.node[0]['skill'] = randomSkill
    # template.node[0]['seniority'] = "high"
    # remainingSkills = set(skills) - set([randomSkill])
    #print "Node Skill DPwithOverlapCheck_t DPwithOverlapCheck_v maxDegree_t maxDegree_v maxCentrality_t maxCentrality_v TopDown_t TopDown_v TopDownCheckAllForRoot_t TopDownCheckAllForRoot_v"
    #print "0", template.node[0]['skill']
    
    # candidatesDict = defaultdict(list)
    # for u in skillToWorkers[template.node[0]['skill']]:
    #     if u in set(seniorityToAuthor[template.node[0]['seniority']]) and u in APSP:
    #         candidatesDict[0].append(u)
    
    if not repeatedSkillsInTemplate:
        maxNodesInTemplate = len(skills)
    else:
        maxNodesInTemplate = 31
    valueSums = dict()
    timeSums = dict()
    templateSizes = range(2,maxNodesInTemplate+1)
    # for i in templateSizes:
    #     valueSums[i] = {
    #         'dp':0,
    #         'maxDeg':0,
    #         'maxCen':0,
    #         'topDown':0,
    #         'topDownPlus':0
    #     }
    #     timeSums[i] = {
    #         'dp':0,
    #         'maxDeg':0,
    #         'maxCen':0,
    #         'topDown':0,
    #         'topDownPlus':0
    #     }
    # 0:dp, 1:maxDeg, 2:maxCen, 3:topDown, 4:topDownPlus
    valueMeasurements = dict()
    timeMeasurements = dict()
    allSuccessfulValueMeasurements = dict()
    allSuccessfulTimeMeasurements = dict()
    failures = dict()
    for i in templateSizes:
        valueMeasurements[i] = dict()
        timeMeasurements[i] = dict()
        allSuccessfulValueMeasurements[i] = dict()
        allSuccessfulTimeMeasurements[i] = dict()
        failures[i] = dict()
        for j in range(0,5):
            valueMeasurements[i][j] = []
            timeMeasurements[i][j] = []
            allSuccessfulValueMeasurements[i][j] = []
            allSuccessfulTimeMeasurements[i][j] = []

    numIterations = 50
    for iteration in range(0,numIterations):
        print "iteration:",iteration
        template = nx.DiGraph()
        candidatesDict = dict()
        remainingSkills = list(skills)
        for i in range(0,maxNodesInTemplate):

            candidatesDict[i] = []  
            # Add node in template
            template = addNodeToTemplate(template,i,templateType)

            # Assign conference to new node.
            newNodeSkill = random.sample(remainingSkills, 1)[0]
            if not repeatedSkillsInTemplate:
                remainingSkills.remove(newNodeSkill)
                
            # if templateType == 'star' and i> 0:
            #     height = 1
            # elif templateType == 'star' and i == 0:
            #     height = 0
            # elif templateType == 'cbt':
            #     height = floor(log(i+1,2))

            # heightToSeniorityDict = {
            #     0:'high',
            #     1:'medium',
            #     2:'low',
            #     3:'low',
            #     4:'low'
            # }
            # newNodeSeniority = heightToSeniorityDict[height]
            template.node[i]['skill'] = newNodeSkill
            # template.node[j]['seniority'] = newNodeSeniority

            # Create candidate set for new node

            for u in skillToWorkers[template.node[i]['skill']]:
                if u in APSP: # and u in set(seniorityToAuthor[template.node[j]['seniority']]):
                    candidatesDict[i].append(u)
            
            # if there is only one node in template move to next iteration
            if i == 0:
                continue

            # Create ordering
            postOrdering = list(nx.dfs_postorder_nodes(template, 0))

            # Execute algorithms
            currentValues,currentTimes = runSingleIteration(candidatesDict,template,APSP,degreeDict,centralityDict,G)
            numberOfAlgs = len(currentValues)
            for x in range(0,numberOfAlgs):
                if currentValues[x] != None:
                    valueMeasurements[i+1][x].append(currentValues[x])
                timeMeasurements[i+1][x].append(currentTimes[x])

            if None not in currentValues:
                for x in range(0,numberOfAlgs): # for each algorithm
                    allSuccessfulValueMeasurements[i+1][x].append(currentValues[x])
                    allSuccessfulTimeMeasurements[i+1][x].append(currentTimes[x])

    for templateSize in valueMeasurements:
        for alg in valueMeasurements[templateSize]:
            measCount = len(valueMeasurements[templateSize][alg])
            iterationsMissing = numIterations - measCount
            measSum = sum(valueMeasurements[templateSize][alg])
            measAvg = measSum/float(measCount)
            valueMeasurements[templateSize][alg] = measAvg

            measCount = len(allSuccessfulValueMeasurements[templateSize][alg])
            measSum = sum(allSuccessfulValueMeasurements[templateSize][alg])
            measAvg = measSum/float(measCount)
            allSuccessfulValueMeasurements[templateSize][alg] = measAvg
            
            measCount = len(timeMeasurements[templateSize][alg])
            measSum = sum(timeMeasurements[templateSize][alg])
            measAvg = measSum/float(measCount)
            timeMeasurements[templateSize][alg] = measAvg

            measCount = len(allSuccessfulTimeMeasurements[templateSize][alg])
            measSum = sum(allSuccessfulTimeMeasurements[templateSize][alg])
            measAvg = measSum/float(measCount)
            allSuccessfulTimeMeasurements[templateSize][alg] = measAvg
            
            failures[templateSize][alg] = iterationsMissing / float(numIterations)

    xaxis = templateSizes
    name = ''
    if manySkillsPerWorker:
        name += 'm'
    else:
        name += 's'
    name +='ot'
    if repeatedSkillsInTemplate:
        name += 'r_'
    else:
        name += 'u_'
    name += templateType
    with open(name + '_all_values.txt','w') as f:
        for templateSize in valueMeasurements:
            f.write(str(templateSize))
            for alg in valueMeasurements[templateSize]:
                f.write(" "+str(valueMeasurements[templateSize][alg]))
            f.write('\n')
    with open(name + '_all_times.txt','w') as f:
        for templateSize in timeMeasurements:
            f.write(str(templateSize))
            for alg in timeMeasurements[templateSize]:
                f.write(" "+str(timeMeasurements[templateSize][alg]))
            f.write('\n')
    with open(name + '_allSuccessful_values.txt','w') as f:
        for templateSize in allSuccessfulValueMeasurements:
            f.write(str(templateSize))
            for alg in allSuccessfulValueMeasurements[templateSize]:
                f.write(" "+str(allSuccessfulValueMeasurements[templateSize][alg]))
            f.write('\n')
    with open(name + '_allSuccessful_times.txt','w') as f:
        for templateSize in allSuccessfulTimeMeasurements:
            f.write(str(templateSize))
            for alg in allSuccessfulTimeMeasurements[templateSize]:
                f.write(" "+str(allSuccessfulTimeMeasurements[templateSize][alg]))
            f.write('\n')
    with open('failures.txt','w') as f:
        for templateSize in failures:
            f.write(str(templateSize))
            for alg in failures[templateSize]:
                f.write(" "+str(failures[templateSize][alg]))
            f.write('\n')
    with open('stats.txt','w') as f:
        f.write('candidates per skill\n')
        for k in skillToWorkers:
            f.write(k +" "+str(len([x for x in skillToWorkers[k] if x in APSP]))+'\n')
        f.write('\nNodes in APSP:' + str(len(APSP)) + '\n')
        f.write('Nodes in G:' + str(G.number_of_nodes()) + '\n')
        f.write('Edges in G:' + str(G.number_of_edges()) + '\n')
        f.write('Iterations: '+str(numIterations))
    

    # with open(str(name)+'_values.txt','w') as f:
    #     for i in valueSums:
    #         f.write(str(i) + "," + str(valueSums[i]['dp']) + "," + str(valueSums[i]['maxDeg']) + "," + str(valueSums[i]['maxCen']) + "," + str(valueSums[i]['topDown']) + "," + str(valueSums[i]['topDownPlus']))
    #         f.write('\n')

    # with open(str(name)+'_times.txt','w') as f:
    #     for i in timeSums:
    #         f.write(str(i) + "," + str(timeSums[i]['dp']) + "," + str(timeSums[i]['maxDeg']) + "," + str(timeSums[i]['maxCen']) + "," + str(timeSums[i]['topDown']) + "," + str(timeSums[i]['topDownPlus']))
    #         f.write('\n')

if __name__ == "__main__":
    main()
