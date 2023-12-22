// initialize global variables.
var edges;
var nodes;
var allNodes;
var allEdges;
var nodeColors;
var originalNodes;
var network;
var container;
var options, data;
var filter = {
    item: '',
    property: '',
    value: []
};





// This method is responsible for drawing the graph, returns the drawn network
function drawGraph() {
    var container = document.getElementById('mynetwork');



    // parsing and collecting nodes and edges from the python
    nodes = new vis.DataSet([{ "color": "#00FF00", "id": "Dam", "label": "Dam", "shape": "circle" }, { "color": "#00FF00", "id": "Stream", "label": "Stream", "shape": "circle" }, { "color": "#00FF00", "id": "Flood", "label": "Flood", "shape": "circle" }]);
    edges = new vis.DataSet([{ "arrows": "to", "from": "Dam", "label": "subclass of", "title": "subclass of", "to": "Stream" }, { "arrows": "to", "from": "Dam", "label": "use", "title": "use", "to": "Flood" }, { "arrows": "to", "from": "Dam", "label": "has effect", "title": "has effect", "to": "Flood" }]);

    nodeColors = {};
    allNodes = nodes.get({ returnType: "Object" });
    for (nodeId in allNodes) {
        nodeColors[nodeId] = allNodes[nodeId].color;
    }
    allEdges = edges.get({ returnType: "Object" });
    // adding nodes and edges to the graph
    data = { nodes: nodes, edges: edges };

    var options = {
        "configure": {
            "enabled": false
        },
        "edges": {
            "color": {
                "inherit": true
            },
            "smooth": {
                "enabled": true,
                "type": "dynamic"
            }
        },
        "interaction": {
            "dragNodes": true,
            "hideEdgesOnDrag": false,
            "hideNodesOnDrag": false
        },
        "physics": {
            "enabled": true,
            "repulsion": {
                "centralGravity": 0.2,
                "damping": 0.09,
                "nodeDistance": 200,
                "springConstant": 0.05,
                "springLength": 200
            },
            "solver": "repulsion",
            "stabilization": {
                "enabled": true,
                "fit": true,
                "iterations": 1000,
                "onlyDynamicEdges": false,
                "updateInterval": 50
            }
        }
    };






    network = new vis.Network(container, data, options);










    return network;

}

console.log('hello')
drawGraph();