import Logger from 'core/Logger';

interface IRule {
    cssText: string;
    selectorText: string;
}

class StylesheetFacade {
    constructor(private readonly name: string) {}

    get rules(): IRule[] {
        const sheet = this.sheet;

        return Array.from(sheet.rules || sheet.cssRules);
    }

    addRule(selector: string, css: string) {
        if (this.sheet.addRule) {
            this.sheet.addRule(selector, css);
        } else {
            // Firefox
            this.sheet.insertRule(`${selector} { ${css} }`, 0);
        }
    }

    deleteRule(index: number) {
        this.sheet.deleteRule(index);
    }

    findRule(selector: string): {rule: IRule; index: number} | null {
        const rules = this.rules;
        const index = rules.findIndex(r => r.selectorText === selector);

        return index === -1 ? null : {rule: rules[index], index};
    }

    private __stylesheet: HTMLStyleElement | undefined;

    private get sheet() {
        return (this.__stylesheet =
            this.__stylesheet ||
            (() => {
                const style = document.createElement('style');
                style.type = 'text/css';
                style.id = this.name;
                document.getElementsByTagName('head')[0].appendChild(style);

                return style;
            })()).sheet as any;
    }
}

export default class Stylesheet {
    private stylesheet: StylesheetFacade;

    constructor(private readonly prefix: string) {
        this.stylesheet = new StylesheetFacade(`${prefix}-dynamic-inline.css`);
    }

    deleteRule(selector: string) {
        selector = `${this.prefix} ${selector}`;

        const result = this.stylesheet.findRule(selector);
        if (result) {
            this.stylesheet.deleteRule(result.index);
        }
    }

    setRule(selector: string, css: string) {
        selector = `${this.prefix} ${selector}`;

        const result = this.stylesheet.findRule(selector);
        if (result) {
            if (
                result.rule.cssText === css ||
                result.rule.cssText === `${selector} { ${css} }`
            ) {
                return;
            } else {
                this.stylesheet.deleteRule(result.index);
            }
        }

        this.stylesheet.addRule(selector, css);
        Logger.trace('stylesheet', selector, css);
    }
}
