/* global window: true */
import {connect} from 'react-redux'
import {contains, isEmpty, isNil} from 'ramda'
import React, {Component, PropTypes} from 'react';
import renderTree from './renderTree';
import {
    computeGraphs,
    computePaths,
    hydrateInitialOutputs,
    loadStateFromRoute,
    setLayout
} from './actions/index';
import {getLayout, getDependencies, getRoutes} from './actions/api';
import {APP_STATES} from './reducers/constants';


/**
 * Fire off API calls for initialization
 */
class UnconnectedContainer extends Component {
    constructor(props) {
        super(props);
        this.initialization = this.initialization.bind(this);
        this.handleHistory = this.handleHistory.bind(this);
    }
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
            paths,
            routesRequest
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
        } else if (dependenciesRequest.status === 200 && isEmpty(graphs)) {
            dispatch(computeGraphs(dependenciesRequest.content));
        }

        if (isEmpty(routesRequest)) {
            dispatch(getRoutes());
        }

        if (dependenciesRequest.status === 200 &&
            !isEmpty(graphs) &&
            routesRequest.status === 200 &&
            appLifecycle === APP_STATES('STARTED')
        ) {
            dispatch(hydrateInitialOutputs());
            this.handleHistory();
        }
    }

    handleHistory() {
        window.onpopstate = () => {
            if (this.props.routesRequest.status === 200) {
                this.props.dispatch(loadStateFromRoute());
            }
        }
    }

    render () {
        const {
            appLifecycle,
            dependenciesRequest,
            layoutRequest,
            layout,
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
        } else if (appLifecycle === APP_STATES('HYDRATED')) {
            return renderTree(layout, dependenciesRequest.content);
        } else {
            return (<div>{'Loading...'}</div>);
        }
    }
}
UnconnectedContainer.propTypes = {
    appLifecycle: PropTypes.oneOf([
        APP_STATES('STARTED'),
        APP_STATES('HYDRATED')
    ]),
    dispatch: PropTypes.function,
    dependenciesRequest: PropTypes.object,
    routesRequest: PropTypes.object,
    layoutRequest: PropTypes.object,
    layout: PropTypes.object,
    paths: PropTypes.object,
    history: PropTypes.array
}

const Container = connect(
    // map state to props
    state => ({
        appLifecycle: state.appLifecycle,
        layoutRequest: state.layoutRequest,
        dependenciesRequest: state.dependenciesRequest,
        routesRequest: state.routesRequest,
        layout: state.layout,
        graphs: state.graphs,
        paths: state.paths,
        history: state.history
    }),
    dispatch => ({dispatch})
)(UnconnectedContainer);

export default Container;
