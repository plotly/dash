import type {ReactNode} from 'react';
import type {Element} from 'hast';

// Here we declare react-markdown's internal types that it will pass to our
// components. See:
// https://github.com/remarkjs/react-markdown/tree/8.0.7#appendix-b-components
export type ReactMarkdownGenericProps = {
    node?: Element;
    children?: ReactNode;
};

export type ReactMarkdownCodeProps = ReactMarkdownGenericProps & {
    inline?: boolean;
    className?: string;
};
