import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { PageConfig } from '@jupyterlab/coreutils';

import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

import { KernelMessage, Kernel } from '@jupyterlab/services';

import { IConsoleTracker } from '@jupyterlab/console';

import { Message } from '@lumino/messaging';

import { Widget } from '@lumino/widgets';

import '../style/index.css';

class DashIFrameWidget extends Widget {
  /**
   * Construct a new DashIFrameWidget.
   */
  constructor(port: string, url: string) {
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
   * The image element associated with the widget.
   */
  readonly iframe: HTMLIFrameElement;

  /**
   * Handle update requests for the widget.
   */
  onUpdateRequest(msg: Message): void {
    this.iframe.src += '';
  }
}

interface DashMessageData {
  type: string;
  port: string;
  url: string;
}

function activate(
  app: JupyterFrontEnd,
  restorer: ILayoutRestorer,
  notebooks: INotebookTracker,
  consoles: IConsoleTracker
) {

  // Declare a widget variable
  let widgets = new Map<string, DashIFrameWidget>();

  // Watch notebook creation
  notebooks.widgetAdded.connect((sender, nbPanel: NotebookPanel) => {
    // const session = nbPanel.session;
    const sessionContext = nbPanel.sessionContext;
    sessionContext.ready.then(() => {
      const session = sessionContext.session;
      let kernel = session.kernel;
      registerCommTarget(kernel, widgets, app);
    })
  });

  // Watch console creation
  consoles.widgetAdded.connect((sender, consolePanel) => {
    const sessionContext = consolePanel.sessionContext;
    sessionContext.ready.then(() => {
      const session = sessionContext.session;
      let kernel = session.kernel;
      registerCommTarget(kernel, widgets, app);
    })
  });
}

function registerCommTarget(
  kernel: Kernel.IKernelConnection,
  widgets: Map<string, DashIFrameWidget>,
  app: JupyterFrontEnd
) {
  kernel.registerCommTarget(
    'dash',
    (comm: Kernel.IComm, msg: KernelMessage.ICommOpenMsg) => {
      comm.onMsg = (msg: KernelMessage.ICommMsgMsg) => {
        let msgData = (msg.content.data as unknown) as DashMessageData;
        if (msgData.type === 'show') {
          let widget: DashIFrameWidget;
          if (!widgets.has(msgData.port)) {
            // Create a new widget
            widget = new DashIFrameWidget(msgData.port, msgData.url);
            widget.update();
            widgets.set(msgData.port, widget);

            // Add instance tracker stuff
          } else {
            widget = widgets.get(msgData.port);
          }

          if (!widget.isAttached) {
            // Attach the widget to the main work area
            // if it's not there
            app.shell.add(widget, 'main');
            widget.update();
          } else {
            // Refresh the widget
            widget.update();
          }

          // Activate the widget
          app.shell.activateById(widget.id);
        } else if (msgData.type === 'base_url_request') {

          // Build server url and base subpath.
          const baseUrl = PageConfig.getBaseUrl();
          const baseSubpath = PageConfig.getOption('baseUrl');
          const n = baseUrl.lastIndexOf(baseSubpath)
          const serverUrl = baseUrl.slice(0, n)
          comm.send({
            type: 'base_url_response',
            server_url: serverUrl,
            base_subpath: baseSubpath,
            frontend: "jupyterlab",
          });
        }
      };
    }
  );
}

/**
 * Initialization data for the jupyterlab-dash extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab_dash',
  autoStart: true,
  requires: [ILayoutRestorer, INotebookTracker, IConsoleTracker],
  activate: activate
};

export default extension;
