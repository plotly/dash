import {replace, path, split, concat, pipe} from 'ramda';

export const formatSliderTooltip = (template, value) => {
    return replace('{value}', value, template);
};

export const transformSliderTooltip = (funcName, value) => {
    const func = pipe(
        split('.'),
        s => concat(['dccFunctions'], s),
        s => path(s, window)
    )(funcName);
    if (!func) {
        throw new Error(
            `Invalid func for slider tooltip transform: ${funcName}`
        );
    }
    return func(value);
};
