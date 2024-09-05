export default class DOM {
    public static getFirstParentOfType(
        element: HTMLElement | undefined,
        type: string
    ): HTMLElement | undefined {
        type = type.toUpperCase();

        let current: HTMLElement | undefined = element;
        while (current) {
            if (current.tagName.toUpperCase() === type) {
                return current;
            }

            if (current.parentElement !== null) {
                current = current.parentElement;
            } else {
                return;
            }
        }
    }

    public static getParentById(
        element: HTMLElement | undefined,
        id: string
    ): HTMLElement | undefined {
        let current: HTMLElement | undefined = element;
        while (current) {
            if (current.id === id) {
                return current;
            }

            if (current.parentElement !== null) {
                current = current.parentElement;
            } else {
                return;
            }
        }
    }
}
