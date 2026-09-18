import type {HLJSApi} from 'highlight.js';

declare global {
    interface Window {
        hljs?: HLJSApi;
    }
}

// Reuse a highlight.js instance already on `window` (e.g. supplied by the host
// page), otherwise lazily load the bundled third-party build.
export default function lazyLoadHljs(): Promise<HLJSApi> {
    return Promise.resolve(
        window.hljs ??
            import(/* webpackChunkName: "highlight" */ './highlight').then(
                mod => mod.default as HLJSApi
            )
    );
}
