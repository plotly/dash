import React from 'react';
import {storiesOf} from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';
import {Presentation} from 'dash-table/components/Table/props';

interface ITest {
    name: string;
    props: any;
}

const setProps = () => {};

const columnFormats = [
    {id: 'a', name: 'MD render', presentation: Presentation.Markdown},
    {id: 'b', name: 'Description'}
];

const variants: ITest[] = [
    {
        name: '',
        props: {
            row_deletable: true,
            style_table: {
                maxWidth: '1000px',
                minWidth: '1000px',
                width: '1000px'
            }
        }
    },
    {
        name: ': fixed_columns',
        props: {
            row_deletable: true,
            fixed_columns: {headers: true},
            style_table: {
                maxWidth: '1000px',
                minWidth: '1000px',
                width: '1000px'
            }
        }
    },
    {
        name: ': fixed_rows',
        props: {
            row_deletable: true,
            fixed_rows: {headers: true},
            style_table: {
                maxWidth: '1000px',
                minWidth: '1000px',
                width: '1000px'
            }
        }
    },
    {
        name: ': fixed_columns & fixed_rows',
        props: {
            row_deletable: true,
            fixed_columns: {headers: true},
            fixed_rows: {headers: true},
            style_table: {
                maxWidth: '1000px',
                minWidth: '1000px',
                width: '1000px'
            }
        }
    }
];

const tests: any[] = [];

tests.push(
    <div>Links and images</div>,
    <DataTable
        setProps={setProps}
        data={[
            {
                a: '[Greatest website ever](http://plotly.com "Plotly site")',
                b: 'normal link with title'
            },
            {
                a: '![the github logo](https://github.githubassets.com/images/modules/logos_page/GitHub-Logo.png)',
                b: 'logo with alt text'
            }
        ]}
        columns={columnFormats}
        {...variants[0]}
    />
);

