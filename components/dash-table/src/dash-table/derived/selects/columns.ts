import {Columns} from 'dash-table/components/Table/props';
import {memoizeOneFactory} from 'core/memoizer';

const getter = (visibleColumns: Columns, selectedColumns: string[]): string[] =>
    visibleColumns
        .map(c => c.id)
        .filter(c => selectedColumns.indexOf(c) !== -1);

export default memoizeOneFactory(getter);
