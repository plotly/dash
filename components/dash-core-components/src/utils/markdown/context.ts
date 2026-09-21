import {createContext, useContext} from 'react';
import type {ReactNode} from 'react';

export type MarkdownContextValue = {
    renderMarkdown: (text: string) => ReactNode;
};

export const MarkdownContext = createContext<MarkdownContextValue | undefined>(
    undefined
);

export function useMarkdownContext(): MarkdownContextValue {
    const value = useContext(MarkdownContext);
    if (!value) {
        throw new Error('MarkdownContext used outside of its provider');
    }
    return value;
}
