import isNumeric from 'fast-isnumeric';

import { INumberColumn } from 'dash-table/components/Table/props';
import { reconcileNull, isNully } from './null';
import { IReconciliation } from '.';

export function coerce(value: any, options: INumberColumn | undefined): IReconciliation {
    return isNumeric(value) ?
        { success: true, value: +value } :
        reconcileNull(value, options);
}

export function validate(value: any, options: INumberColumn | undefined): IReconciliation {
    return typeof value === 'number' && !isNully(value) ?
        { success: true, value } :
        reconcileNull(value, options);
}