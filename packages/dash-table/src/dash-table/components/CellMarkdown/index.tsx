import React, {
    PureComponent
} from 'react';

import DOM from 'core/browser/DOM';
import { memoizeOne } from 'core/memoizer';

import Markdown from 'dash-table/utils/Markdown';

interface IProps {
    active: boolean;
    applyFocus: boolean;
    className: string;
    value: any;
}

export default class CellMarkdown extends PureComponent<IProps, {}> {

    getMarkdown = memoizeOne((value: string, _ready: any) => ({
        dangerouslySetInnerHTML: {
            __html: Markdown.render(String(value))
        }
    }));

    constructor(props: IProps) {
        super(props);

        if (Markdown.isReady !== true) {
            Markdown.isReady.then(() => { this.setState({}); });
        }
    }

    componentDidUpdate() {
        this.setFocus();
    }

    componentDidMount() {
        this.setFocus();
    }

    render() {
        const {
            className,
            value
        } = this.props;

        return (<div
            ref='el'
            className={[className, 'cell-markdown'].join(' ')}
            {...this.getMarkdown(value, Markdown.isReady)}
        />);
    }

    private setFocus() {
        const { active, applyFocus } = this.props;
        if (!active) {
            return;
        }

        const el = this.refs.el as any;

        if (applyFocus && el && document.activeElement !== el) {
            // Limitation. If React >= 16 --> Use React.createRef instead to pass parent ref to child
            const tdParent = DOM.getFirstParentOfType(el, 'td');
            if (tdParent && tdParent.className.indexOf('phantom-cell') !== -1) {
                tdParent.focus();
            }
        }
    }

}
