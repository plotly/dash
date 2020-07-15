declare module 'cookie' {
    const value: {
        parse: (cookie: string) => {
            _csrf_token: string
        }
    };

    export default value;
}

declare module 'fast-isnumeric' {
    const value: (value: any) => boolean;

    export default value;
}