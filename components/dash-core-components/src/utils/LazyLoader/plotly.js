export default (config) => {
    let url;
    if (config.serve_locally) {
        url = `${config.requests_pathname_prefix}_dash-component-suites/plotly/package_data/plotly.min.js`;
    } else {
        url = config.plotlyjs_url;
    }
    return Promise.resolve(window.Plotly || new Promise((resolve, reject) => {
        /* eslint-disable prefer-const */
        let timeoutId;

        const element = document.createElement('script');
        element.src = url;
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
            reject(new Error(`${url} did not load after 30 seconds`));
        }, 3 * 10 * 1000);

        document.querySelector('body').appendChild(element);
    }));
}
