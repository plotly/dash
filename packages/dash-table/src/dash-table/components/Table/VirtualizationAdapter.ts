import * as R from 'ramda';

import { Dataframe, ISettings, ITarget, IViewport } from 'dash-table/virtualization/AbstractStrategy';
import { memoizeOne } from 'core/memoizer';
import sort, { SortSettings } from 'core/sorting';
import SyntaxTree from 'core/syntax-tree';

export default class VirtualizationAdapter implements ITarget {
    constructor(private readonly target: any) {

    }

    private getDataframe = memoizeOne((
        dataframe: Dataframe,
        filtering: string | boolean,
        filtering_settings: string,
        sorting: string | boolean,
        sorting_settings: SortSettings = []
    ): Dataframe => {
        if (filtering === 'fe' || filtering === true) {
            const tree = new SyntaxTree(filtering_settings);

            dataframe = tree.isValid ?
                tree.filter(dataframe) :
                dataframe;
        }

        if (sorting === 'fe' || sorting === true) {
            dataframe = sort(dataframe, sorting_settings);
        }

        return dataframe;
    });

    get dataframe(): Dataframe {
        const {
            dataframe,
            filtering,
            filtering_settings,
            sorting,
            sorting_settings
        } = this.target.props;

        return this.getDataframe(
            dataframe,
            filtering,
            filtering_settings,
            sorting,
            sorting_settings
        );
    }

    get settings(): ISettings {
        return this.target.props.virtualization_settings;
    }

    get virtualization(): string {
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