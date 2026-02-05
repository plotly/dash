// Needs to export types if not in a d.ts file or if any import is present in the d.ts
import React from 'react';

type DashComponent = {
    props: string;
    namespace: string;
    children?: [];
}


type Nested = {
    nested: Nested;
}

export type TypescriptComponentProps = {
    children?: React.ReactNode;
    id?: string;
    /**
     * A string
     */
    required_string: string;
    a_string?: string;
    a_number?: number;
    a_bool?: boolean;
    obj?: {
        value: any;
        label?: string;
    };
    array_string?: string[];
    array_number?: number[];
    array_obj?: {a: string}[];
    array_any?: any[];
    enum_string?: 'one' | 'two';
    enum_number?: 2 | 3 | 4 | 5 | 6;
    union?: number | string;
    union_shape?: {a: string} | string;
    array_union_shape?: ({a: string} | string)[];
    array_primitive_mix?:
        | string
        | number
        | (string | number | boolean)[]
        | boolean;
    element?: JSX.Element;
    array_elements?: JSX.Element[];
    dash_component?: DashComponent;

    string_default?: string;
    number_default?: number;
    obj_default?: {a: string; b: number};
    bool_default?: boolean;
    null_default?: any;

    setProps?: (props: Record<string, any>) => void;
    className?: string;
    style?: any;
    nested?: Nested;

    a_tuple?: [number, string];

    object_of_string?: {[k: string]: string};
    object_of_components?: {[k: string]: JSX.Element};
    ignored_prop?: {ignore: {me: string}};
    union_enum?: number | 'small' | 'large';
    boolean_enum?: boolean | 'small' | 'large';
    duplicated_enum?: boolean | number | number;
};

export type WrappedHTMLProps = {
    children?: React.ReactNode;
    id?: string;
} & Pick<React.ButtonHTMLAttributes<any>, 'autoFocus'>

export type RequiredChildrenComponentProps = {
  children: React.ReactNode;
}
