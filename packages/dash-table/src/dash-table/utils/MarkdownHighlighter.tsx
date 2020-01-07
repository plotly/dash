import { Remarkable } from 'remarkable';
import LazyLoader from 'dash-table/LazyLoader';

export default class MarkdownHighlighter {

    static isReady: Promise<boolean> | true = new Promise<boolean>(resolve => {
        MarkdownHighlighter.hljsResolve = resolve;
    });

    static render = (value: string) => {
        return MarkdownHighlighter.md.render(value);
    }

    private static hljsResolve: () => any;

    private static hljs: any;

    private static readonly md: Remarkable = new Remarkable({
        highlight: (str: string, lang: string) => {
            if (MarkdownHighlighter.hljs) {
                if (lang && MarkdownHighlighter.hljs.getLanguage(lang)) {
                    try {
                        return MarkdownHighlighter.hljs.highlight(lang, str).value;
                    } catch (err) { }
                }

                try {
                    return MarkdownHighlighter.hljs.highlightAuto(str).value;
                } catch (err) { }
            } else {
                MarkdownHighlighter.loadhljs();
            }
            return '';
        }
    });

    private static async loadhljs() {
        MarkdownHighlighter.hljs = await LazyLoader.hljs;
        MarkdownHighlighter.hljsResolve();
        MarkdownHighlighter.isReady = true;
    }
}
