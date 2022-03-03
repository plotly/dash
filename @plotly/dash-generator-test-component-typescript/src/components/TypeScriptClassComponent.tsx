import React from 'react';
import {TypescriptComponentProps} from '../props';

/**
 * Description
 * Example:
 * ```
 * @app.callback("clicks@btn")
 * def on_click(*args):
 *     return 1
 * ```
 */
export default class TypeScriptClassComponent extends React.PureComponent<TypescriptComponentProps> {
    render() {
        const {required_string, id} = this.props;
        return (
            <div className='typescript-class-component' id={id}>
                {required_string}
            </div>
        );
    }

    static defaultProps = {
        string_default: 'default',
        number_default: 42,
        bool_default: false,
        null_default: null,
        obj_default: {
            a: 'a',
            b: 3
        }
    };
}
