export default (
    dropdown: HTMLElement | null,
    cell: HTMLElement | null = null
) => {
    cell =
        cell ||
        (() => {
            cell = dropdown;

            while (cell && cell.nodeName.toLowerCase() !== 'td') {
                cell = cell.parentElement;
            }

            return cell;
        })();

    if (!dropdown || !cell) {
        return;
    }

    let positionalParent = dropdown;
    while (
        getComputedStyle(positionalParent).position !== 'relative' &&
        getComputedStyle(positionalParent).position !== 'sticky'
    ) {
        if (!positionalParent.parentElement) {
            break;
        }

        positionalParent = positionalParent.parentElement;
    }

    let relativeParent = dropdown;
    while (getComputedStyle(relativeParent).position !== 'relative') {
        if (!relativeParent.parentElement) {
            break;
        }

        relativeParent = relativeParent.parentElement;
    }

    const positionalBounds = positionalParent.getBoundingClientRect();
    const relativeBounds = relativeParent.getBoundingClientRect();

    const parentBounds = cell.getBoundingClientRect();

    const left =
        parentBounds.left - positionalBounds.left + positionalParent.scrollLeft;
    const top =
        parentBounds.top -
        positionalBounds.top +
        positionalParent.scrollTop +
        parentBounds.height;

    dropdown.style.width = `${parentBounds.width}px`;
    dropdown.style.top = `${top}px`;
    dropdown.style.left = `${left}px`;
    dropdown.style.position = 'absolute';

    if (
        parentBounds.top + parentBounds.height / 2 > relativeBounds.bottom ||
        parentBounds.top - parentBounds.height / 2 < relativeBounds.top ||
        parentBounds.left < relativeBounds.left ||
        parentBounds.left + 0.25 * parentBounds.width >
            relativeBounds.left + relativeBounds.width
    ) {
        dropdown.style.display = 'none';
    } else {
        dropdown.style.display = 'block';
    }
};
