import React from 'react';
import {TypescriptComponentProps} from '../props';

/**
 * Component docstring
 */
const TypeScriptComponent = (props: TypescriptComponentProps) => {
    const {required_string, id} = props;
    return <div id={id}>{required_string}</div>;
};

TypeScriptComponent.defaultProps = {
    string_default: 'default',
    number_default: 42,
    bool_default: true,
    null_default: null,
    obj_default: {
        a: 'a',
        b: 3
    }
};

export default TypeScriptComponent;
