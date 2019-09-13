import React, {
    PureComponent
} from 'react';

interface IProps {
    className: string;
    value: any;
}

export default class CellLabel extends PureComponent<IProps> {
    render() {
        const {
            className,
            value
        } = this.props;

        return (<div
            className={className}
        >
            {value}
        </div>);
    }
}