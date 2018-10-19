export interface IDropdownOption {
    label: string;
    value: string;
}

export type IDropdownOptions = IDropdownOption[];

export interface IConditionalDropdown {
    condition: string;
    dropdown: IDropdownOptions;
}