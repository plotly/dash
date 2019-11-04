import Markdown from '../../src/fragments/Markdown.react.js';
import React from 'react';
import {shallow, render} from 'enzyme';

test('Input renders', () => {
    const md = render(<Markdown />);

    expect(md.html()).toBeDefined();
});

describe('dedent', () => {
    const md = shallow(<Markdown />).instance();

    test('leading spaces and tabs are removed from a single line', () => {
        [
            'test',
            ' test',
            '        test',
            '\t\t\ttest',
            '    \t    test',
            '\t    \ttest',
        ].forEach(s => {
            expect(md.dedent(s)).toEqual('test');
        });

        expect(md.dedent('    test    ')).toEqual('test    ');
    });

    test('same chars are removed from multiple lines, ignoring blanks', () => {
        ['', '    ', '\t', '\t\t', '          ', '\t    \t'].forEach(pre => {
            expect(
                md.dedent(
                    pre +
                        'a\n' +
                        pre +
                        '  b\r' +
                        pre +
                        'c\r\n' +
                        pre +
                        '\td\n' +
                        '\t\n' +
                        '\n' +
                        pre +
                        'e\n' +
                        '\n' +
                        pre +
                        'f'
                )
            ).toEqual(
                'a\n' +
                    '  b\n' +
                    'c\n' +
                    '\td\n' +
                    '\n' +
                    '\n' +
                    'e\n' +
                    '\n' +
                    'f'
            );
        });
    });

    test('mismatched chars are not removed', () => {
        expect(md.dedent('    \ta\n\t    b')).toEqual('    \ta\n\t    b');
    });

    test('the dedent prop controls behavior', () => {
        const text = '    a\n    b';
        const mdDedented = render(<Markdown children={text} />);
        expect(mdDedented.find('code').length).toEqual(0);
        expect(mdDedented.find('p').length).toEqual(1);

        const mdRaw = render(<Markdown children={text} dedent={false} />);
        expect(mdRaw.find('code').length).toEqual(1);
        expect(mdRaw.find('p').length).toEqual(0);
    });
});
