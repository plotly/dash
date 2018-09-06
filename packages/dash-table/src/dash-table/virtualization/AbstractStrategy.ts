import { Dataframe, IVirtualizationSettings, Virtualization, Indices } from 'dash-table/components/Table/props';

export interface IViewport {
    readonly dataframe: Dataframe;
    readonly indices: Indices;
    readonly settings: IVirtualizationSettings;
    readonly virtualization: Virtualization;

    readonly viewportDataframe: Dataframe;
    readonly viewportIndices: number[];
}

export interface ITarget extends IViewport {
    update: (viewport: Partial<IViewport>) => void;
}

export default abstract class AbstractVirtualizationStrategy
{
    protected __dataframe: Dataframe;
    protected __indices: Indices;

    constructor(protected readonly target: ITarget) {

    }

    public get dataframe(): Dataframe {
        return this.__dataframe;
    }

    public get indices(): Indices {
        return this.__indices;
    }

    public refresh() {
        let { dataframe = [], indices = [] } = this.target.dataframe && this.getDataframe();

        let isEqual =
            !!this.__dataframe &&
            dataframe.length === this.dataframe.length &&
            !!dataframe.every((datum, index) => datum === this.dataframe[index]);

        if (isEqual) {
            return;
        }

        this.__dataframe = dataframe;
        this.__indices = indices;

        this.target.update({
            viewportDataframe: dataframe,
            viewportIndices: indices
        });
    }

    // Abstract
    public abstract get offset(): number;

    public abstract loadNext(): void;
    public abstract loadPrevious(): void;

    protected abstract getDataframe(): { dataframe: Dataframe, indices: number[] };
}