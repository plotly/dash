import {connect} from 'react-redux'
import {contains, isEmpty, isNil} from 'ramda'
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import TreeContainer from './TreeContainer';
import ErrorHandler from './ErrorHandler.react';
import {
    computeGraphs,
    computePaths,
    hydrateInitialOutputs,
    setLayout
} from './actions/index';
import {getDependencies, getLayout} from './actions/api';
import {APP_STATES} from './reducers/constants';

/**
 * Fire off API calls for initialization
 */
class UnconnectedContainer extends Component {
    constructor(props) {
        super(props);
        this.initialization = this.initialization.bind(this);
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
        } else if (dependenciesRequest.status === 200 && isEmpty(graphs)) {
            dispatch(computeGraphs(dependenciesRequest.content));
        }

        if (
            // dependenciesRequest and its computed stores
            dependenciesRequest.status === 200 &&
            !isEmpty(graphs) &&

            // LayoutRequest and its computed stores
            layoutRequest.status === 200 &&
            !isEmpty(layout) &&
            !isNil(paths) &&

            // Hasn't already hydrated
            appLifecycle === APP_STATES('STARTED')
        ) {
            dispatch(hydrateInitialOutputs());
        }
    }

    render () {
        const {
            appLifecycle,
            dependenciesRequest,
            layoutRequest,
            layout,
            error
        } = this.props;

        if (layoutRequest.status &&
            !contains(layoutRequest.status, [200, 'loading'])
        ) {
            return (<div className="_dash-error">{'Error loading layout'}</div>);
        }


        else if (
            dependenciesRequest.status &&
            !contains(dependenciesRequest.status, [200, 'loading'])
        ) {
            return (<div className="_dash-error">{'Error loading dependencies'}</div>);
        }


        else if (appLifecycle === APP_STATES('HYDRATED')) {
            return (
                <div id="_dash-app-content">
                    <ErrorHandler error={error}>
                      <TreeContainer layout={layout}/>
                    </ErrorHandler>
                </div>
            );
        }

        else {
            return (<div className="_dash-loading">{'Loading...'}</div>);
        }
    }
}
UnconnectedContainer.propTypes = {
    appLifecycle: PropTypes.oneOf([
        APP_STATES('STARTED'),
        APP_STATES('HYDRATED')
    ]),
    dispatch: PropTypes.func,
    dependenciesRequest: PropTypes.object,
    layoutRequest: PropTypes.object,
    layout: PropTypes.object,
    paths: PropTypes.object,
    history: PropTypes.array
}

const Container = connect(
    // map state to props
    state => ({
        appLifecycle: state.appLifecycle,
        dependenciesRequest: state.dependenciesRequest,
        layoutRequest: state.layoutRequest,
        layout: state.layout,
        graphs: state.graphs,
        paths: state.paths,
        history: state.history,
        error: state.error
    }),
    dispatch => ({dispatch})
)(UnconnectedContainer);

export default Container;
