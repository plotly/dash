import React, { PureComponent } from 'react';

import IsolatedInput from 'core/components/IsolatedInput';

import { ColumnId } from 'dash-table/components/Table/props';

type SetFilter = (ev: any) => void;

interface IColumnFilterProps {
    classes: string;
    columnId: ColumnId;
    isValid: boolean;
    setFilter: SetFilter;
    value?: string;
}

export default class ColumnFilter extends PureComponent<IColumnFilterProps> {
    constructor(props: IColumnFilterProps) {
        super(props);

        this.state = {
            value: props.value
        };
    }

    private submit = (value: string | undefined) => {
        const { setFilter } = this.props;

        setFilter({
            target: { value }
        } as any);
    }

    render() {
        const {
            classes,
            columnId,
            isValid,
            value
        } = this.props;

        return (<th
            className={classes + (isValid ? '' : ' invalid')}
            data-dash-column={columnId}
        >
            <IsolatedInput
                value={value}
                placeholder={`filter data...`}
                stopPropagation={true}
                submit={this.submit}
            />
        </th>);
    }
}