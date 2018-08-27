import { ChangeEvent, CSSProperties } from 'react';

import {
    IConditionalDropdown,
    IConditionalStyle,
    IDropdownOptions,
    IStyle
} from 'dash-table/components/Cell/types';

export interface ICellProps {
    active: boolean;
    classes?: string[];
    clearable: boolean;
    conditionalDropdowns?: IConditionalDropdown[];
    conditionalStyles?: IConditionalStyle[];
    datum: any;
    editable: boolean;
    focused: boolean;
    onChange: (e: ChangeEvent) => void;
    onClick: (e: React.MouseEvent) => void;
    onDoubleClick: (e: React.MouseEvent) => void;
    onPaste: (e: React.ClipboardEvent<Element>) => void;
    property: string | number;
    selected: boolean;
    staticDropdown?: IDropdownOptions;
    staticStyle?: IStyle;
    tableId: string;
    type?: string;
    value: any;
}

export interface ICellDefaultProps {
    classes: string[];
    conditionalDropdowns: IConditionalDropdown[];
    conditionalStyles: IConditionalStyle[];
    staticStyle: CSSProperties;
    type: string;
}

export interface ICellState {
    value: any;
}

export type ICellPropsWithDefaults = ICellProps & ICellDefaultProps;
