import React, {
    PureComponent
} from 'react';

interface IProps {
    active: boolean;
    className: string;
    value: any;
}

export default class CellLabel extends PureComponent<IProps> {
    render() {
        const {
            className,
            value
        } = this.props;

        return (<div
            ref='el'
            className={className}
            tabIndex={-1}
        >
            {typeof value === 'boolean' ?
                value.toString() :
                value}
        </div>);
    }

    componentDidUpdate() {
        this.setFocus();
    }

    componentDidMount() {
        this.setFocus();
    }

    private setFocus() {
        const { active } = this.props;
        if (!active) {
            return;
        }

        const el = this.refs.el as HTMLDivElement;

        if (el && document.activeElement !== el) {
            el.focus();
        }
    }
}