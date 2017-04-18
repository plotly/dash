/* global fetch: true, document: true */
import cookie from 'cookie';
import {merge} from 'ramda';

function GET(path) {
    return fetch(`${path}`, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': cookie.parse(document.cookie)._csrf_token
        }
    });
}

function POST(path, body = {}, headers={}) {
    return fetch(`${path}`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: merge({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': cookie.parse(document.cookie)._csrf_token
        }, headers),
        body: body ? JSON.stringify(body) : null
    });
}

const request = {GET, POST};


function apiThunk(endpoint, method, store, id, body, headers={}) {
    return dispatch => {
        dispatch({
            type: store,
            payload: {id, status: 'loading'}
        });
        return request[method](endpoint, body, headers)
        .then(res => {
            const contentType = res.headers.get("content-type");
            if(contentType && contentType.indexOf("application/json") !== -1) {
                return res.json().then(
                    json => {
                        dispatch({
                            type: store,
                            payload: {
                                status: res.status,
                                content: json,
                                id
                            }
                        });
                        return json;
                    }
                )
            } else {
                dispatch({
                    type: store,
                    payload: {
                        id,
                        status: res.status
                    }
                });
            }
        }).catch(err => {
            /* eslint-disable no-console */
            console.error(err);
            /* eslint-enable no-console */
            dispatch({
                type: store,
                payload: {
                    id,
                    status: 500
                }
            });
        });
    };
}

export function getLayout() {
    return apiThunk(
        '/layout',
        'GET',
        'layoutRequest'
    );
}

export function getDependencies() {
    return apiThunk(
        '/dependencies',
        'GET',
        'dependenciesRequest'
    );
}

export function getRoutes() {
    return apiThunk(
        '/routes',
        'GET',
        'routesRequest'
    );
}


export function getConfig() {
    return apiThunk(
        '/_config',
        'GET',
        'configRequest'
    );
}

}
