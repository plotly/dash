export default () => Promise.resolve(window.hljs ||
    import(/* webpackChunkName: "highlight" */ '../../third-party/highlight.js').then(
        result => result.default
    ));
