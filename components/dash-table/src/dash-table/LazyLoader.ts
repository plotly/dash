export default class LazyLoader {
    public static get xlsx() {
        return import(
            /* webpackChunkName: "export", webpackMode: "$${{mode}}" */ 'xlsx'
        );
    }

    public static get hljs() {
        return Promise.resolve(
            (window as any).hljs ||
                import(
                    /* webpackChunkName: "highlight", webpackMode: "$${{mode}}" */ '../third-party/highlight.js'
                ).then(result => result.default)
        );
    }

    public static table() {
        return import(
            /* webpackChunkName: "table", webpackMode: "$${{mode}}" */ 'dash-table/dash/fragments/DataTable'
        );
    }
}
