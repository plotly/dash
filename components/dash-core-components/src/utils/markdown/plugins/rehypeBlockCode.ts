import type {Plugin} from 'unified';
import type {Root} from 'hast';
import {visit} from 'unist-util-visit';

declare module 'hast' {
    interface ElementData {
        block?: boolean;
    }
}

// Flags `<code>` inside `<pre>` so the code renderer knows to highlight it.
// Replaces the `inline` prop react-markdown dropped in v9.
const rehypeBlockCode: Plugin<[], Root> = () => tree => {
    visit(tree, 'element', (node, _index, parent) => {
        if (
            node.tagName === 'code' &&
            parent?.type === 'element' &&
            parent.tagName === 'pre'
        ) {
            node.data = {...node.data, block: true};
        }
    });
};

export default rehypeBlockCode;
