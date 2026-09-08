export type DashConfig = {
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
    fetch: {
        credentials: string;
        headers: {
            Accept: string;
            'Content-Type': string;
        };
    };
    serve_locally?: boolean;
    plotlyjs_url?: string;
    validate_callbacks: boolean;
    websocket?: {
        enabled: boolean;
        url: string;
        worker_url: string;
        inactivity_timeout?: number;
        heartbeat_interval?: number;
    };
    stream?: {
        enabled: boolean;
    };
    csrf_token_name?: string;
    csrf_header_name?: string;
    // Server-issued, server-signed token for this page load. Echoed on every
    // callback request so the server can bind/verify background-callback
    // handles (cacheKey/job) to this page load. Treated as an opaque string.
    // (Unrelated to the client-side rendererId used for SharedWorker routing.)
    end_id?: string;
};

export default function getConfigFromDOM(): DashConfig {
    const configElement = document.getElementById('_dash-config');
    return JSON.parse(
        configElement?.textContent ? configElement?.textContent : '{}'
    );
}
