export default () => Promise.resolve(window.MathJax ||
    import(/* webpackChunkName: "mathjax" */ 'mathjax/es5/tex-svg.js').then(() => {
        window.MathJax.config.startup.typeset = false;

        return window.MathJax;
    })
);
