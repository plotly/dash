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
        setProps
    } = propsFn();

    const fillerColumns =
        (row_deletable ? 1 : 0) +
        (row_selectable ? 1 : 0);

    return {
        columns: columns,
        fillerColumns,
        filtering: filtering,
        filtering_settings: filtering_settings,
        filtering_type: filtering_type,
        id: id,
        setFilter: handleSetFilter.bind(undefined, setProps)
    };
}

function getter(
    cellFactory: CellFactory,
    filterFactory: FilterFactory,
    headerFactory: HeaderFactory
): JSX.Element[][] {
    const rows: JSX.Element[][] = [];

    rows.push(...headerFactory.createHeaders());
    rows.push(...filterFactory.createFilters());
    rows.push(...cellFactory.createCells());

    return rows;
}

export default (propsFn: () => ControlledTableProps): (() => JSX.Element[][]) => {
    const cellFactory = new CellFactory(propsFn);
    const filterFactory = new FilterFactory(() => filterPropsFn(propsFn));
    const headerFactory = new HeaderFactory(propsFn);

    return getter.bind(undefined, cellFactory, filterFactory, headerFactory);
};