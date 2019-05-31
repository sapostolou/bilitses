from collections import Counter
import networkx as nx
from math import ceil
import os

def validSolution(solution, template, candidates, value, APSP):
    if solution == None:
        print('no solution found')
        return True
    numKeys = len(solution)
    if numKeys != template.number_of_nodes():
        print('not valid: template nodes missing from solution',solution)
        return False
    duplicates = [k for k,v in Counter(solution.values()).items() if v>1]
    if len(duplicates) > 0:
        print('not valid: duplicates found in solution',solution)
        return False
    for k in solution:
        if solution[k] not in candidates[k]:
            print('not valid: node assigned to position does not belong in candidate set')
            return False
    
    templateEdges = nx.bfs_edges(template,0)
    edgeWeightSum = 0
    for v,u in templateEdges:
        edgeWeightSum += APSP[solution[v]][solution[u]]
    if edgeWeightSum != value:
        print('not valid: actual value is different than reported')
        return False
    return True

def addNodeToTemplate(T, i, templateType):
    if templateType == 'star':
        if i == 0:
            T.add_node(0)
            return T
        T.add_edge(0, i)
    elif templateType == 'cbt':
        if i == 0:
            T.add_node(0)
            return T
        parent = ceil(float(i)/2) - 1
        T.add_edge(parent,i)
    return T
    
class Cell:
    def __init__(self, value, diction):
        self.v = value
        self.d = diction

def getBaseNameOfOutputFiles(manySkillsPerWorker, repeatedSkillsInTemplate, templateType):
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

    return name

def readWorkerDataFiles(G,config):

    workerDataFile = open(os.path.join(os.path.abspath(str(config['filesBasePath'])),str(config['workerData'])),'r')
    skillToWorkers= defaultdict(list)
    skills = set()

    # Assign skills to workers
    for line in workerDataFile:

        tokens = line.split(',')
        id = tokens[0]
        
        if not G.has_node(a):
            continue

        mostFrequentSkill = tokens[1]
        otherSkills = tokens[2:]

        skillToWorkers[mostFrequentSkill].append(id)
        skills.add(mostFrequentSkill)

        if config['manySkillsPerWorker']:
            for s in otherSkills:
                skillToWorkers[s].append(id)
                skills.add(s)
    close(workerDataFile)
    return skillToWorkers, skills