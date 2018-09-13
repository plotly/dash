declare module 'sheetclip' {
    const value: {
        prototype: {
            parse: (text: string) => string[][];
            stringify: (arr: any[][]) => string;
        }
    };

    export default value;
}