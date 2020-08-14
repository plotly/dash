import {ITextColumn} from 'dash-table/components/Table/props';
import {isNully, reconcileNull} from './null';
import {IReconciliation} from './reconcile';

export function coerce(
    value: any,
    options: ITextColumn | undefined
): IReconciliation {
    return isNully(value)
        ? reconcileNull(value, options)
        : typeof value === 'string'
        ? {success: true, value}
        : {success: true, value: JSON.stringify(value)};
}

export function validate(
    value: any,
    options: ITextColumn | undefined
): IReconciliation {
    return typeof value === 'string'
        ? {success: true, value}
        : reconcileNull(value, options);
}
