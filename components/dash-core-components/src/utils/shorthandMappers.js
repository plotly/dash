import {type} from "ramda";

/**
 * Converts shorthand option formats to the format ingestible by dropdown component
 * //todo: explain
 */
export const mapOptions = (options) => {
    if (type(options[0]) === 'String') {
        return options.map((option) => ({label: option, value: option}))
    }

    if (type(options) === 'Object') {
        return Object.entries(options).map(([label, value]) => ({label, value}))
    }

    return options
}
