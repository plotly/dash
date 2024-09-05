import React, {Component} from 'react';
import PropTypes from 'prop-types';

class GlobalErrorContainer extends Component {
    constructor(props) {
        super(props);
    }
    render() {
        return <div id='_dash-app-content'>{this.props.children}</div>;
    }
}

GlobalErrorContainer.propTypes = {
    children: PropTypes.object
};

export default GlobalErrorContainer;
