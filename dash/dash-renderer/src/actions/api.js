import {mergeDeepRight, once} from 'ramda';
import {handleAsyncError, getCSRFHeader} from '../actions';
import {urlBase} from './utils';

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
    return (dispatch, getState) => {
        const {config} = getState();
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
        return request[method](url, config.fetch, body)
            .then(
                res => {
                    setConnectionStatus(true);
                    const contentType = res.headers.get('content-type');
                    if (
                        contentType &&
                        contentType.indexOf('application/json') !== -1
                    ) {
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
                },
                () => {
                    // fetch rejection - this means the request didn't return,
                    // we don't get here from 400/500 errors, only network
                    // errors or unresponsive servers.
                    setConnectionStatus(false);
                }
            )
            .catch(err => {
                const message = 'Error from API call: ' + endpoint;
                handleAsyncError(err, message, dispatch);
            });
    };
}
