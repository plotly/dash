import {reduce, toPairs, assoc} from 'ramda';
import {toCamelCase} from 'dash-table/derived/style/py2jsCssProperties';

const objPropsToCamel = (value: any): any =>
    value !== null && typeof value === 'object'
        ? reduce(
              (acc, [key, pValue]: [string, any]) =>
                  assoc(
                      toCamelCase(key.split('_')),
                      objPropsToCamel(pValue),
                      acc
                  ),
              {} as any,
              toPairs(value)
          )
        : Array.isArray(value)
        ? value.map(objPropsToCamel, value)
        : value;

export default objPropsToCamel;
