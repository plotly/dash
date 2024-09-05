import React from 'react';
import PropTypes from 'prop-types';

const ReceivePropsComponent = (props) => {
    const {id, text, receive} = props;

    return (
        <div id={id}>
            {receive || text}
        </div>
    );
}
ReceivePropsComponent.propTypes = {
    id: PropTypes.string,
    text: PropTypes.string,
    receive: PropTypes.string,
}

export default ReceivePropsComponent;