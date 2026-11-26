// The react-markdown 10 stack calls these at render time. They need Safari 15.4
// / Chrome 93, newer than our browserslist floor, and babel does not polyfill
// builtins.
const ObjectWithHasOwn = Object as ObjectConstructor & {
    hasOwn?: (obj: object, key: PropertyKey) => boolean;
};
if (!ObjectWithHasOwn.hasOwn) {
    ObjectWithHasOwn.hasOwn = (obj, key) =>
        Object.prototype.hasOwnProperty.call(obj, key);
}

if (!('at' in Array.prototype)) {
    // eslint-disable-next-line no-extend-native
    Object.defineProperty(Array.prototype, 'at', {
        configurable: true,
        writable: true,
        value: function at<T>(this: T[], index: number) {
            const i = Math.trunc(index) || 0;
            return this[i < 0 ? this.length + i : i];
        },
    });
}

export {};
