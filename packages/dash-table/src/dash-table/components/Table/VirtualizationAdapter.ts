import * as R from 'ramda';

import { ITarget, IViewport } from 'dash-table/virtualization/AbstractStrategy';
import { memoizeOne } from 'core/memoizer';
import sort, { defaultIsNully, SortSettings } from 'core/sorting';
import SyntaxTree from 'core/syntax-tree';
import Table from 'dash-table/components/Table';
import { Dataframe, IVirtualizationSettings, Virtualization, Datum, Indices } from 'dash-table/components/Table/props';

export default class VirtualizationAdapter implements ITarget {
    constructor(private readonly target: Table) {

    }

    private getDataframe = memoizeOne((
        dataframe: Dataframe,
        filtering: string | boolean,
        filtering_settings: string,
        sorting: string | boolean,
        sorting_settings: SortSettings = [],
        sorting_treat_empty_string_as_none: boolean
    ): { dataframe: Dataframe, indices: Indices } => {
        const map = new Map<Datum, number>();
        R.addIndex(R.forEach)((datum, index) => {
            map.set(datum, index);
        }, dataframe);

        if (filtering === 'fe' || filtering === true) {
            const tree = new SyntaxTree(filtering_settings);

            dataframe = tree.isValid ?
                tree.filter(dataframe) :
                dataframe;
        }

        const isNully = sorting_treat_empty_string_as_none ?
            (value: any) => value === '' || defaultIsNully(value) :
            undefined;

        if (sorting === 'fe' || sorting === true) {
            dataframe = sort(dataframe, sorting_settings, isNully);
        }

        // virtual_indices
        const indices = R.map(datum => map.get(datum) as number, dataframe);

        return { dataframe, indices };
    });

    private get dataframeAndIndices() {
        const {
            dataframe,
            filtering,
            filtering_settings,
            sorting,
            sorting_settings,
            sorting_treat_empty_string_as_none
        } = this.target.props;

        return this.getDataframe(
            dataframe,
            filtering,
            filtering_settings,
            sorting,
            sorting_settings,
            sorting_treat_empty_string_as_none
        );
    }

    get dataframe(): Dataframe {
        return this.dataframeAndIndices.dataframe;
    }

    get indices(): Indices {
        return this.dataframeAndIndices.indices;
    }

    get settings(): IVirtualizationSettings {
        return this.target.props.virtualization_settings;
    }

    get virtualization(): Virtualization {
        return this.target.props.virtualization;
    }

    get viewportDataframe(): Dataframe {
        return this.target.props.virtual_dataframe;
    }

    get viewportIndices(): number[] {
        return this.target.props.virtual_dataframe_indices;
    }

    update(viewport: Partial<IViewport>) {
        const setProps = this.target.setProps;

        const {
            settings,
            viewportDataframe,
            viewportIndices
        } = viewport;

        let props = R.mergeAll([
            settings ? { virtualization_settings: settings } : {},
            viewportDataframe ? { virtual_dataframe: viewportDataframe } : {},
            viewportIndices ? { virtual_dataframe_indices: viewportIndices } : {}
        ]);

        setTimeout(() => { setProps(props); }, 0);
    }
}