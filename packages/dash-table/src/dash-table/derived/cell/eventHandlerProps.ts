
import { memoizeOneFactory } from 'core/memoizer';
import { ICellFactoryProps } from 'dash-table/components/Table/props';
import cellEventHandler, { Handler } from 'dash-table/derived/cell/eventHandler';
import { ICellHandlerProps } from 'dash-table/components/CellInput/props';

type CacheArgs = [number, number];

export type CacheFn = (...args: CacheArgs) => ICellHandlerProps;
export type HandlerFn = (...args: any[]) => any;

const getter = (propsFn: () => ICellFactoryProps): CacheFn => {
    const derivedHandlers = cellEventHandler()(propsFn);

    return (...args: CacheArgs) => {
        const [
            rowIndex,
            columnIndex
        ] = args;

        return {
            onChange: derivedHandlers(Handler.Change, rowIndex, columnIndex),
            onClick: derivedHandlers(Handler.Click, rowIndex, columnIndex),
            onDoubleClick: derivedHandlers(Handler.DoubleClick, rowIndex, columnIndex),
            onMouseUp: derivedHandlers(Handler.MouseUp, rowIndex, columnIndex),
            onPaste: derivedHandlers(Handler.Paste, rowIndex, columnIndex)
        } as ICellHandlerProps;
    };
};

export default memoizeOneFactory(getter);