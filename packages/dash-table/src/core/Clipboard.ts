export default class Clipboard {
    /*#if TEST_COPY_PASTE*/
    private static value: string;
    /*#endif*/

    public static set(value: string): void {
        /*#if TEST_COPY_PASTE*/
        Clipboard.value = value;
        /*#endif*/

        const el = document.createElement('textarea');
        el.value = value;

        // (Adapted from https://hackernoon.com/copying-text-to-clipboard-with-javascript-df4d4988697f)
        // Make it readonly to be tamper-proof
        el.setAttribute('readonly', '');
        // el.style.position = 'absolute';
        // Move outside the screen to make it invisible
        // el.style.left = '-9999px';
        // Append the <textarea> element to the HTML document
        document.body.appendChild(el);

        // Check if there is any content selected previously
        let selected;
        if (document.getSelection().rangeCount > 0) {
            // Store selection if found
            selected = document.getSelection().getRangeAt(0);
        }

        // Select the <textarea> content
        el.select();
        // Copy - only works as a result of a user action (e.g. click events)
        document.execCommand('copy');
        // Remove the <textarea> element
        document.body.removeChild(el);
        // If a selection existed before copying
        if (selected) {
            // Unselect everything on the HTML document
            document.getSelection().removeAllRanges();
            // Restore the original selection
            document.getSelection().addRange(selected);
        }
    }

    public static get(_ev: ClipboardEvent) {
        let value;

        /*#if TEST_COPY_PASTE*/
        value = Clipboard.value;
        /*#else*/
        value = _ev.clipboardData ?
            _ev.clipboardData.getData('text/plain') :
            undefined;
        /*#endif*/

        return value;
    }
}