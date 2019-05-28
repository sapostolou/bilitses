import networkx as nx
import csv
import sys
import os
from collections import defaultdict
import random
random.seed()
import datetime
import json
from math import floor,log,ceil
from functions import validSolution, addNodeToTemplate, getBaseNameOfOutputFiles
from algorithms import DP,DPH,maxDegree,TopDown,TopDownCheckAllForRoot, rarestFirst

def runSingleIteration(candidatesDict,template, APSP, degreeDict, centralityDict, G):

    postOrdering = list(nx.dfs_postorder_nodes(template, 0))
    currentValues = []
    currentTimes = []

    for i in range(0,6):
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
        elif i == 5:
            value, solution = rarestFirst(candidatesDict, APSP)
        
        time = (datetime.datetime.now() - before).total_seconds()

        currentValues.append(value)
        currentTimes.append(time)
    
    return currentValues, currentTimes

def main():

    with open('config.json') as data_file:    
        config = json.load(data_file)
    
    fileLocation = os.path.abspath(str(config['filesBasePath']))
    edgesFileLocation = os.path.join(fileLocation,str(config['edgesFileName']))
    weightedEdges = bool(config['weighted'])

    authorData = json.load(open(os.path.join(fileLocation,str(config['workerData'])),'r'))

    print('Reading edge list and creating G...')

    if 'max_CCS' in edgesFileLocation:
        if weighted:
            G = nx.read_weighted_edgelist(edgesFileLocation)
        else:
            G = nx.read_edgelist(edgesFileLocation)
    else:
        if weighted:
            G = max(nx.connected_component_subgraphs(nx.read_weighted_edgelist(edgesFileLocation)),key=len)
            nx.write_weighted_edgelist(edgesFileLocation.rstrip('.txt') + '_max_CCS.txt')
        else:
            G = max(nx.connected_component_subgraphs(nx.read_edgelist(edgesFileLocation)),key=len)
            nx.write_edgelist(edgesFileLocation.rstrip('.txt') + '_max_CCS.txt')
    
    print('Nodes: ',G.number_of_nodes())
    print('Edges: ',G.number_of_edges())

    before = datetime.datetime.now()
    try:
        if weighted:
            APSP = json.load(open(os.path.join(fileLocation,'apsp_weighted.json'),'r'))
        else:
            APSP = json.load(open(os.path.join(fileLocation,'apsp.json'),'r'))
        print('apsp found')
    except FileNotFoundError:
        if weighted:
            APSP = dict(nx.all_pairs_djikstra(G))
        else:
            APSP = dict(nx.all_pairs_shortest_path_length(G))
        print('apsp created')
        json.dump(APSP,open(os.path.join(fileLocation,'apsp.json'),'w'))
    print("It took:", (datetime.datetime.now() - before).total_seconds(), "seconds.")     

    print('Calculating centrality')
    try:
        centralityDict = json.load(open(os.path.join(fileLocation,'centrality.json'),'r'))
    except FileNotFoundError:
        centralityDict = nx.closeness_centrality(G)
        json.dump(centralityDict,open(os.path.join(fileLocation,'centrality.json'),'w'))

    print('Calculating degrees')
    degreeDict = G.degree()

    # skillToWorkers contains a map of skill to person ids relative to it. used for creating the candidate sets
    skillToWorkers= defaultdict(list)
    skills = set()
    
    if fileLocation.find('movies')>-1:
        dlmtr = ','
    else:
        dlmtr = ' '

    # Assign skills to workers
    for a in authorData:
        if not G.has_node(a):
            continue

        if config['useFields']:
            di = authorData[a]['fields']
        else:
            di = authorData[a]['confs']

        sk = []
        if config['manySkillsPerWorker']:
            for s in di:
                sk.append(s)
        else:
            sk = [max(di.keys(), key=(lambda key: di[key]))]
        
        for s in sk:
            skillToWorkers[s].append(a)
            skills.add(s)
    
    if not config['repeatedSkillsInTemplate']:
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
        for j in range(0,6):
            valueMeasurements[i][j] = []
            timeMeasurements[i][j] = []
            allSuccessfulValueMeasurements[i][j] = []
            allSuccessfulTimeMeasurements[i][j] = []

    numIterations = int(config['numIterations'])
    for iteration in range(0,numIterations):
        print("iteration:",iteration)
        template = nx.DiGraph()
        candidatesDict = dict()
        remainingSkills = list(skills)
        for i in range(0,maxNodesInTemplate):

            candidatesDict[i] = []  
            # Add node in template
            template = addNodeToTemplate(template,i,config['templateStructure'])

            # Assign conference to new node.
            newNodeSkill = random.sample(remainingSkills, 1)[0]
            if not config['repeatedSkillsInTemplate']:
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
            iterationsMissing = numIterations - len(valueMeasurements[templateSize][alg])

            # Get averages
            valueMeasurements[templateSize][alg]                = sum(valueMeasurements[templateSize][alg])                 / float(len(valueMeasurements[templateSize][alg]))
            allSuccessfulValueMeasurements[templateSize][alg]   = sum(allSuccessfulValueMeasurements[templateSize][alg])    / float(len(allSuccessfulValueMeasurements[templateSize][alg]))
            timeMeasurements[templateSize][alg]                 = sum(timeMeasurements[templateSize][alg])                  / float(len(timeMeasurements[templateSize][alg]))
            allSuccessfulTimeMeasurements[templateSize][alg]    = sum(allSuccessfulTimeMeasurements[templateSize][alg])     / float(len(allSuccessfulTimeMeasurements[templateSize][alg]))
            
            failures[templateSize][alg] = iterationsMissing / float(numIterations)

    xaxis = templateSizes

    baseName = os.path.join(fileLocation,"results",getBaseNameOfOutputFiles(config['manySkillsPerWorker'], config['repeatedSkillsInTemplate'], config['templateStructure']))
    
    with open(baseName + '_all_values.txt','w') as f:
        for templateSize in valueMeasurements:
            f.write(str(templateSize))
            for alg in valueMeasurements[templateSize]:
                f.write(" "+str(valueMeasurements[templateSize][alg]))
            f.write('\n')
    with open(baseName + '_all_times.txt','w') as f:
        for templateSize in timeMeasurements:
            f.write(str(templateSize))
            for alg in timeMeasurements[templateSize]:
                f.write(" "+str(timeMeasurements[templateSize][alg]))
            f.write('\n')
    with open(baseName + '_allSuccessful_values.txt','w') as f:
        for templateSize in allSuccessfulValueMeasurements:
            f.write(str(templateSize))
            for alg in allSuccessfulValueMeasurements[templateSize]:
                f.write(" "+str(allSuccessfulValueMeasurements[templateSize][alg]))
            f.write('\n')
    with open(baseName + '_allSuccessful_times.txt','w') as f:
        for templateSize in allSuccessfulTimeMeasurements:
            f.write(str(templateSize))
            for alg in allSuccessfulTimeMeasurements[templateSize]:
                f.write(" "+str(allSuccessfulTimeMeasurements[templateSize][alg]))
            f.write('\n')
    with open(os.path.join(baseName,'failures.txt'),'w') as f:
        for templateSize in failures:
            f.write(str(templateSize))
            for alg in failures[templateSize]:
                f.write(" "+str(failures[templateSize][alg]))
            f.write('\n')
    with open(os.path.join(baseName,'stats.txt'),'w') as f:
        f.write('candidates per skill\n')
        for k in skillToWorkers:
            f.write(k +" "+str(len([x for x in skillToWorkers[k] if x in APSP]))+'\n')
        f.write('\nNodes in APSP:' + str(len(APSP)) + '\n')
        f.write('Nodes in G:' + str(G.number_of_nodes()) + '\n')
        f.write('Edges in G:' + str(G.number_of_edges()) + '\n')
        f.write('Iterations: '+str(numIterations))

if __name__ == "__main__":
    main()
