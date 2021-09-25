function limit_name(name, limit=30)
{
    if (name.length < limit)
        return name;

    let options = shorter_names(name);
    while (opt = options.shift())
    {
        if (opt.length < limit)
        {
            return opt;
        }
    }
    return name.slice(0, limit);
}

function render_sunburst(data)
{
    let svg = d3.select("svg");
    const width = svg.attr("width");
    const height = svg.attr("height");
    const radius = width / 6;

    const arcFactory = d3.arc()
        .startAngle(d => d.x0)
        .endAngle(d => d.x1)
        .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005))
        .padRadius(radius * 1.5)
        .innerRadius(d => d.y0 * radius)
        .outerRadius(d => Math.max(d.y0 * radius, d.y1 * radius - 1));

    svg.attr("viewBox", [0, 0, width, height])
        .style("font", "9px sans-serif");

    let root_data = d3.hierarchy(data)
        .sum(d => d.value)
        .sort((a, b) => b.value - a.value);
    root = d3.partition()
        .size([2 * Math.PI, root_data.height+1])
        (root_data);
    root.each(d => d.current = d);

    const colorScale = d3.scaleOrdinal(
        d3.quantize(d3.interpolateTurbo, Math.min(root_data.leaves().length, 21))
    );

    let group = svg.append("g").attr("transform", `translate(${width / 2},${width / 2})`);
    let items = group.append("g")
        .selectAll("path")
        .data(root.descendants().slice(1))
        .join("path")
            .attr("fill", d => colorScale(d.data.easy_path))
            .attr("fill-opacity", d => arcVisible(d.current) ? (d.children ? 0.6 : 0.4) : 0)
            .attr("d", d => arcFactory(d.current));

    items.filter(d => d.children)
        .style("cursor", "pointer")
        .on("click", clicked);

    items.filter(d => !d.children)
        .style("cursor", "pointer")
        .on("click", d => update_info_view(d));

    items.append("title")
            .text(d => `${d.data.easy_path}\n${d.value.toLocaleString()}`);

    const label = group.append("g")
        .attr("pointer-events", "none")
        .attr("text-anchor", "middle")
        .style("user-select", "none")
        .selectAll("text")
        .data(root.descendants().slice(1))
        .join("text")
        .attr("dy", "0.35em")
        .attr("fill-opacity", d => +labelVisible(d.current))
        .attr("transform", d => labelTransform(d.current))
        .text(d => limit_name(d.data.name));

    const parent = group.append("circle")
        .datum(root)
        .attr("r", radius)
        .attr("fill", "none")
        .attr("pointer-events", "all")
        .on("click", clicked);

    update_info_view(root);

    function clicked(p)
    {
        parent.datum(p.parent || root);

        update_info_view(p);

        root.each(d => d.target = {
            x0: Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
            x1: Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
            y0: Math.max(0, d.y0 - p.depth),
            y1: Math.max(0, d.y1 - p.depth)
        });

        const t = group.transition().duration(750);

        // Transition the data on all arcs, even the ones that aren’t visible,
        // so that if this transition is interrupted, entering arcs will start
        // the next transition from the desired position.
        items.transition(t)
            .tween("data", d => {
                const i = d3.interpolate(d.current, d.target);
                return t => d.current = i(t);
            })
            .filter(function(d) {
                return +this.getAttribute("fill-opacity") || arcVisible(d.target);
            })
            .attr("fill-opacity", d => arcVisible(d.target) ? (d.children ? 0.6 : 0.4) : 0)
            .attrTween("d", d => () => arcFactory(d.current));

        label.filter(function(d) {
                return +this.getAttribute("fill-opacity") || labelVisible(d.target);
            }).transition(t)
            .attr("fill-opacity", d => +labelVisible(d.target))
            .attrTween("transform", d => () => labelTransform(d.current));
    }

    function arcVisible(d)
    {
        return d.y1 <= 3 && d.y0 >= 1 && d.x1 > d.x0;
    }

    function labelVisible(d)
    {
        return d.y1 <= 3 && d.y0 >= 1 && (d.y1 - d.y0) * (d.x1 - d.x0) > 0.03;
    }

    function labelTransform(d) {
        const x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
        const y = (d.y0 + d.y1) / 2 * radius;
        return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`;
    }
}

function render_sunburst_view()
{
    let svg = create_svg_element(768, 768);
    let json_url = project_selector.val();

    graphic_view.empty();
    graphic_view.append(svg);

    d3.json(json_url).then( function (data) {
        render_sunburst(data);
    });
}
