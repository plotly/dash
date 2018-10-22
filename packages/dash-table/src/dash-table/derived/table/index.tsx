import CellFactory from 'dash-table/components/CellFactory';
import FilterFactory from 'dash-table/components/FilterFactory';
import HeaderFactory from 'dash-table/components/HeaderFactory';
import { ControlledTableProps, SetProps } from 'dash-table/components/Table/props';

const handleSetFilter = (setProps: SetProps, filtering_settings: string) => setProps({ filtering_settings });

function filterPropsFn(propsFn: () => ControlledTableProps) {
    const {
        columns,
        filtering,
        filtering_settings,
        filtering_type,
        id,
        row_deletable,
        row_selectable,
        setProps,
        style_cell,
        style_cell_conditional,
        style_filter,
        style_filter_conditional
    } = propsFn();

    const fillerColumns =
        (row_deletable ? 1 : 0) +
        (row_selectable ? 1 : 0);

    return {
        columns,
        fillerColumns,
        filtering,
        filtering_settings,
        filtering_type,
        id,
        setFilter: handleSetFilter.bind(undefined, setProps),
        style_cell,
        style_cell_conditional,
        style_filter,
        style_filter_conditional
    };
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

export default (propsFn: () => ControlledTableProps): (() => JSX.Element[][]) => {
    const cellFactory = new CellFactory(propsFn);
    const filterFactory = new FilterFactory(() => filterPropsFn(propsFn));
    const headerFactory = new HeaderFactory(propsFn);

    return getter.bind(undefined, cellFactory, filterFactory, headerFactory);
};