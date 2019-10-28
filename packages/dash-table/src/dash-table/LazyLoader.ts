export default class LazyLoader {
    public static get xlsx() {
        return import(/* webpackChunkName: "export", webpackMode: "$${{mode}}" */ 'xlsx');
    }

    public static table() {
        return import(/* webpackChunkName: "table", webpackMode: "$${{mode}}" */ 'dash-table/dash/fragments/DataTable');
    }
}