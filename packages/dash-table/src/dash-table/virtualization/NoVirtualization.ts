import * as R from 'ramda';

import AbstractStrategy, { ITarget } from 'dash-table/virtualization/AbstractStrategy';

export default class NoStrategy extends AbstractStrategy {
    constructor(target: ITarget) {
        super(target);

        this.refresh();
    }

    protected getDataframe() {
        let { dataframe } = this.target;

        return { dataframe, indices: R.range(0, dataframe.length) };
    }

    public get offset() {
        return 0;
    }

    public loadNext() {

    }

    public loadPrevious() {

    }
}