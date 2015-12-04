$(document).ready(function(){

    // Record and send the state when inputs change
    $('input, select').each(function(i, obj) {
        if(obj.type==="checkbox" || obj.type==="radio"){
            $(obj).change(function(){
                console.log(getState());
                sendState({}, {});
            });
        } else {
            obj.oninput = function(){
                if($(obj).hasClass("show-output")){
                    $('output[for='+obj.name+']')[0].value = obj.value;
                }
                console.log(getState());
                sendState({}, {});
            };
        }
    });
});

function getState(payload) {
    var payload = payload || {};
    $('input').each(function(i, el) {
        if (el.type==="radio") {
            var value = $('input[name='+el.name+']:checked').val();
            if(typeof value === "undefined"){
                value = null;
            }
            payload[el.name] = value;
        } else if (el.type==="checkbox") {
            payload[el.name] = $(el).is(':checked');
        } else if (el.type==="text") {
            payload[el.name] = el.value;
        } else {
            payload[el.name] = el.value;
        }
    });
    $('select').each(function(i, el) {
        payload[el.name] = el.value;
    });
    return payload;
}

function sendState(that, payload){
    var payload = payload || {};
    payload = getState(payload);
    socket.emit('replot', payload);
}
