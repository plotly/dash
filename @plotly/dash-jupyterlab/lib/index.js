"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const application_1 = require("@jupyterlab/application");
const coreutils_1 = require("@jupyterlab/coreutils");
const notebook_1 = require("@jupyterlab/notebook");
const console_1 = require("@jupyterlab/console");
const widgets_1 = require("@lumino/widgets");
require("../style/index.css");
class DashIFrameWidget extends widgets_1.Widget {
    /**
     * Construct a new DashIFrameWidget.
     */
    constructor(port, url) {
        super();
        this.id = port;
        this.title.label = `Dash (port: ${port})`;
        this.title.closable = true;
        this.addClass('jp-dashWidget');
        // Add jp-IFrame class to keep drag events from being lost to the iframe
        // See https://github.com/phosphorjs/phosphor/issues/305
        // See https://github.com/jupyterlab/jupyterlab/blob/master/packages/apputils/style/iframe.css#L17-L35
        this.addClass('jp-IFrame');
        const serviceUrl = url;
        const iframeElement = document.createElement('iframe');
        iframeElement.setAttribute('baseURI', serviceUrl);
        this.iframe = iframeElement;
        this.iframe.src = serviceUrl;
        this.iframe.id = 'iframe-' + this.id;
        this.node.appendChild(this.iframe);
    }
    /**
     * Handle update requests for the widget.
     */
    onUpdateRequest(msg) {
        this.iframe.src += '';
    }
}
function activate(app, restorer, notebooks, consoles) {
    // Declare a widget variable
    let widgets = new Map();
    // Watch notebook creation
    notebooks.widgetAdded.connect((sender, nbPanel) => {
        // const session = nbPanel.session;
        const sessionContext = nbPanel.sessionContext;
        sessionContext.ready.then(() => {
            const session = sessionContext.session;
            let kernel = session.kernel;
            registerCommTarget(kernel, widgets, app);
        });
    });
    // Watch console creation
    consoles.widgetAdded.connect((sender, consolePanel) => {
        const sessionContext = consolePanel.sessionContext;
        sessionContext.ready.then(() => {
            const session = sessionContext.session;
            let kernel = session.kernel;
            registerCommTarget(kernel, widgets, app);
        });
    });
}
function registerCommTarget(kernel, widgets, app) {
    kernel.registerCommTarget('dash', (comm, msg) => {
        comm.onMsg = (msg) => {
            let msgData = msg.content.data;
            if (msgData.type === 'show') {
                let widget;
                if (!widgets.has(msgData.port)) {
                    // Create a new widget
                    widget = new DashIFrameWidget(msgData.port, msgData.url);
                    widget.update();
                    widgets.set(msgData.port, widget);
                    // Add instance tracker stuff
                }
                else {
                    widget = widgets.get(msgData.port);
                }
                if (!widget.isAttached) {
                    // Attach the widget to the main work area
                    // if it's not there
                    app.shell.add(widget, 'main');
                    widget.update();
                }
                else {
                    // Refresh the widget
                    widget.update();
                }
                // Activate the widget
                app.shell.activateById(widget.id);
            }
            else if (msgData.type === 'base_url_request') {
                // Build server url and base subpath.
                const baseUrl = coreutils_1.PageConfig.getBaseUrl();
                const baseSubpath = coreutils_1.PageConfig.getOption('baseUrl');
                const n = baseUrl.lastIndexOf(baseSubpath);
                const serverUrl = baseUrl.slice(0, n);
                comm.send({
                    type: 'base_url_response',
                    server_url: serverUrl,
                    base_subpath: baseSubpath,
                    frontend: "jupyterlab",
                });
            }
        };
    });
}
/**
 * Initialization data for the jupyterlab-dash extension.
 */
const extension = {
    id: 'jupyterlab_dash',
    autoStart: true,
    requires: [application_1.ILayoutRestorer, notebook_1.INotebookTracker, console_1.IConsoleTracker],
    activate: activate
};
exports.default = extension;
