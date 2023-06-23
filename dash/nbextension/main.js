// file my_extension/main.js

define([
    'base/js/namespace',
    'base/js/utils',
], function(Jupyter, utils){

    function load_ipython_extension(){
        var notebookUrl = window.location.href
        var baseUrl = utils.get_body_data('baseUrl');
        var baseNotebooks = baseUrl + "notebooks"
        var n = notebookUrl.search(baseNotebooks)
        var jupyterServerUrl = notebookUrl.slice(0, n)

        var register_comm = function() {
            Jupyter.notebook.kernel.comm_manager.register_target('dash',
                function (comm, msg) {
                    // Register handlers for later messages:
                    comm.on_msg(function (msg) {
                        console.log("Dash message", msg);
                        var msgData = msg.content.data;
                        if (msgData.type === 'base_url_request') {
                            comm.send({
                                type: 'base_url_response',
                                server_url: jupyterServerUrl,
                                base_subpath: baseUrl,
                                frontend: "notebook"
                            });
                        } else if (msgData.type === 'show') {

                        }
                    });
                });
        };

        Jupyter.notebook.events.on('kernel_ready.Kernel', register_comm)
    }

    return {
        load_ipython_extension: load_ipython_extension
    };
});
