import * as React from 'react';
import {TypescriptComponentProps} from '../props';

/**
 * Description
 * Example:
 * ```
 * @app.callback(...)
 * def on_click(*args):
 *     return 1
 * ```
 */
const MemoTypeScriptComponent = (props: TypescriptComponentProps) => (
    <div id={props.id}>{props.required_string}</div>
);

export default React.memo(MemoTypeScriptComponent, () => true);
