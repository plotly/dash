type Config = {
    url_base_pathname: string;
    requests_pathname_prefix: string;
    ui: boolean;
    props_check: boolean;
    show_undo_redo: boolean;
    suppress_callback_exceptions: boolean;
    update_title: string;
    hot_reload?: {
        interval: number;
        max_retry: number;
    };
    validation_layout: any;
    children_props: {[k: string]: {[k: string]: string[]}};
};

const configElement = document.getElementById('_dash-config');

const config: Config = JSON.parse(
    configElement?.textContent ? configElement?.textContent : '{}'
);

export default config;
