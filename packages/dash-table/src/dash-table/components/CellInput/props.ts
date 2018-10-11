import { ChangeEvent } from 'react';

import {
    IConditionalDropdown,
    IDropdownOptions
} from 'dash-table/components/CellInput/types';

import {
    ColumnId,
    ColumnType
} from 'dash-table/components/Table/props';

export interface ICellHandlerProps {
    onChange: (e: ChangeEvent) => void;
    onClick: (e: React.MouseEvent) => void;
    onDoubleClick: (e: React.MouseEvent) => void;
    onPaste: (e: React.ClipboardEvent<Element>) => void;
}

export interface ICellProps extends ICellHandlerProps {
    active: boolean;
    clearable?: boolean;
    datum: any;
    dropdown: IDropdownOptions | undefined;
    editable: boolean;
    focused: boolean;
    property: ColumnId;
    tableId: string;
    type?: string;
    value: any;
}

export interface ICellDefaultProps {
    conditionalDropdowns: IConditionalDropdown[];
    type: ColumnType;
}

export interface ICellState {
    value: any;
}

export type ICellPropsWithDefaults = ICellProps & ICellDefaultProps;
