export const REDIRECT_URI_PATHNAME = '/_oauth2/callback';
export const OAUTH_COOKIE_NAME = 'plotly_oauth_token';

export const STATUS = {
    OK: 200,
    PREVENT_UPDATE: 204,
    CLIENTSIDE_ERROR: 'CLIENTSIDE_ERROR',
    NO_RESPONSE: 'NO_RESPONSE',
};

export const STATUSMAP = {
    [STATUS.OK]: 'SUCCESS',
    [STATUS.PREVENT_UPDATE]: 'NO_UPDATE',
};
