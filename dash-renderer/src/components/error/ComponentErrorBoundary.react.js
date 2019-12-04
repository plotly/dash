import {connect} from 'react-redux';
import {Component} from 'react';
import PropTypes from 'prop-types';
import Radium from 'radium';
import {onError, revert} from '../../actions';

class UnconnectedComponentErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = {
            myID: props.componentId,
            oldChildren: null,
            hasError: false,
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
                info,
            })
        );
        dispatch(revert);
    }

    /* eslint-disable react/no-did-update-set-state */
    componentDidUpdate(prevProps, prevState) {
        const prevChildren = prevProps.children;
        if (
            !this.state.hasError &&
            prevChildren !== prevState.oldChildren &&
            prevChildren !== this.props.children
        ) {
            this.setState({
                oldChildren: prevChildren,
            });
        }
    }
    /* eslint-enable react/no-did-update-set-state */

    render() {
        const {hasError, oldChildren} = this.state;
        return hasError ? oldChildren : this.props.children;
    }
}

UnconnectedComponentErrorBoundary.propTypes = {
    children: PropTypes.object,
    componentId: PropTypes.string,
    error: PropTypes.object,
    dispatch: PropTypes.func,
};

const ComponentErrorBoundary = connect(
    state => ({
        error: state.error,
    }),
    dispatch => {
        return {dispatch};
    }
)(Radium(UnconnectedComponentErrorBoundary));

export default ComponentErrorBoundary;
