import * as R from 'ramda';
import React, {
    Component,
    CSSProperties,
    KeyboardEvent
} from 'react';
import Dropdown from 'react-select';

import { isEqual } from 'core/comparer';
import { memoizeOne } from 'core/memoizer';
import memoizerCache from 'core/memoizerCache';
import SyntaxTree from 'core/syntax-tree';

import {
    ICellDefaultProps,
    ICellProps,
    ICellPropsWithDefaults,
    ICellState
} from 'dash-table/components/Cell/props';

import {
    IDropdownOptions,
    IConditionalDropdown,
    IConditionalStyle
} from 'dash-table/components/Cell/types';

import {
    KEY_CODES
} from 'dash-table/utils/unicode';

export default class Cell extends Component<ICellProps, ICellState> {
    private static readonly dropdownAstCache = memoizerCache<[string, string | number, number], [string], SyntaxTree>(
        (query: string) => new SyntaxTree(query)
    );

    private static readonly styleAstCache = memoizerCache<[string, string | number, number], [string], SyntaxTree>(
        (query: string) => new SyntaxTree(query)
    );

    public static defaultProps: ICellDefaultProps = {
        classes: [],
        conditionalDropdowns: [],
        conditionalStyles: [],
        staticStyle: {},
        type: 'text'
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

    private get classes(): string[] {
        let {
            active,
            classes,
            editable,
            selected,
            type
        } = this.propsWithDefaults;

        return [
            ...(active ? ['focused'] : []),
            ...(!editable ? ['cell--uneditable'] : []),
            ...(selected ? ['cell--selected'] : []),
            ...(type === 'dropdown' ? ['dropdown'] : []),
            ...classes
        ];
    }

    private renderDropdown() {
        const {
            clearable,
            onChange,
            value
        } = this.propsWithDefaults;

        const dropdown = this.dropdown;

        return !dropdown ?
            this.renderValue() :
            (<Dropdown
                ref='dropdown'
                clearable={clearable}
                onChange={(newValue: any) => {
                    onChange(newValue ? newValue.value : newValue);
                }}
                onOpen={this.handleOpenDropdown}
                options={dropdown}
                placeholder={''}
                value={value}
            />);
    }

    private renderInput() {
        const {
            active,
            focused,
            onClick,
            onDoubleClick,
            onPaste
        } = this.propsWithDefaults;

        const classes = [
            ...(active ? ['input-active'] : []),
            ...(focused ? ['focused'] : ['unfocused']),
            ...['cell-value']
        ];

        const attributes = {
            className: classes.join(' '),
            onClick: onClick,
            onDoubleClick: onDoubleClick
        };

        return (!active && this.state.value === this.props.value) ?
            this.renderValue(attributes) :
            (<input
                ref='textInput'
                type='text'
                value={this.state.value}
                onBlur={this.propagateChange}
                onChange={this.handleChange}
                onKeyDown={this.handleKeyDown}
                onPaste={onPaste}
                {...attributes}
            />);
    }

    private renderValue(attributes = {}) {
        const { value } = this.propsWithDefaults;

        return (<div
            {...attributes}
        >
            {value}
        </div>);
    }

    private renderInner() {
        const {
            type
        } = this.props;

        switch (type) {
            case 'text':
            case 'numeric':
                return this.renderInput();
            case 'dropdown':
                return this.renderDropdown();
            default:
                return this.renderValue();
        }
    }

    private getDropdown = memoizeOne((...dropdowns: IDropdownOptions[]): IDropdownOptions | undefined => {
        return dropdowns.length ? dropdowns.slice(-1)[0] : undefined;
    });

    private get dropdown() {
        let {
            conditionalDropdowns,
            datum,
            property,
            staticDropdown,
            tableId
        } = this.propsWithDefaults;

        const dropdowns = [
            ...(staticDropdown ? [staticDropdown] : []),
            ...R.map(
                ([cd]) => cd.dropdown,
                R.filter(
                    ([cd, i]) => Cell.dropdownAstCache([tableId, property, i], [cd.condition]).evaluate(datum),
                    R.addIndex<IConditionalDropdown, [IConditionalDropdown, number]>(R.map)(
                        (cd, i) => [cd, i],
                        conditionalDropdowns
                    ))
            )
        ];

        return this.getDropdown(...dropdowns);
    }

    private getStyle = memoizeOne((...styles: CSSProperties[]) => {
        return styles.length ? R.mergeAll<CSSProperties>(styles) : undefined;
    });

    private get style() {
        let {
            conditionalStyles,
            datum,
            property,
            staticStyle,
            tableId
        } = this.propsWithDefaults;

        const styles = [staticStyle, ...R.map(
            ([cs]) => cs.style,
            R.filter(
                ([cs, i]) => Cell.styleAstCache([tableId, property, i], [cs.condition]).evaluate(datum),
                R.addIndex<IConditionalStyle, [IConditionalStyle, number]>(R.map)(
                    (cs, i) => [cs, i],
                    conditionalStyles
                )
            )
        )];

        return this.getStyle(...styles);
    }

    render() {
        return (<td
            ref='td'
            tabIndex={-1}
            className={this.classes.join(' ')}
            style={this.style}
        >
            {this.renderInner()}
        </td>);
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
        if (e.keyCode !== KEY_CODES.ENTER) {
            return;
        }

        this.propagateChange();
    }

    handleOpenDropdown = () => {
        const { dropdown, td }: { [key: string]: any } = this.refs;

        const menu: HTMLElement = dropdown.wrapper.querySelector('.Select-menu-outer');
        const parentBounds = td.getBoundingClientRect();

        let relativeParent = menu;
        while (getComputedStyle(relativeParent).position !== 'relative') {
            if (!relativeParent.parentElement) {
                break;
            }

            relativeParent = relativeParent.parentElement;
        }

        const relativeBounds = relativeParent.getBoundingClientRect();

        const left = (parentBounds.left - relativeBounds.left) + relativeParent.scrollLeft;
        const top = (parentBounds.top - relativeBounds.top) + relativeParent.scrollTop + parentBounds.height;

        menu.style.width = `${parentBounds.width}px`;
        menu.style.top = `${top}px`;
        menu.style.left = `${left}px`;
        menu.style.position = 'absolute';
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
        const input = this.refs.textInput as HTMLInputElement;

        if (active && input && document.activeElement !== input) {
            input.focus();
            input.setSelectionRange(0, input.value ? input.value.length : 0);
        }

        if (active && this.refs.dropdown) {
            (this.refs.td as HTMLElement).focus();
        }
    }

    shouldComponentUpdate(nextProps: ICellPropsWithDefaults, nextState: ICellState) {
        const props = this.props;
        const state = this.state;

        return !isEqual(props, nextProps, true) ||
            !isEqual(state, nextState, true);
    }
}