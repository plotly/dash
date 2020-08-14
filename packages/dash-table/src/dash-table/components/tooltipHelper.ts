export default (el: HTMLElement | null, parent: HTMLElement | null = null) => {
    parent =
        parent ||
        (() => {
            parent = el;

            while (parent && parent.nodeName.toLowerCase() !== 'td') {
                parent = parent.parentElement;
            }

            return parent;
        })();

    if (!el || !parent) {
        return {};
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

    let relativeParent = el;
    while (getComputedStyle(relativeParent).position !== 'relative') {
        if (!relativeParent.parentElement) {
            break;
        }

        relativeParent = relativeParent.parentElement;
    }

    return {positionalParent, parent};
};
