export interface DebugTitleProps {
    id: string;
    property: string;
}

export interface SpinnerProps {
    status: DebugTitleProps[] | null;
    color?: string;
    className?: string;
    fullscreen?: boolean;
    style?: React.CSSProperties;
    debug?: boolean;
}
