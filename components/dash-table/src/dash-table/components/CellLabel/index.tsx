import React, {createRef, PureComponent} from 'react';

interface IProps {
    active: boolean;
    applyFocus: boolean;
    className: string;
    value: any;
}

export default class CellLabel extends PureComponent<IProps> {
    elRef: React.RefObject<any>;
    constructor(props: IProps) {
        super(props);
        this.elRef = createRef();
    }
    render() {
        const {className, value} = this.props;

        return (
            <div ref={this.elRef} className={className} tabIndex={-1}>
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

        const el = this.elRef.current;

        if (applyFocus && el && document.activeElement !== el) {
            window.getSelection()?.selectAllChildren(el);
            el.focus();
        }
    }
}
