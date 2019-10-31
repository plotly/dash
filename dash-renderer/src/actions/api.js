/* global fetch: true */
import {mergeDeepRight} from 'ramda';
import {handleAsyncError, getCSRFHeader} from '../actions';
import {urlBase} from '../utils';

function GET(path, fetchConfig, csrfConfig) {
    return fetch(
        path,
        mergeDeepRight(fetchConfig, {
            method: 'GET',
            headers: getCSRFHeader(csrfConfig),
        })
    );
}

function POST(path, fetchConfig, csrfConfig, body = {}) {
    return fetch(
        path,
        mergeDeepRight(fetchConfig, {
            method: 'POST',
            headers: getCSRFHeader(csrfConfig),
            body: body ? JSON.stringify(body) : null,
        })
    );
}

const request = {GET, POST};

export default function apiThunk(endpoint, method, store, id, body) {
    return (dispatch, getState) => {
        const {config, hooks} = getState();
        const url = `${urlBase(config)}${endpoint}`;

        dispatch({
            type: store,
            payload: {id, status: 'loading'},
        });
        return request[method](url, config.fetch, hooks.csrf_config, body)
            .then(res => {
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
                                id,
                            },
                        });
                        return json;
                    });
                }
                return dispatch({
                    type: store,
                    payload: {
                        id,
                        status: res.status,
                    },
                });
            })
            .catch(err => {
                const message = 'Error from API call: ' + endpoint;
                handleAsyncError(err, message, dispatch);
            });
    };
}
