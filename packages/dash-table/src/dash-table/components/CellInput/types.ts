import { CSSProperties } from 'react';

export interface IDropdownOption {
    label: string;
    value: string;
}

export type IDropdownOptions = IDropdownOption[];

export interface IConditionalDropdown {
    condition: string;
    dropdown: IDropdownOptions;
}

export interface IStyle {
    target?: undefined;
    style: CSSProperties;
}

export interface IConditionalStyle extends IStyle {
    condition: string;
}