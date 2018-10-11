import * as R from 'ramda';

import { memoizeOneFactory } from 'core/memoizer';
import { Columns, VisibleColumns } from 'dash-table/components/Table/props';

const getter = (columns: Columns): VisibleColumns => R.filter(column => !column.hidden, columns);

export default memoizeOneFactory(getter);
