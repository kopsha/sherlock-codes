function update_info_view(d)
{
    info_text = "<p>"
    info_text += d.data.name + "<hr>";

    if (d.children) {
        info_text += "source files: <b>" + d.data.counter.source_files + "</b><br>";
        info_text += "lines of code: <b>" + d.data.counter.sloc_count + "</b><br>";
        info_text += "risk messages: <b>" + d.data.counter.risks_count + "</b><br>";
        info_text += "aggregated complexity: <b>" + d.data.counter.value_count + "</b><br>";
    } else {
        info_text += "file type: <b>" + d.data.meta.type + "</b><br>";
        info_text += "lines of code: <b>" + d.data.meta.sloc + "</b><br>";
        info_text += "decision complexity: <b>" + d.data.meta.decision_complexity + "</b><br>";
        info_text += "nested complexity: <b>" + d.data.meta.nested_complexity + "</b><br>";
        if (d.data.meta.imports) {
            info_text += "imports:<br>"
            d.data.meta.imports.forEach( function (el) {
                info_text += el + "<br>";
            });
        }
        if (d.data.meta.libraries) {
            info_text += "uses:<br>"
            d.data.meta.libraries.forEach( function (el) {
                info_text += el + "<br>";
            });
        }
        info_text += "risks:<br>";
        d.data.meta.risks.forEach( function (el) {
            info_text += el + "<br>";
        });
    }
    info_text += "</p>"
    info_view.html( info_text );
}

function create_svg_element(s)
{
    let div= document.createElementNS('http://www.w3.org/1999/xhtml', 'div');
    div.innerHTML= '<svg xmlns="http://www.w3.org/2000/svg">'+s+'</svg>';
    let frag= document.createDocumentFragment();
    while (div.firstChild.firstChild)
        frag.appendChild(div.firstChild.firstChild);
    return frag;
}

function display_circlepack(data)
{
    let svg = d3.select("svg"),
        margin = 20,
        diameter = svg.attr("width"),
        g = svg.append("g").attr(
            "transform",
            "translate(" + diameter / 2 + "," + diameter / 2 + ")"
        );

    let color = d3.scaleLinear()
        .domain([-1, 13])
        .range(["hsl(150,80%,80%)", "hsl(300,52%,38%)"])
        .interpolate(d3.interpolateHcl);

    let pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    root = d3.hierarchy(data)
        .sum(function(d) { return d.value; })
        .sort(function(a, b) { return b.value - a.value; });

    let focus = root,
        nodes = pack(root).descendants(),
        view;
    update_info_view(root);

    let circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
            .attr("class", function(d) {
                return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root";
            })
            .style("fill", function(d) {
                return d.children ? color(d.depth) : null;
            })
            .on("click", function(d) {
                if (d.children) {
                    zoom(d);
                    update_info_view(d);
                }
                else {
                    zoom(d.parent);
                    update_info_view(d);
                }
                d3.event.stopPropagation();
            });

    let text = g.selectAll("text")
        .data(nodes)
        .enter().append("text")
            .attr("class", "label")
            .style("fill-opacity", function(d) {
                return d.parent === root ? 1 : 0.25;
            })
            .style("display", function(d) {
                return d.parent === root ? "inline" : "none";
            })
            .text(function(d) { return d.data.name; });

    let node = g.selectAll("circle,text");

    svg.style("background", color(-1))
        .on("click", function() { zoom(root); });

    zoomTo([root.x, root.y, root.r * 2 + margin]);

    function zoom(d) {
        let focus0 = focus; focus = d;

        let transition = d3.transition()
            .duration(d3.event.altKey ? 7500 : 750)
            .tween("zoom", function(d) {
                var i = d3.interpolateZoom(
                    view,
                    [focus.x, focus.y, focus.r * 2 + margin]
                );
                return function(t) { zoomTo(i(t)); };
            });

        transition.selectAll("text")
            .filter(function(d) {
                return d.parent === focus || this.style.display === "inline";
            })
            .style("fill-opacity", function(d) {
                return d.parent === focus ? 1 : 0.25;
            })
            .on("start", function(d) {
                if (d.parent === focus || d === focus) this.style.display = "inline";
            })
            .on("end", function(d) {
                if (d.parent !== focus && d !== focus) this.style.display = "none";
            });
    }

    function zoomTo(v)
    {
        let k = diameter / v[2]; view = v;
        node.attr("transform", function(d) {
            return "translate("
                + (d.x - v[0]) * k
                + "," + (d.y - v[1]) * k
                + ")";
        });
        circle.attr("r", function(d) { return d.r * k; });
    }
}

