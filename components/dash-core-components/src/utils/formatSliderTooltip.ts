import {replace, path, split, concat, pipe} from 'ramda';

export const formatSliderTooltip = (template: string, value: string | number) => {
    return replace('{value}', `${value}`, template);
};

export const transformSliderTooltip = (funcName: string, value: string | number) => {
    type TransformFunc = (value: string | number) => string | number;
    const func = pipe(
        split('.'),
        s => concat(['dccFunctions'], s),
        s => path(s, window)
    )(funcName) as TransformFunc;
    if (!func) {
        throw new Error(
            `Invalid func for slider tooltip transform: ${funcName}`
        );
    }
    return func(value);
};
