from pyvis.network import Network
import networkx as nx
from rdflib import Graph

# Create a pyvis Network instance
nt = Network("500px", "500px")
n3_file = 'kbpedia_reference_concepts.n3'

g = Graph()
g.parse(n3_file, format='n3')
print('Parsed succesfully')
limit = 25
counter = 0

for subject, predicate, obj in g:
    # Add nodes (entities) and edges (relations)
    if counter > limit:
        break
    nt.add_node(subject)
    nt.add_node(obj)
    nt.add_edge(subject, obj, title=predicate)
    print (counter, subject, predicate, obj, something)
    counter += 1

# Save the pyvis visualization as an HTML file
filename = "kbpedia.html"
nt.write_html(filename)
