
import valueCache from 'core/cache/value';
import { ICellFactoryProps } from 'dash-table/components/Table/props';
import { handleChange, handleClick, handleDoubleClick, handleOnMouseUp, handlePaste } from 'dash-table/handlers/cellEvents';

type CacheArgs = [Handler, number, number];

export enum Handler {
    Change = 'change',
    Click = 'click',
    DoubleClick = 'doubleclick',
    MouseUp = 'mouseup',
    Paste = 'paste'
}

export type CacheFn = (...args: CacheArgs) => Function;
export type HandlerFn = (...args: any[]) => any;

export default (propsFn: () => ICellFactoryProps) => new EventHandler(propsFn).get;

class EventHandler {
    constructor(private readonly propsFn: () => ICellFactoryProps) {

    }

    private readonly handlers = new Map<Handler, HandlerFn>([
        [Handler.Change, handleChange.bind(undefined, this.propsFn)],
        [Handler.Click, handleClick.bind(undefined, this.propsFn)],
        [Handler.DoubleClick, handleDoubleClick.bind(undefined, this.propsFn)],
        [Handler.MouseUp, handleOnMouseUp.bind(undefined, this.propsFn)],
        [Handler.Paste, handlePaste.bind(undefined, this.propsFn)]
    ]);

    private readonly cache = valueCache<[Handler, number, number]>()((
        handler: Handler,
        columnIndex: number,
        rowIndex: number
    ) => {
        let handlerFn = this.handlers.get(handler);

        return handlerFn && handlerFn.bind(undefined, rowIndex, columnIndex);
    });

    get = (
        handler: Handler,
        columnIndex: number,
        rowIndex: number
    ) => {
        return this.cache.get(handler, columnIndex, rowIndex);
    }
}