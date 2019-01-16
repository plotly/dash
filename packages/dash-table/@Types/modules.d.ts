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