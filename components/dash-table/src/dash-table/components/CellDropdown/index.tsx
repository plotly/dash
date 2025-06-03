import React, {ChangeEvent, Component, createRef} from 'react';
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

export default class CellDropdown extends Component<IProps> {
    dropdownRef: React.RefObject<any>;
    constructor(props: IProps) {
        super(props);
        this.dropdownRef = createRef();
    }
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
                    ref={this.dropdownRef}
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

        const dropdown = this.dropdownRef.current;

        if (applyFocus && dropdown && document.activeElement !== dropdown) {
            // Limitation. If React >= 16 --> Use React.createRef instead to pass parent ref to child
            const tdParent = DOM.getFirstParentOfType(dropdown.wrapper, 'td');
            if (tdParent && tdParent.className.indexOf('phantom-cell') === -1) {
                tdParent.focus();
            }
        }
    }

    private handleOpenDropdown = () => {
        dropdownHelper(
            this.dropdownRef.current.wrapper.querySelector('.Select-menu-outer')
        );
    };
}
