import React, {lazy, Suspense, useEffect} from 'react';
import {MarkdownProps} from '../types';
import markdown from '../utils/LazyLoader/markdown';
import lazyLoadMathJax from '../utils/LazyLoader/third-party/mathjax';

const RealMarkdown = lazy(markdown);

/**
 * A component that renders Markdown text as specified by the
 * GitHub Markdown spec. These component uses
 * [react-markdown](https://github.com/remarkjs/react-markdown) under the hood.
 */
export default function Markdown({
    mathjax = false,
    dangerously_allow_html = false,
    dedent = true,
    ...props
}: MarkdownProps) {
    useEffect(() => {
        if (mathjax) {
            lazyLoadMathJax();
        }
    }, [mathjax]);

    return (
        <Suspense fallback={null}>
            <RealMarkdown
                mathjax={mathjax}
                dangerously_allow_html={dangerously_allow_html}
                dedent={dedent}
                {...props}
            />
        </Suspense>
    );
}
