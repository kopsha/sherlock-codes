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

function create_svg_element(width, height) {
    if (!graphic_view || !project_selector || !info_view)
    {
        throw "Cannot find graphic_view, project_selector and info_view; did you load the right templates?";
    }

    let svg_element = d3.create("svg")
        .attr('width', width)
        .attr('height', height);

    return svg_element.node();
}
