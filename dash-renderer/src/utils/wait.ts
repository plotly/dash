export default async (duration: number) => {
    let _resolve: any;
    const p = new Promise(resolve => (_resolve = resolve));

    setTimeout(_resolve, duration);

    return p;
};
