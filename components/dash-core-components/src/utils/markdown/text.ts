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

// Work around remark-math treating `\$` inside `$...$` as the closing
// delimiter. Single-line `$$...$$` remains inline math in remark-math.
// Only rewrite Markdown text, not code, link destinations or raw HTML.
export function normalizeEscapedDollarMath(text: string): string {
    const mathOrHtml =
        /<[^>\r\n]+>|(?<![\\$])\$(?!\$)((?:\\[^\r\n]|[^$\r\n])+?)\$(?!\$)/g;
    let fence: {char: string; length: number} | null = null;
    let htmlProtectedDepth = 0;
    let inlineCodeTicks = 0;

    return text
        .split(/(\r\n|\r|\n)/)
        .map(line => {
            if (line === '\n' || line === '\r' || line === '\r\n') {
                return line;
            }
            if (fence) {
                if (
                    new RegExp(
                        `^ {0,3}${fence.char}{${fence.length},}\\s*$`
                    ).test(line)
                ) {
                    fence = null;
                }
                return line;
            }
            const opening = inlineCodeTicks
                ? null
                : /^ {0,3}(`{3,}|~{3,})/.exec(line);
            if (opening) {
                fence = {char: opening[1][0], length: opening[1].length};
                return line;
            }
            if (/^( {4}|\t)/.test(line) || /^ {0,3}\[[^\]]+\]:/.test(line)) {
                return line;
            }

            return line
                .split(/(<\/?(?:code|pre|script|style|textarea)\b[^>]*>)/gi)
                .map(part => {
                    if (/^<(?:code|pre|script|style|textarea)\b/i.test(part)) {
                        htmlProtectedDepth++;
                        return part;
                    }
                    if (
                        /^<\/(?:code|pre|script|style|textarea)\b/i.test(part)
                    ) {
                        htmlProtectedDepth = Math.max(
                            0,
                            htmlProtectedDepth - 1
                        );
                        return part;
                    }
                    if (htmlProtectedDepth) {
                        return part;
                    }
                    return part
                        .split(/(\]\([^)\r\n]*\))/g)
                        .map(segment => {
                            // Leave Markdown link/image destinations unchanged.
                            if (segment.startsWith('](')) {
                                return segment;
                            }
                            return segment
                                .split(/(`+)/g)
                                .map(piece => {
                                    if (/^`+$/.test(piece)) {
                                        if (!inlineCodeTicks) {
                                            inlineCodeTicks = piece.length;
                                        } else if (
                                            inlineCodeTicks === piece.length
                                        ) {
                                            inlineCodeTicks = 0;
                                        }
                                        return piece;
                                    }
                                    return inlineCodeTicks
                                        ? piece
                                        : piece.replace(
                                              mathOrHtml,
                                              (
                                                  full,
                                                  math: string | undefined
                                              ) =>
                                                  math?.includes('\\$')
                                                      ? `$$${math}$$`
                                                      : full
                                          );
                                })
                                .join('');
                        })
                        .join('');
                })
                .join('');
        })
        .join('');
}
