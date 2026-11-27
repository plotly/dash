import type {Plugin} from 'unified';
import type {Root} from 'hast';
import {visit} from 'unist-util-visit';

// Sets `target` on every link, including raw-HTML ones. Replaces the
// `linkTarget` option react-markdown dropped in v9.
const rehypeLinkTarget: Plugin<[string], Root> = target => tree => {
    visit(tree, 'element', node => {
        if (node.tagName === 'a') {
            node.properties.target = target;
        }
    });
};

export default rehypeLinkTarget;
