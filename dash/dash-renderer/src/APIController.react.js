import {batch, connect} from 'react-redux';
import {includes, isEmpty} from 'ramda';
import React, {useEffect, useRef, useState, createContext} from 'react';
import PropTypes from 'prop-types';
import TreeContainer from './TreeContainer';
import GlobalErrorContainer from './components/error/GlobalErrorContainer.react';
import {
    dispatchError,
    hydrateInitialOutputs,
    onError,
    setGraphs,
    setPaths,
    setLayout
} from './actions';
import {computePaths} from './actions/paths';
import {computeGraphs} from './actions/dependencies';
import apiThunk from './actions/api';
import {EventEmitter} from './actions/utils';
import {applyPersistence} from './persistence';
import {getAppState} from './reducers/constants';
import {STATUS} from './constants/constants';
import {getLoadingState, getLoadingHash} from './utils/TreeContainer';
import wait from './utils/wait';

export const DashContext = createContext({});

/**
 * Fire off API calls for initialization
 * @param {*} props props
 * @returns {*} component
 */
const UnconnectedContainer = props => {
    const {
        appLifecycle,
        config,
        dependenciesRequest,
        error,
        layoutRequest,
        layout,
        loadingMap
    } = props;

    const [errorLoading, setErrorLoading] = useState(false);

    const events = useRef(null);
    if (!events.current) {
        events.current = new EventEmitter();
    }
    const renderedTree = useRef(false);

    const propsRef = useRef({});
    propsRef.current = props;

    const provider = useRef({
        fn: () => ({
            _dashprivate_config: propsRef.current.config,
            _dashprivate_dispatch: propsRef.current.dispatch,
            _dashprivate_graphs: propsRef.current.graphs,
            _dashprivate_loadingMap: propsRef.current.loadingMap
        })
    });

    useEffect(storeEffect.bind(null, props, events, setErrorLoading));

    useEffect(() => {
        if (renderedTree.current) {
            (async () => {
                renderedTree.current = false;
                await wait(0);
                events.current.emit('rendered');
            })();
        }
    });

    useEffect(() => {
        if (config.serve_locally) {
            window._dashPlotlyJSURL = `${config.requests_pathname_prefix}_dash-component-suites/plotly/package_data/plotly.min.js`;
        } else {
            window._dashPlotlyJSURL = config.plotlyjs_url;
        }
    }, []);

    let content;
    if (
        layoutRequest.status &&
        !includes(layoutRequest.status, [STATUS.OK, 'loading'])
    ) {
        content = <div className='_dash-error'>Error loading layout</div>;
    } else if (
        errorLoading ||
        (dependenciesRequest.status &&
            !includes(dependenciesRequest.status, [STATUS.OK, 'loading']))
    ) {
        content = <div className='_dash-error'>Error loading dependencies</div>;
    } else if (appLifecycle === getAppState('HYDRATED')) {
        renderedTree.current = true;

        content = (
            <DashContext.Provider value={provider.current}>
                <TreeContainer
                    _dashprivate_error={error}
                    _dashprivate_layout={layout}
                    _dashprivate_loadingState={getLoadingState(
                        layout,
                        [],
                        loadingMap
                    )}
                    _dashprivate_loadingStateHash={getLoadingHash(
                        [],
                        loadingMap
                    )}
                    _dashprivate_path={JSON.stringify([])}
                />
            </DashContext.Provider>
        );
    } else {
        content = <div className='_dash-loading'>Loading...</div>;
    }

    return config && config.ui === true ? (
        <GlobalErrorContainer>{content}</GlobalErrorContainer>
    ) : (
        content
    );
};

function storeEffect(props, events, setErrorLoading) {
    const {
        appLifecycle,
        dependenciesRequest,
        dispatch,
        error,
        graphs,
        hooks,
        layout,
        layoutRequest
    } = props;

    batch(() => {
        if (isEmpty(layoutRequest)) {
            if (typeof hooks.layout_pre === 'function') {
                hooks.layout_pre();
            }
            dispatch(apiThunk('_dash-layout', 'GET', 'layoutRequest'));
        } else if (layoutRequest.status === STATUS.OK) {
            if (isEmpty(layout)) {
                if (typeof hooks.layout_post === 'function') {
                    hooks.layout_post(layoutRequest.content);
                }
                const finalLayout = applyPersistence(
                    layoutRequest.content,
                    dispatch
                );
                dispatch(
                    setPaths(
                        computePaths(finalLayout, [], null, events.current)
                    )
                );
                dispatch(setLayout(finalLayout));
            }
        }

        if (isEmpty(dependenciesRequest)) {
            dispatch(
                apiThunk('_dash-dependencies', 'GET', 'dependenciesRequest')
            );
        } else if (
            dependenciesRequest.status === STATUS.OK &&
            isEmpty(graphs)
        ) {
            dispatch(
                setGraphs(
                    computeGraphs(
                        dependenciesRequest.content,
                        dispatchError(dispatch)
                    )
                )
            );
        }

        if (
            // dependenciesRequest and its computed stores
            dependenciesRequest.status === STATUS.OK &&
            !isEmpty(graphs) &&
            // LayoutRequest and its computed stores
            layoutRequest.status === STATUS.OK &&
            !isEmpty(layout) &&
            // Hasn't already hydrated
            appLifecycle === getAppState('STARTED')
        ) {
            let hasError = false;
            try {
                dispatch(hydrateInitialOutputs(dispatchError(dispatch)));
            } catch (err) {
                // Display this error in devtools, unless we have errors
                // already, in which case we assume this new one is moot
                if (!error.frontEnd.length && !error.backEnd.length) {
                    dispatch(onError({type: 'backEnd', error: err}));
                }
                hasError = true;
            } finally {
                setErrorLoading(hasError);
            }
        }
    });
}

UnconnectedContainer.propTypes = {
    appLifecycle: PropTypes.oneOf([
        getAppState('STARTED'),
        getAppState('HYDRATED'),
        getAppState('DESTROYED')
    ]),
    dispatch: PropTypes.func,
    dependenciesRequest: PropTypes.object,
    graphs: PropTypes.object,
    hooks: PropTypes.object,
    layoutRequest: PropTypes.object,
    layout: PropTypes.object,
    loadingMap: PropTypes.any,
    history: PropTypes.any,
    error: PropTypes.object,
    config: PropTypes.object
};

const Container = connect(
    // map state to props
    state => ({
        appLifecycle: state.appLifecycle,
        dependenciesRequest: state.dependenciesRequest,
        hooks: state.hooks,
        layoutRequest: state.layoutRequest,
        layout: state.layout,
        loadingMap: state.loadingMap,
        graphs: state.graphs,
        history: state.history,
        error: state.error,
        config: state.config
    }),
    dispatch => ({dispatch})
)(UnconnectedContainer);

export default Container;
