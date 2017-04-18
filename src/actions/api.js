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

function POST(path, body = {}) {
    return fetch(`${path}`, {
        method: 'POST',
        headers: {
        credentials: 'same-origin',
            'Accept': 'application/json',
        },
            'Content-Type': 'application/json',
            'X-CSRFToken': cookie.parse(document.cookie)._csrf_token
        body: body ? JSON.stringify(body) : null
    });
}

function apiThunk(endpoint, method, store, id, body) {
    return dispatch => {
        dispatch({
            type: store,
            payload: {id, status: 'loading'}
        });
        return request[method](endpoint, body)
        .then(res => res.json().then(
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
        ))
        .catch(err => {
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
    )
}

export function getDependencies() {
    return apiThunk(
        '/dependencies',
        'GET',
        'dependenciesRequest'
    )
}

export function getRoutes() {
    return apiThunk(
        '/routes',
        'GET',
        'routesRequest'
    )
}
