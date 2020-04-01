import {mergeDeepRight} from 'ramda';
import {handleAsyncError, getCSRFHeader} from '../actions';
import {urlBase} from '../utils';

/* eslint-disable-next-line no-console */
const logWarningOnce = once(console.warn);

function GET(path, fetchConfig) {
    return fetch(
        path,
        mergeDeepRight(fetchConfig, {
            method: 'GET',
            headers: getCSRFHeader(),
        })
    );
}

function POST(path, fetchConfig, body = {}) {
    return fetch(
        path,
        mergeDeepRight(fetchConfig, {
            method: 'POST',
            headers: getCSRFHeader(),
            body: body ? JSON.stringify(body) : null,
        })
    );
}

const request = {GET, POST};

export default function apiThunk(endpoint, method, store, id, body) {
    return (dispatch, getState) => {
        const config = getState().config;
        const url = `${urlBase(config)}${endpoint}`;

        dispatch({
            type: store,
            payload: {id, status: 'loading'},
        });
        return request[method](url, config.fetch, body)
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
                logWarningOnce("Response miss content-type application/json")
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
