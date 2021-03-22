import React, {CSSProperties, PureComponent} from 'react';

import IsolatedInput from 'core/components/IsolatedInput';

import {ColumnId} from 'dash-table/components/Table/props';
import TableClipboardHelper from 'dash-table/utils/TableClipboardHelper';

type SetFilter = (ev: any) => void;

interface IColumnFilterProps {
    className: string;
    columnId: ColumnId;
    isValid: boolean;
    setFilter: SetFilter;
    style?: CSSProperties;
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
        const {className, columnId, isValid, style, value} = this.props;

        return (
            <th
                className={className + (isValid ? '' : ' invalid')}
                data-dash-column={columnId}
                style={style}
            >
                <IsolatedInput
                    onCopy={(e: any) => {
                        e.stopPropagation();
                        TableClipboardHelper.clearClipboard();
                    }}
                    onPaste={(e: any) => {
                        e.stopPropagation();
                    }}
                    value={value}
                    placeholder={'filter data...'}
                    stopPropagation={true}
                    submit={this.submit}
                />
            </th>
        );
    }
}
