import type {Plugin} from 'unified';
import type {Root} from 'hast';
import {visit} from 'unist-util-visit';

const DCC_ALLOWED_TAGS_LOWERCASE = ['dcclink', 'dccmarkdown'];

/**
 * Renders supported dash components according to the allowlist.
 * Slightly obscure because HTML on its own ignores the self-closing `/>` form
 * of custom tags, so we correct for that here:
 *
 *   in markdown:           Click <dccLink href="#" children="here" /> for info
 *   received here (wrong): Click <dccLink href="#" children="here"> for info</dccLink>
 *   corrected here:        Click <dccLink href="#" children="here"></dccLink> for info
 */
const rehypeDccComponents: Plugin<[], Root> = () => tree => {
    visit(tree, 'element', (node, index, parent) => {
        if (!parent || typeof index !== 'number') {
            return;
        }

        const isDccTag = DCC_ALLOWED_TAGS_LOWERCASE.includes(node.tagName);
        const hasChildrenAttribute = node.properties?.children !== undefined;
        if (!isDccTag || !hasChildrenAttribute) {
            return;
        }

        parent.children.splice(index + 1, 0, ...node.children);
        node.children = [];
    });
};

export default rehypeDccComponents;
