import {Component, PropTypes} from 'react';
/* global window:true */

export default class Location extends Component {
    constructor(props) {
        super(props);
        this.updateLocation = this.updateLocation.bind(this);
    }

    updateLocation(props) {
        const {pathname, setProps} = props;

        /*
         * if pathname isn't defined, then it wasn't set by the user
         * and it needs to be equal to the window.location.pathname
         * this just happens on page load
         */
        if (!pathname) {
            setProps({pathname: window.location.pathname});
        } else if (pathname !== window.location.pathname) {
            if (props.refresh) {
                // Refresh the page
                window.location.pathname = pathname;
            } else {
                // Just push the new location into the URL
                if (setProps) setProps({pathname});
                window.history.pushState({}, '', pathname);
            }
        }
    }

    componentDidMount() {
        const listener = () => {
            return () => {
                const {setProps} = this.props;
                if (setProps) setProps({pathname: window.location.pathname});
            }
        };
        window.addEventListener('onpopstate', listener());
        window.onpopstate = listener('POP');

        // non-standard, emitted by Link.react
        window.addEventListener('onpushstate', listener());
        this.updateLocation(this.props);
    }

    componentWillReceiveProps(nextProps) {
        this.updateLocation(nextProps);
    }

    render() {
        return null;
    }
}

Location.propTypes = {
    id: PropTypes.string.isRequired,
    pathname: PropTypes.string,
    refresh: PropTypes.bool
};

Location.defaultProps = {
    refresh: true
};
