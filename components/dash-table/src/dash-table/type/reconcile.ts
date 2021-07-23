import * as R from 'ramda';

import {
    ChangeAction,
    ChangeFailure,
    ColumnType,
    IColumnType
} from 'dash-table/components/Table/props';

import reconcileAny from './any';
import {coerce as coerceNumber, validate as validateNumber} from './number';
import {coerce as coerceText, validate as validateText} from './text';
import {coerce as coerceDate, validate as validateDate} from './date';
import {OptionalPluck} from 'core/type';

export interface IReconciliation {
    action?: ChangeAction;
    failure?: ChangeFailure;
    success: boolean;
    value?: any;
}

type Options = OptionalPluck<IColumnType, 'on_change'> &
    OptionalPluck<IColumnType, 'type'> &
    OptionalPluck<IColumnType, 'validation'>;

function getCoercer(c: Options): (value: any, c?: any) => IReconciliation {
    switch (c.type) {
        case ColumnType.Numeric:
            return coerceNumber;
        case ColumnType.Text:
            return coerceText;
        case ColumnType.Datetime:
            return coerceDate;
        case ColumnType.Any:
        default:
            return reconcileAny;
    }
}

function getValidator(c: Options): (value: any, c?: any) => IReconciliation {
    switch (c.type) {
        case ColumnType.Numeric:
            return validateNumber;
        case ColumnType.Text:
            return validateText;
        case ColumnType.Datetime:
            return validateDate;
        case ColumnType.Any:
        default:
            return reconcileAny;
    }
}

function doAction(value: any, c: Options) {
    const action =
        (c && c.on_change && c.on_change.action) || ChangeAction.Coerce;

    switch (action) {
        case ChangeAction.Coerce:
            return {action, ...getCoercer(c)(value, c)};
        case ChangeAction.None:
            return {success: true, value, action};
        case ChangeAction.Validate:
            return {action, ...getValidator(c)(value, c)};
    }
}

function doFailureRecovery(result: IReconciliation, c: Options) {
    // If c/v unsuccessful, process failure
    const failure =
        (c && c.on_change && c.on_change.failure) || ChangeFailure.Reject;
    result.failure = failure;

    if (failure === ChangeFailure.Default) {
        const validationDefault = c && c.validation && c.validation.default;
        const defaultValue = R.isNil(validationDefault)
            ? null
            : validationDefault;
        result.success = true;
        result.value = defaultValue;
    } else if (failure === ChangeFailure.Accept) {
        result.success = true;
    }

    return result;
}

export default (value: any, c: Options) => {
    const res: IReconciliation = doAction(value, c);

    if (res.success) {
        return res;
    }

    return doFailureRecovery(res, c);
};
