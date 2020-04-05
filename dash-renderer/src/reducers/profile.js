import {clone} from 'ramda';
import {getAction} from '../actions/constants';
import {STATUS} from '../constants/constants';

const defaultProfile = {
  callCount: 0,
  totalTime: 0,
  status: {
    current: null,
    success: 0,
    rejected: 0,
    error: 0
  },
  uid: null
};

const defaultState = {
  updated: [],
  callbacks: {}
};

const profile = (state = defaultState, action) => {
    switch (action.type) {

        // Keep a record of the most recent change. This
        // is subtly different from history.present becasue
        // it watches all props, not just inputs.
        case getAction('SET_REQUEST_QUEUE'): {

          // Keep track of the callbacks that actually changed.
          const newState = {
            updated: [],
            callbacks: clone(state.callbacks)
          };

          // Process the entire request queue.
          action.payload.forEach(request => {
            const {controllerId, status, uid, requestTime, responseTime} = clone(request);
            const profile = newState.callbacks[controllerId] || clone(defaultProfile);

            if (!profile.uid || profile.uid === uid) {
              if (profile.status.current !== status) {

                // Update status.
                newState.updated.push(controllerId);
                profile.status.current = status;

                // Request.
                if (status === 'loading') {
                  profile.uid = uid;
                }

                // Response.
                else {
                  profile.uid = null;
                  profile.callCount += 1;
                  profile.totalTime += (responseTime-requestTime);

                  switch (status) {
                    case STATUS.OK:
                      profile.status.success += 1;
                      break;

                    case STATUS.PREVENT_UPDATE:
                      profile.status.rejected += 1;
                      break;

                    default:
                      profile.status.error += 1;
                  }

                }

                newState.callbacks[controllerId] = profile;

              }
            }
          });

          return newState;

        }

        default: {
            return state;
        }
    }
};

export default profile;
