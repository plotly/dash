import * as R from 'ramda';

const __1day = 86400 * 1000;
const __20years = 86400 * 1000 * 365 * 20;

export default class CookieStorage {
    // From https://github.com/Modernizr/Modernizr/blob/f4d3aa0b3c9eeb7338e8d89ed77929a8e969c502/feature-detects/cookies.js#L1
    // try..catch because some in situations `document.cookie` is exposed but throws a
    // SecurityError if you try to access it; e.g. documents created from data URIs
    // or in sandboxed iframes (depending on flags/context)
    public static enabled = R.once((): boolean => {
        try {
            // Create cookie
            document.cookie = 'cookietest=1';
            const ret = document.cookie.indexOf('cookietest=') !== -1;
            // Delete cookie
            document.cookie =
                'cookietest=1; expires=Thu, 01-Jan-1970 00:00:01 GMT';
            return ret;
        } catch (e) {
            return false;
        }
    });

    public static delete(id: string, domain = '', path = '/') {
        if (!CookieStorage.enabled()) {
            return;
        }

        const expires = new Date(Date.now() - __1day).toUTCString();

        document.cookie = `${id}=;expires=${expires};domain=${domain};path=${path}`;
    }

    public static get(id: string) {
        if (!id.length) {
            return;
        }

        if (!CookieStorage.enabled()) {
            return;
        }

        id = id.toLowerCase();

        const cookies = document.cookie.split(';').map(cookie => {
            const fragments = cookie.split('=');

            return {
                id: fragments[0].trim(),
                value: fragments[1]
            };
        });

        return (
            cookies.find(cookie => id === cookie.id.toLocaleLowerCase()) ||
            ({} as any)
        ).value;
    }

    public static set(id: string, value: string, domain = '', path = '/') {
        if (!CookieStorage.enabled()) {
            return;
        }

        const expires = new Date(Date.now() + __20years).toUTCString();

        const entry = `${id}=${value};expires=${expires};domain=${domain};path=${path}`;

        if (CookieStorage.get(id)) {
            CookieStorage.delete(id, domain, path);
        }

        document.cookie = entry;
    }
}
