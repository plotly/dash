import * as R from 'ramda';

import { memoizeOne } from 'core/memoizer';

import CellFactory from 'dash-table/components/CellFactory';
import FilterFactory from 'dash-table/components/FilterFactory';
import HeaderFactory from 'dash-table/components/HeaderFactory';
import { ControlledTableProps, SetProps, SetState } from 'dash-table/components/Table/props';

const handleSetFilter = (setProps: SetProps, setState: SetState, filter: string, rawFilterQuery: string) => {
    setProps({ filter });
    setState({ rawFilterQuery });
};

function filterPropsFn(propsFn: () => ControlledTableProps, setFilter: any) {
    const props = propsFn();

    return R.merge(props, { setFilter });
}

function getter(
    cellFactory: CellFactory,
    filterFactory: FilterFactory,
    headerFactory: HeaderFactory
): JSX.Element[][] {
    const cells: JSX.Element[][] = [];

    const dataCells = cellFactory.createCells();
    const filters = filterFactory.createFilters();
    const headers = headerFactory.createHeaders();

    cells.push(...headers);
    cells.push(...filters);
    cells.push(...dataCells);

    return cells;
}

export default (propsFn: () => ControlledTableProps) => {
    const setFilter = memoizeOne((
        setProps: SetProps,
        setState: SetState
    ) => handleSetFilter.bind(undefined, setProps, setState));

    const cellFactory = new CellFactory(propsFn);
    const filterFactory = new FilterFactory(() => {
        const props = propsFn();

        return filterPropsFn(propsFn, setFilter(props.setProps, props.setState));
    });
    const headerFactory = new HeaderFactory(propsFn);

    return getter.bind(undefined, cellFactory, filterFactory, headerFactory);
};