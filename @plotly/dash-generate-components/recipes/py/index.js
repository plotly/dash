function toPython(value) {
    if (value === true) {
        return 'True';
    } else if (value === false) {
        return 'False';
    } else if (value === null) {
        return 'None';
    } else {
        return `"${value}"`;
    }
}

function getJsDist(dist, js_name, py_name, version) {
    let str = '{\n';
    str += `    "relative_package_path": "${dist.target}",\n`;
    str += `    "namespace": "${py_name}",\n`;
    if (dist.async !== undefined) {
        str += `    "async": ${toPython(dist.async)},\n`;
    }
    if (dist.dynamic !== undefined) {
        str += `    "dynamic": ${toPython(dist.dynamic)},\n`;
    }
    if (dist.external) {
        str += `    "external_url": "https://unpkg.com/${js_name}/${dist.source}"\n`
    }
    str += '}';

    return str;
}

function filterJsDist(dist) {
    return dist.filter(d => !d.recipe);
}

function stringify(value) {
    return JSON.stringify(value, null, '  ');
}

module.exports = {
    filterJsDist,
    getJsDist,
    stringify
};