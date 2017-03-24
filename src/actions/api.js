/* global fetch: true */

const request = {GET, POST};

function GET(path) {
    return fetch(`${path}`, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    });
}

function POST(path, body = {}) {
    return fetch(`${path}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
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
