'use strict';

import React, {Component, PropTypes} from 'react';

/**
 * A component that greets a person in a header
 */
class Header extends Component {
    render() {
        return <h2>Hello, {this.props.name}</h2>;
    }
}

Header.propTypes = {

    /**
     * The name of the person you want to greet
     */
    name: PropTypes.string.isRequired
};

export default Header;
