import React from 'react';
import AbstractVirtualizationStrategy from 'dash-table/virtualization/AbstractStrategy';
import Row from 'dash-table/components/Row';

interface IOptions {
    id: string;
    virtualizer: AbstractVirtualizationStrategy;
}

export default class RowFactory {
    static createRows(options: IOptions) {
        const { id, virtualizer } = options;

        const dataframe = virtualizer.dataframe;

        return dataframe.map((datum, index) => (
            <Row
                key={virtualizer.offset + index}
                datum={datum}
                idx={virtualizer.offset + index}
                tableId={id}
                {...options}
            />
        ));
    }
}