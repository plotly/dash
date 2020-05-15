import {clone} from 'ramda';

const defaultProfile = {
  count: 0,
  total: 0,
  compute: 0,
  network: {
    time: 0,
    upload: 0,
    download: 0,
  },
  resources: {},
  status: {
    current: null,
    success: 0,
    rejected: 0,
    error: 0
  }
};

const defaultState = {
  updated: [],
  resources: {},
  callbacks: {}
};

const profile = (state = defaultState, action) => {
    switch (action.type) {

        // Keep a record of the most recent change. This
        // is subtly different from history.present becasue
        // it watches all props, not just inputs.
        case 'UPDATE_RESOURCE_USAGE': {

          const {id, usage} = action.payload;
          const {
            __dash_client,
            __dash_server,
            __dash_upload,
            __dash_download,
            ...user
          } = usage;


          // Keep track of the callback that actually changed.
          const newState = {
            updated: [id],
            resources: state.resources,
            callbacks: state.callbacks
          };

          newState.callbacks[id] = newState.callbacks[id] || clone(defaultProfile);

          const cb = newState.callbacks[id];
          const cbResources = cb.resources;
          const totalResources = newState.resources;

          // Update resource usage.
          cb.count += 1;
          cb.total += __dash_client;
          cb.compute += __dash_server;
          cb.network.time += (__dash_client - __dash_server);
          cb.network.upload += __dash_upload;
          cb.network.download += __dash_download;

          for (const r in user) {
            if (user.hasOwnProperty(r)) {
              cbResources[r] = (cbResources[r] || 0) + user[r];
              totalResources[r] = (totalResources[r] || 0) + user[r];
            }
          }

          return newState;

        }

        default: {
            return state;
        }
    }
};

export default profile;
