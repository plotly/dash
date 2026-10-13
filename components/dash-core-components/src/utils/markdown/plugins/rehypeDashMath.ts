import type {Plugin} from 'unified';
import type {Element, Root} from 'hast';
import {visit} from 'unist-util-visit';

// Inline `$...$` or display `$$...$$` math.
const MATH_RE = /(\${1,2})((?:\\.|[^$])+)\1/g;

function escapeHtml(value: string): string {
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

// Rewrite `$...$` runs inside a raw-HTML string into `<dashmathjax>` tags. This
// runs on the raw string *before* rehype-raw decodes entities, so an escaped
// `&#36;` is left alone and renders as a literal `$`.
function rewriteRawMath(value: string): string {
    return value.replace(MATH_RE, (_full, delimiter, source) => {
        const inline = delimiter.length === 1 || source.indexOf('\n') === -1;
        return `<dashmathjax inline="${inline}">${escapeHtml(
            source
        )}</dashmathjax>`;
    });
}

// remark-math emits `<span class="math math-inline">` / `<div class="math
// math-display">`; report which (if either) an element is.
function mathKind(node: Element): 'inline' | 'display' | null {
    const className = node.properties?.className;
    if (Array.isArray(className)) {
        if (className.includes('math-inline')) {
            return 'inline';
        }
        if (className.includes('math-display')) {
            return 'display';
        }
    }
    return null;
}

/**
 * Routes both math sources into the Math component as `<dashmathjax>` elements:
 *   - Markdown `$...$` parsed by remark-math (as `.math-inline`/`.math-display`).
 *   - raw-HTML `$...$`, rewritten in place before rehype-raw runs.
 *
 *   in markdown:  Euler: $e=mc^2$
 *   transformed:  Euler: <dashmathjax inline="true">e=mc^2</dashmathjax>
 */
const rehypeDashMath: Plugin<[], Root> = () => tree => {
    visit(tree, node => {
        if (node.type === 'raw') {
            const raw = node as unknown as {value: string};
            raw.value = rewriteRawMath(raw.value);
            return;
        }
        if (node.type === 'element') {
            const kind = mathKind(node);
            if (kind) {
                node.tagName = 'dashmathjax';
                node.properties = {
                    inline: kind === 'inline' ? 'true' : 'false',
                };
            }
        }
    });
};

export default rehypeDashMath;
