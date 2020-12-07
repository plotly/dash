function isDetailedType(type) {
    const { name, value } = type;

    if (name === 'union') {
        return !!type.value.filter(v => isDetailedType(v)).length;
    }

    if (name === 'exact' || name === 'shape') {
        return true;
    }

    if (name === 'arrayOf') {
        const { name: nestedName } = value;

        return nestedName === 'exact' || nestedName === 'shape' || nestedName === 'arrayOf';
    }

    return false;
}


function toDefaultValue(value) {
    if (value === 'true') {
        return 'True';
    } else if (value === 'false') {
        return 'False';
    } else {
        return value;
    }
}

function isRequired(type, defaultValue) {
    if (!type.required && type.defaultValue) {
        console.log('*****', type);
    }
    return type.required ?
        'required' :
        defaultValue && ['[]', '{}'].indexOf(defaultValue.value) === -1 ?
            `default ${toDefaultValue(defaultValue.value)}` :
            'optional';
}

function resolveExactOrShape(type, indent = 0) {
    return typeof type.value !== 'object' ?
        '' :
        'those elements have the following types:\n' +
        Object.entries(type.value).map(([key, t]) => {
            let res = `${'  '.repeat(indent)}- ${key} (${resolveType(t)}; ${isRequired(t)})`;

            if (t.description) {
                res += `${t.description ? ': ' + t.description : ''}`;
            }

            if (isDetailedType(t)) {
                if (t.description) {
                    if (t.description.slice(-1) !== '.') {
                        res += '.';
                    }
                } else {
                    res += ':';
                }

                res += ` ${resolveDetailedType(t, key, indent)}`;
            }

            return res;
        }).join('\n')
}

function resolveDetailedType(type, key, indent = 0) {
    switch (type.name) {
        case 'arrayOf':
            // if (resolveDetailedType(type.value, indent) === '') {
            //     return '';
            // }
            return `${key} has the following type: ` +
                resolveType(type) +
                ` containing keys ` +
                resolveExactOrShape(type.value, indent + 1);
        case 'exact':
        case 'shape':
            return `${key} has the following type: ` +
                `dict containing keys ` +
                resolveExactOrShape(type, indent + 1);
        default:
            return '';
    }
}

function resolveType(type) {
    switch (type.name) {
        case 'any':
            return 'boolean | numeric | character | dict | list';
        case 'array':
            return 'list';
        case 'arrayOf':
            const innerType = resolveType(type.value);

            return 'List of ' + innerType[0].toLowerCase() + innerType.slice(1);
        case 'bool':
        case 'boolean':
            return 'boolean';
        case 'Element':
            return 'dash component';
        case 'enum':
            return 'a value equal to: ' +
                type.value.map(v => v.value).join(', ');
        case 'exact':
        case 'shape':
            return `List containing elements ${Object.keys(type.value).map(k=>`'${k}'`)}.`;
        case 'Node':
            return 'a list of or a singular dash component, character or numeric';
        case 'number':
            return 'numeric';
        case 'string':
            return 'character';
        case 'object':
        case 'Object':
            return 'dict';
        case 'objectOf':
            return resolveType(type.value);
        case 'union':
            return type
                .value
                .filter(v => v.value !== '')
                .map(resolveType)
                .join(' | ');
        default:
            return 'any';
    }
}

function getPropDescription(key, target) {
    const { defaultValue, description, type } = target;

    return `\\item{${key}}{${resolveType(type)}
${resolveExactOrShape(type)}. ${description}
}`.replace(/%/g, '\\%');
}

module.exports = {
    getPropDescription
};