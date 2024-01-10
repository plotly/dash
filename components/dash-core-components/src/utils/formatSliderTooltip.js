import {replace} from 'ramda';

export const formatSliderTooltip = (template, value) => {
    return replace('{value}', value, template);
};
