import { Remarkable } from 'remarkable';
import LazyLoader from 'dash-table/LazyLoader';

export default class Markdown {

    static isReady: Promise<boolean> | true = new Promise<boolean>(resolve => {
        Markdown.hljsResolve = resolve;
    });

    static render = (value: string) => {
        return Markdown.md.render(value);
    }

    private static hljsResolve: () => any;

    private static hljs: any;

    private static readonly md: Remarkable = new Remarkable({
        highlight: (str: string, lang: string) => {
            if (Markdown.hljs) {
                if (lang && Markdown.hljs.getLanguage(lang)) {
                    try {
                        return Markdown.hljs.highlight(lang, str).value;
                    } catch (err) { }
                }

                try {
                    return Markdown.hljs.highlightAuto(str).value;
                } catch (err) { }
            } else {
                Markdown.loadhljs();
            }
            return '';
        },
        linkTarget:'_blank'
    });

    private static async loadhljs() {
        Markdown.hljs = await LazyLoader.hljs;
        Markdown.hljsResolve();
        Markdown.isReady = true;
    }
}
