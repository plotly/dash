import '../utils/markdown/polyfills';
import React, {useCallback, useMemo} from 'react';
import ReactMarkdown, {
    defaultUrlTransform,
    type UrlTransform,
} from 'react-markdown';
import type {PluggableList} from 'unified';

import LoadingElement from '../utils/_LoadingElement';
import {MarkdownContentProps, MarkdownProps} from '../types';
import {components} from '../utils/markdown/components';
import {MarkdownContext} from '../utils/markdown/context';
import {
    linkTargetPlugins,
    rawHtmlPlugins,
    rehypeBlockCodePlugins,
    rehypeMathPlugins,
    remarkMathPlugins,
    remarkGfmPlugins,
} from '../utils/markdown/plugins';
import {dedentText} from '../utils/markdown/text';

// react-markdown 9 dropped `tel:` from its safe protocols; v8 allowed it.
const urlTransform: UrlTransform = url =>
    /^tel:/i.test(url) ? url : defaultUrlTransform(url);

const MarkdownContent = React.memo(function MarkdownContent({
    children,
    dedent,
    dangerously_allow_html,
    mathjax,
    link_target,
}: MarkdownContentProps & {children: string}) {
    const displayText = dedent && children ? dedentText(children) : children;

    const remarkPlugins: PluggableList = [...remarkGfmPlugins];
    const rehypePlugins: PluggableList = [];
    if (mathjax) {
        remarkPlugins.push(...remarkMathPlugins);
        rehypePlugins.push(...rehypeMathPlugins);
    }
    if (dangerously_allow_html) {
        rehypePlugins.push(...rawHtmlPlugins);
    }
    rehypePlugins.push(...rehypeBlockCodePlugins);
    if (link_target) {
        rehypePlugins.push(...linkTargetPlugins(link_target));
    }

    return (
        <ReactMarkdown
            remarkPlugins={remarkPlugins}
            urlTransform={urlTransform}
            rehypePlugins={rehypePlugins}
            components={components}
        >
            {displayText}
        </ReactMarkdown>
    );
});

function MarkdownContainer({
    id,
    style,
    className,
    highlight_config,
    dangerously_allow_html,
    link_target,
    mathjax,
    children,
    dedent,
}: MarkdownProps) {
    const textProp = Array.isArray(children) ? children.join('\n') : children;

    const classNames = [
        className,
        highlight_config?.theme === 'dark' ? 'hljs-dark' : '',
    ].filter(Boolean);

    // provides a recursive method to render nested markdown elements
    const renderMarkdown = useCallback(
        (text: string) => (
            <MarkdownContent
                dedent={dedent}
                dangerously_allow_html={dangerously_allow_html}
                mathjax={mathjax}
                link_target={link_target}
            >
                {text}
            </MarkdownContent>
        ),
        [dedent, dangerously_allow_html, mathjax, link_target]
    );

    const markdownContext = useMemo(() => ({renderMarkdown}), [renderMarkdown]);

    return (
        <LoadingElement>
            {loadingProps => (
                <div
                    id={id}
                    style={style}
                    className={classNames.join(' ')}
                    {...loadingProps}
                >
                    <MarkdownContext.Provider value={markdownContext}>
                        {renderMarkdown(textProp ?? '')}
                    </MarkdownContext.Provider>
                </div>
            )}
        </LoadingElement>
    );
}

export default MarkdownContainer;
