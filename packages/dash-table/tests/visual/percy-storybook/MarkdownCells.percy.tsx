import React from 'react';
import { storiesOf } from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';
import { Presentation } from 'dash-table/components/Table/props';

const setProps = () => { };

const columnFormats = [
    { id: 'a', name: 'MD render', presentation: Presentation.Markdown },
    { id: 'b', name: 'Description' }
]

storiesOf('DashTable/Markdown', module)
    .add('Headers', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={[
                { a: '# H1', b: 'header one' },
                { a: '## H2', b: 'header two' },
                { a: '### H3', b: 'header three' },
                { a: '#### H4', b: 'header four' },
                { a: '##### H5', b: 'header five' },
                { a: '###### H6', b: 'header six' }
            ]}
            columns={columnFormats}
        />))
    .add('Emphasis', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={[
                { a: '*italics*', b: 'italics with stars' },
                { a: '_italics_', b: 'italics with underscores' },
                { a: '**bold**', b: 'bold with stars' },
                { a: '__bold__', b: 'bold with underscores' },
                { a: '~~strikethrough~~', b: 'strikethrough' },
                { a: '**_~~emphasis bonanza~~_**', b: 'everything all at once' }
            ]}
            columns={columnFormats}
        />))
    .add('Lists', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={[
                { a: '1. Ordered list\n  - with subitem\n    * and sub sub item\n  - and another subitem\n2. and another item', b: 'ordered' },
                { a: '* Unordered list\n  - with subitem\n    * and sub sub item\n  * and another subitem\n- and another item', b: 'unordered' }
            ]}
            columns={columnFormats}
        />))
    .add('Links and images', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={[
                { a: '[Greatest website ever](http://plot.ly "Plotly site")', b: 'normal link with title' },
                { a: '![the github logo](https://github.githubassets.com/images/modules/logos_page/GitHub-Logo.png)', b: 'logo with alt text' }
            ]}
            columns={columnFormats}
        />))
    .add('Quotes, code, and syntax highlighting', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={[
                { a: '> This is a quote.', b: 'simple quote' },
                { a: '> This is a multiline\n> quote.', b: 'multiline quote' },
                { a: 'The `dash_table` package is super cool!', b: 'inline code' },
                {
                    a: ['```plaintext',
                        'export default helloworld(){',
                        '  print("hello, world!")}',
                        '```'].join('\n'),
                    b: 'code block without syntax highlighting'
                },
                {
                    a: ['```python',
                        'def hello_world():',
                        '  print("hello, world!")',
                        '```'].join('\n'),
                    b: 'code block with syntax highlighting'
                }
            ]}
            columns={columnFormats}
        />))
    .add('Tables', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={[
                {
                    a: ['Statement | Is it true?',
                        '--- | ---',
                        'This page has two tables | yes',
                        'This table has two rows | no',
                        'This is an example of tableception | yes'].join('\n'),
                    b: 'simple two-column table'
                }
            ]}
            columns={columnFormats}
        />))
