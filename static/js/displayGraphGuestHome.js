async function fetchDataAndCreateGraph(url) {
    let kb;

    try {
        const response = await axios.get(url);
        const entityKeys = Object.keys(response.data.entities);
        const relations = response.data.relations;
        kb = {
            entities: entityKeys,
            relations: relations
        };

        // Create the graph using kb
        var svg = d3.select("svg");

        // Define a 'g' element that will contain all graph elements
        var g = svg.append("g");

        // Define zoom behavior
        var zoom = d3.zoom()
            .scaleExtent([0.5, 5]) // Set the zoom scale limits
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            });

        // Apply zoom behavior to the SVG
        svg.call(zoom);

        // Create nodes for entities
        var nodes = kb.entities.map(function (entity) {
            return { id: entity, type: "entity" };
        });

        // Create links for relations
        var links = kb.relations.map(function (relation) {
            return {
                source: relation.head,
                target: relation.tail,
                type: relation.type
            };
        });

        var simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(function (d) { return d.id; }))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(350, 350));

        var link = g.selectAll(".link")
            .data(links)
            .enter().append("line")
            .attr("class", "link");

        // Add labels for links
        var linkLabel = g.selectAll(".link-label")
            .data(links)
            .enter().append("text")
            .attr("class", "link-label")
            .text(function (d) { return d.type; });

        var node = g.selectAll(".node")
            .data(nodes)
            .enter().append("circle")
            .attr("class", function (d) { return "node " + d.type; })
            .attr("r", 10);

        // Add labels for nodes
        var nodeLabel = g.selectAll(".node-label")
            .data(nodes)
            .enter().append("text")
            .attr("class", "node-label")
            .text(function (d) { return d.id; });

        // Define the drag behavior
        var drag = d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);

        // Apply the drag behavior to nodes
        node.call(drag);

        // Define drag event handlers
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        simulation.on("tick", function () {
            link
                .attr("x1", function (d) { return d.source.x; })
                .attr("y1", function (d) { return d.source.y; })
                .attr("x2", function (d) { return d.target.x; })
                .attr("y2", function (d) { return d.target.y; });

            node
                .attr("cx", function (d) { return d.x; })
                .attr("cy", function (d) { return d.y; });

            // Update positions of node labels
            nodeLabel
                .attr("x", function (d) { return d.x; })
                .attr("y", function (d) { return d.y; });

            // Update positions of link labels
            linkLabel
                .attr("x", function (d) { return (d.source.x + d.target.x) / 2; })
                .attr("y", function (d) { return (d.source.y + d.target.y) / 2; });
        });
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

document.addEventListener('DOMContentLoaded', function () {

    const guestKbContainer = document.querySelector('#guest-kb-list');
    const messageElement = document.querySelector('#select-kb-message');
    const svgContainer = document.querySelector('#svg-graph-container');
    let knowledgeBaseId = null; 

    guestKbContainer.addEventListener('click', function (e) {
        messageElement.style.display = 'none';
        const knowledgeBaseItem = e.target.closest('div.kb-item'); 

        if (knowledgeBaseItem) {
            knowledgeBaseId = knowledgeBaseItem.id;
            const url = `/api/knowledge-bases/${knowledgeBaseId}`;
            svgContainer.innerHTML = '';
            fetchDataAndCreateGraph(url);
        }
    });


});
