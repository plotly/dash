import {connect} from 'react-redux';
import {includes, isEmpty} from 'ramda';
import React, {useEffect, useRef, createContext} from 'react';
import PropTypes from 'prop-types';
import TreeContainer from './TreeContainer';
import GlobalErrorContainer from './components/error/GlobalErrorContainer.react';
import {
    dispatchError,
    setHydrated,
    setGraphs,
    setLayout,
    setRendered,
    initialLayoutValidationTrigger
} from './actions';
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
        loadingMap,
        dispatch,
        graphs
    } = props;

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

    useEffect(() => {
        if (isEmpty(layoutRequest)) {
            dispatch(apiThunk('_dash-layout', 'GET', 'layoutRequest'));
        } else if (layoutRequest.status === STATUS.OK) {
            if (isEmpty(layout)) {
                const finalLayout = applyPersistence(
                    layoutRequest.content,
                    dispatch
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
            dispatch(setHydrated());
        }
    }, [appLifecycle, dependenciesRequest, graphs, layout, layoutRequest]);

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
        if (appLifecycle === getAppState('HYDRATED')) {
            // effects called after rendering, paths all added can validate.
            dispatch(initialLayoutValidationTrigger());
        }
    }, [appLifecycle]);

    useEffect(() => {
        dispatch(setRendered(events.current));
    }, []);

    let content;
    if (
        layoutRequest.status &&
        !includes(layoutRequest.status, [STATUS.OK, 'loading'])
    ) {
        content = <div className='_dash-error'>Error loading layout</div>;
    } else if (
        dependenciesRequest.status &&
        !includes(dependenciesRequest.status, [STATUS.OK, 'loading'])
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

UnconnectedContainer.propTypes = {
    appLifecycle: PropTypes.oneOf([
        getAppState('STARTED'),
        getAppState('HYDRATED'),
        getAppState('DESTROYED')
    ]),
    dispatch: PropTypes.func,
    dependenciesRequest: PropTypes.object,
    graphs: PropTypes.object,
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
