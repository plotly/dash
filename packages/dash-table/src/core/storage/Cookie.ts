const __1day = 86400 * 1000;
const __20years = 86400 * 1000 * 365 * 20;

export default class CookieStorage {
    public static delete(id: string, domain: string = '', path: string = '/') {
        let expires = new Date((new Date().getTime() - __1day)).toUTCString();

        document.cookie = `${id}=;expires=${expires};domain=${domain};path=${path}`;
    }

    public static get(id: string) {
        if (!id.length) {
            return;
        }

        id = id.toLowerCase();

        let cookies = document.cookie.split(';').map(cookie => {
            let fragments = cookie.split('=');

            return {
                id: fragments[0].trim(),
                value: fragments[1]
            };
        });

        return (cookies.find(cookie => id === cookie.id.toLocaleLowerCase()) || {} as any).value;
    }

    public static set(id: string, value: string, domain: string = '', path: string = '/') {
        let expires = new Date((new Date().getTime() + __20years)).toUTCString();

        let entry = `${id}=${value};expires=${expires};domain=${domain};path=${path}`;

        if (CookieStorage.get(id)) {
            CookieStorage.delete(id, domain, path);
        }

        document.cookie = entry;
    }
}