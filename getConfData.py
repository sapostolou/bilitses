import json
import networkx as nx
from collections import defaultdict

# ONLY FOR SOTU WITH CONFS  

basePath = '../datasets/academic_small/'

G = nx.read_edgelist(basePath + 'edges_unweighted.txt')

with open(basePath + 'authorData.json','r') as f:
    authorData = json.load(f)

skillsData = dict()

for a in authorData:
    if a not in G:
        continue
    
    confs = authorData[a]['confs']
    m = max(confs, key=confs.get)

    if m not in skillsData:
        skillsData[m] = {'count':1, 'sum':confs[m]}
    else:
        skillsData[m]['count'] += 1
        skillsData[m]['sum'] += confs[m]

for s in skillsData:
    skillsData[s]['avg'] = float(skillsData[s]['sum']) / skillsData[s]['count']
    del skillsData[s]['count']
    del skillsData[s]['sum']

with open(basePath + 'skillData.json','w') as f:
    json.dump(skillsData,f)