'use strict';

var http = require('http');
var ecstatic = require('ecstatic');
var Server = require('agora').Server;

var staticOptions = { root: __dirname + '/static' };
var staticServer = http.createServer(ecstatic(staticOptions));
var wsServer = new Server({ port: 8000 });

wsServer.on('connection', function registerListeners (conn) {
    var id = conn.id;

    /* returned inStream is an emitter */
    var inStream = conn.inStream;

    /* you can emit to the outStream and data will be piped off to the client */
    var outStream = conn.outStream;

    /*
     * listen on a per client basis
     * in this case, we listen for the 'addOne' event from the client,
     * and we can wrangle it, then send it back with an 'addResult' event
     */
    inStream.on('addOne', function (input) {

        var output = input + 1;

        wsServer.emitTo(outStream, 'addResult', output);
    });

    /* emit to one client */
    wsServer.emitTo(outStream, 'ready', id);
});

staticServer.listen(8080);
