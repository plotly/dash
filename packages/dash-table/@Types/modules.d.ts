declare module 'sheetclip' {
    const value: {
        prototype: {
            parse: (text: string) => string[][];
        }
    };

    export default value;
}