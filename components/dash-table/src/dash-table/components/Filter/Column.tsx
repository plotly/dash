import React, {CSSProperties, PureComponent} from 'react';

import IsolatedInput from 'core/components/IsolatedInput';

import {ColumnId, IFilterOptions} from 'dash-table/components/Table/props';
import TableClipboardHelper from 'dash-table/utils/TableClipboardHelper';
import FilterOptions from 'dash-table/components/Filter/FilterOptions';

type SetFilter = (ev: any) => void;

interface IColumnFilterProps {
    className: string;
    columnId: ColumnId;
    filterOptions: IFilterOptions;
    isValid: boolean;
    setFilter: SetFilter;
    style?: CSSProperties;
    toggleFilterOptions: () => void;
    value?: string;
}

interface IState {
    value?: string;
}

export default class ColumnFilter extends PureComponent<
    IColumnFilterProps,
    IState
> {
    constructor(props: IColumnFilterProps) {
        super(props);

        this.state = {
            value: props.value
        };
    }

    private submit = (value: string | undefined) => {
        const {setFilter} = this.props;

        setFilter({
            target: {value}
        } as any);
    };

    render() {
        const {
            className,
            columnId,
            filterOptions,
            isValid,
            style,
            toggleFilterOptions,
            value
        } = this.props;

        return (
            <th
                className={className + (isValid ? '' : ' invalid')}
                data-dash-column={columnId}
                style={style}
            >
                <div>
                    <IsolatedInput
                        onCopy={(e: any) => {
                            e.stopPropagation();
                            TableClipboardHelper.clearClipboard();
                        }}
                        onPaste={(e: any) => {
                            e.stopPropagation();
                        }}
                        value={value}
                        placeholder={filterOptions.placeholder_text}
                        stopPropagation={true}
                        submit={this.submit}
                    />
                    <FilterOptions
                        filterOptions={filterOptions}
                        toggleFilterOptions={toggleFilterOptions}
                    />
                </div>
            </th>
        );
    }
}
