export default class LazyLoader {
    public static get xlsx() {
        return import(/* webpackChunkName: "export", webpackMode: "$${{mode}}" */ 'xlsx');
    }
}