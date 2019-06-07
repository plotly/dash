import React, {
    ChangeEvent,
    PureComponent
} from 'react';
import Dropdown from 'react-select';

import DOM from 'core/browser/DOM';

import dropdownHelper from 'dash-table/components/dropdownHelper';

import { IDropdownValue } from '../Table/props';

interface IProps {
    active: boolean;
    clearable?: boolean;
    dropdown?: IDropdownValue[];
    onChange: (e: ChangeEvent) => void;
    value: any;
}

export default class CellDropdown extends PureComponent<IProps> {
    render() {
        const {
            clearable,
            dropdown,
            onChange,
            value
        } = this.props;

        return (<div className='dash-dropdown-cell-value-container dash-cell-value-container'>
            <div className='dropdown-cell-value-shadow cell-value-shadow'>
                {(dropdown && dropdown.find(entry => entry.value === value) || { label: undefined }).label}
            </div>
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

        const dropdown = this.refs.dropdown as any;

        if (dropdown && document.activeElement !== dropdown) {
            // Limitation. If React >= 16 --> Use React.createRef instead to pass parent ref to child
            const tdParent = DOM.getFirstParentOfType(dropdown.wrapper, 'td');
            if (tdParent) {
                tdParent.focus();
            }
        }
    }

    private handleOpenDropdown = () => {
        const { dropdown }: { [key: string]: any } = this.refs;

        dropdownHelper(dropdown.wrapper.querySelector('.Select-menu-outer'));
    }
}