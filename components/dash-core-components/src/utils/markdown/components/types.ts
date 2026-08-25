import type {ReactNode} from 'react';
import type {Element} from 'hast';

// react-markdown only publicly exports `Components`/`Options`, not the per-tag
// prop types it hands each renderer. Rather than deep-import its internals, we
// re-declare (loosened) the shapes here. For the props each tag receives, see
// https://github.com/remarkjs/react-markdown/tree/8.0.7#appendix-b-components
export type ReactMarkdownGenericProps = {
    node?: Element;
    children?: ReactNode;
};

export type ReactMarkdownCodeProps = ReactMarkdownGenericProps & {
    inline?: boolean;
    className?: string;
};
