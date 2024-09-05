export default (mathjax) => Promise.resolve(window.MathJax || (
    mathjax === false ?
        undefined :
        import(/* webpackChunkName: "mathjax" */ '../mathjax').then(() => window.MathJax)
));
