var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);
$(document).ready(function(){

    function init_graph_obj(id){
        var obj = {
            graphContentWindow: $('#'+id)[0].contentWindow,
            id: id
        };
        obj.pinger = setInterval(function(){
            obj.graphContentWindow.postMessage({task: 'ping'}, 'https://plot.ly');
        }, 500);
        return obj;
    }

    var graphs = {};
    $('iframe').each(function(i, obj){
        graphs[obj.id] = init_graph_obj(obj.id);
    });

    //
    // Sockets
    //

    namespace = ''; // change to an empty string to use the global namespace

    // the socket.io documentation recommends sending an explicit package upon connection
    // this is specially important when using the global namespace

    socket.on('connect', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });

    socket.on('postMessage', function(msg_string) {
        $('.left-pane').show();
        $('.loading').hide();
        var msgs = JSON.parse(msg_string);
        for(var i=0; i<msgs.length; i++){
            graphs[msgs[i].id].graphContentWindow.postMessage(msgs[i], 'https://plot.ly');
        }
    });

    window.addEventListener('message', function(e){
        var message = e.data;
        var graph;
        for(var i in graphs) {
            if(graphs[i].graphContentWindow === e.source) {
                graph = graphs[i];
            }
        }
        if(typeof graph === "undefined") {
            return;
        }

        var pinger = graph.pinger;
        var graphContentWindow = graph.graphContentWindow;
        var id = graph.id;

        if('pong' in message && message.pong) {
            clearInterval(pinger);
            graphContentWindow.postMessage({
                'task': 'listen',
                'events': ['click']
            }, 'https://plot.ly');
            var payload = getState({});
            payload[id] = id;
            socket.emit('pong', payload);
        } else if (message.type==='hover' ||
                    message.type==='zoom'  ||
                    message.type==='click') {
            if(message.type !== 'zoom') {
                for(var i in message.points) {
                    delete message.points[i].data;
                }
            }
            sendState({}, {'click': message});
        }
    });
});
