import type {ReactNode} from 'react';
import type {Content} from 'hast';

// Concatenate the text content of hast nodes, descending into element children.
export function collectText(nodes: Content[] | undefined): string {
    if (!nodes) {
        return '';
    }
    return nodes
        .map(node => {
            if (node.type === 'text') {
                return node.value;
            }
            if (node.type === 'element') {
                return collectText(node.children);
            }
            return '';
        })
        .join('');
}

export function reactNodeToText(node: ReactNode): string {
    if (node === null || node === undefined || typeof node === 'boolean') {
        return '';
    }
    if (typeof node === 'string' || typeof node === 'number') {
        return String(node);
    }
    if (Array.isArray(node)) {
        return node.map(reactNodeToText).join('');
    }
    const element = node as {props?: {children?: ReactNode}};
    return element.props ? reactNodeToText(element.props.children) : '';
}

export function dedentText(text: string): string {
    const lines = text.split(/\r\n|\r|\n/);
    let commonPrefix: string | null = null;
    for (const line of lines) {
        const preMatch = line && line.match(/^\s*(?=\S)/);
        if (preMatch) {
            const prefix = preMatch[0];
            if (commonPrefix !== null) {
                for (let i = 0; i < commonPrefix.length; i++) {
                    // Like Python's textwrap.dedent, we'll remove both space
                    // and tab characters, but only if they match
                    if (prefix[i] !== commonPrefix[i]) {
                        commonPrefix = commonPrefix.substr(0, i);
                        break;
                    }
                }
            } else {
                commonPrefix = prefix;
            }
            if (!commonPrefix) {
                break;
            }
        }
    }
    const commonLen = commonPrefix ? commonPrefix.length : 0;
    return lines
        .map(line => (line.match(/\S/) ? line.substr(commonLen) : ''))
        .join('\n');
}
