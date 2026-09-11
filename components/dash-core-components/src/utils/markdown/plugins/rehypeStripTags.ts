import type {Plugin} from 'unified';
import type {Root} from 'hast';
import {visit, SKIP} from 'unist-util-visit';

// Tags removed from raw HTML even when `dangerously_allow_html` is True.
// New additions here may require a major version bump
const STRIPPED_TAGS = ['script', 'style'];

const rehypeStripTags: Plugin<[], Root> = () => tree => {
    visit(tree, 'element', (node, index, parent) => {
        if (
            STRIPPED_TAGS.includes(node.tagName) &&
            parent &&
            typeof index === 'number'
        ) {
            parent.children.splice(index, 1);
            return [SKIP, index];
        }
        return undefined;
    });
};

export default rehypeStripTags;
