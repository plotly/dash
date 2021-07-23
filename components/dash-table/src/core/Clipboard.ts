export default class Clipboard {
    /*#if TEST_COPY_PASTE*/
    private static value: string;
    /*#endif*/

    public static set(_ev: any, value: string): void {
        /*#if TEST_COPY_PASTE*/
        Clipboard.value = value;
        /*#else*/
        _ev.clipboardData.setData('text/plain', value);
        _ev.preventDefault();
        /*#endif*/
    }

    public static get(_ev: ClipboardEvent) {
        let value;

        /*#if TEST_COPY_PASTE*/
        value = Clipboard.value;
        /*#else*/
        value = _ev.clipboardData
            ? _ev.clipboardData.getData('text/plain')
            : undefined;
        /*#endif*/

        return value;
    }
}
