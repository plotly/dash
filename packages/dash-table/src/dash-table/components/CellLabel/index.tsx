import React, {PureComponent} from 'react';

interface IProps {
    active: boolean;
    applyFocus: boolean;
    className: string;
    value: any;
}

export default class CellLabel extends PureComponent<IProps> {
    render() {
        const {className, value} = this.props;

        return (
            <div ref='el' className={className} tabIndex={-1}>
                {typeof value === 'boolean' ? value.toString() : value}
            </div>
        );
    }

    componentDidUpdate() {
        this.setFocus();
    }

    componentDidMount() {
        this.setFocus();
    }

    private setFocus() {
        const {active, applyFocus} = this.props;
        if (!active) {
            return;
        }

        const el = this.refs.el as HTMLDivElement;

        if (applyFocus && el && document.activeElement !== el) {
            window.getSelection()?.selectAllChildren(el);
            el.focus();
        }
    }
}
