import React, {
    MouseEvent,
    PureComponent
} from 'react';

interface IProps {
    className: string;
    onClick: (e: MouseEvent) => void;
    onDoubleClick: (e: MouseEvent) => void;
    value: any;
}

export default class CellLabel extends PureComponent<IProps> {
    render() {
        const {
            className,
            onClick,
            onDoubleClick,
            value
        } = this.props;

        return (<div
            className={className}
            onClick={onClick}
            onDoubleClick={onDoubleClick}
        >
            {value}
        </div>);
    }
}