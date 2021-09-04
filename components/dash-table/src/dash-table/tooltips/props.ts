import {ConditionalDataCell} from 'dash-table/conditional';

export enum TooltipSyntax {
    Text = 'text',
    Markdown = 'markdown'
}

export enum TooltipUsage {
    Both = 'both',
    Data = 'data',
    Header = 'header'
}

export interface ITooltip {
    use_with?: TooltipUsage;
    delay?: number | null;
    duration?: number | null;
    type?: TooltipSyntax;
    value: string;
}

export type Tooltip = string | ITooltip;
export type ConditionalTooltip = ITooltip & {if: ConditionalDataCell};
