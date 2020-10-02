function toR(value) {
    if (value === true) {
        return 'TRUE';
    } else if (value === false) {
        return 'FALSE';
    } else if (value === null) {
        return 'None';
    } else {
        return `"${value}"`;
    }
}

function toAsync(value) {
    if (value === undefined || value === null) {
        return toR(false);
    } else if (typeof value === 'boolean') {
        return toR(value);
    }
}

module.exports = {
    toAsync,
    toR
};