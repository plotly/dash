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

function contains(list, value) {
    return Array.isArray(list) && list.indexOf(value) >= 0;
}

module.exports = {
    contains,
    toAsync,
    toR
};