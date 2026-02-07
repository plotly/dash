import React from 'react';
import {TypescriptComponentProps} from '../props';

/**
 * Component docstring
 */
const TypeScriptComponent = ({
  required_string,
  id,
  string_default = 'default',
  number_default = 42,
  bool_default = true,
  null_default = null,
  obj_default = { a: 'a', b: 3 },
  array_primitive_mix = 1,
  ...props
}: TypescriptComponentProps) => {
  return <div id={id}>{required_string}</div>;
};

export default TypeScriptComponent;
