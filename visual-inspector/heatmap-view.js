function smart_text_fit(text_tags)
{
    const padding = 6;
    const line_height = 7;

    text_tags.each(function () {
        let text = d3.select(this);
        let content = text.text();
        let cx = parseFloat(text.attr("x"));
        let cy = parseFloat(text.attr("y"));
        let width = parseFloat(text.attr("box_width"));
        let height = parseFloat(text.attr("box_height"));

        if (height > width)
        {
            text.attr("transform", `rotate(-90, ${cx}, ${cy})`);
            [width, height] = [height, width]
        }

        if ((height < 13) || (width < 21))
        {
            text.text(null);
            return;
        }

        if (text.node().getComputedTextLength() >= (width - padding))
        {
            text.classed("small-label", false)
                .classed("xsmall-label", true);
            if (text.node().getComputedTextLength() >= (width - padding))
            {
                let options = shorter_names(content);
                while (opt = options.shift())
                {
                    text.text(opt);
                    if (text.node().getComputedTextLength() <= (width - padding))
                    {
                        return;
                    }
                }
                text.text(null);
            }
        }
    });
}

function render_heatmap(data)
{
    let svg = d3.select("svg");
    const width = svg.attr("width");
    const height = svg.attr("height");

    let root = d3.hierarchy(data)
        .sum(d => Math.max(d.value, 3))
        .sort((a, b) => b.data.temperature - a.data.temperature);

    let thermal_set = new Set(Array.from(root.leaves(), d => d.data.temperature ));
    let thermal_scale = Array.from(thermal_set).sort((a,b) => b-a)
    let legend_box_width = 60
    let legend_box_height = height / thermal_scale.length
    let color = d3.scaleSequential(d3.interpolateTurbo)
        .domain([-0.125*thermal_scale[0], 1.25*thermal_scale[0]]);  // Leave off the edges of the scale

    // legend
    let legend = svg.append("g")
    legend.selectAll('rect')
        .data(thermal_scale)
        .enter()
            .append('rect')
            .style('fill', d => color(d))
            .attr('rx', 1.5)
            .attr('x', width - legend_box_width + 8)
            .attr('y', (d,i) => i*legend_box_height)
            .attr('width', legend_box_width-16)
            .attr('height', legend_box_height-2);
    legend.selectAll('text')
        .data(thermal_scale)
        .enter()
            .append('text')
            .attr("class", "xsmall-label")
            .attr('x', width - legend_box_width + 10 + (legend_box_width-16)/2)
            .attr('y', (d,i) => (legend_box_height/2) + i*legend_box_height)
            .attr('dy', 2.8)
            .text(function (d) {return `${d} °`})

    // heatmap
    d3.treemap()
        .size([width - legend_box_width, height])
        .tile(d3.treemapBinary)
        .round(true)
        .paddingInner(1.8)
        (root);

    let files = svg.append("g")
    files.selectAll("rect")
        .data(root.leaves())
        .enter()
        .append("rect")
            .attr("class", "node")
            .style("fill", d => color(d.data.temperature))
            .attr('rx', d => 1.8)
            .attr('x', d => d.x0)
            .attr('y', d => d.y0)
            .attr('width', d => d.x1-d.x0)
            .attr('height', d => d.y1-d.y0)
            .on("click", function(d) {
                update_info_view(d);
                d3.event.stopPropagation();
            });

    files.selectAll("text")
        .data(root.leaves())
        .enter()
        .append("text")
            .attr("class","small-label")
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
