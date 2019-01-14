import networkx as nx
import csv
import sys
from collections import defaultdict
import random
random.seed()
import datetime
import json
from math import floor,log,ceil
from functions import validSolution, addNodeToTemplate
from algorithms import DP,DPH,maxDegree

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
    
    if not repeatedSkillsInTemplate:
        maxNodesInTemplate = len(skills)
    else:
        maxNodesInTemplate = 31
    valueSums = dict()
    timeSums = dict()
    templateSizes = range(2,maxNodesInTemplate+1)
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
                
            template.node[i]['skill'] = newNodeSkill

            # Create candidate set for new node

            for u in skillToWorkers[template.node[i]['skill']]:
                if u in APSP:
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

if __name__ == "__main__":
    main()
