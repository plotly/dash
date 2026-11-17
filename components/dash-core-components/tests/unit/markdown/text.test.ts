import React from 'react';
import type {Content} from 'hast';

import {
    collectText,
    reactNodeToText,
    dedentText,
    normalizeEscapedDollarMath,
} from '../../../src/utils/markdown/text';

describe('collectText', () => {
    it('returns an empty string for undefined', () => {
        expect(collectText(undefined)).toBe('');
    });

    it('concatenates adjacent text nodes', () => {
        const nodes: Content[] = [
            {type: 'text', value: 'Hello, '},
            {type: 'text', value: 'world'},
        ];
        expect(collectText(nodes)).toBe('Hello, world');
    });

    it('descends into element children', () => {
        const nodes: Content[] = [
            {
                type: 'element',
                tagName: 'strong',
                properties: {},
                children: [
                    {type: 'text', value: 'a'},
                    {
                        type: 'element',
                        tagName: 'em',
                        properties: {},
                        children: [{type: 'text', value: 'b'}],
                    },
                ],
            },
        ];
        expect(collectText(nodes)).toBe('ab');
    });

    it('ignores nodes that are neither text nor element', () => {
        const nodes: Content[] = [
            {type: 'comment', value: 'skip me'},
            {type: 'text', value: 'keep me'},
        ];
        expect(collectText(nodes)).toBe('keep me');
    });
});

describe('reactNodeToText', () => {
    it('returns an empty string for null, undefined, and booleans', () => {
        expect(reactNodeToText(null)).toBe('');
        expect(reactNodeToText(undefined)).toBe('');
        expect(reactNodeToText(true)).toBe('');
        expect(reactNodeToText(false)).toBe('');
    });

    it('stringifies strings and numbers', () => {
        expect(reactNodeToText('abc')).toBe('abc');
        expect(reactNodeToText(42)).toBe('42');
    });

    it('joins array members, dropping empty ones', () => {
        expect(reactNodeToText(['a', 1, null, 'b'])).toBe('a1b');
    });

    it('reads text out of element children recursively', () => {
        const node = React.createElement(
            'div',
            null,
            React.createElement('span', null, 'x'),
            'y'
        );
        expect(reactNodeToText(node)).toBe('xy');
    });
});

describe('dedentText', () => {
    it('strips the common leading indent', () => {
        expect(dedentText('    # Heading\n    body')).toBe('# Heading\nbody');
    });

    it('normalizes blank and whitespace-only lines to empty', () => {
        expect(dedentText('  a\n   \n  b')).toBe('a\n\nb');
    });

    it('only strips tabs and spaces where they match, like textwrap.dedent', () => {
        // A tab-indented line and a space-indented line share no common prefix,
        // so nothing is stripped.
        expect(dedentText('\ta\n  b')).toBe('\ta\n  b');
        // Identical mixed prefixes are stripped.
        expect(dedentText('\t a\n\t b')).toBe('a\nb');
    });

    it('leaves unindented text unchanged', () => {
        expect(dedentText('a\nb')).toBe('a\nb');
    });
});

describe('normalizeEscapedDollarMath', () => {
    it('protects escaped dollars inside inline math', () => {
        expect(normalizeEscapedDollarMath(String.raw`$x=\$3$`)).toBe(
            String.raw`$$x=\$3$$`
        );
        expect(normalizeEscapedDollarMath(String.raw`$x=\$3 + \$4$`)).toBe(
            String.raw`$$x=\$3 + \$4$$`
        );
        expect(normalizeEscapedDollarMath(String.raw`$x=\$3$ and $y=5$`)).toBe(
            String.raw`$$x=\$3$$ and $y=5$`
        );
    });

    it('does not rewrite currency, display math, or even backslashes', () => {
        for (const source of [
            String.raw`\$5 and \$10`,
            String.raw`$$x=\$3$$`,
            String.raw`$x=\\$3$`,
        ]) {
            expect(normalizeEscapedDollarMath(source)).toBe(source);
        }
    });

    it('does not rewrite Markdown links or raw HTML', () => {
        const cases = [
            String.raw`[link](https://example.org/$x=\$3$)`,
            String.raw`![image](https://example.org/$x=\$3$)`,
            String.raw`[ref]: https://example.org/$x=\$3$`,
            String.raw`<script>const x = '$x=\$3$';</script>`,
        ];

        for (const source of cases) {
            expect(normalizeEscapedDollarMath(source)).toBe(source);
        }
    });

    it('does not rewrite inline/fenced/indented code or HTML code', () => {
        const source = [
            'Before `$x=\\$3$` after',
            '```python',
            String.raw`$x=\$3$`,
            '```',
            String.raw`    $x=\$3$`,
            String.raw`<pre><code>$x=\$3$</code></pre>`,
            '<code>',
            String.raw`$x=\$3$`,
            '</code>',
            '`multi-line \n$x=\\$3$\n code`',
        ].join('\n');

        expect(normalizeEscapedDollarMath(source)).toBe(source);
    });
});
