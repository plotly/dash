export default (seed: number | undefined = undefined) => {
    const lcg = (a: number) => (a * 48271) % 2147483647;

    let safeSeed = seed !== undefined ? lcg(seed) : lcg(Math.random());

    return () => (safeSeed = lcg(safeSeed)) / 2147483648;
};