variants.forEach(variant => {
    const {name, props} = variant;

    tests.push(
        <div>{`Headers${name}`}</div>,
        <DataTable
            setProps={setProps}
            data={[
                {a: '# H1', b: 'header one'},
                {a: '## H2', b: 'header two'},
                {a: '### H3', b: 'header three'},
                {a: '#### H4', b: 'header four'},
                {a: '##### H5', b: 'header five'},
                {a: '###### H6', b: 'header six'}
            ]}
            columns={columnFormats}
            {...props}
        />,
        <div>{`Emphasis${name}`}</div>,
        <DataTable
            setProps={setProps}
            data={[
                {a: '*italics*', b: 'italics with stars'},
                {a: '_italics_', b: 'italics with underscores'},
                {a: '**bold**', b: 'bold with stars'},
                {a: '__bold__', b: 'bold with underscores'},
                {a: '~~strikethrough~~', b: 'strikethrough'},
                {
                    a: '**_~~emphasis bonanza~~_**',
                    b: 'everything all at once'
                }
            ]}
            columns={columnFormats}
            {...props}
        />,
        <div>{`Lists${name}`}</div>,
        <DataTable
            setProps={setProps}
            data={[
                {
                    a: '1. Ordered list\n  - with subitem\n    * and sub sub item\n  - and another subitem\n2. and another item',
                    b: 'ordered'
                },
                {
                    a: '* Unordered list\n  - with subitem\n    * and sub sub item\n  * and another subitem\n- and another item',
                    b: 'unordered'
                }
            ]}
            columns={columnFormats}
            {...props}
        />,
        <div>{`Syntax highlighting${name}`}</div>,
        <DataTable
            setProps={setProps}
            id='table'
            data={[
                {
                    a: [
                        '```plaintext',
                        'export default helloworld(){',
                        '  print("hello, world!")}',
                        '```'
                    ].join('\n'),
                    b: 'plaintext'
                },
                {
                    a: [
                        '```bash',
                        'ls -laR | grep .gz',
                        'find . -name "*.gz" | xargs pip install',
                        '```'
                    ].join('\n'),
                    b: 'bash'
                },
                {
                    a: [
                        '```css',
                        '#div-id { background-color: red; }',
                        '.item:not(.subitem)[data-type="text"] { font-size: 1.5rem; }',
                        '```'
                    ].join('\n'),
                    b: 'css'
                },
                {
                    a: [
                        '```html',
                        '<html>',
                        '  <body>',
                        '    <div>Hello World</div>',
                        '  </body>',
                        '</html>',
                        '```'
                    ].join('\n'),
                    b: 'html'
                },
                {
                    a: [
                        '```javascript',
                        'function getDate() {',
                        '  return new Date();',
                        '}',
                        '```'
                    ].join('\n'),
                    b: 'javascript'
                },
                {
                    a: ['```json', '{', '  "prop": "value"', '}', '```'].join(
                        '\n'
                    ),
                    b: 'json'
                },
                {
                    a: [
                        '```julia',
                        'function init(r)',
                        '  println("hello world")',
                        'end',
                        '```'
                    ].join('\n'),
                    b: 'julia'
                },
                {
                    a: ['```markdown', '# Hello', '## World', '```'].join('\n'),
                    b: 'markdown'
                },
                {
                    a: [
                        '```python',
                        'def hello_world():',
                        '  print("hello, world!")',
                        '```'
                    ].join('\n'),
                    b: 'code block with syntax highlighting'
                },
                {
                    a: ['```r', 'print("Hello World!")', '```'].join('\n'),
                    b: 'r'
                },
                {
                    a: ['```ruby', 'puts "Hello World"', '```'].join('\n'),
                    b: 'ruby'
                },
                {
                    a: [
                        '```shell',
                        '#!/bin/sh',
                        'echo "Hello world"',
                        '```'
                    ].join('\n'),
                    b: 'shell'
                },
                {
                    a: [
                        '```sql',
                        'SELECT first_name, last_name FROM person',
                        '```'
                    ].join('\n'),
                    b: 'sql'
                },
                {
                    a: [
                        '```xml',
                        '<person>',
                        '  <firstname>John</firstname>',
                        '  <lastname>Doe</lastname>',
                        '</person>',
                        '```'
                    ].join('\n'),
                    b: 'xml'
                },
                {
                    a: [
                        '```yaml',
                        'obj:',
                        '  prop: value',
                        '',
                        'list:',
                        '  - value1',
                        '  - value2',
                        '```'
                    ].join('\n'),
                    b: 'yaml'
                }
            ]}
            columns={columnFormats}
            {...props}
        />,
        <div>{`Quotes, code, and syntax highlighting${name}`}</div>,
        <DataTable
            setProps={setProps}
            data={[
                {a: '> This is a quote.', b: 'simple quote'},
                {
                    a: '> This is a multiline\n> quote.',
                    b: 'multiline quote'
                },
                {
                    a: 'The `dash_table` package is super cool!',
                    b: 'inline code'
                },
                {
                    a: [
                        '```plaintext',
                        'export default helloworld(){',
                        '  print("hello, world!")}',
                        '```'
                    ].join('\n'),
                    b: 'code block without syntax highlighting'
                },
                {
                    a: [
                        '```python',
                        'def hello_world():',
                        '  print("hello, world!")',
                        '```'
                    ].join('\n'),
                    b: 'code block with syntax highlighting'
                }
            ]}
            columns={columnFormats}
            {...props}
        />,
        <div>{`Tables${name}`}</div>,
        <DataTable
            setProps={setProps}
            data={[
                {
                    a: [
                        'Statement | Is it true?',
                        '--- | ---',
                        'This page has two tables | yes',
                        'This table has two rows | no',
                        'This is an example of tableception | yes'
                    ].join('\n'),
                    b: 'simple two-column table'
                },
                {
                    a: [
                        'Statement | Is it true?',
                        '--- | ---',
                        'This page has two tables | yes',
                        'This table has two rows | no',
                        'This is an example of tableception | yes'
                    ].join('\n'),
                    b: 'simple two-column table'
                }
            ]}
            columns={columnFormats}
            {...props}
        />
    );
});

storiesOf('DashTable/Markdown', module).add('all variants', () => (
    <div>{...tests}</div>
));
