import React from 'react';

import {useMarkdownContext} from '../context';
import {collectText} from '../text';
import type {ReactMarkdownGenericProps} from './types';

export default function DccMarkdownRenderer({node}: ReactMarkdownGenericProps) {
    const {renderMarkdown} = useMarkdownContext();
    const content = String(
        node?.properties?.children ?? collectText(node?.children)
    );
    return <>{renderMarkdown(content)}</>;
}
