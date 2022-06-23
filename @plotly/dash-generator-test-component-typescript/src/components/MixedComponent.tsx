import PropTypes from 'prop-types';
import React from 'react';

type Props = {
    id?: string;
    prop: string[];
}

const MixedComponent: React.FC<Props> = (props) => {
    return (
        <div id={props.id}>{props.children}</div>
    )
}

MixedComponent.propTypes = {
    prop: PropTypes.arrayOf(PropTypes.string).isRequired
}

export default MixedComponent;
