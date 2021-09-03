import {CSSProperties, MouseEvent} from 'react';

interface IAttributes {
    [key: string]: string | number | boolean;
}

export interface ICellProps {
    active: boolean;
    attributes: IAttributes;
    className: string;
    onClick: (e: MouseEvent) => void;
    onDoubleClick: (e: MouseEvent) => void;
    onMouseEnter: (e: MouseEvent) => void;
    onMouseLeave: (e: MouseEvent) => void;
    onMouseMove: (e: MouseEvent) => void;
    style?: CSSProperties;
}

export type ICellPropsWithDefaults = ICellProps;
