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
    }

}