function display_change_heatmap(data)
{
    var margin = {
            top: 10,
            right: 10,
            bottom: 10,
            left: 10
        }
    let svg = d3.select("svg"),
        g = svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    let width = svg.attr("width");
    let height = svg.attr("height");

    let root = d3.hierarchy(data)
        .sum(function(d) { return d.value+13; })

    let thermal_set = new Set(Array.from(root.leaves(), d => d.data.temperature ));
    let thermal_scale = Array.from(thermal_set).sort((a,b) => b-a)
    let legend_box_height = height / thermal_scale.length
    let color = d3.scaleSequential(d3.interpolateTurbo)
        .domain([-3, thermal_scale[0] * 1.25]);    // Leave off the edges of the scale

    d3.select("#info_view").selectAll("*").remove()
    let legend_info = d3.select("#info_view").style("text-align", "left")
        .append("svg")
            .attr("width", 80)
            .attr("height", height);

    legend_info
        .selectAll()
        .data(thermal_scale)
        .enter()
            .append('rect')
            .style('fill', d => color(d))
            .attr('x', 10)
            .attr('y', (d,i) => i*legend_box_height)
            .attr('width', 60)
            .attr('height', legend_box_height-2);
    legend_info.selectAll('text')
        .data(thermal_scale)
        .enter()
            .append('text')
            .attr("class", "small-label")
            .attr('x', 40)
            .attr('y', (d,i) => (legend_box_height/2) + i*legend_box_height)
            .text(function (d) {return `${d} °`})

    d3.treemap()
        .size([width, height])
        .padding(1)
        (root);

    let squares = svg.selectAll("rect")
        .data(root.leaves())
        .enter()
        .append("rect")
            .style("fill", function(d) {
                return color((d.data.temperature) ? d.data.temperature : 1);
            })
            .attr('x', function(d) {
                return d.x0;
            })
            .attr('y', function(d) {
                return d.y0;
            })
            .attr('width', function(d) {
                return d.x1 - d.x0;
            })
            .attr('height', function(d) {
                return d.y1 - d.y0;
            });

    svg
        .selectAll("text")
        .data(root.leaves())
        .enter()
        .append("text")
        .attr("class", "small-label")
        .attr("x", function(d) { return d.x0 + (d.x1-d.x0)/2 })
        .attr("y", function(d) { return d.y0 + (d.y1-d.y0)/2 })
        .text(function(d) { return d.data.name })
        .attr("transform", function (d) {
            let w = d.x1 - d.x0;
            let h = d.y1 - d.y0;
            let x = d.x0 + w/2 
            let y = d.y0 + h/2 
            return (h > w) ? `rotate(-90, ${x}, ${y})` : `rotate(0, ${x}, ${y})`;
        });
}

function display_couplings(data)
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

function render_architecture_view()
{
    let url = project_selector.val();
    let svg_tag = create_svg_element('<svg width="768" height="768">');
    graphic_view.empty();
    graphic_view.append(svg_tag);
    d3.json(url).then( function (data) {
        console.log("The promised display_circlepack");
        display_circlepack(data);
    });
}

function render_heatmap_view()
{
    let url = project_selector.val();
    let svg_tag = create_svg_element('<svg width="768" height="768">');
    graphic_view.empty();
    graphic_view.append(svg_tag);
    d3.json(url).then( function (data) {
        console.log("The promised display_change_heatmap");
        display_change_heatmap(data);
    });
}

function render_coupling_view()
{
    let url = project_selector.val();
    let svg_tag = create_svg_element('<svg width="768" height="768">');
    graphic_view.empty();
    graphic_view.append(svg_tag);
    d3.json(url).then( function (data) {
        console.log("The promised display_couplings");
        display_couplings(data);
    });
}
