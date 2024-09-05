import React, {PureComponent} from 'react';

import IsolatedInput from 'core/components/IsolatedInput';

type SetFilter = (ev: any) => void;

interface IAdvancedFilterProps {
    classes: string[];
    colSpan: number;
    setFilter: SetFilter;
    value?: string;
}

export default class AdvancedFilter extends PureComponent<IAdvancedFilterProps> {
    constructor(props: IAdvancedFilterProps) {
        super(props);
    }

    private submit = (ev: any) => this.props.setFilter(ev);

    render() {
        const {colSpan, value} = this.props;

        return (
            <th colSpan={colSpan}>
                <IsolatedInput
                    stopPropagation={true}
                    value={value}
                    submit={this.submit}
                />
            </th>
        );
    }
}
