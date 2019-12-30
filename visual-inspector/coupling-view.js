function render_coupling(data)
{
    function full_id(node)
    {
        return `${node.parent ? full_id(node.parent) + "/" : ""}${node.data.name}`;
    }    
    function bilink(root)
    {
        const map = new Map(root.leaves().map(d => [full_id(d), d]));
        for (const d of root.leaves())
        {
            d.incoming = [];
            if (d.data.meta.imports)
            {
                d.outgoing = d.data.meta.imports.map(i => [d, map.get(i)]);
            }
            else
            {
                d.outgoing = []
            }
        }

        for (const d of root.leaves())
        {
            for (const o of d.outgoing)
            {
                o[1].incoming.push(o);    
            }            
        }  
        return root;
    }
    function overed(d)
    {
        link.style("mix-blend-mode", null);
        d3.select(this).attr("font-weight", "bold");
        d3.selectAll(d.incoming.map(d => d.path)).attr("stroke", color_in).raise();
        d3.selectAll(d.incoming.map(([d]) => d.text)).attr("fill", color_in).attr("font-weight", "bold");
        d3.selectAll(d.outgoing.map(d => d.path)).attr("stroke", color_out).raise();
        d3.selectAll(d.outgoing.map(([, d]) => d.text)).attr("fill", color_out).attr("font-weight", "bold");
    }

    function outed(d)
    {
        link.style("mix-blend-mode", "multiply");
        d3.select(this).attr("font-weight", null);
        d3.selectAll(d.incoming.map(d => d.path)).attr("stroke", null);
        d3.selectAll(d.incoming.map(([d]) => d.text)).attr("fill", null).attr("font-weight", null);
        d3.selectAll(d.outgoing.map(d => d.path)).attr("stroke", null);
        d3.selectAll(d.outgoing.map(([, d]) => d.text)).attr("fill", null).attr("font-weight", null);
    }

    let svg = d3.select("svg");
    let width = svg.attr("width");
    let radius =  width / 2;
    svg.attr("viewBox", [-width / 2, -width / 2, width, width]);

    tree = d3.cluster()
        .size([2 * Math.PI, radius - 100])

    line = d3.lineRadial()
        .curve(d3.curveBundle.beta(0.85))
        .radius(d => d.y)
        .angle(d => d.x);

    let color_none = "#ccc";
    let color_out = "#f00";
    let color_in = "#00f";

    const root = tree(bilink(d3.hierarchy(data)));
    const node = svg.append("g")
        .attr("font-family", "sans-serif")
        .attr("font-size", 8)
        .selectAll("g")
        .data(root.leaves())
        .join("g")
            .attr("transform", d => `rotate(${d.x * 180 / Math.PI - 90}) translate(${d.y},0)`)
        .append("text")
            .attr("dy", "0.31em")
            .attr("x", d => d.x < Math.PI ? 6 : -6)
            .attr("text-anchor", d => d.x < Math.PI ? "start" : "end")
            .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
            .text(d => d.data.name)
            .each(function(d) { d.text = this; })
            .on("mouseover", overed)
            .on("mouseout", outed)
            .call(text => text.append("title").text(d => `${full_id(d)}
                ${d.outgoing.length} outgoing
                ${d.incoming.length} incoming`));

    const link = svg.append("g")
        .attr("stroke", color_none)
        .attr("fill", "none")
        .selectAll("path")
        .data(root.leaves().flatMap(leaf => leaf.outgoing))
        .join("path")
            .style("mix-blend-mode", "multiply")
            .attr("d", ([i, o]) => line(i.path(o)))
            .each(function(d) { d.path = this; });
}

function render_coupling_view()
{
    let svg = create_svg_element(768, 768);
    let json_url = project_selector.val();

    graphic_view.empty();
    graphic_view.append(svg);

    d3.json(json_url).then( function (data) {
        render_coupling(data);
    });
}
