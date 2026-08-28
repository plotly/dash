import React from 'react';
import type {Properties} from 'hast';

import DccLink from '../../../components/Link';
import type {ReactMarkdownGenericProps} from './types';

export default function DccLinkRenderer({
    node,
    children,
}: ReactMarkdownGenericProps) {
    const properties: Properties = node?.properties ?? {};
    const content =
        node && node.children.length
            ? children
            : (properties.children as React.ReactNode);
    return (
        <DccLink
            href={properties.href as string}
            target={properties.target as string}
            title={properties.title as string}
        >
            {content}
        </DccLink>
    );
}
