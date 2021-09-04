declare module 'sheetclip' {
    const value: {
        prototype: {
            parse: (text: string) => string[][];
            stringify: (arr: any[][]) => string;
        }
    };

    export default value;
}

declare module 'fast-isnumeric' {
    const value: (value: any) => boolean;

    export default value;
}

declare class Remarkable {
    constructor(options?: any);
    render(value: string): any;
}

declare interface RemarkableCtor {
    new(options?: any): Remarkable;
}

declare module 'remarkable' {
    export const Remarkable: RemarkableCtor;
}
