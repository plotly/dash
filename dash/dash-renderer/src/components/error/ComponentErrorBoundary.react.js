import {Component} from 'react';
import PropTypes from 'prop-types';
import {onError, revert} from '../../actions';

class ComponentErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = {
            myID: props.componentId,
            oldChildren: null,
            hasError: false
        };
    }

    static getDerivedStateFromError(_) {
        return {hasError: true};
    }

    componentDidCatch(error, info) {
        const {dispatch} = this.props;
        dispatch(
            onError({
                myID: this.state.myID,
                type: 'frontEnd',
                error,
                info
            })
        );
        dispatch(revert);
    }

    componentDidUpdate(prevProps, prevState) {
        const prevChildren = prevProps.children;
        if (
            !this.state.hasError &&
            prevChildren !== prevState.oldChildren &&
            prevChildren !== this.props.children
        ) {
            /* eslint-disable-next-line react/no-did-update-set-state */
            this.setState({
                oldChildren: prevChildren
            });
        }
    }

    render() {
        const {hasError, oldChildren} = this.state;
        return hasError ? oldChildren : this.props.children;
    }
}

ComponentErrorBoundary.propTypes = {
    children: PropTypes.object,
    componentId: PropTypes.string,
    error: PropTypes.object,
    dispatch: PropTypes.func
};

export default ComponentErrorBoundary;
