/* global window:true */

import React, {Component, PropTypes} from 'react';

export default class Link extends Component {
    constructor(props) {
        super(props);
        this.updateLocation = this.updateLocation.bind(this);
    }

    updateLocation() {
        const {href, refresh} = this.props;
        if (refresh) {
            window.location.pathname = href;
        } else {
            window.history.pushState({}, '', href);
            window.dispatchEvent(new Event('onpushstate'));
        }
    }

    render() {
        const {className, style, id} = this.props;
        /*
         * ideally, we would use cloneElement however
         * that doesn't work with dash's recursive
         * renderTree implementation for some reason
         */
        return (
            <a id={id}
               className={className}
               style={style}
               onClick={this.updateLocation}
            >
                {this.props.children}
            </a>
        );
    }
}

Link.propTypes = {
    href: PropTypes.string,
    refresh: PropTypes.bool,
    className: PropTypes.string,
    style: PropTypes.object,
    id: PropTypes.string,
    children: PropTypes.node
};

Link.defaultProps = {
    refresh: false
};
