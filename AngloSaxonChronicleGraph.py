
import nltk
from nltk import word_tokenize
from nltk import sent_tokenize
import spacy
import plotly
import plotly.graph_objects as go
import networkx as nx


txt_file = open("C:\\data\\anglo_saxon_chronicle_only.txt", "r")
file_content = txt_file.read()
#print("The file content are: ", file_content)

content_list = file_content
txt_file.close()

sentences = sent_tokenize(content_list)

# Tokenize each sentence into words: token_sentences
token_sentences = [word_tokenize(sent) for sent in sentences]

# Tag each tokenized sentence into parts of speech: pos_sentences
pos_sentences = [nltk.pos_tag(sent) for sent in token_sentences] 

# Create the named entity chunks: chunked_sentences
chunked_sentences = nltk.ne_chunk_sents(pos_sentences,binary=True)

# Instantiate the English model: nlp
nlp = spacy.load('en_core_web_trf')

by_years = [year.replace("\n", " ") for year in file_content.split("\n\n")]

def get_year (year_entry):
    if "A.D." in year_entry:
        ad_ix = year_entry.index("A.D.")
        return year_entry[ad_ix:year_entry.index(".", ad_ix+5)]
    else:
        return None

year_dict = dict([(get_year(entry) ,len(entry)) for entry in by_years])

import matplotlib.pyplot as plt


names = list(year_dict.keys())
values = list(year_dict.values())

plt.bar(range(len(year_dict)), values, tick_label=names)
plt.show()

docs = list(nlp.pipe(by_years))

people = []
people_dict = {}
year_dict = {}

DG = nx.DiGraph()

for doc in docs:
    year = get_year(doc.text)
    for ent in doc.ents:
           #print(ent.label_)
           if ent.label_ == "PERSON":
               ent_id = nlp.vocab.strings[ent.text]
               people_dict[ent.text] = ent
               
               
               if year in year_dict.keys():
                   year_dict[year].append(ent)
               else:
                    year_dict[year] =[ent]

for year in list(year_dict)[320:]:
    print(year)
    for person1 in list(year_dict[year]):
        DG.add_node(person1.text)
        for person2 in year_dict[year]:
            if person1.text != person2.text:
                DG.add_edge(person1.text, person2.text)

all_people = {}
other_prop_n = {}
black_list = ['Lady','Holy','New','Bishops','island',"Deus",'Christendom''Lady','May','earls','Earls','Queen','February','Exeter','Dover','Hexham','Emperor','dedit','Chester','Northumbria','Flanders','Jerusalem','Lincoln','January','Candlemas','East','West','South','Kent','Saxons','Glocester','thanes','May','Abbot','Archbishop','Angles','Pope','Bishop','Rome','Old','Isle','Wight','A.D.','August','King','July','heaven','Rochester','North', 'Pentecost', 'April','St.','earl','minster','Earl','Ethling','Anjou','Sandwidch','Michaelmas','England','Sunday','Wales','May',"Mercia",'Alderman','June','Lord', 'Nativity', 'Anglia', 'May', 'Almighty','September','November', 'Canterbury', 'Easter', 'October','York',]

places_file = open("C:\\data\\uk_places.txt", "r")
places_content = places_file.read()
places = []
for line in places_content.split("\n"):
    places.append(line);


for doc in docs:
    labels = {}
    for ent in doc.ents:
        labels[ent.text] = ent.label_
    for t in doc:
        if t.pos_ == "PROPN" and t.text not in black_list and t.text not in places:
            if t.text in labels:
                if t.text in other_prop_n:
                    other_prop_n[t.text] += 1
                else:
                    other_prop_n[t.text] = 1
            elif t.text in all_people:
               all_people[t.text] += 1
            else:
                all_people[t.text] = 1


            
import networkx as nx
import networkx as nx
G = nx.Graph()

more_than_10_keys = [key for key in all_people.keys() if all_people[key] >= 5]



weights = {}
for doc in docs:
    for s in doc.sents:
        people_in_year = []
        for t in doc:
            if t.text in more_than_10_keys and t.sent == s:
                people_in_year.append(t.text)
        #print(people_in_year)
        for p1 in people_in_year:
            if p1 not in G:
                #print(p1)
                G.add_node(p1)
            for p2 in people_in_year:
                if p1 != p2:
                    if (p1,p2) in weights:
                        weights[(p1,p2)] += 1
                    else:
                        weights[(p1,p2)] = 1
                    G.add_edge(p1,p2)
                    
                    
pos = nx.spring_layout(G)

edge_x = []
edge_y = []
weight_list = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]#G.nodes[edge[0]]['pos']
    x1, y1 = pos[edge[1]]#G.nodes[edge[1]]['pos']
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)
    weight_list.append(weights[(edge[0],edge[1])])
    
edge_traces =[]
for weight in set(weight_list):
    idxs = [i for i in range(0,len(weight_list)) if weight_list[i] == weight]
    for i in idxs:
        edge_traces.append( go.Scatter(
            x=edge_x[i:i+3], y=edge_y[i:i+3],
            line=dict(width=weight/3, color='#244145'),
            hoverinfo='none',
            mode='lines'))

node_x = []
node_y = []
colors = []
for node in G.nodes():
    x, y = pos[node] #G.nodes[node]['pos']
    node_x.append(x)
    node_y.append(y)
    colors.append('#c2cfd1')

Nodes = [comp for comp in nx.connected_components(G)] # Looks for the graph's communities
Edges = G.edges()
edge_weights = nx.get_edge_attributes(G,'weight')

labels = [] # names of the nodes to plot
group = [] # id of the communities
group_cnt = 0


node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    hoverinfo='text',
    #text=labels,
    marker=dict(
        showscale=False,
        # colorscale options
        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='YlGnBu',
        reversescale=True,
        color=[],
        size=10,
        line_width=2))

node_adjacencies = []
node_text = []
for node, adjacencies in enumerate(G.adjacency()):
    node_adjacencies.append(len(adjacencies[1]))
    node_text.append(adjacencies[0])
    #print(adjacencies)
    #print("test")

node_trace.marker.color = node_adjacencies
node_trace.text = node_text

all_traces = edge_traces
all_traces.append(node_trace)

fig = go.Figure(data=all_traces,
             layout=go.Layout(
                title='Most Mentioned People in the Anglo Saxon Chronicles',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                #annotations=[ dict(
                #    text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                #    showarrow=False,
                #    xref="paper", yref="paper",
                #    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

fig.update_layout(paper_bgcolor="#c7eded", plot_bgcolor="#c7eded")

fig.show()
 