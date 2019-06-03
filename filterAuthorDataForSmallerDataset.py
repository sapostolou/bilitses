import networkx as nx
import json
with open('../datasets/academic_small/authorData.json','r') as f:
    authorData = json.load(f)

G = nx.read_edgelist('../datasets/academic_small/edges_unweighted.txt')

authorDataSmall = authorData.copy()

for a in authorData:
    if a not in G:
        del authorDataSmall[a]

with open('../datasets/academic_small/authorData_small.json','w') as f:
    json.dump(authorDataSmall,f)