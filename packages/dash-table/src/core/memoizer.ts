type ResultFn = (...args: any[]) => any;

function isEqualArgs(args1: any[] | null, args2: any[]): boolean {
    return (
        !!args1 &&
        args1.length === args2.length &&
        !!args1.every((arg, index) => arg === args2[index])
    );
}

export const memoizeOne: ResultFn = (resultFn: ResultFn) => {
    let lastArgs: any[] | null = null;
    let lastResult: any;

    return (...args: any[]) => {
        return isEqualArgs(lastArgs, args) ?
            lastResult :
            (lastArgs = args) && (lastResult = resultFn(...args));
    };
};

export const memoizeAll: ResultFn = (resultFn: ResultFn) => {
    let cache: { args: any[], result: any }[] = [];

    return (...args: any[]) => {
        let entry = cache.find(e => isEqualArgs(e.args, args));

        return entry ?
            entry.result :
            cache.push({ args, result: resultFn(...args) }) && cache.slice(-1)[0].result;
    };
};