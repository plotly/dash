export default (mathjax) => Promise.resolve(window.MathJax || (
    mathjax === false ?
        undefined :
        import(/* webpackChunkName: "mathjax" */ 'mathjax/es5/tex-svg.js').then(() => {
            window.MathJax.config.startup.typeset = false;

            return window.MathJax;
        })
));
