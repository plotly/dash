import React, {
    PureComponent,
    KeyboardEvent
} from 'react';
import Dropdown from 'react-select';

import DOM from 'core/browser/DOM';

import {
    ICellDefaultProps,
    ICellProps,
    ICellPropsWithDefaults,
    ICellState
} from 'dash-table/components/CellInput/props';

import {
    KEY_CODES, isNavKey
} from 'dash-table/utils/unicode';
import { ColumnType } from 'dash-table/components/Table/props';
import dropdownHelper from 'dash-table/components/dropdownHelper';

export default class CellInput extends PureComponent<ICellProps, ICellState> {

    public static defaultProps: ICellDefaultProps = {
        conditionalDropdowns: [],
        type: ColumnType.Text
    };

    constructor(props: ICellProps) {
        super(props);

        this.state = {
            value: props.value
        };
    }

    private get propsWithDefaults(): ICellPropsWithDefaults {
        return this.props as ICellPropsWithDefaults;
    }

    private renderDropdown() {
        const {
            active,
            clearable,
            dropdown,
            editable,
            focused,
            onChange,
            onClick,
            onDoubleClick,
            value
        } = this.propsWithDefaults;

        const classes = [
            ...(active ? ['input-active'] : []),
            ...(focused ? ['focused'] : ['unfocused']),
            ...['dash-cell-value']
        ];

        const attributes = {
            className: classes.join(' '),
            onClick: onClick,
            onDoubleClick: onDoubleClick
        };

        const readonly = !editable;

        return !dropdown || readonly ?
            this.renderValue(attributes) :
            (<div className='dash-dropdown-cell-value-container dash-cell-value-container'>
                {this.renderValue(
                    { className: 'dropdown-cell-value-shadow cell-value-shadow' },
                    (dropdown.find(entry => entry.value === value) || { label: undefined }).label
                )}
                <Dropdown
                    ref='dropdown'
                    clearable={clearable}
                    onChange={(newValue: any) => {
                        onChange(newValue ? newValue.value : newValue);
                    }}
                    onOpen={this.handleOpenDropdown}
                    options={dropdown}
                    placeholder={''}
                    value={value}
                />
            </div>);
    }

    private renderInput() {
        const {
            active,
            editable,
            focused,
            onClick,
            onDoubleClick,
            onMouseUp,
            onPaste
        } = this.propsWithDefaults;

        const classes = [
            ...(active ? ['input-active'] : []),
            ...(focused ? ['focused'] : ['unfocused']),
            ...['dash-cell-value']
        ];

        const attributes = {
            className: classes.join(' '),
            onClick: onClick,
            onDoubleClick: onDoubleClick,
            onMouseUp: onMouseUp
        };

        const readonly = (!active && this.state.value === this.props.value) || !editable;

        return readonly ?
            this.renderValue(attributes) :
            (<div className='dash-input-cell-value-container dash-cell-value-container'>
                {this.renderValue({ className: 'input-cell-value-shadow cell-value-shadow' })}
                <input
                    ref='textInput'
                    type='text'
                    value={this.state.value}
                    onBlur={this.propagateChange}
                    onChange={this.handleChange}
                    onKeyDown={this.handleKeyDown}
                    onPaste={onPaste}
                    {...attributes}
                />
            </div>);
    }

    private renderValue(attributes = {}, value?: string) {
        value = value || this.propsWithDefaults.value;

        return (<div
            {...attributes}
        >
            {value}
        </div>);
    }

    render() {
        const { type } = this.props;

        switch (type) {
            case ColumnType.Text:
            case ColumnType.Numeric:
                return this.renderInput();
            case ColumnType.Dropdown:
                return this.renderDropdown();
            default:
                return this.renderValue();
        }
    }

    propagateChange = () => {
        if (this.state.value === this.props.value) {
            return;
        }

        const { onChange } = this.props;

        onChange(this.state.value);
    }

    handleChange = (e: any) => {
        this.setState({ value: e.target.value });
    }

    handleKeyDown = (e: KeyboardEvent) => {
        const is_focused = this.props.focused;

        if (is_focused &&
            (e.keyCode !== KEY_CODES.TAB && e.keyCode !== KEY_CODES.ENTER)
        ) {
            return;
        }

        if (!is_focused && !isNavKey(e.keyCode)) {
            return;
        }

        this.propagateChange();
    }

    handleOpenDropdown = () => {
        const { dropdown, td }: { [key: string]: any } = this.refs;

        dropdownHelper(
            dropdown.wrapper.querySelector('.Select-menu-outer'),
            td
        );
    }

    componentWillReceiveProps(nextProps: ICellPropsWithDefaults) {
        const { value: nextValue } = nextProps;

        if (this.state.value !== nextValue) {
            this.setState({
                value: nextValue
            });
        }
    }

    componentDidUpdate() {
        const { active } = this.propsWithDefaults;
        if (!active) {
            return;
        }

        const input = this.refs.textInput as HTMLInputElement;
        const dropdown = this.refs.dropdown as any;

        if (input && document.activeElement !== input) {
            input.focus();
            input.setSelectionRange(0, input.value ? input.value.length : 0);
        }

        if (dropdown && document.activeElement !== dropdown) {
            // Limitation. If React >= 16 --> Use React.createRef instead to pass parent ref to child
            const tdParent = DOM.getFirstParentOfType(dropdown.wrapper, 'td');
            if (tdParent) {
                tdParent.focus();
            }
        }
    }
}