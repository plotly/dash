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
    constructor();
    render(value: string): any;
}

declare module 'remarkable' {
    export default Remarkable;
}