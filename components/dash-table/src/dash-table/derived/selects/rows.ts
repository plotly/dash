import {Indices} from 'dash-table/components/Table/props';
import {memoizeOneFactory} from 'core/memoizer';

const getter = (indices: Indices, selectedRows: Indices): Indices => {
    const map = new Map<number, number>();

    indices.forEach((virtualIndex, index) => {
        map.set(virtualIndex, index);
    });

    const mappedSelectedRows: number[] = [];
    selectedRows.forEach(rowIndex => {
        const virtualIndex = map.get(rowIndex);

        if (virtualIndex !== undefined) {
            mappedSelectedRows.push(virtualIndex);
        }
    });

    return mappedSelectedRows;
};

export default memoizeOneFactory(getter);
