function natural_split(text)
{
    const caseChanged = (string) => /[a-z][A-Z]/.test(string)

    parts = []
    points = []
    last = 0

    for (i = 1; i < text.length; i++)
    {
        if (caseChanged(text.slice(i-1,i+1)))
        {
            points.push(i-last)
            last = i
        }
        else if (/[-_\.]/.test(text.slice(i,i+1))) {
            points.push(i-last)
            last = i
        }
    }
    points.push(text.length)

    while (pos = points.shift())
    {
        parts.push(text.slice(0, pos))
        text = text.slice(pos)
    }

    return parts
}

function smart_text_fit(text_tags)
{
    const padding = 8
    text_tags.each(function () {
        let text = d3.select(this);
        let content = text.text()
        let cx = parseFloat(text.attr("x"));
        let cy = parseFloat(text.attr("y"));
        let width = parseFloat(text.attr("box_width"));
        let height = parseFloat(text.attr("box_height"));

        if (height > width)
        {
            text.attr("transform", `rotate(-90, ${cx}, ${cy})`);
            [width, height] = [height, width]
        }

        if (text.node().getComputedTextLength() >= (width - padding)
            || (height < 20))
        {
            text.classed("small-label", false)
                .classed("xsmall-label", true);

            if (text.node().getComputedTextLength() >= (width - padding))
            {
                lines = natural_split(content)
                line_height = 7;
                if (lines.length*line_height < (height - padding))
                {
                    half = lines.length/2;
                    top_dy = -line_height*half + 2.9;
                    bottom_dy = line_height*half + 2.9;
                    line_ys = d3.scaleLinear()
                        .domain([0, lines.length-1])
                        .range([top_dy, bottom_dy]);

                    text.text(null);
                    lines.forEach( function(line,i) {
                        text.append("tspan")
                            .attr("x", cx)
                            .attr("y", cy)
                            .attr("dy", line_ys(i))
                            .text(line);
                    });
                }
                // again, if it does not fit, give up
                if (text.node().getComputedTextLength() >= (width - padding))
                {
                    text.text("···");  // last resort
                }
            }
        }
    });
}

function render_heatmap(data)
{
    var margin = {
            top: 10,
            right: 10,
            bottom: 10,
            left: 10
        }
    let svg = d3.select("svg"),
        g = svg.append("g")
    let width = svg.attr("width");
    let height = svg.attr("height");

    let root = d3.hierarchy(data)
        .sum(function(d) { return d.value+13; })

    let thermal_set = new Set(Array.from(root.leaves(), d => d.data.temperature ));
    let thermal_scale = Array.from(thermal_set).sort((a,b) => b-a)
    let legend_box_height = height / thermal_scale.length
    let color = d3.scaleSequential(d3.interpolateTurbo)
        .domain([-0.125*thermal_scale[0], 1.25*thermal_scale[0]]);  // Leave off the edges of the scale

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
            .attr("class", "xsmall-label")
            .attr('x', 40)
            .attr('y', (d,i) => (legend_box_height/2) + i*legend_box_height)
            .attr('dy', 2.9)
            .text(function (d) {return `${d} °`})

    d3.treemap()
        .size([width, height])
        .tile(d3.treemapResquarify)
        .padding(1)
        (root);

    let squares = svg.selectAll("rect")
        .data(root.leaves())
        .enter()
        .append("rect")
            .style("fill", d => color(d.data.temperature))
            .attr('x', d => d.x0)
            .attr('y', d => d.y0)
            .attr('width', d => d.x1-d.x0)
            .attr('height', d => d.y1-d.y0);

    svg
        .selectAll("text")
        .data(root.leaves())
        .enter()
        .append("text")
            .classed("small-label", true)
            .attr("x", d => d.x0 + (d.x1-d.x0)/2)
            .attr("y", d => 2 + d.y0 + (d.y1-d.y0)/2)
            .attr('dy', 2)
            .attr("box_width",  d => d.x1 - d.x0)
            .attr("box_height", d => d.y1 - d.y0)
            .text(d => d.data.name)
        .call(smart_text_fit);
}

function render_heatmap_view()
{
    let svg = create_svg_element(768, 768);
    let json_url = project_selector.val();

    graphic_view.empty();
    graphic_view.append(svg);

    d3.json(json_url).then( function (data) {
        render_heatmap(data);
    });
}
