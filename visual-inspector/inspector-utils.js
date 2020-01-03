function filename(path) {
    return path.split("/").pop()
}

function shorter_names(text)
{
    const caseChanged = (string) => /[a-z][A-Z]/.test(string)
    const isSeparator = (string) => /[0-9_\-\.\+]/.test(string)

    points = []

    for (i = 1; i < text.length; i++)
    {
        if (caseChanged(text.slice(i-1,i+1)))
        {
            points.push(i)
        }
        else if (isSeparator(text.slice(i,i+1)))
        {
            points.push(i)
        }
    }

    options = []
    while (pos = points.pop())
    {
        options.push(text.slice(0, pos))
    }

    return options
}

function humanize_filesize(bytes, precision=1) {
        if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) return '-';
        var units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'];
        var number = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, Math.floor(number))).toFixed(precision) +  ' ' + units[number];
}

function table_from_array(data)
{
    let table = $('<table></table>');
    table.addClass('two-columns')
    $(data).each(function (i, rowData)
    {
        let row = $('<tr></tr>');
        $(rowData).each(function (j, cellData)
        {
            let cell = $(`<td>${cellData}</td>`);
            cell.addClass(1-j ? 'left-column' : 'right-column');
            row.append(cell);
        });
        table.append(row);
    });
    return table;
}

function update_info_view(d)
{
    info_view.empty();
    info_view.text(d.data.name);
    if (d.children)
    {
        info_view.append(table_from_array([
            ['files', d.data.counter.source_files.toLocaleString()],
            ['lines of code', d.data.counter.sloc_count.toLocaleString()],
            ['size', humanize_filesize(d.data.counter.bytes_count)],
            ['cognitive complexity', d.data.counter.value_count.toLocaleString()],
        ]));
    }
    else
    {
        info_view.append(table_from_array([
            ['lines of code', d.data.meta.sloc.toLocaleString()],
            ['blanks', d.data.meta.blank_lines.toLocaleString()],
            ['cognitive complexity', d.data.meta.cognitive_complexity.toLocaleString()],
        ]));

        if (d.data.meta.imports)
        {
            let import_table = [];
            for (const i of d.data.meta.imports)
            {
                import_table.push([filename(i), ''])
            }
            info_view.append("<p>couplings</p>");
            info_view.append(table_from_array(import_table));
        }
        if (d.data.meta.libraries)
        {
            let import_table = [];
            for (const i of d.data.meta.libraries)
            {
                import_table.push([filename(i), ''])
            }
            info_view.append("<p>external</p>");
            info_view.append(table_from_array(import_table));
        }
        if (d.data.meta.messages && d.data.meta.messages.length)
        {
            len = d.data.meta.messages.length * 2;
            content = d.data.meta.messages.join("\n");
            info_view.append("<p>messages</p>");
            info_view.append(`<textarea rows="${len}" cols="60" readonly>${content}</textarea>`);
        }
    }
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
