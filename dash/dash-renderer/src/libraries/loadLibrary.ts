import {LibraryResource} from './libraryTypes';

export default function (resource: LibraryResource) {
    let prom;
    const head = document.querySelector('head');
    if (resource.type === '_js_dist') {
        const element = document.createElement('script');
        element.src = resource.url;
        element.async = true;
        prom = new Promise<void>((resolve, reject) => {
            element.onload = () => {
                resolve();
            };
            element.onerror = error => reject(error);
        });

        head?.appendChild(element);
    } else if (resource.type === '_css_dist') {
        const element = document.createElement('link');
        element.href = resource.url;
        element.rel = 'stylesheet';
        prom = new Promise<void>((resolve, reject) => {
            element.onload = () => {
                resolve();
            };
            element.onerror = error => reject(error);
        });
        head?.appendChild(element);
    }
    return prom;
}
