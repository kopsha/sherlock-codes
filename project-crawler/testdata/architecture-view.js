function render_architecture(data)
{
    let svg = d3.select("svg");
    let margin = 20;
    let diameter = Math.min(svg.attr("width"), svg.attr("height"));

    let g = svg.append("g").attr(
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

function render_architecture_view()
{
    let svg = create_svg_element(768, 768);
    let json_url = project_selector.val();

    graphic_view.empty();
    graphic_view.append(svg);

    d3.json(json_url).then( function (data) {
        render_architecture(data);
    });
}
