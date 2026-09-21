import React, {useEffect, useRef} from 'react';

import lazyLoadMathJax from '../../LazyLoader/third-party/mathjax';
import {collectText} from '../text';
import type {ReactMarkdownGenericProps} from './types';

export default function MathJaxRenderer({node}: ReactMarkdownGenericProps) {
    const tex = collectText(node?.children);
    const inline = node?.properties?.inline !== 'false';
    const spanRef = useRef<HTMLSpanElement>(null);

    useEffect(() => {
        const current = spanRef.current;
        lazyLoadMathJax().then(mathjax => {
            mathjax?.typeset([current]);
        });
    }, [tex, inline]);

    return (
        <span ref={spanRef}>
            {inline ? '\\(' : '\\['}
            {tex}
            {inline ? '\\)' : '\\]'}
        </span>
    );
}
