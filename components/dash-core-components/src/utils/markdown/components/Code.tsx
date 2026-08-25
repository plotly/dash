import React, {useEffect, useRef} from 'react';

import lazyLoadHljs from '../../LazyLoader/third-party/hljs';
import {reactNodeToText} from '../text';
import type {ReactMarkdownCodeProps} from './types';

/*
 * highlight.js mutates the DOM in place (replacing the code text with coloured
 * <span>s), which conflicts with React's ownership of that subtree and left
 * updated code blocks stale under react-markdown v8. This component sidesteps
 * the conflict: React only owns the empty <code> element, while the source text
 * and highlighting are applied imperatively and re-run whenever the code or the
 * language changes - so content updates always re-highlight correctly.
 */
function HighlightedCode({className, children}: ReactMarkdownCodeProps) {
    const ref = useRef<HTMLElement>(null);
    const code = reactNodeToText(children);

    useEffect(() => {
        const node = ref.current;
        if (!node) {
            return;
        }
        // Reset to the raw source first so any stale highlight spans from a
        // previous render are discarded before re-highlighting.
        node.textContent = code;
        lazyLoadHljs().then(hljs => {
            node.removeAttribute('data-highlighted');
            hljs.highlightElement(node);
        });
    }, [code, className]);

    return <code ref={ref} className={className} />;
}

export default function CodeRenderer({
    inline,
    className,
    children,
}: ReactMarkdownCodeProps) {
    return inline ? (
        <code className={className}>{children}</code>
    ) : (
        <HighlightedCode className={className}>{children}</HighlightedCode>
    );
}
