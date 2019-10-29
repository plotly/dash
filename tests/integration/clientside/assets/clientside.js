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
    }

}
