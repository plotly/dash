import {has} from 'ramda';

type PropPathKey = string | number;

function resolveArrayKey(value: unknown[], key: PropPathKey): unknown {
    if (typeof key !== 'number' || !Number.isSafeInteger(key)) {
        return undefined;
    }

    const index = key < 0 ? value.length + key : key;
    if (index < 0 || index >= value.length || !has(String(index), value)) {
        return undefined;
    }

    return value[index];
}

function resolveObjectKey(value: object, key: PropPathKey): unknown {
    if (typeof key !== 'string' || !has(key, value)) {
        return undefined;
    }

    return (value as Record<string, unknown>)[key];
}

/**
 * Read a dictionary/list location without copying or changing the source value.
 * Like Patch locations, negative indices are relative to the current list.
 * String keys select own dictionary properties; integers select list entries.
 * Missing or incompatible locations return undefined. Empty paths select the
 * entire value. Iteration takes O(path.length) time and O(1) extra space; it
 * never traverses siblings or clones the selected subtree.
 */
export function resolvePropPath(value: unknown, path: PropPathKey[]): unknown {
    if (!Array.isArray(path)) {
        return undefined;
    }

    let current = value;
    for (const key of path) {
        if (Array.isArray(current)) {
            current = resolveArrayKey(current, key);
            continue;
        }
        if (current === null || typeof current !== 'object') {
            return undefined;
        }
        current = resolveObjectKey(current, key);
    }
    return current;
}
