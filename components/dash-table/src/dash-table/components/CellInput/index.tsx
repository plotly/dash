import React, {
    ChangeEvent,
    ClipboardEvent,
    KeyboardEvent,
    MouseEvent,
    PureComponent
} from 'react';

import {KEY_CODES, isNavKey} from 'dash-table/utils/unicode';

interface ICellProps {
    active: boolean;
    applyFocus: boolean;
    className: string;
    focused: boolean;
    onChange: (e: ChangeEvent) => void;
    onMouseUp: (e: MouseEvent) => void;
    onPaste: (e: ClipboardEvent<Element>) => void;
    type?: string;
    value: any;
}

interface ICellState {
    value: any;
}

export default class CellInput extends PureComponent<ICellProps, ICellState> {
    constructor(props: ICellProps) {
        super(props);

        this.state = {
            value: props.value
        };
    }

    render() {
        const {className, onMouseUp, onPaste, value} = this.props;

        // input does not handle `null` correct (causes console error)
        const sanitizedValue =
            this.state.value === null ? undefined : this.state.value;

        return (
            <div className='dash-input-cell-value-container dash-cell-value-container'>
                <div className='input-cell-value-shadow cell-value-shadow'>
                    {value}
                </div>
                <input
                    ref='textInput'
                    type='text'
                    className={className}
                    onBlur={this.propagateChange}
                    onChange={this.handleChange}
                    onKeyDown={this.handleKeyDown}
                    onMouseUp={onMouseUp}
                    onPaste={onPaste}
                    value={sanitizedValue}
                />
            </div>
        );
    }

    propagateChange = () => {
        if (this.state.value === this.props.value) {
            return;
        }

        const {onChange} = this.props;

        onChange(this.state.value);
    };

    handleChange = (e: any) => {
        this.setState({value: e.target.value});
    };

    handleKeyDown = (e: KeyboardEvent) => {
        const is_focused = this.props.focused;

        if (
            is_focused &&
            e.keyCode !== KEY_CODES.TAB &&
            e.keyCode !== KEY_CODES.ENTER
        ) {
            return;
        }

        if (!is_focused && !isNavKey(e.keyCode)) {
            return;
        }

        this.propagateChange();
    };

    UNSAFE_componentWillReceiveProps(nextProps: ICellProps) {
        const {value: nextValue} = nextProps;

        if (this.state.value !== nextValue) {
            this.setState({
                value: nextValue
            });
        }
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

        const input = this.refs.textInput as HTMLInputElement;

        if (applyFocus && input && document.activeElement !== input) {
            input.focus();
            input.setSelectionRange(0, input.value ? input.value.length : 0);
        }
    }
}
