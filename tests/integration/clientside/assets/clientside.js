if (!window.dash_clientside) {
    window.dash_clientside = {}
}
window.dash_clientside.clientside = {

    add: function(a, b) {
        return window.R.add(a, b);
    },

    display: function (value) {
        return 'Client says "' + value + '"';
    },

    mean: function (...args) {
        return R.mean(args);
    },

    add1_break_at_11: function (value) {
        if (parseInt(value, 10) === 11) {
            throw new Error('Unexpected error');
        }
        return parseInt(value, 10) + 1;
    },

    add1_prevent_at_11: function (value1, value2) {
        if (parseInt(value1, 10) === 11) {
            throw window.dash_clientside.PreventUpdate;
        }
        return parseInt(value2, 10) + 1;
    },

    add1_no_update_at_11: function (value1, value2, value3) {
        if (parseInt(value1, 10) === 11) {
            return [window.dash_clientside.no_update, parseInt(value3, 10) + 1];
        }
        return [parseInt(value2, 10) + 1, parseInt(value3, 10) + 1];
    },

    add_to_four_outputs: function(value) {
        return [
            parseInt(value) + 1,
            parseInt(value) + 2,
            parseInt(value) + 3,
            parseInt(value) + 4
        ]
    },

    side_effect_and_return_a_promise: function(value) {
        return new Promise(function(resolve, reject) {
            setTimeout(function() {
                setTimeout(function() {
                    document.getElementById('side-effect').innerText = (
                        'side effect'
                    );
                }, 100);
                resolve('foo');
            }, 1);
        });
    },

    triggered_to_str: function(n_clicks0, n_clicks1) {
        const triggered = dash_clientside.callback_context.triggered;
        return triggered.map(t => `${t.prop_id} = ${t.value}`).join(', ');
    },

    inputs_to_str: function(n_clicks0, n_clicks1) {
        const inputs = dash_clientside.callback_context.inputs;
        const keys = Object.keys(inputs);
        return keys.map(k => `${k} = ${inputs[k]}`).join(', ');
    },

    inputs_list_to_str: function(n_clicks0, n_clicks1) {
        return JSON.stringify(dash_clientside.callback_context.inputs_list);
    },

    states_to_str: function(val0, val1, st0, st1) {
        const states = dash_clientside.callback_context.states;
        const keys = Object.keys(states);
        return keys.map(k => `${k} = ${states[k]}`).join(', ');
    },

    states_list_to_str: function(val0, val1, st0, st1) {
        return JSON.stringify(dash_clientside.callback_context.states_list);
    },

    input_output_callback: function(inputValue) {
        const triggered = dash_clientside.callback_context.triggered;
        if (triggered.length==0){
            return inputValue;
        } else {
            return inputValue + 1;
        }
    },

    input_output_follower: function(inputValue) {
        if (!window.callCount) {
            window.callCount = 0
        }
        window.callCount += 1;
        return inputValue.toString();
    },

    chained_promise: function (inputValue) {
        return new Promise(function (resolve) {
            setTimeout(function () {
                resolve(inputValue + "-chained");
            }, 100);
        });
    },

    delayed_promise: function (inputValue) {
        return new Promise(function (resolve) {
            window.callbackDone = function (deferredValue) {
                resolve("clientside-" + inputValue + "-" + deferredValue);
            };
        });
    },

    non_delayed_promise: function (inputValue) {
        return new Promise(function (resolve) {
            resolve("clientside-" + inputValue);
        });
    },
};
