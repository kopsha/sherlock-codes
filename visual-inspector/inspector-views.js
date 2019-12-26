function update_info_view(d) {
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
            d.data.meta.imports.local.forEach( function (el) {
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

function create_svg_element(s) {
    let div= document.createElementNS('http://www.w3.org/1999/xhtml', 'div');
    div.innerHTML= '<svg xmlns="http://www.w3.org/2000/svg">'+s+'</svg>';
    let frag= document.createDocumentFragment();
    while (div.firstChild.firstChild)
        frag.appendChild(div.firstChild.firstChild);
    return frag;
}

function display_circlepack(data) {
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

    function zoomTo(v) {
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

function display_radialdendro(data) {
    let svg = d3.select("svg").style("box-sizing", "border-box"),
        margin = 20,
        diameter = svg.attr("width"),
        g = svg.append("g").attr(
            "transform",
            "translate(" + diameter / 2 + "," + diameter / 2 + ")"
        );

    let cluster = d3.cluster()
        .size([2 * Math.PI, diameter/4])
    const root = cluster(d3.hierarchy(data));
    update_info_view(root);

    let color = d3.scaleLinear()
        .domain([-1, 13])
        .range(["hsl(150,80%,80%)", "hsl(300,52%,38%)"])
        .interpolate(d3.interpolateHcl);

    const link = g.append("g")
        .attr("fill", "none")
        .attr("stroke", "#555")
        .attr("stroke-opacity", 0.4)
        .attr("stroke-width", 1.5)
    .selectAll("path")
    .data(root.links())
    .enter().append("path")
        .attr("d", d3.linkRadial()
            .angle(d => d.x)
            .radius(d => d.y));

    const node = g.append("g")
        .attr("stroke-linejoin", "round")
        .attr("stroke-width", 3)
    .selectAll("g")
    .data(root.descendants().reverse())
    .enter().append("g")
        .attr("transform", d => `
            rotate(${d.x * 180 / Math.PI - 90})
            translate(${d.y},0)
        `);

    node.append("circle")
        .attr("fill", d => d.children ? "#555" : "#999")
        .attr("r", d => d.data.value ? d.data.value/10 : 0 + 2);

    node.append("text")
        .attr("class", "label")
        .attr("dy", "0.31em")
        .attr("x", d => d.x < Math.PI === !d.children ? 6 : -6)
        .attr("text-anchor", d => d.x < Math.PI === !d.children ? "start" : 
        "end")
        .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
        .text(d => d.data.name)
        .filter(d => d.children)
        .clone(true).lower()
        .attr("stroke", "white");
}

function render_architecture_view() {
    let url = project_selector.val();
    let svg_tag = create_svg_element('<svg width="768" height="768">');
    graphic_view.empty();
    graphic_view.append(svg_tag);
    d3.json(url).then( function (data) {
        console.log("The promised display_circlepack");
        display_circlepack(data);
    });
}

function render_dependencies_view() {
    let url = project_selector.val();
    console.log(url, project_selector.val())
    let svg_tag = create_svg_element('<svg width="768" height="768">');
    graphic_view.empty();
    graphic_view.append(svg_tag);
    d3.json(url).then( function (data) {
        console.log("The promised display_radialdendro");
        display_radialdendro(data);
    });
}
