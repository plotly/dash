import valueCache from 'core/cache/value';

import {ICellFactoryProps} from 'dash-table/components/Table/props';
import {
    handleChange,
    handleClick,
    handleDoubleClick,
    handleEnter,
    handleEnterHeader,
    handleLeave,
    handleMove,
    handleMoveHeader,
    handleOnMouseUp,
    handlePaste
} from 'dash-table/handlers/cellEvents';

export enum Handler {
    Change = 'change',
    Click = 'click',
    DoubleClick = 'doubleclick',
    Enter = 'enter',
    EnterHeader = 'enterheader',
    Leave = 'leave',
    Move = 'move',
    MoveHeader = 'moveheader',
    MouseUp = 'mouseup',
    Paste = 'paste'
}

export default (propsFn: () => ICellFactoryProps) =>
    new EventHandler(propsFn).get;

class EventHandler {
    constructor(private readonly propsFn: () => ICellFactoryProps) {}

    private readonly cache = valueCache<[Handler, number, number]>()(
        (handler: Handler, rowIndex: number, columnIndex: number) => {
            switch (handler) {
                case Handler.Change:
                    return handleChange.bind(
                        undefined,
                        this.propsFn,
                        rowIndex,
                        columnIndex
                    );
                case Handler.Click:
                    return handleClick.bind(
                        undefined,
                        this.propsFn,
                        rowIndex,
                        columnIndex
                    );
                case Handler.DoubleClick:
                    return handleDoubleClick.bind(
                        undefined,
                        this.propsFn,
                        rowIndex,
                        columnIndex
                    );
                case Handler.Enter:
                    return handleEnter.bind(
                        undefined,
                        this.propsFn,
                        rowIndex,
                        columnIndex
                    );
                case Handler.EnterHeader:
                    return handleEnterHeader.bind(
                        undefined,
                        this.propsFn,
                        rowIndex,
                        columnIndex
                    );
                case Handler.Leave:
                    return handleLeave.bind(
                        undefined,
                        this.propsFn,
                        rowIndex,
                        columnIndex
                    );
                case Handler.Move:
                    return handleMove.bind(
                        undefined,
                        this.propsFn,
                        rowIndex,
                        columnIndex
                    );
                case Handler.MoveHeader:
                    return handleMoveHeader.bind(
                        undefined,
                        this.propsFn,
                        rowIndex,
                        columnIndex
                    );
                case Handler.MouseUp:
                    return handleOnMouseUp.bind(
                        undefined,
                        this.propsFn,
                        rowIndex,
                        columnIndex
                    );
                case Handler.Paste:
                    return handlePaste.bind(
                        undefined,
                        this.propsFn,
                        rowIndex,
                        columnIndex
                    );
                default:
                    throw new Error(`unexpected handler ${handler}`);
            }
        }
    );

    get = (handler: Handler, rowIndex: number, columnIndex: number) => {
        return this.cache.get(handler, rowIndex, columnIndex);
    };
}
