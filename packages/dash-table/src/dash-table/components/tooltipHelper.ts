export const getPositionalParent = (el: HTMLElement | null = null) => {
    if (!el) {
        return;
    }

    let positionalParent = el;
    while (
        getComputedStyle(positionalParent).position !== 'relative' &&
        getComputedStyle(positionalParent).position !== 'sticky'
    ) {
        if (!positionalParent.parentElement) {
            break;
        }

        positionalParent = positionalParent.parentElement;
    }

    return positionalParent;
};
