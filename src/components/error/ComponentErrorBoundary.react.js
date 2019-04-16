import {connect} from 'react-redux';
import {Component} from 'react';
import PropTypes from 'prop-types';
import Radium from 'radium';
import {contains, pluck} from 'ramda';
import uniqid from 'uniqid';
import {onError, revert} from '../../actions';

class UnconnectedComponentErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = {
            myID: props.componentId,
            myUID: uniqid(),
            oldChildren: null,
        };
    }

    componentDidCatch(error, info) {
        const {dispatch} = this.props;
        dispatch(
            onError({
                myUID: this.state.myUID,
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
        const {error} = this.props;
        const {myUID} = this.state;
        const hasError = contains(myUID, pluck('myUID')(error.frontEnd));
        if (
            !hasError &&
            prevState.oldChildren !== prevProps.children &&
            prevProps.children !== this.props.children
        ) {
            this.setState({
                oldChildren: prevProps.children,
            });
        }
    }
    /* eslint-enable react/no-did-update-set-state */

    render() {
        const {error} = this.props;
        const {myUID} = this.state;
        const hasError = contains(myUID, pluck('myUID')(error.frontEnd));

        if (hasError) {
            return this.state.oldChildren;
        }
        return this.props.children;
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
