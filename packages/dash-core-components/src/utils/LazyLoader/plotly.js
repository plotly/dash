export default () => Promise.resolve(window.Plotly ||
    import(/* webpackChunkName: "plotlyjs" */ 'plotly.js').then(({ default: Plotly }) => {
        window.Plotly = Plotly;
        return Plotly;
    }));

