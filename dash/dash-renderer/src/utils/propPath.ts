/**
 * Read a dictionary/list location without copying or changing the source value.
 * Like Patch locations, negative indices are relative to the current list.
 * String keys select own dictionary properties; integers select list entries.
 * Missing or incompatible locations return undefined. Empty paths select the
 * entire value. Iteration takes O(path.length) time and O(1) extra space; it
 * never traverses siblings or clones the selected subtree.
 */
export function resolvePropPath(
    value: unknown,
    path: (string | number)[]
): unknown {
    if (!Array.isArray(path)) {
        return undefined;
    }

    let current = value;
    for (const key of path) {
        if (Array.isArray(current)) {
            if (typeof key !== 'number' || !Number.isSafeInteger(key)) {
                return undefined;
            }
            const index = key < 0 ? current.length + key : key;
            if (
                index < 0 ||
                index >= current.length ||
                !Object.prototype.hasOwnProperty.call(current, index)
            ) {
                return undefined;
            }
            current = current[index];
        } else if (
            current !== null &&
            typeof current === 'object' &&
            typeof key === 'string' &&
            Object.prototype.hasOwnProperty.call(current, key)
        ) {
            current = (current as Record<string, unknown>)[key];
        } else {
            return undefined;
        }
    }
    return current;
}
