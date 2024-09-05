declare module 'cookie' {
    const value: {
        parse: (cookie: string) => {
            _csrf_token: string
        }
    };

    export default value;
}
