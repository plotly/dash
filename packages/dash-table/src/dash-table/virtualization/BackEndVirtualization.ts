import AbstractStrategy, { ITarget } from 'dash-table/virtualization/AbstractStrategy';

export default class BackEndPageStrategy extends AbstractStrategy {
    constructor(target: ITarget) {
        super(target);
    }

    protected getDataframe() {
        let { dataframe, indices } = this.target;

        return { dataframe, indices };
    }

    public get offset() {
        return 0;
    }

    public loadNext() {
        let { settings } = this.target;

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