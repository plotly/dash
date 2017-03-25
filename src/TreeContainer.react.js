import { connect } from 'react-redux'
import { contains, isEmpty, isNil } from 'ramda'
import React, {Component, PropTypes} from 'react';
import renderTree from './renderTree';
import {
    hydrateInitialOutputs,
    computeGraphs,
    computePaths,
    setLayout
} from './actions/index';
import {getLayout, getDependencies} from './actions/api';
import {APP_STATES} from './reducers/appLifecycle';

/**
 * Fire off API calls for initialization
 */
class UnconnectedContainer extends Component {
    componentDidMount() {
        this.initialization(this.props);
    }

    componentWillReceiveProps(props) {
        this.initialization(props);
    }

    initialization(props) {
        const {
            appLifecycle,
            dependenciesRequest,
            dispatch,
            graphs,
            layout,
            layoutRequest,
            paths
        } = props;
        if (isEmpty(layoutRequest)) {
            dispatch(getLayout());
        } else if (layoutRequest.status === 200) {
            if (isEmpty(layout)) {
                dispatch(setLayout(layoutRequest.content));
            } else if (isNil(paths)) {
                dispatch(computePaths({subTree: layout, startingPath: []}));
            }
        }

        if (isEmpty(dependenciesRequest)) {
            dispatch(getDependencies());
        } else if (dependenciesRequest.status === 200) {
            if (isEmpty(graphs)) {
                dispatch(computeGraphs(dependenciesRequest.content));
            } else if (appLifecycle === APP_STATES('STARTED')) {
                dispatch(hydrateInitialOutputs());
            }
        }
    }

    render () {
        const {
            appLifecycle,
            dependenciesRequest,
            layoutRequest,
            layout
        } = this.props;
        if (layoutRequest.status &&
            !contains(layoutRequest.status, [200, 'loading'])
        ) {
            return (<div>{'Error loading layout'}</div>);
        } else if (
            dependenciesRequest.status &&
            !contains(dependenciesRequest.status, [200, 'loading'])
        ) {
            return (<div>{'Error loading dependencies'}</div>);
        } else if (appLifecycle === APP_STATES('INITIALIZED')) {
            return renderTree(
                layout,
                dependenciesRequest.content
            );
        } else {
            return (<div>{'Loading...'}</div>);
        }
    }
}
UnconnectedContainer.propTypes = {
    appLifecycle: PropTypes.oneOf([
        APP_STATES('STARTED'),
        APP_STATES('INITIALIZED')
    ]),
    dispatch: PropTypes.function,
    dependenciesRequest: PropTypes.object,
    layoutRequest: PropTypes.object,
    layout: PropTypes.object,
    paths: PropTypes.object
}

const Container = connect(
    // map state to props
    state => ({
        appLifecycle: state.appLifecycle,
        layoutRequest: state.layoutRequest,
        dependenciesRequest: state.dependenciesRequest,
        layout: state.layout,
        graphs: state.graphs,
        paths: state.paths
    }),
    dispatch => ({dispatch})
)(UnconnectedContainer);

export default Container;
