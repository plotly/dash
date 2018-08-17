export type Dataframe = any[];

export interface ISettings {
    displayed_pages: number;
    current_page: number;
    page_size: number;
}

export interface IViewport {
    readonly dataframe: Dataframe;
    readonly settings: ISettings;
    readonly virtualization: string;

    readonly viewportDataframe: Dataframe;
    readonly viewportIndices: number[];
}

export interface ITarget extends IViewport {
    update: (viewport: Partial<IViewport>) => void;
}

export default abstract class AbstractVirtualizationStrategy
{
    protected __dataframe: Dataframe;

    constructor(protected readonly target: ITarget) {

    }

    public get dataframe(): Dataframe {
        return this.__dataframe;
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