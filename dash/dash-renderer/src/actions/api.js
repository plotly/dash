import {mergeDeepRight, once} from 'ramda';
import {getCSRFHeader, handleAsyncError, setConfigNoRefresh} from '../actions';
import {urlBase} from './utils';
import {MAX_AUTH_RETRIES} from './constants';
import {JWT_EXPIRED_MESSAGE, STATUS} from '../constants/constants';

/* eslint-disable-next-line no-console */
const logWarningOnce = once(console.warn);

function GET(path, fetchConfig) {
    return fetch(
        path,
        mergeDeepRight(fetchConfig, {
            method: 'GET',
            headers: getCSRFHeader()
        })
    );
}

function POST(path, fetchConfig, body = {}) {
    return fetch(
        path,
        mergeDeepRight(fetchConfig, {
            method: 'POST',
            headers: getCSRFHeader(),
            body: body ? JSON.stringify(body) : null
        })
    );
}

const request = {GET, POST};

export default function apiThunk(endpoint, method, store, id, body) {
    return async (dispatch, getState) => {
        let {config, hooks} = getState();
        let configChanged = false;

        const url = `${urlBase(config)}${endpoint}`;

        function setConnectionStatus(connected) {
            if (getState().error.backEndConnected !== connected) {
                dispatch({
                    type: 'SET_CONNECTION_STATUS',
                    payload: connected
                });
            }
        }

        dispatch({
            type: store,
            payload: {id, status: 'loading'}
        });

        try {
            let res;
            for (let retry = 0; retry <= MAX_AUTH_RETRIES; retry++) {
                try {
                    res = await request[method](url, config.fetch, body);
                } catch (e) {
                    // fetch rejection - this means the request didn't return,
                    // we don't get here from 400/500 errors, only network
                    // errors or unresponsive servers.
                    console.log('fetch error', res);
                    setConnectionStatus(false);
                    throw e;
                }

                if (res.status === STATUS.UNAUTHORIZED) {
                    console.log(getState());
                    if (hooks.request_refresh_jwt) {
                        const body = await res.text();
                        if (body.includes(JWT_EXPIRED_MESSAGE)) {
                            const newJwt = await hooks.request_refresh_jwt(
                                config.fetch.headers.Authorization.substr(
                                    'Bearer '.length
                                )
                            );
                            if (newJwt) {
                                config = mergeDeepRight(config, {
                                    fetch: {
                                        headers: {
                                            Authorization: `Bearer ${newJwt}`
                                        }
                                    }
                                });
                                configChanged = true;

                                continue;
                            }
                        }
                    }
                }
                break;
            }

            const contentType = res.headers.get('content-type');

            if (configChanged) {
                dispatch(setConfigNoRefresh(config));
            }
            setConnectionStatus(true);
            if (contentType && contentType.indexOf('application/json') !== -1) {
                return res.json().then(json => {
                    dispatch({
                        type: store,
                        payload: {
                            status: res.status,
                            content: json,
                            id
                        }
                    });
                    return json;
                });
            }
            logWarningOnce(
                'Response is missing header: content-type: application/json'
            );
            return dispatch({
                type: store,
                payload: {
                    id,
                    status: res.status
                }
            });
        } catch (err) {
            const message = 'Error from API call: ' + endpoint;
            handleAsyncError(err, message, dispatch);
        }
    };
}
