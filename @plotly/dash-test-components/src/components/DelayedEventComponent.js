import PropTypes from 'prop-types';
import React from 'react';

const DelayedEventComponent = ({ id, n_clicks = 0, setProps }) => (<button
    id={id}
    onClick={() => setTimeout(() => setProps({ n_clicks: n_clicks + 1 }), 20)}
/>);

DelayedEventComponent.propTypes = {
    id: PropTypes.string,
    n_clicks: PropTypes.number
};

export default DelayedEventComponent;