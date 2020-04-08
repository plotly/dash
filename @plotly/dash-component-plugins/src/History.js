const ON_CHANGE = '_dashprivate_historychange';

export default class History {
    static dispatchChangeEvent() {
        window.dispatchEvent(new CustomEvent(ON_CHANGE));
    }

    static onChange(listener) {
        window.addEventListener(ON_CHANGE, listener);

        return () => window.removeEventListener(ON_CHANGE, listener);
    }
}