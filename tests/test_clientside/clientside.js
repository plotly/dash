window.clientside = {

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

    add_to_four_outputs: function(value) {
        return [
            parseInt(value) + 1,
            parseInt(value) + 2,
            parseInt(value) + 3,
            parseInt(value) + 4
        ]
    }

}
