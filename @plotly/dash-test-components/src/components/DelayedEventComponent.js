import PropTypes from 'prop-types';
import React from 'react';

const DelayedEventComponent = ({ id, n_clicks, setProps }) => (<button
    id={id}
    onClick={() => setTimeout(() => setProps({ n_clicks: n_clicks + 1 }), 20)}
/>);

DelayedEventComponent.propTypes = {
    id: PropTypes.string,
    n_clicks: PropTypes.number
};

DelayedEventComponent.defaultProps = {
    n_clicks: 0
};

export default DelayedEventComponent;