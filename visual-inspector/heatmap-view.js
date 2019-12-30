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
