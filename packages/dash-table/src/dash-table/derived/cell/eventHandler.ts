
import { memoizeOneFactory } from 'core/memoizer';
import memoizerCache from 'core/memoizerCache';
import { ICellFactoryProps } from 'dash-table/components/Table/props';
import { handleChange, handleClick, handleDoubleClick, handleOnMouseUp, handlePaste } from 'dash-table/handlers/cellEvents';

type CacheArgs = [Handler, number, number];
type GetterArgs = [HandlerFn, number, number];

export enum Handler {
    Change = 'change',
    Click = 'click',
    DoubleClick = 'doubleclick',
    MouseUp = 'mouseup',
    Paste = 'paste'
}

export type CacheFn = (...args: CacheArgs) => Function;
export type HandlerFn = (...args: any[]) => any;

const getter = (propsFn: () => ICellFactoryProps): CacheFn => {
    const cache = memoizerCache<CacheArgs, GetterArgs, Function>((...args: GetterArgs) => {
        let [
            handler,
            rowIndex,
            columnIndex
        ] = args;

        return handler && handler.bind(undefined, rowIndex, columnIndex);
    });

    const handlers = new Map<Handler, HandlerFn>([
        [Handler.Change, handleChange.bind(undefined, propsFn)],
        [Handler.Click, handleClick.bind(undefined, propsFn)],
        [Handler.DoubleClick, handleDoubleClick.bind(undefined, propsFn)],
        [Handler.MouseUp, handleOnMouseUp.bind(undefined, propsFn)],
        [Handler.Paste, handlePaste.bind(undefined, propsFn)]
    ]);

    return (...args: CacheArgs) => {
        let [
            handler,
            rowIndex,
            columnIndex
        ] = args;

        return cache(args, handlers.get(handler) as HandlerFn, rowIndex, columnIndex);
    };
};

export default memoizeOneFactory(getter);