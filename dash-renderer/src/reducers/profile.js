import {clone} from 'ramda';

import {STATUSMAP} from '../constants/constants';

const defaultProfile = {
    count: 0,
    total: 0,
    compute: 0,
    network: {
        time: 0,
        upload: 0,
        download: 0
    },
    resources: {},
    status: {
        latest: null
    },
    result: {}
};

const defaultState = {
    updated: [],
    resources: {},
    callbacks: {},
    graphLayout: null
};

const profile = (state = defaultState, action) => {
    if (action.type === 'UPDATE_RESOURCE_USAGE') {
        // Keep a record of the most recent change. This
        // is subtly different from history.present because
        // it watches all props, not just inputs.
        const {id, usage, status} = action.payload;
        const statusMapped = STATUSMAP[status] || status;

        // Keep track of the callback that actually changed.
        const newState = {
            updated: [id],
            resources: state.resources,
            callbacks: state.callbacks,
            // graphLayout is never passed in via actions, because we don't
            // want it to trigger a rerender of the callback graph.
            // See CallbackGraphContainer.react
            graphLayout: state.graphLayout
        };

        newState.callbacks[id] =
            newState.callbacks[id] || clone(defaultProfile);

        const cb = newState.callbacks[id];
        const cbResources = cb.resources;
        const totalResources = newState.resources;

        // Update resource usage & params.
        cb.count += 1;
        cb.status.latest = statusMapped;
        cb.status[statusMapped] = (cb.status[statusMapped] || 0) + 1;
        cb.result = action.payload.result;
        cb.inputs = action.payload.inputs;
        cb.state = action.payload.state;

        if (usage) {
            const {
                __dash_client,
                __dash_server,
                __dash_upload,
                __dash_download,
                ...user
            } = usage;

            cb.total += __dash_client;
            cb.compute += __dash_server;
            cb.network.time += __dash_client - __dash_server;
            cb.network.upload += __dash_upload;
            cb.network.download += __dash_download;

            for (const r in user) {
                if (user.hasOwnProperty(r)) {
                    cbResources[r] = (cbResources[r] || 0) + user[r];
                    totalResources[r] = (totalResources[r] || 0) + user[r];
                }
            }
        }

        return newState;
    }

    return state;
};

export default profile;
