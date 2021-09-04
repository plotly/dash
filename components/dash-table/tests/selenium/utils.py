from datetime import date, timedelta

read_write_modes = [dict(virtualization=False), dict(virtualization=True)]
basic_modes = read_write_modes + [dict(editable=False)]


def generate_markdown_mock_data(rows=100):
    return dict(
        columns=[
            dict(id="markdown-headers", name=["", "Headers"], presentation="markdown"),
            dict(
                id="markdown-italics",
                name=["Emphasis", "Italics"],
                presentation="markdown",
            ),
            dict(id="markdown-links", name=["", "Links"], presentation="markdown"),
            dict(id="markdown-lists", name=["", "Lists"], presentation="markdown"),
            dict(id="markdown-tables", name=["", "Tables"], presentation="markdown"),
            dict(id="markdown-quotes", name=["", "Quotes"], presentation="markdown"),
            dict(
                id="markdown-inline-code",
                name=["", "Inline code"],
                presentation="markdown",
            ),
            dict(
                id="markdown-code-blocks",
                name=["", "Code blocks"],
                presentation="markdown",
            ),
            dict(id="markdown-images", name=["", "Images"], presentation="markdown"),
        ],
        data=[
            {
                "markdown-headers": "{0} row {1}".format("#" * (i % 6), i),
                "markdown-italics": "{0}{1}{0}".format("*" if i % 2 == 1 else "_", i),
                "markdown-links": "[Learn about {0}](http://en.wikipedia.org/wiki/{0})".format(
                    i
                ),
                "markdown-lists": """1. Row number {0}
                    - subitem {0}
                      - subsubitem {0}
                    - subitem two {0}
                2. Next row {1}""".format(
                    i, i + 1
                ),
                "markdown-tables": """Current | Next
                    --- | ---
                    {0} | {1}""".format(
                    i, i + 1
                ),
                "markdown-quotes": "> A quote for row number {0}".format(i),
                "markdown-inline-code": "This is row `{0}` in this table.".format(i),
                "markdown-code-blocks": """```python
                    def hello_table(i={0}):
                        print("hello, " + i)
                """.format(
                    i
                ),
                "markdown-images": "![image {0} alt text](assets/logo.png)".format(i),
            }
            for i in range(rows)
        ],
    )


def generate_mixed_markdown_data(rows=100):
    return dict(
        columns=[
            dict(id="not-markdown-column", name=["Not Markdown"], editable=True),
            dict(
                id="markdown-column",
                name=["Markdown"],
                type="text",
                presentation="markdown",
            ),
            dict(
                id="also-not-markdown-column",
                name=["Also Not Markdown"],
                editable=False,
            ),
            dict(
                id="also-also-not-markdown-column",
                name=["Also Also Not Markdown"],
                editable=True,
            ),
        ],
        data=[
            {
                "not-markdown-column": "this is not a markdown cell",
                "markdown-column": """```javascript
console.warn("this is a markdown cell")
```"""
                if i % 2 == 0
                else """```javascript
console.log("logging things")
console.warn("this is a markdown cell")
```""",
                "also-not-markdown-column": i,
                "also-also-not-markdown-column": "this is also also not a markdown cell",
            }
            for i in range(rows)
        ],
    )


def generate_mock_data(rows=100):
    return dict(
        columns=[
            dict(id="rows", type="numeric", editable=False),
            dict(
                id="ccc",
                name=["City", "Canada", "Toronto"],
                type="numeric",
            ),
            dict(
                id="ddd",
                name=["City", "Canada", "Montréal"],
                type="numeric",
            ),
            dict(
                id="eee",
                name=["City", "America", "New York City"],
                type="numeric",
            ),
            dict(
                id="fff",
                name=["City", "America", "Boston"],
                type="numeric",
            ),
            dict(
                id="ggg",
                name=["City", "France", "Paris"],
                type="numeric",
            ),
            dict(
                id="bbb",
                name=["", "Weather", "Climate"],
                type="text",
                presentation="dropdown",
            ),
            dict(
                id="bbb-readonly",
                name=["", "Weather", "Climate-RO"],
                type="text",
                editable=False,
                presentation="dropdown",
            ),
            dict(id="aaa", name=["", "Weather", "Temperature"], type="numeric"),
            dict(
                id="aaa-readonly",
                name=["", "Weather", "Temperature-RO"],
                type="numeric",
                editable=False,
            ),
        ],
        data=[
            {
                "rows": i,
                "ccc": i,
                "ddd": i,
                "eee": i,
                "fff": i + 1,
                "ggg": i * 10,
                "bbb": ["Humid", "Wet", "Snowy", "Tropical Beaches"][i % 4],
                "bbb-readonly": ["Humid", "Wet", "Snowy", "Tropical Beaches"][i % 4],
                "aaa": i + 1,
                "aaa-readonly": i + 1,
            }
            for i in range(rows)
        ],
        dropdown={
            "bbb": dict(
                clearable=True,
                options=[
                    dict(label="label {}".format(i), value=i)
                    for i in ["Humid", "Wet", "Snowy", "Tropical Beaches"]
                ],
            ),
            "bbb-readonly": dict(
                clearable=True,
                options=[
                    dict(label="label {}".format(i), value=i)
                    for i in ["Humid", "Wet", "Snowy", "Tropical Beaches"]
                ],
            ),
        },
        style_cell_conditional=[
            {
                "if": dict(
                    column_id="rows",
                ),
                "maxWidth": 60,
                "minWidth": 60,
                "width": 60,
            },
            {
                "if": dict(
                    column_id="bbb",
                ),
                "maxWidth": 200,
                "minWidth": 200,
                "width": 200,
            },
            {
                "if": dict(
                    column_id="bbb-readonly",
                ),
                "maxWidth": 200,
                "minWidth": 200,
                "width": 200,
            },
        ],
    )


def generate_mock_data_with_date(rows=100):
    props = generate_mock_data(rows)

    for c in props["columns"]:
        if c["id"] == "ccc":
            c.update(
                dict(
                    name=["Date", "only"],
                    type="datetime",
                    validation=dict(allow_YY=True),
                )
            )
        elif c["id"] == "ddd":
            c.update(dict(name=["Date", "with", "time"], type="datetime"))

    for i in range(len(props["data"])):
        d = props["data"][i]
        d["ccc"] = (date(2018, 1, 1) + timedelta(days=3 * i)).strftime("%Y-%m-%d")
        d["ddd"] = (date(2018, 1, 1) + timedelta(seconds=7211 * i)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return props


def get_props(rows=100, data_fn=generate_mock_data):
    mockProps = data_fn(rows)

    mockProps.update(
        dict(
            columns=[
                dict(
                    c,
                    name=c["name"] if "name" in c else c["id"],
                    on_change=dict(action="none"),
                    renamable=True,
                    deletable=True,
                )
                for c in mockProps["columns"]
            ]
        )
    )

    baseProps = dict(
        id="table",
        editable=True,
        page_action="none",
        style_table=dict(
            maxHeight="800px", height="800px", maxWidth="1000px", width="1000px"
        ),
        style_cell=dict(maxWidth=150, minWidth=150, width=150),
    )

    baseProps.update(mockProps)

    return baseProps
