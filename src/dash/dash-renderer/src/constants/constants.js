export const REDIRECT_URI_PATHNAME = '/_oauth2/callback';
export const OAUTH_COOKIE_NAME = 'plotly_oauth_token';
export const JWT_EXPIRED_MESSAGE = 'JWT Expired';

export const STATUS = {
    OK: 200,
    PREVENT_UPDATE: 204,
    // We accept both 400 and 401 for JWT token expiry responses.
    // Some servers use code 400 for expired tokens, because
    // they reserve 401 for cases that require user action
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    CLIENTSIDE_ERROR: 'CLIENTSIDE_ERROR',
    NO_RESPONSE: 'NO_RESPONSE'
};

export const STATUSMAP = {
    [STATUS.OK]: 'SUCCESS',
    [STATUS.PREVENT_UPDATE]: 'NO_UPDATE'
};
