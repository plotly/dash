import {Remarkable} from 'remarkable';
import objPropsToCamel from 'core/objPropsToCamel';
import LazyLoader from 'dash-table/LazyLoader';
import {IMarkdownOptions} from 'dash-table/components/Table/props';

export default class Markdown {
    private readonly md: Remarkable;

    constructor(private readonly options: IMarkdownOptions) {
        this.md = new Remarkable({
            highlight: (str: string, lang: string) => {
                if (Markdown.hljs) {
                    if (lang && Markdown.hljs.getLanguage(lang)) {
                        try {
                            return Markdown.hljs.highlight(lang, str).value;
                        } catch (err) {}
                    }

                    try {
                        return Markdown.hljs.highlightAuto(str).value;
                    } catch (err) {}
                } else {
                    Markdown.loadhljs();
                }
                return '';
            },
            ...objPropsToCamel(this.options)
        });
    }

    public render = (value: string) => this.md.render(value);

    public static get isReady() {
        return Markdown._isReady;
    }

    private static hljs: any;
    private static hljsResolve: () => any;
    private static _isReady: Promise<boolean> | true = new Promise<boolean>(
        resolve => {
            Markdown.hljsResolve = resolve as any;
        }
    );

    private static async loadhljs() {
        Markdown.hljs = await LazyLoader.hljs;
        Markdown.hljsResolve();
        Markdown._isReady = true;
    }
}
