import React from 'react';
import AbstractVirtualizationStrategy from 'dash-table/virtualization/AbstractStrategy';
import Row from 'dash-table/components/Row';

interface IOptions {
    virtualizer: AbstractVirtualizationStrategy;
}

export default class RowFactory {
    static createRows(options: IOptions) {
        const { virtualizer } = options;

        const dataframe = virtualizer.dataframe;

        return dataframe.map((datum, index) => (
            <Row
                key={virtualizer.offset + index}
                row={datum}
                idx={virtualizer.offset + index}
                {...options}
            />
        ));
    }
}