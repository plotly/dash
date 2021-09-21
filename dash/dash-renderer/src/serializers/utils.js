import {type, has, prop} from 'ramda';

const PROP_TYPE = '__type';
const PROP_VALUE = '__value';

export function isSerializableComponent(componentDefinition) {
    return (
        type(componentDefinition) === 'Object' &&
        has(PROP_TYPE, componentDefinition) &&
        has(PROP_VALUE, componentDefinition)
    );
}

export function stripSerializedValue(componentDefinition) {
    return prop(PROP_VALUE, componentDefinition);
}
