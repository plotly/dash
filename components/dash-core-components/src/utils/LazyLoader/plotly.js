export default () => {
    return Promise.resolve(window.Plotly || new Promise((resolve, reject) => {
        /* eslint-disable prefer-const */
        let timeoutId;

        const element = document.createElement('script');
        element.src = window._dashPlotlyJSURL;
        element.async = true;
        element.onload = () => {
            clearTimeout(timeoutId);
            resolve();
        };
        element.onerror = (error) => {
            clearTimeout(timeoutId);
            reject(error);
        };

        timeoutId = setTimeout(() => {
            element.src = '';
            reject(new Error(`plotly.js did not load after 30 seconds`));
        }, 3 * 10 * 1000);

        document.querySelector('body').appendChild(element);
    }));
}
