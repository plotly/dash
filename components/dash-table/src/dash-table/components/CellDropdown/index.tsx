import React, {ChangeEvent, PureComponent} from 'react';
import Dropdown from 'react-select';

import DOM from 'core/browser/DOM';

import dropdownHelper from 'dash-table/components/dropdownHelper';

import {IDropdownValue} from '../Table/props';

interface IProps {
    active: boolean;
    applyFocus: boolean;
    clearable?: boolean;
    dropdown?: IDropdownValue[];
    onChange: (e: ChangeEvent) => void;
    value: any;
    disabled?: boolean;
}

export default class CellDropdown extends PureComponent<IProps> {
    render() {
        const {clearable, dropdown, onChange, value, disabled} = this.props;

        return (
            <div
                className='dash-dropdown-cell-value-container dash-cell-value-container'
                onClick={this.handleClick}
            >
                <div className='dropdown-cell-value-shadow cell-value-shadow'>
                    {
                        (
                            (dropdown &&
                                dropdown.find(
                                    entry => entry.value === value
                                )) || {label: undefined}
                        ).label
                    }
                </div>
                <Dropdown
                    ref='dropdown'
                    clearable={clearable}
                    onChange={(newValue: any) => {
                        onChange(newValue ? newValue.value : newValue);
                    }}
                    scrollMenuIntoView={false}
                    onOpen={this.handleOpenDropdown}
                    options={dropdown}
                    placeholder={''}
                    value={value}
                    disabled={disabled}
                />
            </div>
        );
    }

    componentDidUpdate() {
        this.setFocus();
    }

    componentDidMount() {
        this.setFocus();
    }

    private handleClick(e: React.MouseEvent) {
        e.stopPropagation();
    }

    private setFocus() {
        const {active, applyFocus} = this.props;
        if (!active) {
            return;
        }

        const dropdown = this.refs.dropdown as any;

        if (applyFocus && dropdown && document.activeElement !== dropdown) {
            // Limitation. If React >= 16 --> Use React.createRef instead to pass parent ref to child
            const tdParent = DOM.getFirstParentOfType(dropdown.wrapper, 'td');
            if (tdParent && tdParent.className.indexOf('phantom-cell') === -1) {
                tdParent.focus();
            }
        }
    }

    private handleOpenDropdown = () => {
        const {dropdown}: {[key: string]: any} = this.refs;

        dropdownHelper(dropdown.wrapper.querySelector('.Select-menu-outer'));
    };
}
