import { mergeDeepRight, once } from 'ramda';
import { getCSRFHeader, handleAsyncError, addHttpHeaders } from '../actions';
import { urlBase } from './utils';
import { MAX_AUTH_RETRIES } from './constants';
import { JWT_EXPIRED_MESSAGE, STATUS } from '../constants/constants';

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

const request = { GET, POST };

export default function apiThunk(endpoint, method, store, id, body) {
    return async (dispatch, getState) => {
        let { config, hooks } = getState();
        let newHeaders = null;

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
            payload: { id, status: 'loading' }
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
                    // eslint-disable-next-line no-console
                    console.log('fetch error', res);
                    setConnectionStatus(false);
                    return;
                }

                if (
                    res.status === STATUS.UNAUTHORIZED ||
                    res.status === STATUS.BAD_REQUEST
                ) {
                    if (hooks.request_refresh_jwt) {
                        let body;
                        try {
                            body = await res.text();
                        } catch (e) {
                            body = await res.json();
                        }
                        let jwtExpired = false;
                        if (typeof body == 'string') {
                            jwtExpired = body.includes(JWT_EXPIRED_MESSAGE);
                        } else if (typeof body == 'object') {
                            for (const key in body) {
                                if (body[key] && typeof body[key] == 'string' && body[key].includes(JWT_EXPIRED_MESSAGE)) {
                                    jwtExpired = true;
                                    break;
                                }
                            }
                        }
                        if (jwtExpired) {
                            const newJwt = await hooks.request_refresh_jwt(
                                config.fetch.headers.Authorization.substr(
                                    'Bearer '.length
                                )
                            );
                            if (newJwt) {
                                newHeaders = {
                                    Authorization: `Bearer ${newJwt}`
                                };

                                config = mergeDeepRight(config, {
                                    fetch: {
                                        headers: newHeaders
                                    }
                                });

                                continue;
                            }
                        }
                    }
                }
                break;
            }

            const contentType = res.headers.get('content-type');

            if (newHeaders) {
                dispatch(addHttpHeaders(newHeaders));
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
