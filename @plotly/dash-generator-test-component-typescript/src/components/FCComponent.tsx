import React from 'react';
import { TypescriptComponentProps } from '../props';

const FCComponent: React.FC<TypescriptComponentProps> = (props) => (
    <div>{props.children}</div>
);

export default FCComponent;
