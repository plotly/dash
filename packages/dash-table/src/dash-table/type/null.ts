import {ITypeColumn} from 'dash-table/components/Table/props';
import {IReconciliation} from './reconcile';

export const reconcileNull = (
    value: any,
    options: ITypeColumn | undefined
): IReconciliation => {
    const allowNull = Boolean(
        options && options.validation && options.validation.allow_null
    );
    const nully = isNully(value);

    return {
        success: nully && allowNull,
        value: nully ? null : value
    };
};

export const isNully = (value: any) =>
    value === undefined ||
    value === null ||
    (typeof value === 'number' && (isNaN(value) || !isFinite(value)));
