function isPlainObject(candidate: any) {
    return candidate !== undefined &&
        candidate !== null &&
        typeof candidate === 'object' &&
        candidate.constructor === Object;
}

export function isEqual(obj1: object, obj2: object, deep: boolean = false) {
    return obj1 === obj2 || isEqualArgs(
        Object.values(obj1),
        Object.values(obj2),
        deep
    );
}

export function isEqualArgs(args1: any[] | null, args2: any[], deep: boolean = false): boolean {
    return (
        !!args1 &&
        args1.length === args2.length &&
        !!args1.every((arg1, index) => {
            const arg2 = args2[index];

            return arg1 === arg2 || (deep && (
                (Array.isArray(arg1) && Array.isArray(arg2) && isEqualArgs(arg1, arg2, deep)) ||
                (isPlainObject(arg1) && isPlainObject(arg2) && isEqual(arg1, arg2, deep))
            ));
        })
    );
}