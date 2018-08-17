import * as R from 'ramda';

import AbstractStrategy, { ITarget } from 'dash-table/virtualization/AbstractStrategy';

export default class FrontEndPageStrategy extends AbstractStrategy {
    private firstIndex: number;
    private lastIndex: number;

    constructor(target: ITarget) {
        super(target);
    }

    protected getDataframe() {
        let { settings, dataframe } = this.target;

        let currentPage = Math.min(
            settings.current_page,
            Math.floor(dataframe.length / settings.page_size)
        );

        this.firstIndex = settings.page_size * currentPage;

        this.lastIndex = Math.min(
            this.firstIndex + settings.displayed_pages * settings.page_size,
            dataframe.length
        );

        return {
            dataframe: dataframe.slice(
                this.firstIndex,
                this.lastIndex
            ),
            indices: R.range(this.firstIndex, this.lastIndex)
        };
    }

    public get offset() {
        return this.firstIndex;
    }

    public loadNext() {
        let { settings, dataframe } = this.target;

        let maxPageIndex = Math.floor(dataframe.length / settings.page_size);

        if (settings.current_page >= maxPageIndex) {
            return;
        }

        settings.current_page++;
        this.target.update({ settings });
    }

    public loadPrevious() {
        let { settings } = this.target;

        if (settings.current_page <= 0) {
            return;
        }

        settings.current_page--;
        this.target.update({ settings });
    }
}