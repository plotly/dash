import {
    ChangeEvent,
    ClipboardEvent,
    MouseEvent
} from 'react';

import { memoizeOneFactory } from 'core/memoizer';
import { ICellFactoryProps } from 'dash-table/components/Table/props';
import cellEventHandler, { Handler } from 'dash-table/derived/cell/eventHandler';

interface IFunctionCache {
    onChange: (e: ChangeEvent) => void;
    onClick: (e: MouseEvent) => void;
    onDoubleClick: (e: MouseEvent) => void;
    onMouseUp: (e: MouseEvent) => void;
    onPaste: (e: ClipboardEvent<Element>) => void;
}

const getter = (propsFn: () => ICellFactoryProps) => {
    const derivedHandlers = cellEventHandler(propsFn);

    return (rowIndex: number, columnIndex: number): IFunctionCache => {
        return {
            onChange: derivedHandlers(Handler.Change, columnIndex, rowIndex),
            onClick: derivedHandlers(Handler.Click, columnIndex, rowIndex),
            onDoubleClick: derivedHandlers(Handler.DoubleClick, columnIndex, rowIndex),
            onMouseUp: derivedHandlers(Handler.MouseUp, columnIndex, rowIndex),
            onPaste: derivedHandlers(Handler.Paste, columnIndex, rowIndex)
        };
    };
};

export default memoizeOneFactory(getter);