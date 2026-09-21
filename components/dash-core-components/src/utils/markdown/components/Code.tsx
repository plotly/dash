import React, {useEffect, useRef} from 'react';

import lazyLoadHljs from '../../LazyLoader/third-party/hljs';
import {reactNodeToText} from '../text';
import type {ReactMarkdownCodeProps} from './types';

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
    if (inline) {
        return <code className={className}>{children}</code>;
    }
    return <HighlightedCode className={className}>{children}</HighlightedCode>;
}
