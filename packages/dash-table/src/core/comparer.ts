export function isEqual(obj1: object, obj2: object) {
    return (
        obj1 === obj2 || isEqualArgs(Object.values(obj1), Object.values(obj2))
    );
}

export function isEqualArgs(args1: any[] | null, args2: any[]): boolean {
    if (!args1) {
        return false;
    }

    const _args1_ = args1.length;
    if (_args1_ !== args2.length) {
        return false;
    }

    for (let i = 0; i < _args1_; ++i) {
        if (args1[i] !== args2[i]) {
            return false;
        }
    }

    return true;
}
