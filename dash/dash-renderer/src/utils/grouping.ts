import {GroupingIndices} from '../types/callbacks';

/**
 * Grouping utilities mirroring dash/_grouping.py, operating on the
 * index-groupings serialized into the callback spec (`outputs_indices`,
 * `inputs_state_indices`): structures of plain numbers, arrays and objects
 * whose leaves are indices into a flat dependency list.
 */

/**
 * Build a value grouping with the same shape as `grouping`, replacing each
 * leaf index i with fn(i).
 */
export function mapGrouping(
    fn: (index: number) => any,
    grouping: GroupingIndices
): any {
    if (Array.isArray(grouping)) {
        return grouping.map(g => mapGrouping(fn, g));
    }
    if (typeof grouping === 'object' && grouping !== null) {
        const mapped: {[key: string]: any} = {};
        for (const key of Object.keys(grouping)) {
            mapped[key] = mapGrouping(fn, grouping[key]);
        }
        return mapped;
    }
    return fn(grouping);
}

function schemaPathError(
    schema: GroupingIndices,
    path: (string | number)[],
    detail: string
): Error {
    return new Error(
        'Callback return value does not match the declared output grouping.\n' +
            `Path: ${JSON.stringify(path)}\n` +
            `Expected shape: ${JSON.stringify(schema)}\n` +
            detail
    );
}

/**
 * Inverse of mapGrouping: walk `grouping` and `value` together, placing each
 * leaf of `value` into a flat array at the leaf's index. Validates that
 * `value` matches the shape of `grouping` (mirrors validate_grouping in
 * dash/_grouping.py) and throws a descriptive Error on mismatch. Leaves of
 * the schema are numbers, so leaf values that are themselves arrays or
 * objects (pattern-matching ALL values, no_update sentinels, dict props) are
 * unambiguous.
 */
export function flattenGroupingByIndex(
    grouping: GroupingIndices,
    value: any,
    flatLength: number,
    path: (string | number)[] = []
): any[] {
    const flat: any[] = new Array(flatLength);
    const fill = (
        schema: GroupingIndices,
        val: any,
        currentPath: (string | number)[]
    ) => {
        if (Array.isArray(schema)) {
            if (!Array.isArray(val)) {
                throw schemaPathError(
                    schema,
                    currentPath,
                    `Expected an array, received: ${JSON.stringify(val)}`
                );
            }
            if (val.length !== schema.length) {
                throw schemaPathError(
                    schema,
                    currentPath,
                    `Expected an array of length ${schema.length}, ` +
                        `received one of length ${val.length}`
                );
            }
            schema.forEach((s, i) => fill(s, val[i], currentPath.concat(i)));
        } else if (typeof schema === 'object' && schema !== null) {
            const expectedKeys = Object.keys(schema);
            if (typeof val !== 'object' || val === null || Array.isArray(val)) {
                throw schemaPathError(
                    schema,
                    currentPath,
                    `Expected an object with keys ${JSON.stringify(
                        expectedKeys
                    )}, received: ${JSON.stringify(val)}`
                );
            }
            const receivedKeys = Object.keys(val);
            if (
                expectedKeys.length !== receivedKeys.length ||
                expectedKeys.some(k => !(k in val))
            ) {
                throw schemaPathError(
                    schema,
                    currentPath,
                    `Expected an object with keys ${JSON.stringify(
                        expectedKeys
                    )}, received keys ${JSON.stringify(receivedKeys)}`
                );
            }
            expectedKeys.forEach(k =>
                fill(schema[k], val[k], currentPath.concat(k))
            );
        } else {
            flat[schema] = val;
        }
    };
    fill(grouping, value, path);
    return flat;
}
