export default (target: HTMLElement): Promise<number> => {
    const parent = document.createElement('div');
    parent.style.position = 'absolute';
    parent.style.visibility = 'hidden';
    parent.style.width = '100px';
    parent.style.height = '100px';
    parent.style.overflow = 'scroll';

    const child = document.createElement('div');
    child.style.width = '100px';
    child.style.height = '100px';

    parent.appendChild(child);
    target.appendChild(parent);

    return new Promise<number>(resolve => {
        setTimeout(() => {
            const width = child.clientWidth - parent.clientWidth;

            target.removeChild(parent);
            resolve(width);
        }, 0);
    });
};
